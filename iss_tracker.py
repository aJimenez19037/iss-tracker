#need to add type error to functions that take in a string
import requests
import xmltodict
import math
import time
from flask import Flask, request
from geopy.geocoders import Nominatim

app = Flask(__name__)

global data
url = 'https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml'
response = requests.get(url)
data = xmltodict.parse(response.text)
def get_data() -> dict:
    """Gather data from ISS website

    Gather XML file from the ISS website and converts it into a dicitionary.

    Args:
       None

    Returns:
        Dictionary: Entire data set.
    """    
    global data
    url = 'https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml'
    response = requests.get(url)
    data = xmltodict.parse(response.text)
    return data
def find_index(epoch:str) -> int:
    """Find Epoch Index
    
    Based on the inputted epoch by the user, return the index of that specific epoch.

    Args: 
      String: Epoch of interest.

    Returns
      Integer: Index of the eopch that the user is looking for. 
    """
    epochs = data['ndm']['oem']['body']['segment']['data']['stateVector']
    
    for d in range(len(epochs)):
        if epoch == epochs[d]['EPOCH']:
            return d
        
@app.route('/', methods = ['GET'])#returns the entire data set
def get_data_set() -> dict:
    """Return entire data set from ISS Website

    Takes in request using flask to return entire set. 

    Args:
       None

    Returns:
        Dictionary: Entire ephimeris data set.
    """
    return data
    

@app.route('/epochs', methods = ['GET'])#A list of all Epochs in the data set
def get_epoch_list() -> list:
    """Return list of all Epochs in the data set

    Takes in request using flask and returns a list of all the epochs in the data set.

    Args:
       None

    Returns:
        List: List of dictionaries with all the epochs and their index value.
    """
    epochs_list = []
    offset = request.args.get('offset',0)
    if offset:
        try:
            offset = int(offset)
        except ValueError:
            return "Invalid offset parameter; offset must be an integer.\n"
    try:
        5>=int(offset)
    except ValueError:
        return "Invalid offset parameter"
    try:
        epochs = data['ndm']['oem']['body']['segment']['data']['stateVector']
    except KeyError:
        #return epochs_list
        return "Data is empty. Try loading the data using $curl url -X POST 'localhost:5000/post-data'\n"
    epochs = data['ndm']['oem']['body']['segment']['data']['stateVector']
    limit = request.args.get('limit',len(epochs))
    if limit:
        try:
            limit = int(limit)
        except ValueError:
            return "Invalid limit parameter; limit must be an integer.\n"
    try:
        if len(epochs_list) == int(limit):
            i=5
    except ValueError:
        return "Invalid limit parameter\n"
    counter = 0;
    for d in range(len(epochs)):
        
        if (d >= int(offset)):
            epochs_list.append({epochs[d]['EPOCH']:d})
        if (len(epochs_list) == int(limit)):
            return epochs_list
    return epochs_list


@app.route('/epochs/<string:epoch>', methods = ['GET'])#State vectors for a specific Epoch from the data set
def get_state_vector(epoch:str) -> dict:
    """Return specific epoch

    Takes in request using flask and returns specific epoch in the list.

    Args:
       String: Epoch of interest/

    Returns:
        Dictionary:  Data related to that epoch. For example:
        
        {"X": "5503.7762252426101",
         "X_DOT": "-3.1022300368795301",
         "Y": "3965.17406451955",
         "Y_DOT": "3.6253043212810101",
         "Z": "437.90169769306402",
         "Z_DOT": "5.9928466431153904"}
    """
    
    
    try:
        epochs = data['ndm']['oem']['body']['segment']['data']['stateVector']
    except KeyError:
        
        return "Data is empty. Try loading the data using $curl url -X POST 'localhost:5000/post-data'"
    
    epochs = data['ndm']['oem']['body']['segment']['data']['stateVector']
    exist = False
    for x in epochs:
        if x['EPOCH'] == epoch:
            exist = True
    if exist == False:
        return "Epoch does not exist\n"
    i = find_index(epoch)
    return {"X": epochs[i]['X']['#text'],
            "Y": epochs[i]['Y']['#text'],
            "Z": epochs[i]['Z']['#text'],
            "X_DOT": epochs[i]['X_DOT']['#text'],
            "Y_DOT": epochs[i]['Y_DOT']['#text'],
            "Z_DOT": epochs[i]['Z_DOT']['#text']}
