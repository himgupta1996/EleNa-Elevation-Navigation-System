# EleNa-Elevation-Navigation-System

Given a start location in the form of latitiude and longitude as well as end location, Elevation-based Navigation
(EleNa) is an application that finds a route which either maximizes or minimizes the elevation gain according to the user preference.
The route returned is x% of the shortest path between given location where x is also a variable based on user input.


Maximizing the elevation gain would be useful for health enthusiasts who are looking to perform intense workout by
jogging or bicycling through elevated path whereas old people or people who wants to avoid climbing elevated roads because of health issues can 
minimize elevation gain.



# Architecture
![Alt text](files/ArchitectureDiagram.PNG?raw=true "Elena")


# UI
![Alt text](files/Image1.jpeg?raw=true "ElenaUI Image 1")
![Alt text](files/Image2.jpeg?raw=true "ElenaUI Image 2")

#  Instructions for application setup and execution

## How to install ?
The following versions have been used for building and installing the dependencies
* Python 2.7
* npm 6.14.8


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

npm install
```

## How to build and install ?


## How to run app ?

After installing the required dependencies and building the app server as mentioned above, follow the steps to start the server.


* The flask server server would start by on port ``8080``. Please make sure the port is free for use.
* Flask server URL ``http://127.0.0.1:8080/``
* Start the flask server using the command


```
python src/App/ElenaApp.py

```

* npm server would start on port ``3000``. Please make sure the port is free for use
* npm server URL : ``http://127.0.0.1:3000/``
* Start the npm server using the command

```
npm start
```
# Test Suites

Unit test have been added for our application.

Unit test location : `` server/tests/test_home.py``