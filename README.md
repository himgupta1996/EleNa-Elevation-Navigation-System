# EleNa-Elevation-Navigation-System
### Final project deliverable submission for COMPSCI 520, Theory and Practice of Software Engineering
### SUBMITTED BY: Maroon5  

Given a start location in the form of latitiude and longitude as well as end location, Elevation-based Navigation
(EleNa) is an application that finds a route which either maximizes or minimizes the elevation gain according to the user preference.
The route returned is x% of the shortest path between given location where x is also a variable based on user input.


Maximizing the elevation gain would be useful for health enthusiasts who are looking to perform intense workout by
jogging or bicycling through elevated path whereas old people or people who wants to avoid climbing elevated roads because of health issues can 
minimize elevation gain.

# Video Explanation of Architecture/Demo 
The demo video is located here: https://youtu.be/hskTD87tZUE

# Architecture
![Alt text](files/ArchitectureDiagram.PNG?raw=true "Elena")


# UI
![Alt text](files/Image1.jpeg?raw=true "ElenaUI Image 1")
![Alt text](files/Image2.jpeg?raw=true "ElenaUI Image 2")

#  Instructions for application setup and execution

## How to install ?
The following versions have been used for building and installing the dependencies
* Python 3.8

Create virtual environment ( This is an optional step, the application can be install using system level python as well)
https://docs.python.org/3/tutorial/venv.html
```
(Optional)
Create a virtual environment : virtualenv virtualenvname
Activate virtual environment : source virtualenvname activate
```
Install dependencies / requirements using the command

```
pip install -r src/requirements.txt

```

## How to build the app ?
Run Flask server using command: "python -m flask run"

## How to run app ?

After installing the required dependencies and building the app server as mentioned above, follow the steps to start the server.


* The flask server server would start by on port ``5000``. Please make sure the port is free for use.
* Flask server URL ``http://127.0.0.1:5000/``
   
# Test Suites

Unit test have been added for our application.

Unit test location : ``tests/test.py``

# Developer Documentation

The Developer documentation pdf can be found at : `` doc/EleNA Developer doc.pdf``
