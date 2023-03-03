# Containerized Flask Application for Analyzing International Space Station Data 

## Purpose

The purpose of this project is to make working with and looking at the International Space Station data much easier. The project uses recent and publicly available data that allows the user to be able to see the ISS position and velocities. This project is a containerized through the use of Docker and uses Flask to create a server client model. Within this repository there is a dockerfile (Dockerfile) that containerizes the flask app. There is also the flask app (iss_tracker.py), which creates a framework where the user is able to send request and the server will return an appropriate response.

## ISS Data 

The data can be downloaded from this link: https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml
The data, however, is gathered through the python script from the link using the request library. The data is an XML file containing epochs with their respective position (x,y,z) and their velocity (x,y,z). The units are respectively km and km/s. While this is the information we are interested, the XML file also contains metadata and more. 

## Flask app

Flask is a Python library and framework for building web servers. This is used to create a server where the user can make request and the server will return an appropriate resonse.   

## Running the app through Docker

Before running the app you need to pull the Docker image from DockerHub:

```
$docker pull antjim19037/iss_tracker:hw05
```

We will then build the image:

```
$docker build -t antjim19037/iss_tracker:hw05 .
```

We will now run the Docker image:

```
$docker run -it --rm -p 5000:5000 antjim19037/iss_tracker:hw05
```
The -p flag takes the form <host port>:<container port> and connects the two ports. The Flask app is now running. You should see the ports which are being used. These ports can be used to make request:
```
 * Running on http://127.0.0.1:5000
 * Running on http://172.17.0.2:5000
```
## Making request
In another terminal we can now make request using the curl command. Below are examples of making request using the curl command. For some commands '-X [VERB]' is needed after curl. When making a query a '?' is placed at the end of the route followed by the query. If there are multiple queries being used the enveloping the route with single quotes ('') is needed. The help route is especially useful as it shows all the available routes/queries as well as what they do. 
```
$curl '127.0.0.1:5000/'
$curl 127.0.0.1:5000/help
$curl 127.0.0.1:5000/epochs?start=5
$curl '127.0.0.1:5000/epochs?start=5&limit=10'  
$curl 127.0.0.1:5000/epochs/<int:epoch> 
$curl 127.0.0.1:5000/epochs/<int:epoch>/speed
```
## Outputs
The first route ("/") will result in the entire dataset being returned. You will see all of the information wihtin the XML file as a dictionary. As you can see there is metadata as well as other data that you can sift through. The end of your output will look like: 
```
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
The second route (/epochs) will result in a list of epochs being returned. Within this output you will see the epoch as well as its index value. The index value lets us see how many epochs there are in the dataset, as well as it allows use to see that our queries are working correctly. The end of your output will look like: 
```
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
```
$curl '127.0.0.1:5000/epochs?start=10&limit=5'
   
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
   
The third route (/epochs/<int:epoch>) will return the information from the epoch requested based on the index inputted to the route. Within the information you will find the time of the epoch as well as its x,y,z positions and x,y,z velocity. The output will look like:
```
{
  "EPOCH": "2023-048T12:04:00.000Z",
  "X": {
    "#text": "-5998.4652356788401",
    "@units": "km"
  },
  "X_DOT": {
    "#text": "-2.8799691318087701",
    "@units": "km/s"
  },
  "Y": {
    "#text": "391.26194859011099",
    "@units": "km"
  },
  "Y_DOT": {
    "#text": "-5.2020406581448801",
    "@units": "km/s"
  },
  "Z": {
    "#text": "-3164.26047476555",
    "@units": "km"
  },
  "Z_DOT": {
    "#text": "4.8323394499086101",
    "@units": "km/s"
  }
}
```
The fourth route (/epochs/<int:epoch>/speed) will return the velocity of the epoch requested in the route as a dictionary. The result will be the scalar value of the velocity on km/s. The result will look like:
```
{
  "Velocity": 7.662046317290625
}
```
As mentioned, there are more routes that can be found through the use of the help route. 
   
## Building your own docker image
   
Some of you might want to build upon the code I have written. To do so you will need to build your own docker image. 
   
### Dockerfile
Tutorials on how to construct a dockerfile can be found online. The one in this project consist of the base image, installation of libraries needed for the python script to function and the version, copying the python script into the image, and command to be ran. 
 
### Building the image   
Once you have made the edits necessary you now need to build the docker image.
```
$docker build -t <dockerhubusername>/<script name without the .py>:<version> .
```
Running the image:
```
$docker run -it --rm -p <dockerhubusername>/<script name without the .py>:<version>
```   
### Pushing the image to DockerHub
If you wish to push the image to dockerhub:
```
$docker push <dockerhubusername>/<script name without the .py>:<version>
```