@app.route('/epochs/<string:epoch>/speed', methods = ['GET'])#Instantaneous speed for a specific Epoch in the data set (math required!)
def get_instantaneous_speed(epoch:str) -> dict:
    """Return Epoch's speed

    Based on requested epoch number calculate and return its velocity.

    Args:
       String: Epoch of interest.

    Returns:
        Dictionary: Containing velocity of the epoch and its units. For example:

        {"Velocity": 7.6603442162552815,
         "units": "km/s"}
    """
    try:
        epochs = data['ndm']['oem']['body']['segment']['data']['stateVector']
    except KeyError:
        return "Data is empty. Try $curl -X POST localhost::5000/post-data"
    
    epochs = data['ndm']['oem']['body']['segment']['data']['stateVector']
    exist = False
    for x in epochs:
        if x['EPOCH'] == epoch:
            exist = True
    if exist == False:
        return "Epoch does not exist\n"
    i = find_index(epoch)
    x_velocity = float(epochs[i]['X_DOT']['#text'])
    y_velocity = float(epochs[i]['Y_DOT']['#text'])
    z_velocity = float(epochs[i]['Z_DOT']['#text'])
    velocity = math.sqrt((x_velocity ** 2) + (y_velocity ** 2) + (z_velocity ** 2))
    return {'Velocity':velocity, 'units': 'km/s'}

@app.route('/help', methods = ['GET'])#returns the entire data set
def help() -> str:
    """Display helpful information

    Display information regarding usage of routes and queries.

    Args: 
      NONE
    
    Returns:
      String: Brief description of all available routes plus their methods.

    """
    message = "usage: curl localhost:5000[Options]\n\n     Options: \n       [/]                             Return entire data set \n       [/epochs]                       Return list of all Epochs in the data set \n       [/epochs?limit=int&offset=int]  Return modified list of Epochs given query parameters. \n                                       Offset parameter: returns the data after the inputted value. \n                                       Limit parameter: limits number of epochs returned.\n                                       **** Note: When using multiple queries use of single quotes will be necessary (' '). \n       [/epochs/<epoch>]               Return state vectors for a specific Epoch from the data set \n       [/epochs/<epoch>/speed]         Return instantaneous speed for a specific Epoch in the data set\n       [/help]                         Return help text (as a string) that briefly describes each route \n       [/delete-data]                  Delete all data from the dictionary object. In the terminal curl should be followed by -X DELETE \n       [/post-data]                    Reload the dictionary object with data from the web. In the terminal curl should be followed by -X POST \n       [/comment]                      Return ‘comment’ list obejct from ISS data \n       [/header]                       Return ‘header’ dict object from ISS data\n       [/metadata]                     Return ‘metadata’ dict object from ISS data\n       [/epochs/<epoch>/location]      Return latitude, longitude, altitude, and geoposition for given Epoch\n       [/now]                          Return latitude, longitude, altidue, and geoposition for Epoch that is nearest in time \n"
    return message

@app.route('/delete-data', methods = ['DELETE'])
def delete_data() -> str:
    """Delete data

    Deletes data contained within the global variable data

    Args: 
      NONE

    Returns:
      String: Explaining that data was deleted.

    """
    data.clear()
    return "Deleted data.\n"

@app.route('/post-data', methods = ['POST'])
def post_data() -> str:
    """Load in data

    Command to load in data. Helpful for after having deleted the data.

    Args: 
      NONE

    Returns:
      String: explaining that data has been loaded in.

    """
    global data
    data = get_data()
    return "You have loaded in data. \n"

@app.route('/comment', methods = ['GET'])
def get_comment() -> list:
    """Get Comment Data

    Returns the data under the key "COMMENT" from the ISS data.

    Args:
      NONE

    Returns:
      List: Data in comment key.

    """
    try:
        commentList = data['ndm']['oem']['body']['segment']['data']['COMMENT']
    except KeyError:
        return "Data is empty. Try loading the data using $curl url -X POST 'localhost:5000/post-data'"
    
    return data['ndm']['oem']['body']['segment']['data']['COMMENT']

@app.route('/header', methods = ['GET'])
def get_header() -> dict:
    """Get Header Data

    Route that returns the ‘header’ dictionary object from the ISS data.

    Args:
      NONE

    Returns:  
      Dictionary: Creation date and originator. For example:

      {"CREATION_DATE": "2023-067T21:02:49.080Z",
       "ORIGINATOR": "JSC"}

    """
    try:
        commentList = data['ndm']['oem']['header']
    except KeyError:
        return "Data is empty. Try loading the data using $curl url -X POST 'localhost:5000/post-data'"
    return data['ndm']['oem']['header']

