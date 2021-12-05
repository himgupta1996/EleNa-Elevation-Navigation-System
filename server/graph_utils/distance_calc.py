import collections
import osmnx as ox
import networkx as nx
from collections import deque, defaultdict
from heapq import *

class route: 
    def __init__(self, end_to_end_path = [], total_distance = 0.0, elevation_gain = float('-inf'), elevation_drop = 0.0):
        self.end_to_end_path = end_to_end_path
        self.total_distance = total_distance
        self.elevation_gain = elevation_gain
        self.elevation_drop = elevation_drop

class graph_node: 
    def __init__(self, distance = 0.0, priority = 0.0, start_node = None): 
        self.distance = distance 
        self.priority = priority
        self.node = start_node 

class distance_calculate: 
    def __init___(self, graph, elevation_adjust = 0.0, elevation_type = "max"): 
        self.nx_graph = graph 
        self.elevation_adjust = elevation_adjust 
        self.elevation_type = elevation_type 
        self.maximize = elevation_type == "max"
        self.best_route = route()
        self.shortest_route = None 
        self.shortest_distance = 0.0 
        self.begin_node = None 
        self.terminal_node = None 
        self.weight = 0.1
    
    def get_edge_cost(self, start_node, end_node, cost = "normal"): 
        if not start_node or not end_node or not self.nx_graph: 
            return 
        if cost == "normal": 
            return self.nx_graph.edges[start_node, end_node, 0]["length"]
        elif cost == "drop": 
            return max(0.0, self.nx_graph.nodes[start_node]["elevation"] - self.nx_graph.nodes[end_node]["elevation"])
        elif cost == "gain": 
            return max(0.0, self.nx_graph.nodes[end_node]["elevation"] - self.nx_graph.nodes[start_node]["elevation"])
        elif cost == "difference": 
            return self.nx_graph.nodes[end_node]["elevation"] - self.nx_graph.nodes[start_node]["elevation"] 
        return 

    def get_route(self): 
        # TODO: Implement route generation using osmnx 
        pass
    
    def get_elevation_cost(self): 
        # TODO: Implement cost computation for a particular path
        # Path may have 2 or more points to compute the total cost with 
        pass 

    # Implementation of Dijkstra's weighted shortest path algorithm 
    # weight of node decided dynamically as per given elevation cost 
    def get_dijkstra_distance(self): 
        if not self.begin_node or not self.terminal_node: 
            return 
        temp_graph = self.nx_graph
        elevation = self.elevation_adjust 
        temp_shortest = self.shortest_distance 
        elevation_type = self.elevation_type 
        start_node = self.begin_node 
        end_node = self.terminal_node 

        seen_nodes = set() 
        iterable_nodes = [graph_node()]
        parent_node_map = collections.defaultdict(int)
        # the start node cannot have a valid parent node 
        parent_node_map[start_node] = float('-inf')
        priority_map = {start_node: 0}
        while iterable_nodes is not None: 
            current_node = heappop(iterable_nodes)
            node = current_node.node 
            distance = current_node.distance 
            priority = current_node.priority
            if node not in seen_nodes: 
                seen_nodes.add(node)
                if node == end_node: break 

                for neighbor in temp_graph.neighbors(node): 
                    if neighbor in seen_nodes: 
                        continue 
                    
                    previous_priority = None 
                    if neighbor in priority_map: 
                        previous_priority = priority_map[neighbor]
                        edge_length = self.get_edge_cost(node, neighbor, "normal")
                    
                        if elevation_type == "max":
                            if elevation > 0.5:
                                next_priority = (edge_length * self.weight  - self.get_edge_cost(node, neighbor, "difference"))* edge_length * self.weight 
                            else:
                                next_priority = self.get_edge_cost(node, neighbor, "drop") + edge_length * self.weight   
                                next_priority += priority 
                        else:
                            next_priority = self.get_edge_cost(node, neighbor, "gain") + edge_length*self.weight
                            next_priority += priority
                        
                        next_distance = edge_length + distance

                        if next_distance <= temp_shortest*(1.0 + elevation): 
                            if(next_priority < previous_priority or not previous_priority):
                                parent_node_map[neighbor] = node
                                priority_map[neighbor] = next_priority
                                new_node = graph_node(next_priority, next_distance, neighbor)
                                heappush(iterable_nodes, new_node)        
        
            if not distance: 
                return

        current_route = self.get_route(parent_node_map, end_node)
        gain_distance = self.get_elevation_cost(route, "gain")
        drop_distance = self.get_elevation_cost(route, "drop")
        self.best_route.end_to_end_path = current_route[:]  
        self.best_route.total_distance = distance 
        self.best_route.elevation_gain = gain_distance
        self.best_route.elevation_gain = drop_distance
        return




