# TODO: Change data object initialisation  
from geopy.geocoders import Photon
from server.graph_utils.graph_abstract import AbstractGraph
from server.graph_utils.distance_calc import distance_calculate

class DataAbstract(object):
    def __init__(self, logger):
        self.logger = logger
        self.data = {}
        self.geojson = {}
        self.init = False
        self.nx_graph = None
        self.algorithms = None

    def initialize_data(self):
        self.data = {
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
        self.geojson["properties"] = {}
        self.geojson["type"] = "Feature"
        self.geojson["geometry"] = {}
        self.geojson["geometry"]["type"] = "LineString"
        self.geojson["geometry"]["coordinates"] = coordinates
        return self.geojson

    def get_data_from_path(self, start, end, shortest_path, elevated_path):
        if shortest_path is None and elevated_path is None:
            return self.data
        self.data["start"] = start
        self.data["end"] = end
        self.data["elevation_route"] = self.get_geojson(elevated_path.end_to_end_path)
        self.data["shortest_route"] = self.get_geojson(shortest_path.end_to_end_path)
        self.data["shortDist"] = shortest_path.total_distance
        self.data["gainShort"] = shortest_path.elevation_gain
        self.data["dropShort"] = shortest_path.elevation_drop
        self.data["elenavDist"] = elevated_path.total_distance
        self.data["gainElenav"] = elevated_path.elevation_gain
        self.data["dropElenav"] = elevated_path.elevation_drop
        if len(elevated_path.end_to_end_path) == 0:
            self.data["popup_flag"] = 1
        else:
            self.data["popup_flag"] = 2
        return self.data

    # TODO: Clean up this function, what are the indices? 
    def get_data_point_from_location(self, locate, len_location):
        return locate[0] + ',' + locate[1] + ',' + locate[2] + ',' + locate[len_location - 5] + ',' + locate[
            len_location - 3] + ', USA - ' + locate[len_location - 2]

    def get_data(self, begin_point, end_point, elevation_ratio, min_max, log=True):
        # gets data for plotting the routes.
        self.initialize_data()

        locator = Photon(user_agent="myGeocoder")
        print("The start point is", begin_point)
        location = locator.reverse(end_point)
        locate = location.address.split(',')

        len_location = len(locate)
        start = self.get_data_point_from_location(locate, len_location)
        if log:
            print("Start: ", start)

        location = locator.reverse(end_point)
        locate = location.address.split(',')

        len_location = len(locate)

        end = self.get_data_point_from_location(locate, len_location)
        if log:
            print("End: ", end)
        if log:
            print("Percent of Total path: ", elevation_ratio)
            print("Elevation Type: ", min_max)
        if not self.init:
            abstract = AbstractGraph()
            self.nx_graph = abstract.get_graph(end_point)
            self.algorithms = distance_calculate(self.nx_graph, elevation_adjust=elevation_ratio, elevation_type=min_max)
            self.init = True
        shortest_path, elevated_path = self.algorithms.shortest_path(begin_point, end_point, elevation_ratio, 
        elevation_type=min_max)
        return self.get_data_from_path(start, end, shortest_path, elevated_path)