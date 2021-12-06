# TODO: Change data object initialisation  
from geopy.geocoders import Photon
from server.graph_utils.graph_abstract import Graph_Abstraction
from server.graph_utils.distance_calc import Algorithms

class DataAbstract(object):
    def __init__(self):
        self.data = {}
        self.geojson = {}
        self.init = False
        self.nx_graph = None
        self.algorithms = None
        self.abstract = None 

    def initialize_data(self):
        self.data = {
            "start": None, 
            "end": None, 
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

    def get_geojson(self, coordinates):
        self.geojson = {}
        self.geojson["properties"] = {}
        self.geojson["type"] = "Feature"
        self.geojson["geometry"] = {}
        self.geojson["geometry"]["type"] = "LineString"
        self.geojson["geometry"]["coordinates"] = coordinates
        return self.geojson

    def get_data_from_path(self, start, end, shortest_path, elevated_path):
        # assert(shortest_path.end_to_end_path != elevated_path.end_to_end_path)
        self.data["start"] = start
        self.data["end"] = end
        self.data["elevation_route"] = self.get_geojson(elevated_path[0])
        self.data["shortest_route"] = self.get_geojson(shortest_path[0])
        self.data["shortDist"] = shortest_path[1]
        self.data["gainShort"] = shortest_path[2]
        self.data["dropShort"] = shortest_path[3]
        self.data["elenavDist"] = elevated_path[1]
        self.data["gainElenav"] = elevated_path[2]
        self.data["dropElenav"] = elevated_path[3]
        if len(elevated_path[0]) == 0:
            self.data["popup_flag"] = 1
        else:
            self.data["popup_flag"] = 2
        return self.data

    # TODO: Clean up this function, what are the indices? 
    def get_data_point_from_location(self, locate, len_location):
        return locate[0] + ',' + locate[1] + ',' + locate[2] + ',' + locate[len_location - 5] + ',' + locate[
            len_location - 3] + ', USA - ' + locate[len_location - 2]

    def get_data(self, startpt, endpt, x, min_max, log=True):
        # gets data for plotting the routes.
        locator = Photon(user_agent="myGeocoder")
        location = locator.reverse(startpt)
        locate = location.address.split(',')
        
        len_location = len(locate)

        start = locate[0] + ',' + locate[1] + ',' + locate[2] + ',' + locate[len_location-5] + ',' + locate[len_location-3] + ', USA - ' + locate[len_location-2] 
        if log:
            print("Start: ",start)
        
        location = locator.reverse(endpt)
        locate = location.address.split(',')
        
        len_location = len(locate)

        end = locate[0] + ',' + locate[1] + ',' + locate[2] + ',' + locate[len_location-5] + ',' + locate[len_location-3] + ', USA - ' + locate[len_location-2]
        if log:
            print("End: ",end)
        
        if log:
            print("Percent of Total path: ",x)
            print("Elevation: ",min_max)
        
        abstract = Graph_Abstraction()
        G = abstract.get_graph(endpt)
        algorithms = Algorithms(G, elevation_adjust = x, elevation_type = min_max)    
        shortestPath, elevPath = algorithms.get_shortest_path(startpt, endpt, x, elevation_type = min_max, log = log)   
        print()
        print("elevPath", elevPath)
        print()
        if shortestPath is None and elevPath is None:
            print("inside both none ")
            data = {"elevation_route" : [] , "shortest_route" : []}        
            data["shortDist"] = 0
            data["gainShort"] = 0
            data["dropShort"] = 0
            data["elenavDist"]  = 0
            data["gainElenav"] = 0
            data["dropElenav"] = 0
            data["popup_flag"] = 0 
            return data
        data = {"elevation_route" : self.get_geojson(elevPath[0]), "shortest_route" : self.get_geojson(shortestPath[0])}
        data["shortDist"] = shortestPath[1]
        data["gainShort"] = shortestPath[2]
        data["dropShort"] = shortestPath[3]
        data["start"] = start
        data["end"] = end
        data["elenavDist"] = elevPath[1]
        data["gainElenav"] = elevPath[2]
        data["dropElenav"] = elevPath[3] 
        if len(elevPath[0])==0:
            data["popup_flag"] = 1
        else: 
            data["popup_flag"] = 2  
        print()
        print("elevation_route", data["elevation_route"])
        print()
        return data