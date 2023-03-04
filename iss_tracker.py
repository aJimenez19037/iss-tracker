import requests
import xmltodict
import math
from flask import Flask, request
from geopy.geocoders import Nominatim

app = Flask(__name__)

global data
url = 'https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml'
response = requests.get(url)
data = xmltodict.parse(response.text)
def get_data() -> dict:
    """Gather data from ISS website

    Gather XML file from the ISS website and converts it into a dicitionary

    Args:
       None

    Returns:
        Dictionary with entire dataset.
    """    
    global data
    url = 'https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml'
    response = requests.get(url)
    data = xmltodict.parse(response.text)
    return data

@app.route('/', methods = ['GET'])#returns the entire data set
def get_data_set() -> dict:
    """Return entire data set from ISS Website

    Takes in request using flask to return entire set. 

    Args:
       None

    Returns:
        Dictionary with entire dataset.
    """
    return data
    

@app.route('/epochs', methods = ['GET'])#A list of all Epochs in the data set
def get_epoch_list() -> list:
    """Return list of all Epochs in the data set

    Takes in request using flask and returns a list of all the epochs in the dataset.

    Args:
       None

    Returns:
        List of dictionaries with all the epochs and their index value.
    """
    epochs_list = []
    offset = request.args.get('offset',0)
    if offset:
        try:
            offset = int(offset)
        except ValueError:
            return "Invalid offset parameter; offset must be an integer.\n"
    try:
        epochs = data['ndm']['oem']['body']['segment']['data']['stateVector']
    except KeyError:
        #return epochs_list
        return "Data is empty. Try loading the data using $curl url -X POST '127.0.0.1:5000/post-data'"
    epochs = data['ndm']['oem']['body']['segment']['data']['stateVector']
    limit = request.args.get('limit',len(epochs))
    if limit:
        try:
            limit = int(limit)
        except ValueError:
            return "Invalid limit parameter; limit must be an integer.\n"
    counter = 0;
    for d in range(len(epochs)):
        if (d >= int(offset)):
            epochs_list.append({epochs[d]['EPOCH']:d})
        if (len(epochs_list) == int(limit)):
            return epochs_list
    return epochs_list


@app.route('/epochs/<int:epoch>', methods = ['GET'])#State vectors for a specific Epoch from the data set
def get_each_vectors(epoch:int) -> dict:
    """Return specific epoch

    Takes in request using flask and returns specific epoch in the list.

    Args:
       Takes in an integer that is the ith epoch in the list

    Returns:
        Dictionary with all of the data related to that epoch.
    """
    
    
    try:
        epochs = data['ndm']['oem']['body']['segment']['data']['stateVector']
    except KeyError:
        #return {}
        return "Data is empty. Try loading the data using $curl url -X POST '127.0.0.1:5000/post-data'"
    epochs = data['ndm']['oem']['body']['segment']['data']['stateVector']
    if epoch:
        try:
            epochs[epoch]
        except IndexError:
            return "Input is too large. Try an int between 0 and " + str(len(epochs)-1) + "\n"
    return {"X": epochs[epoch]['X']['#text'], "Y": epochs[epoch]['Y']['#text'],"Z": epochs[epoch]['Z']['#text'],"X_DOT": epochs[epoch]['X_DOT']['#text'], "Y_DOT": epochs[epoch]['Y_DOT']['#text'],"Z_DOT": epochs[epoch]['Z_DOT']['#text']}


@app.route('/epochs/<int:epoch>/speed', methods = ['GET'])#Instantaneous speed for a specific Epoch in the data set (math required!)
def get_instantaneous_speed(epoch:int) -> dict:
    """Return Epoch's speed

    Based on requested epoch number calculate and return its velocity.

    Args:
       Takes in an integer that is the ith epoch in the list

    Returns:
        Dictionary containing the velocity of the epoch
    """
    try:
        epochs = data['ndm']['oem']['body']['segment']['data']['stateVector']
    except KeyError:
        return "Data is empty. Try $curl -X POST localhost:5000/post-data"
    
    epochs = data['ndm']['oem']['body']['segment']['data']['stateVector']
    i = int (epoch)
    x_velocity = float(epochs[i]['X_DOT']['#text'])
    y_velocity = float(epochs[i]['Y_DOT']['#text'])
    z_velocity = float(epochs[i]['Z_DOT']['#text'])
    velocity = math.sqrt((x_velocity ** 2) + (y_velocity ** 2) + (z_velocity ** 2))
    return {'Velocity':velocity}

