import collections
import osmnx 
import networkx as nx
from collections import deque, defaultdict
from heapq import *

class route_statistics: 
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
        self.best_route_statistics = route_statistics()
        self.shortest_path_statistics = route_statistics()
        self.shortest_route = None 
        self.shortest_distance = 0.0 
        self.begin_node = None 
        self.terminal_node = None 
        self.weight = 0.1
        self.osmnx_weight = "length"

    def get_edge_cost(self, start_node, end_node, cost = "normal"): 
        if not start_node or not end_node or not self.nx_graph: 
            return 
        if cost == "normal": 
            return self.nx_graph.edges[start_node, end_node, 0]["length"]
        elif cost == "drop": 
            return max(0.0, self.nx_graph.nodes[start_node]["elevation"] - 
                        self.nx_graph.nodes[end_node]["elevation"])
        elif cost == "gain": 
            return max(0.0, self.nx_graph.nodes[end_node]["elevation"] - 
                        self.nx_graph.nodes[start_node]["elevation"])
        elif cost == "difference": 
            return self.nx_graph.nodes[end_node]["elevation"] - \
            self.nx_graph.nodes[start_node]["elevation"] 
        return 

    def get_route(self, mapping_parent_nodes, terminus): 
        path = [terminus]
        pointer = mapping_parent_nodes[terminus]
        # since float('-inf') indicates that the topmost node has been reached 
        # in the form of a reverse traversal from the terminal node. 
        while pointer != float('-inf'):
            path.append(pointer)
            pointer = mapping_parent_nodes[pointer]
        # the actual path is in the reverse direction 
        path = path.reverse()
        return path
    
    def get_elevation_cost(self, route, cost_category):
        # TODO: Implement cost computation for a particular path
        # Path may have 2 or more points to compute the total cost with 
        total = 0 
        for index, _ in enumerate(route): 
            if index < len(route) - 1: 
                if cost_category == "both": 
                    delta = self.get_edge_cost(route[index], route[index + 1], "difference")
                else: 
                    delta = self.get_edge_cost(route[index], route[index + 1], cost_category)
                total += delta
        return total 
            
    # Implementation of Dijkstra's weighted shortest path algorithm 
    # weight of node decided dynamically as per given elevation cost 
    def get_dijkstra_distance(self): 
        # stop search if either node is absent 
        if not self.begin_node or not self.terminal_node: 
            return 
        
        # define the start points for the weighted breadth-first search 
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
        # start the traversal 
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
                                next_priority = (edge_length * self.weight  - 
                                self.get_edge_cost(node, neighbor, "difference")) * edge_length * self.weight 
                            else:
                                next_priority = self.get_edge_cost(node, neighbor, "drop") + \
                                                edge_length * self.weight   
                                next_priority += priority 
                        else:
                            next_priority = self.get_edge_cost(node, neighbor, "gain") + \
                                            edge_length * self.weight
                            next_priority += priority
                        
                        next_distance = edge_length + distance

                        if next_distance <= temp_shortest*(elevation + 1.0): 
                            if(next_priority < previous_priority or not previous_priority):
                                parent_node_map[neighbor] = node
                                priority_map[neighbor] = next_priority
                                new_node = graph_node(next_priority, next_distance, neighbor)
                                heappush(iterable_nodes, new_node)        
        
            if not distance: 
                return

        self.best_route_statistics.end_to_end_path = self.get_route(parent_node_map, end_node)[:]
        self.best_route_statistics.total_distance = distance 
        self.best_route_statistics.elevation_gain = self.get_elevation_cost(self.best_route_stats.end_to_end_path, "gain")
        self.best_route_statistics.elevation_drop = self.get_elevation_cost(self.best_route_stats.end_to_end_path, "drop")
        return

    # TODO: Implement A-star search algorithm for finding the shortest path 
    def get_a_star_distance(self): 
        if not self.begin_node or not self.terminal_node: 
            return 

        final_route_score = {}
        best_route_node = {}
        cost_to_start_node = {} 
        second_cost_to_start_node = {}
        
        nodes_to_evaluate = set()
        evaluated_nodes = set()

        temp_graph = self.nx_graph
        elevation = self.elevation_adjust 
        temp_shortest = self.shortest_distance 
        elevation_type = self.elevation_type 
        start_node = self.begin_node 
        end_node = self.terminal_node 

        nodes_to_evaluate.add(start_node)
        for node in temp_graph.nodes(): 
            cost_to_start_node[node] = float('inf')
            second_cost_to_start_node = float('inf')
        
        cost_to_start_node[start_node] = 0 
        second_cost_to_start_node[start_node] = 0 

        final_route_score[start_node] = self.weight * temp_graph.nodes[start_node]['dist_from_dest']
        while len(nodes_to_evaluate) != 0:
            this_node = min([(node, final_route_score[node]) for node in nodes_to_evaluate], key=lambda t: t[1])[0] 
            if this_node == end_node: 
                if not this_node or not best_route_node: return
                path = [this_node]
                while node_pointer in this_node:
                    node_pointer = this_node[node_pointer]
                    path.append(node_pointer)
                self.best_route_statistics.end_to_end_path = path[:]
                self.best_route_statistics.total_distance = self.get_elevation_cost(path, "normal")
                self.best_route_statistics.elevation_gain = self.get_elevation_cost(path, "gain")
                self.best_route_statistics.elevation_drop = self.get_elevation_cost(path, "drop")
                return 
            
            nodes_to_evaluate.remove(this_node)
            evaluated_nodes.add(this_node)
            for neighbor in temp_graph.neighbors(this_node): 
                if neighbor in evaluated_nodes: continue 
                if elevation_type == "max": 
                    predicted_cost_to_start_node = self.get_cost(this_node, neighbor, "gain") + cost_to_start_node[this_node]
                elif elevation_type == "min": 
                    predicted_cost_to_start_node = self.get_cost(this_node, neighbor, "drop") + cost_to_start_node[this_node]
                second_predicted_cost = self.get_cost(this_node, neighbor, "normal") + second_cost_to_start_node[this_node]
            
                if second_predicted_cost <= (1+elevation) * temp_shortest and neighbor not in nodes_to_evaluate:
                    nodes_to_evaluate.add(neighbor)
                else: 
                    if predicted_cost_to_start_node >= (1+elevation) * temp_shortest or \
                    predicted_cost_to_start_node >= cost_to_start_node[neighbor]:
                        continue 

                    best_route_node[neighbor] = this_node
                    cost_to_start_node[neighbor] = predicted_cost_to_start_node
                    second_cost_to_start_node[neighbor] = second_predicted_cost
                    final_route_score[neighbor] = (temp_graph.nodes[neighbor]['dist_from_dest']*self.weight) 
                    + cost_to_start_node[neighbor]

    def reset_best_route(self, elevation_type): 
        self.best_route_statistics.end_to_end_path = []
        self.best_route_statistics.total_distance = 0.0 
        if elevation_type == "max": 
            self.best_route_statistics.elevation_drop = float('-inf')
            self.best_route_statistics.elevation_gain = float('-inf')
        else: 
            self.best_route_statistics.elevation_drop = float('inf')
            self.best_route_statistics.elevation_gain = float('-inf')

    def shortest_path(self, begin_point, end_point, elevation, elevation_type = "max"): 
        self.elevation_adjust = elevation / 100 
        self.begin_node = None  
        self.terminal_node = None  

        nx_graph = self.nx_graph 
        self.reset_best_route_stats(elevation_type)
        self.begin_node, _ = osmnx.get_nearest_node(nx_graph, point=begin_point, return_dist = True)
        self.terminal_node, _ = osmnx.get_nearest_node(nx_graph, point=end_point, return_dist = True)
        self.shortest_route = nx.shortest_path(nx_graph, source=self.begin_node, 
        target=self.terminal_node, weight = self.osmnx_weight)
        self.shortest_path_coordinates = []
        for node in self.shortest_route: 
            self.shortest_path_coordinates.append((nx_graph.nodes[node]['x'], nx_graph.nodes[node]['y']))
        self.shortest_path_statistics.total_distance = sum(osmnx.get_route_edge_attributes(nx_graph, 
        self.shortest_route, self.osmnx_weight))
        self.shortest_path_statistics.elevation_gain = self.get_elevation_cost(self.shortest_route, "gain")
        self.shortest_path_statistics.elevation_drop = self.get_elevation_cost(self.shortest_route, "drop")
        
        if(elevation == 0.0): 
            return self.shortest_path_statistics, self.shortest_path_statistics
        
        self.get_dijkstra_distance()
        # TODO: Add runtime and logging 
        dijkstra_route = self.best_route_statistics 
        self.reset_best_route_stats(elevation_type) 
        self.get_a_star_distance()
        a_star_route = self.best_route_statistics

        if self.elevation_type == "max": 
            if (dijkstra_route.elevation_gain > a_star_route.elevation_gain or 
            (dijkstra_route.elevation_gain == a_star_route.elevation_gain 
            and dijkstra_route.total_distance < a_star_route.total_distance)): 
                self.best_route_statistics = dijkstra_route 
            else: 
                self.best_route_statistics = a_star_route 
        else: 
            if (dijkstra_route.elevation_gain < a_star_route.elevation_gain or 
            (dijkstra_route.elevation_gain == a_star_route.elevation_gain
            and dijkstra_route.total_distance < dijkstra_route.total_distance)): 
                self.best_route_statistics = dijkstra_route 
            else: 
                self.best_route_statistics = a_star_route 
            
        if (self.elevation_type == "max" and self.best_route_statistics.elevation_gain == float('-inf')) or \
        (self.elevation_type == "min" and self.best_route_statistics.elevation_drop == float('-inf')):
            return self.shortest_path_statistics, route_statistics(elevation_drop=0, elevation_gain=0)

        # calculate actual route 
        self.best_route_statistics.end_to_end_path = [[nx_graph.nodes[node]['x'], 
        nx_graph.nodes[node]['y']] for node in self.best_route_statistics.end_to_end_path]        
        # edge case: neither algorithm finds the desired path 
        # assign shortest path as the best path  
        # TODO: convey this information on the frontend? 
        if ((self.elevation_type == "max" and 
        self.best_route_statistics.elevation_gain < self.shortest_path_statistics.elevation_gain)
        or (self.elev_type == "min" and 
        self.best_route_statistics.elevation_gain > self.shortest_path_statistics.elevation_gain)):
            self.best_route_statistics = self.shortest_path_statistics
        return self.shortest_path_statistics, self.best_route_statistics





