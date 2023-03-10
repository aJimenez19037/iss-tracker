# Containerized Flask Application for Analyzing International Space Station Data 

## Purpose

The purpose of this project is to make working with and looking at the International Space Station data ephemeris much easier. Ephemeris' data is updated every 3 days and is publicly available data that allows the user to be able to see the ISS position, velocity, location, and more. This data is used and maintained by ISS Trajectory Operations and Planning Officer. This data is vital for maintaining communications links, planning visiting vehicle encounters, and maintaining the ISS away from possible collisions. This project makes the data easier to read and allows users to build upon the ISS tracker for their own personal projects. 

## Files in Repository

1. Dockerfile:            Dockerfile to containerize iss_tracker.py script
2. iss_tracker.py:        Flask application that creates server-client model.
3. docker-compose.yml:    Compose file to automate the deployment of flask application.

## Ways to Build Container

For both methods of building the container, you must clone this repository onto your device. Furthermore, you need to build the container within the repository with the "Dockerfile" and "iss_tracker.py".

### Downloading from source
Downloading from source makes it easier to edit and build your own container. Clone repository into your device:
```console
[user]:$git clone [clone link from github]
```
Build containerized app:
```console
[user]:$docker build -t <dockerhubusername>/iss_tracker.py:<version> .
```

### Pull a pre-containerized copy of the app from Docker Hub

You are also able to pull a pre-containerized copy.
```console
[user]:$ docker pull antjim19037/iss_tracker:1.0
[user]:$ docker build -t antjim19037/iss_tracker:1.0 .
```

## Running container
Through the use of the docker-compose.yml file we are able to run the flask app using the line below:
```console
[user]$docker-compose up 
```
If you have downloaded the application from source and created your own image then you will need to edit the docker-compose file image line to one that matches your image. 

## ISS Data 

The public [ISS Data](https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml) can be downloaded as a txt or xml file. Within the python script the 'request' library is used to extract the data from the website. 
```console
[user]:$RUN pip3 install requests==2.22.0
```
The script then uses the 'xmltodict' library to convert the xml data to a dictionary object.
```console
[user]:$RUN pip3 install xmltodict==0.13.0
```
Running the lines above is not necessary as the container has them installed. It would only be necessary to run the lines if you were looking to run the flask application without the contaner in your terminal. 

## Flask app

Flask is a Python library and framework for building web servers. This is used to create a server where the user can make request and the server will return an appropriate resonse.   

## Usage
After running the container, in another terminal we can now make request using the curl command.

### [/help]
The /help route will return a list of all the possible routes and what they do. It also contains instructions/information about the use of queries.In the second terminal run the command:
```console
[user]:$curl localhost:5000/help
usage: curl localhost:5000[Options]

     Options:
       [/]                             Return entire data set
       [/epochs]                       Return list of all Epochs in the data set
       [/epochs?limit=int&offset=int]  Return modified list of Epochs given query parameters.
                                       Offset parameter: returns the data after the inputted value.
                                       Limit parameter: limits number of epochs returned.
                                       **** Note: When using multiple queries use of single quotes will be necessary (' ').
       [/epochs/<epoch>]               Return state vectors for a specific Epoch from the data set
       [/epochs/<epoch>/speed]         Return instantaneous speed for a specific Epoch in the data set
       [/help]                         Return help text (as a string) that briefly describes each route
       [/delete-data]                  Delete all data from the dictionary object. In the terminal curl should be followed by -X DELETE
       [/post-data]                    Reload the dictionary object with data from the web. In the terminal curl should be followed by -X POST
       [/comment]                      Return ‘comment’ list obejct from ISS data
       [/header]                       Return ‘header’ dict object from ISS data
       [/metadata]                     Return ‘metadata’ dict object from ISS data
       [/epochs/<epoch>/location]      Return latitude, longitude, altitude, and geoposition for given Epoch
       [/now]                          Return latitude, longitude, altidue, and geoposition for Epoch that is nearest in time
```

