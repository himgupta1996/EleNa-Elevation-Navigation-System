import osmnx as ox
import networkx as nx
from collections import deque, defaultdict
from heapq import *
import time

class route: 
    def __init__(self, end_to_end_path, total_distance, elevation_gain, elevation_drop):
        self.end_to_end_path = [] 
        self.total_distance = 0.0 
        self.elevation_gain = float('-inf')
        self.elevation_drop = 0.0

class graph_node: 
    def __init__(self, start_node = None): 
        self.priority = 0.0 
        self.distance = 0.0 
        self.node = start_node 

class distance_calculate: 
    def __init___(self, graph, elevation_adjust = 0.0, elevation_type = "max"): 
        self.nx_graph = graph 
        self.elevation_adjust = elevation_adjust 
        self.elevation_type = elevation_type 
        self.maximize = elevation_type == "max"
        self.best_route = Route()
        self.begin_node = None 
        self.terminal_node = None 
    
    def get_dijkstra_distance(self): 
        if not self.begin_node or not self.terminal_node: 
            return 
        nx_graph = self.nx_graph 
        pass 

