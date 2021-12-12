import osmnx as ox
import networkx as nx
import os
import numpy as np
import pickle as p

class Graph_Abstraction:
    # Function to initialize the data variables 
    def __init__(self):
        print("Initializing the model")        
        self.GOOGLEAPIKEY="AIzaSyCJgTZU8StpSFsIulOvO40iF684-g6m4IA"      
        if os.path.exists("server/graph_utils/graph.p"):
            self.G = p.load( open( "server/graph_utils/graph.p", "rb" ) )
            self.init = True
            print("Graph loaded")
        else:
            self.init = False

    # Function that returns networkx graph with eleveation data and rise or fall grade.
    def elevation_graph(self, G):

        G = ox.add_node_elevations(G, api_key=self.GOOGLEAPIKEY)        
        return G

    # Function that returns the distance between two nodes when given their longitudes and latitudes
    def dist_nodes(self,lat1,long1,lat2,long2):
        radius=6371008.8 # Earth radius
        
        lat1, long1 = np.radians(lat1), np.radians(long1)
        lat2, long2 = np.radians(lat2),np.radians(long2)

        dlong,dlat = long2 - long1,lat2 - lat1

        temp1 = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlong / 2)**2
        temp2 = 2 * np.arctan2(np.sqrt(temp1), np.sqrt(1 - temp1))
        return radius * temp2


    # Function that adds in the distance of all nodes in a graph to the final destination
    def add_dist_frm_endpt(self,G,endpt):
        end_node=G.nodes[ox.get_nearest_node(G, point=endpt)]
        lat1, long1 =end_node["y"],end_node["x"]        
        for node,data in G.nodes(data=True):
            lat2=G.nodes[node]['y']
            long2=G.nodes[node]['x']
            distance=self.dist_nodes(lat1,long1,lat2,long2)            
            data['dist_from_dest'] = distance
            
        return G

    # Function that returns elevation data along with the graph
    def get_graph(self, endpt):    
        start = [42.384803, -72.529262]
        if not self.init:
            print("Loading the Graph")
            self.G = ox.graph_from_point(start, distance=20000, network_type='walk')
            self.G = self.elevation_graph(self.G)                         
            p.dump( self.G, open( "server/graph_utils/graph.p", "wb" ))
            self.init = True
            print("The Graph has been saved")
        self.G = self.add_dist_frm_endpt(self.G,endpt)
        return self.G