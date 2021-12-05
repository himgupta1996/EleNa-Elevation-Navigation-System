from Elena.abstraction.abstraction import Graph_Abstraction
from Elena.control.algorithms import Algorithms
from Elena.control.settings import *
from geopy.geocoders import Photon

init = False
G, M, algorithms = None, None, None

def initialize_data():
    data = {
        "elevation_route": [],
        "shortest_route": [],
        "shortDist": 0,
        "gainShort": 0,
        "dropShort": 0,
        "elenavDist": 0,
        "gainElenav": 0,
        "dropElenav": 0,
        "popup_flag": 0
    }
    
def get_geojson(coordinates):
    geojson = {}
    geojson["properties"] = {}
    geojson["type"] = "Feature"
    geojson["geometry"] = {}
    geojson["geometry"]["type"] = "LineString"
    geojson["geometry"]["coordinates"] = coordinates

    return geojson

def get_data_from_path(start, end, shortestPath, elevPath):
    if shortestPath is None and elevPath is None:
        return data
    data["start"] = start
    data["end"] = end
    data["elevation_route"] = get_geojson(elevPath[0])
    data["shortest_route"] = get_geojson(shortestPath[0])
    data["shortDist"] = shortestPath[1]
    data["gainShort"] = shortestPath[2]
    data["dropShort"] = shortestPath[3]
    data["elenavDist"] = elevPath[1]
    data["gainElenav"] = elevPath[2]
    data["dropElenav"] = elevPath[3]
    if len(elevPath[0]) == 0:
        data["popup_flag"] = 1
    else:
        data["popup_flag"] = 2
    return data

def get_data_point_from_location(locate, len_location):
    return locate[0] + ',' + locate[1] + ',' + locate[2] + ',' + locate[len_location - 5] + ',' + locate[
        len_location - 3] + ', USA - ' + locate[len_location - 2]

def get_data(startpt, endpt, x, min_max, log=True):
    # gets data for plotting the routes. 
    global init, G, M, algorithms

    data = initialize_data()

    locator = Photon(user_agent="myGeocoder")
    print("The start point is", startpt)
    location = locator.reverse(startpt)
    locate = location.address.split(',')

    len_location = len(locate)

    start = get_data_point_from_location(locate, len_location)
    if log:
        print("Start: ", start)

    location = locator.reverse(endpt)
    locate = location.address.split(',')

    len_location = len(locate)

    end = get_data_point_from_location(locate, len_location)
    if log:
        print("End: ", end)

    if log:
        print("Percent of Total path: ", x)
        print("Elevation: ", min_max)
    if not init:
        abstract = Graph_Abstraction()
        G = abstract.get_graph(endpt)
        algorithms = Algorithms(G, x=x, elev_type=min_max)
        init = True

    shortestPath, elevPath = algorithms.get_shortest_path(startpt, endpt, x, elev_type=min_max, log=log)

    return get_data_from_path(start, end, shortestPath, elevPath)