### [/]
The first route ("/") will result in the entire dataset being returned. You will see all of the information wihtin the XML file as a dictionary. As you can see there is metadata as well as other data that you can sift through. The end of your output will look like: 
```console
[user]:$curl localhost:5000/
...
...
   },
          "metadata": {
            "CENTER_NAME": "EARTH",
            "OBJECT_ID": "1998-067-A",
            "OBJECT_NAME": "ISS",
            "REF_FRAME": "EME2000",
            "START_TIME": "2023-048T12:00:00.000Z",
            "STOP_TIME": "2023-063T12:00:00.000Z",
            "TIME_SYSTEM": "UTC"
          }
        }
      },
      "header": {
        "CREATION_DATE": "2023-049T01:38:49.191Z",
        "ORIGINATOR": "JSC"
      }
    }
  }
}
```
### [/epochs]
Result in a list of epochs being returned. Within this output you will see the epoch as well as its index value. The end of your output will look like: 
```console
[user]:$curl localhost:5000/epochs
...
...
  {
    "2023-070T11:44:00.000Z": 5656
  },
  {
    "2023-070T11:48:00.000Z": 5657
  },
  {
    "2023-070T11:52:00.000Z": 5658
  },
  {
    "2023-070T11:56:00.000Z": 5659
  },
  {
    "2023-070T12:00:00.000Z": 5660
  }
]
```
Through the use of queries we can limit the number of epochs we are seeing. You can see here that we chose to start at epoch 10 and are limiting the output to only 5 epochs.  
```console
$curl 'localhost:5000/epochs?start=10&limit=5'
[
  {
    "2023-055T12:40:00.000Z": 10
  },
  {
    "2023-055T12:44:00.000Z": 11
  },
  {
    "2023-055T12:48:00.000Z": 12
  },
  {
    "2023-055T12:52:00.000Z": 13
  },
  {
    "2023-055T12:56:00.000Z": 14
  }
]
```
### [/epochs/<string:epoch>]  
Return information from the epoch requested based on epoch requested within the route. Within the information you will find its x,y,z positions and x,y,z velocity. The units are km and km/s.
```console
[user]:$ curl localhost:5000/epochs/2023-082T12:00:00.000Z
{
  "X": "5503.7762252426101",
  "X_DOT": "-3.1022300368795301",
  "Y": "3965.17406451955",
  "Y_DOT": "3.6253043212810101",
  "Z": "437.90169769306402",
  "Z_DOT": "5.9928466431153904"
}
```
The fourth route (/epochs/<string:epoch>/speed) will return the velocity of the epoch requested in the route as a dictionary. The result will be the scalar value of the velocity. The result will look like:
```console
[user]:$ curl localhost:5000/epochs/2023-082T12:00:00.000Z/speed
{
  "Velocity": 7.6603442162552815,
  "units": "km/s"
}
```
### [/delete-data]
Deletes all of the ISS data gethered through the use of the 'requests' library.
```console
[user]:$curl -X DELETE localhost:5000/delete-data
You have deleted data that was loaded in.
```
### [/post-data]
If there is no data, you are able to load in the latest data using this route.
```console
[user]:$curl -X POST localhost:5000/post-data
You have loaded in data.
```
### [/comment]
Returns data found in within the comment key in the ISS data. You are given information about the ISS itself, events, and more. 
```console
[user]$curl localhost:5000/comment
[
  "Units are in kg and m^2",
  "MASS=473291.00",
  "DRAG_AREA=1421.50",
  "DRAG_COEFF=2.80",
  "SOLAR_RAD_AREA=0.00",
  "SOLAR_RAD_COEFF=0.00",
  "Orbits start at the ascending node epoch",
  "ISS first asc. node: EPOCH = 2023-03-08T12:50:10.295 $ ORBIT = 2617 $ LAN(DEG) = 108.61247",
  "ISS last asc. node : EPOCH = 2023-03-23T11:58:44.947 $ ORBIT = 2849 $ LAN(DEG) = 32.65474",
  "Begin sequence of events",
  "TRAJECTORY EVENT SUMMARY:",
  null,
  "|       EVENT        |       TIG        | ORB |   DV    |   HA    |   HP    |",
  "|                    |       GMT        |     |   M/S   |   KM    |   KM    |",
  "|                    |                  |     |  (F/S)  |  (NM)   |  (NM)   |",
  "=============================================================================",
  "GMT067 Reboost        067:19:47:00.000             0.6     428.1     408.4",
  "(2.0)   (231.1)   (220.5)",
  null,
  "Crew05 Undock         068:22:00:00.000             0.0     428.7     409.6",
  "(0.0)   (231.5)   (221.2)",
  null,
  "SpX27 Launch          074:00:30:00.000             0.0     428.3     408.7",
  "(0.0)   (231.2)   (220.7)",
  null,
  "SpX27 Docking         075:12:00:00.000             0.0     428.2     408.6",
  "(0.0)   (231.2)   (220.6)",
  null,
  "=============================================================================",
  "End sequence of events"
]
```
### [/header]
Returns information found in the header key of the ISS data. Results shw creation date of the data and that it originated from the Johnson Space Center
```console
[user]:$ curl localhost:5000/header
{
  "CREATION_DATE": "2023-067T21:02:49.080Z",
  "ORIGINATOR": "JSC"
}
```
### [/metadata]
Returns information found in the metadata key of the ISS data. 
```console
[user]:$ curl localhost:5000/metadata
{
  "CENTER_NAME": "EARTH",
  "OBJECT_ID": "1998-067-A",
  "OBJECT_NAME": "ISS",
  "REF_FRAME": "EME2000",
  "START_TIME": "2023-067T12:00:00.000Z",
  "STOP_TIME": "2023-082T12:00:00.000Z",
  "TIME_SYSTEM": "UTC"
}
```
### [/epoch/str:epoch/location]
Gives information about the location of the ISS at the specific epoch. Altitude units are km. When the ISS is over the ocean geopy does not return a geoposition. However, if it is over land it will output the country it was over at the time. 
```console
[user]:$ curl localhost:5000/epochs/2023-082T12:00:00.000Z/location
{
  "ALTITUDE": 426.42233125654093,
  "GEO_POSITION": "NONE: ISS is likely over the ocean",
  "LATITUDE": 3.693612400678767,
  "LONGITUDE": 67.77071661260686
}
```
### [/now]
Return the location information of the closest epoch to our actual time. There is a key that mentions how much time has spanned since the closest epoch. It also returns information on its current velocity. 
```console
[user]$:curl localhost:5000/now
{
  "closest_epoch": "2023-068T09:24:17.828Z",
  "location": {
    "ALTITUDE": {
      "units": "km",
      "value": 416.68868745287455
    },
    "GEO_POSITION": {
      "ISO3166-2-lvl4": "CA-QC",
      "country": "Canada",
      "country_code": "ca",
      "state": "Quebec"
    },
    "LATITUDE": 49.8876375336817,
    "LONGITUDE": -75.81563250554203
  },
  "seconds_from_now": 55.47815942764282,
  "speed": {
    "Velocity": 7.665863354222683,
    "units": "km/s"
  }
}
```
   
### Pushing the image to DockerHub
If you wish to push the image to dockerhub:
```
$docker push <dockerhubusername>/<script name without the .py>:<version>
```