@app.route('/metadata', methods = ['GET'])
def get_metadata() -> dict:
    """Get Metadata Data

    Route that returns the ‘metadata’ dictionary object from the ISS data.

    Args:
      NONE

    Returns:
      Dictionary: Informaton from 'metadata' key. For example:

      {"CENTER_NAME": "EARTH",
       "OBJECT_ID": "1998-067-A",
       "OBJECT_NAME": "ISS",
       "REF_FRAME": "EME2000",
       "START_TIME": "2023-067T12:00:00.000Z",
       "STOP_TIME": "2023-082T12:00:00.000Z",
       "TIME_SYSTEM": "UTC"}

    """
    try:
        metaDict = data['ndm']['oem']['body']['segment']['metadata']
    except KeyError:
        return "Data is empty. Try loading the data using $curl url -X POST 'localhost:5000/post-data'"
    return data['ndm']['oem']['body']['segment']['metadata']

@app.route('/epochs/<string:epoch>/location', methods = ['GET'])
def get_location(epoch:str) -> dict:
    """Get Location at Epoch

    Route that returns latitude, longitude, altitude, and geoposition for a given epoch.

    Args:
      String: Epoch of interest.

    Returns:
      Dictionary:  Contains {latitude, longitude, altitude, and geoposition}. For example:

      {"ALTITUDE": 426.42233125654093,
       "GEO_POSITION": "NONE: ISS is likely over the ocean",
       "LATITUDE": 3.693612400678767,
       "LONGITUDE": 67.77071661260686}

    """
    
    try:
        epochs = data['ndm']['oem']['body']['segment']['data']['stateVector']
    except KeyError:
        return "Data is empty. Try loading the data using $curl url -X POST 'localhost:5000/post-data'"
    epochs = data['ndm']['oem']['body']['segment']['data']['stateVector']#list of epoch + state vector
    exist = False
    for x in epochs:
        if x['EPOCH'] == epoch:
            exist = True
    if exist == False:
        return "Epoch does not exist\n"
    i = find_index(epoch)
    MEAN_EARTH_RADIUS = 6371.07103 #km
    x = float(epochs[i]['X']['#text'])
    y = float(epochs[i]['Y']['#text'])
    z = float(epochs[i]['Z']['#text'])
    EPOCH = epochs[i]['EPOCH']#string that has time 
    hrs = float(EPOCH[9:11])
    mins = float(EPOCH[12:14])
    lat = math.degrees(math.atan2(z, math.sqrt(x**2 + y**2)))
    lon = math.degrees(math.atan2(y, x)) - ((hrs-12)+(mins/60))*(360/24) + 32
    alt = math.sqrt(x**2 + y**2 + z**2) - MEAN_EARTH_RADIUS
    geocoder = Nominatim(user_agent=__name__)
    try:
        location =  geocoder.reverse((lat, lon), zoom=5, language='en')
    except Error as e:
        return f'Geopy returned an error - {e}'
    
    geoloc = geocoder.reverse((lat, lon), zoom=5, language='en')
    try:
        {'LATITUDE': lat, 'LONGITUDE': lon, 'ALTITUDE':alt, 'GEO_POSITION':geoloc.raw['display_name']}
    except AttributeError:
        return {'LATITUDE': lat, 'LONGITUDE': lon, 'ALTITUDE':alt, 'GEO_POSITION':'NONE: ISS is likely over the ocean'}
    
    return {'LATITUDE': lat, 'LONGITUDE': lon, 'ALTITUDE':{'value':alt,'units':'km'}, 'GEO_POSITION':geoloc.raw['address']}

@app.route('/now', methods = ['GET'])
def get_location_now() -> dict:
    """Get Location at Epoch

    Route that returns information on the epoch closest to real time.

    Args:
      NONE

    Returns:
      Dictionary: Contains keys latitude, longitude, altitude, geoposition, velocity, seconds away from current time, and the epoch itself.

    """

    try:
        epochs = data['ndm']
    except KeyError:
        return "Data is empty. Try loading the data using $curl url -X POST 'localhost:5000/post-data'"    
    time_now = time.time()
    epochs = data['ndm']['oem']['body']['segment']['data']['stateVector']
    closest_epoch = 0
    closest_epoch_difference = 10000000000000;
    closest_epoch_time = 0;
    for i in range(len(epochs)):
        epoch = epochs[i]['EPOCH']
        time_epoch = time.mktime(time.strptime(epoch[:-5], '%Y-%jT%H:%M:%S'))        # gives epoch (eg 2023-058T12:00:00.000Z) time in seconds since unix epoch
        difference = abs(time_now - time_epoch)
        if (difference <= closest_epoch_difference):
            closest_epoch_difference = difference
            closest_epoch = i
            closest_epoch_time = time_epoch
        
        
    return {'closest_epoch':epochs[closest_epoch]['EPOCH'], 'seconds_from_now':abs(time_now - closest_epoch_time),'location': get_location(epochs[closest_epoch]['EPOCH']), 'speed':get_instantaneous_speed(epochs[closest_epoch]['EPOCH']) }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

