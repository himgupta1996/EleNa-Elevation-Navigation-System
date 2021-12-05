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

class distance_calculate: 
    def __init__(self, logger, graph, elevation_adjust = 0.0, elevation_type = "max"):
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
        self.logger = logger

    def get_edge_cost(self, start_node, end_node, cost = "normal"): 
        graph = self.nx_graph
        if start_node is None or end_node is None: 
            return 
        if cost == "normal":
            try: 
                return graph.edges[start_node, end_node ,0]["length"]
            except: 
                return graph.edges[start_node, end_node]["weight"]
        elif cost == "difference":
            return graph.nodes[end_node]["elevation"] - graph.nodes[start_node]["elevation"]
        elif cost == "gain":
            return max(0.0, graph.nodes[end_node]["elevation"] - graph.nodes[start_node]["elevation"])
        elif cost == "drop":
            return max(0.0, graph.nodes[start_node]["elevation"] - graph.nodes[end_node]["elevation"])
        else:
            return abs(graph.nodes[start_node]["elevation"] - graph.nodes[end_node]["elevation"])

    def retrace_path(self, from_node, curr_node):
        # Reconstructs the path and plots it.
        if not from_node or not curr_node: return
        total = [curr_node]
        while curr_node in from_node:
            curr_node = from_node[curr_node]
            total.append(curr_node)
        self.best_route_statistics.end_to_end_path = total[:]
        self.best_route_statistics.total_distance = self.get_elevation_cost(self.best_route_statistics.end_to_end_path, "normal") 
        self.best_route_statistics.elevation_gain = self.get_elevation_cost(self.best_route_statistics.end_to_end_path, "gain")
        self.best_route_statistics.elevation_drop = self.get_elevation_cost(self.best_route_statistics.end_to_end_path, "drop")
        return


    def get_route(self, mapping_parent_nodes, terminus): 
        path = [terminus]
        curr = mapping_parent_nodes[terminus]
        while curr!=-1:
            path.append(curr)
            curr = mapping_parent_nodes[curr]
        return path[::-1]
    
    def get_elevation_cost(self, route, cost_type):
        # TODO: Implement cost computation for a particular path
        # Path may have 2 or more points to compute the total cost with 
        total = 0
        for i in range(len(route)-1):
            if cost_type == "both":
                diff = self.get_edge_cost(route[i],route[i+1],"difference")	
            elif cost_type == "gain":
                diff = self.get_edge_cost(route[i],route[i+1],"gain")
            elif cost_type == "drop":
                diff = self.get_edge_cost(route[i],route[i+1],"drop")
            elif cost_type == "normal":
                diff = self.get_edge_cost(route[i],route[i+1],"normal")
            total += diff
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
        temp = [(0.0, 0.0, start_node)]
        parent_node_map = collections.defaultdict(int)
        # the start node cannot have a valid parent node 
        parent_node_map[start_node] = -1
        priority_map = {start_node: 0}
        # start the traversal 
        while temp:
            priority, distance, node = heappop(temp)      
            self.logger.debug(f"distance: {distance}")      
            if node not in seen_nodes:
                seen_nodes.add(node)
                if node == end_node:
                    break

                for neighbor in temp_graph.neighbors(node):
                    if neighbor in seen_nodes: 
                        continue
                    
                    prev = priority_map.get(neighbor, None) # get past priority of the node
                    edge_len = self.get_edge_cost(node, neighbor, "normal")
                    
                    # Update distance btw the nodes depending on maximize(subtract) or minimize elevation(add)
                    if elevation_type == "max":
                        if elevation <= 0.5:
                            next_priority = edge_len*0.1 + self.get_edge_cost(node, neighbor, "drop")
                            next_priority += priority
                        else:
                            next_priority = (edge_len*0.1 - self.get_edge_cost(node, neighbor, "difference")) * edge_len*0.1
                    else:
                        next_priority = edge_len*0.1 + self.get_edge_cost(node, neighbor, "gain")
                        next_priority += priority
                    
                    next_distance = distance + edge_len
                    
                    if next_distance <= temp_shortest*(1.0+elevation) and (prev is None or next_priority < prev):
                        parent_node_map[neighbor] = node
                        priority_map[neighbor] = next_priority
                        heappush(temp, (next_priority, next_distance, neighbor))        

        if not distance:
            self.logger.debug(f"the distance is {distance}")
            return

        self.logger.debug(f"route dijkstra {self.get_route(parent_node_map, end_node)}")
        self.best_route_statistics.end_to_end_path = self.get_route(parent_node_map, end_node)[:]
        self.logger.debug(f"the end to end path is djikstra {self.best_route_statistics.end_to_end_path}")
        self.best_route_statistics.total_distance = distance 
        self.best_route_statistics.elevation_gain = self.get_elevation_cost(self.best_route_statistics.end_to_end_path, "gain")
        self.best_route_statistics.elevation_drop = self.get_elevation_cost(self.best_route_statistics.end_to_end_path, "drop")
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
            second_cost_to_start_node[node] = float('inf')
        
        cost_to_start_node[start_node] = 0 
        second_cost_to_start_node[start_node] = 0 

        final_route_score[start_node] = temp_graph.nodes[start_node]['dist_from_dest'] * 0.1
        while len(nodes_to_evaluate):
            curr_node = min([(node, final_route_score[node]) for node in nodes_to_evaluate], key=lambda t: t[1])[0]            
            if curr_node == end_node:
                self.retrace_path(best_route_node, curr_node)
                return
            
            nodes_to_evaluate.remove(curr_node)
            evaluated_nodes.add(curr_node)
            for neighbor in temp_graph.neighbors(curr_node):
                if neighbor in evaluated_nodes: 
                    continue 
                if elevation_type == "min":
                    pred_costToStart = cost_to_start_node[curr_node] + self.get_edge_cost(curr_node, neighbor, "gain")
                elif elevation_type == "max":
                    pred_costToStart = cost_to_start_node[curr_node] + self.get_edge_cost(curr_node, neighbor, "drop")

                pred_costToStart1 = second_cost_to_start_node[curr_node] + self.get_edge_cost(curr_node, neighbor, "normal")

                if neighbor not in nodes_to_evaluate and pred_costToStart1<=(1+elevation)*temp_shortest:# Discover a new node
                    nodes_to_evaluate.add(neighbor)
                else: 
                    if (pred_costToStart >= cost_to_start_node[neighbor]) or (pred_costToStart1>=(1+elevation)*temp_shortest):
                        continue 

                best_route_node[neighbor] = curr_node
                cost_to_start_node[neighbor] = pred_costToStart
                second_cost_to_start_node[neighbor] = pred_costToStart1
                final_route_score[neighbor] = cost_to_start_node[neighbor] + temp_graph.nodes[neighbor]['dist_from_dest']*0.1

    def reset_best_route_stats(self, elevation_type):
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
        self.logger.debug(f"the begin node is {self.begin_node}")
        self.terminal_node, _ = osmnx.get_nearest_node(nx_graph, point=end_point, return_dist = True)
        self.logger.debug(f"the end node is {self.terminal_node}")
        self.shortest_route = nx.shortest_path(nx_graph, source=self.begin_node, 
        target=self.terminal_node, weight = self.osmnx_weight)
        self.logger.debug(f"the shortest route is {self.shortest_route}")
        self.shortest_distance  = sum(osmnx.get_route_edge_attributes(nx_graph, self.shortest_route, 'length'))
        for node in self.shortest_route: 
            self.shortest_path_statistics.end_to_end_path.append([nx_graph.nodes[node]['x'], nx_graph.nodes[node]['y']])
        # self.logger.debug(f"the shortest route is {self.shortest_route}")
        self.shortest_path_statistics.total_distance = sum(osmnx.get_route_edge_attributes(nx_graph, 
        self.shortest_route, self.osmnx_weight))
        self.shortest_path_statistics.elevation_gain = self.get_elevation_cost(self.shortest_route, "gain")
        self.shortest_path_statistics.elevation_drop = self.get_elevation_cost(self.shortest_route, "drop")
        
        if(elevation == 0.0): 
            return self.shortest_path_statistics, self.shortest_path_statistics
        
        self.get_dijkstra_distance()
        # TODO: Add runtime and logging 
        dijkstra_route = self.best_route_statistics
        self.logger.debug(f"the dijkstra route is {dijkstra_route.__dict__}")
        self.reset_best_route_stats(elevation_type)

        self.get_a_star_distance()
        a_star_route = self.best_route_statistics
        self.logger.debug(f"the a star route is {a_star_route.__dict__}")

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
        self.logger.debug("In shortest path")
        self.best_route_statistics.end_to_end_path = [[nx_graph.nodes[node]['x'], 
        nx_graph.nodes[node]['y']] for node in self.best_route_statistics.end_to_end_path]

        self.logger.debug(self.best_route_statistics.end_to_end_path)
        # edge case: neither algorithm finds the desired path 
        # assign shortest path as the best path  
        # TODO: convey this information on the frontend? 
        if ((self.elevation_type == "max" and 
        self.best_route_statistics.elevation_gain < self.shortest_path_statistics.elevation_gain)
        or (self.elevation_type == "min" and
        self.best_route_statistics.elevation_gain > self.shortest_path_statistics.elevation_gain)):
            self.best_route_statistics = self.shortest_path_statistics
        return self.shortest_path_statistics, self.best_route_statistics