@app.route('/help', methods = ['GET'])#returns the entire data set
def help() -> str:
    """Display helpful information

    Display information regarding usage of routes and queries

    Args: 
      NONE
    
    Returns:
      String that gives a brief description of all available routes plus their methods.

    """
    message = "usage: curl 127.0.0.1:5000[Options]\n\n     Options: \n       [/]                             Return entire data set \n       [/epochs]                       Return list of all Epochs in the data set \n       [/epochs?limit=int&offset=int]  Return modified list of Epochs given query parameters. Offswt parameter makes it so that it returns the data after the inputted value. The limit parameter limits the number of epochs are returned. \n       [/epochs/<epoch>]               Return state vectors for a specific Epoch from the data set \n       [/epochs/<epoch>/speed]         Return instantaneous speed for a specific Epoch in the data set\n       [/help]                         Return help text (as a string) that briefly describes each route \n       [/delete-data]                  Delete all data from the dictionary object. In the terminal curl should be followed by -X DELETE \n       [/post-data]                    Reload the dictionary object with data from the web. In the terminal curl should be followed by -X POST \n **** Note if running multiple queries the use of single quotes will be necessary (' '). \n"
    return message

@app.route('/delete-data', methods = ['DELETE'])
def delete_data() -> str:
    """Delete data

    Deletes data contained within the global variable data

    Args: 
      NONE

    Returns:
      String explaining that the data was deleted

    """
    data.clear()
    return "You have deleted data that was loaded in.\n"
@app.route('/post-data', methods = ['POST'])
def post_data() -> str:
    """Load in data

    Command to load in data. Helpful for after having deleted the data.

    Args: 
      NONE

    Returns:
      String explaining that the data has been loaded.

    """
    global data
    data = get_data()
    return "You have loaded in data. \n"
# the next statement should usually appear at the bottom of a flask app
@app.route('/comment', methods = ['GET'])
def get_comment() -> list:
    """Get Comment Data

    Returns the data under the key "COMMENT" from the ISS data.

    Args:
      NONE

    Returns:
      List of comments

    """
    try:
        commentList = data['ndm']['oem']['body']['segment']['data']['COMMENT']
    except KeyError:
        return "Data is empty. Try loading the data using $curl url -X POST '127.0.0.1:5000/post-data'"
    
    return data['ndm']['oem']['body']['segment']['data']['COMMENT']

@app.route('/header', methods = ['GET'])
def get_header() -> dict:
    """Get Header Data

    Route that returns the ‘header’ dictionary object from the ISS data

    Args:
      NONE

    Returns:  
      Dictionary with creation date and originator

    """
    try:
        commentList = data['ndm']['oem']['header']
    except KeyError:
        return "Data is empty. Try loading the data using $curl url -X POST '127.0.0.1:5000/post-data'"
    return data['ndm']['oem']['header']

@app.route('/metadata', methods = ['GET'])
def get_metadata() -> dict:
    """Get Metadata Data

    Route that returns the ‘header’ dictionary object from the ISS data

    Args:
      NONE

    Returns:
      Dictionary with creation date and originator

    """
    try:
        metaDict = data['ndm']['oem']['body']['segment']['metadata']
    except KeyError:
        return "Data is empty. Try loading the data using $curl url -X POST '127.0.0.1:5000/post-data'"
    return data['ndm']['oem']['body']['segment']['metadata']

@app.route('/epochs/<int:epoch>/location', methods = ['GET'])
def get_location(epoch:int) -> dict:
    """Get Location at Epoch

    Route that returns latitude, longitude, altitude, and geoposition for a given epoch.

    Args:
      Takes in an integer that is the ith epoch in the list

    Returns:
      Dictionary with latitude, longitude, altitude, and geoposition,

    """
    
    try:
        epochs = data['ndm']['oem']['body']['segment']['data']['stateVector']
    except KeyError:
        return "Data is empty. Try loading the data using $curl url -X POST '127.0.0.1:5000/post-data'"
    epochs = data['ndm']['oem']['body']['segment']['data']['stateVector']#list of epoch + state vector
    MEAN_EARTH_RADIUS = 6371.07103 #km
    x = float(epochs[epoch]['X']['#text'])
    y = float(epochs[epoch]['Y']['#text'])
    z = float(epochs[epoch]['Z']['#text'])
    EPOCH = epochs[epoch]['EPOCH']#string that has time 
    hrs = float(EPOCH[9:11])
    mins = float(EPOCH[12:14])
    lat = math.degrees(math.atan2(z, math.sqrt(x**2 + y**2)))
    lon = math.degrees(math.atan2(y, x)) - ((hrs-12)+(mins/60))*(360/24) + 24
    alt = math.sqrt(x**2 + y**2 + z**2) - MEAN_EARTH_RADIUS
    
    geocoder = Nominatim(user_agent=__name__)
    geoloc = geocoder.reverse((lat, lon), zoom=15, language='en')
    
    return {'LATIIITUDE': lat, 'LONGITUDE': lon, "ALTITUDE":alt, 'GEO_POSITION':geoloc}

@app.route('/now', methods = ['GET'])
def get_location_now() -> dict:
    """Get Location at Epoch

    Route that returns latitude, longitude, altitude, and geoposition for a given epoch.

    Args:
      Takes in an integer that is the ith epoch in the list

    Returns:
      Dictionary with latitude, longitude, altitude, and geoposition,

    """

    try:
        epochs = data['ndm']['oem']['body']['segment']['data']['stateVector']
    except KeyError:
        return "Data is empty. Try loading the data using $curl url -X POST '127.0.0.1:5000/post-data'"
    return "Work in progress"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

