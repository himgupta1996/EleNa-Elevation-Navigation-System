import osmnx as map
import networkx as nx
import numpy as np
import os 
import pickle as p 

class AbstractGraph:
    def __init__(self, logger):
        
        # hard code constants 
        self.API_KEY = "AIzaSyCJgTZU8StpSFsIulOvO40iF684-g6m4IA"
        self.radius = 6371008.8
        # UMass Amherst is the start point 
        self.start = [42.384803, -72.529262]
        self.logger = logger 

    # calculate the physical "metre" distance between 2 points given coordinates 
    def distance(self, latitudeA, longitudeA, latitudeB, longitudeB):
        latitudeA_rad = np.radians(latitudeA) 
        longitudeA_rad = np.radians(longitudeA)
        latitudeB_rad = np.radians(latitudeB)
        longitudeB_rad = np.radians(longitudeB)

        delta_longitude = longitudeB_rad - longitudeA_rad
        delta_latitude = latitudeB_rad - latitudeA_rad

        radial_distance_theta = np.sin(delta_latitude / 2)**2 + \
        np.cos(latitudeA_rad) * np.cos(latitudeB_rad) * np.sin(delta_longitude / 2) ** 2
        radial_distance_metre = 2 * np.arctan2(np.sqrt(radial_distance_theta), np.sqrt(1 - radial_distance_theta))
        return radial_distance_metre * self.radius

    # generate the initial graph 
    def generate(self, terminal_point): 
        self.nx_graph = None    
        self.graph = p.load(open("server/graph_utils/graph.p", "rb"))       
        self.nx_graph = self.distance_from_endpoint(self.graph, terminal_point)
        return self.nx_graph

    def distance_from_endpoint(self, nx_graph, endpt):
        terminal_point = nx_graph.nodes[map.get_nearest_node(nx_graph, point=endpt)]
        longitudeA = terminal_point["x"]   
        latitudeA = terminal_point["y"]    
        for node_location, node_data in nx_graph.nodes(data=True):
            longitudeB = nx_graph.nodes[node_location]['x']
            latitudeB = nx_graph.nodes[node_location]['y']
            node_data['dist_from_dest'] = self.distance(latitudeA, longitudeA, latitudeB, longitudeB)            
        return nx_graph