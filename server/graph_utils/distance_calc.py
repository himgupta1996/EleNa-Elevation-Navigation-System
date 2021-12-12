import osmnx as ox
import networkx as nx
from collections import deque, defaultdict
from heapq import *
import time

class Algorithms:

    # Function to initialize the nesscessary class variables 
    def __init__(self, G, elevation_adjust = 0.0, elevation_type = "maximize"):
        self.G = G
        self.elevation_type = elevation_type
        self.elevation_adjust = elevation_adjust
        self.best = [[], 0.0, float('-inf'), 0.0]
        self.start_node= None
        self.end_node =None

    # Function to compute cost between two given nodes node1, node2 with the given cost_type 
    def get_cost(self, node1, node2, cost_type = "normal"):
        G = self.G
        if node1 is None or node2 is None : 
            return 
        if cost_type == "normal":
            try: 
                return G.edges[node1, node2 ,0]["length"]
            except : 
                return G.edges[node1, node2]["weight"]
        elif cost_type == "elevation_difference":
            return G.nodes[node2]["elevation"] - G.nodes[node1]["elevation"]
        elif cost_type == "elevation_gain":
            return max(0.0, G.nodes[node2]["elevation"] - G.nodes[node1]["elevation"])
        elif cost_type == "elevation_drop":
            return max(0.0, G.nodes[node1]["elevation"] - G.nodes[node2]["elevation"])
        else:
            return abs(G.nodes[node1]["elevation"] - G.nodes[node2]["elevation"])
        

    # Function to compute total cost or piecewise cost for a given route
    def get_Elevation(self, route, cost_type = "both", isPiecewise = False):
        total = 0
        if isPiecewise : 
            piece_elevation = []
        for i in range(len(route)-1):
            if cost_type == "both":
                diff = self.get_cost(route[i],route[i+1],"elevation_difference")	
            elif cost_type == "elevation_gain":
                diff = self.get_cost(route[i],route[i+1],"elevation_gain")
            elif cost_type == "elevation_drop":
                diff = self.get_cost(route[i],route[i+1],"elevation_drop")
            elif cost_type == "normal":
                diff = self.get_cost(route[i],route[i+1],"normal")
            total += diff
            if isPiecewise : 
                piece_elevation.append(diff)
        if isPiecewise:
            return total, piece_elevation
        else:
            return total

    
    # Function that returns the path given a parent mapping and the final dest
    def get_route(self, parent_node, dest):
        path = [dest]
        curr = parent_node[dest]
        while curr!=-1:
            path.append(curr)
            curr = parent_node[curr]
        return path[::-1]

    # Function that does the sanity check to see whether the start or end nodes are None values
    def check_nodes(self):
        if self.start_node is None or self.end_node is None:
            return False
        return True



    # Function that implements Djikstra's routing algorithm
    def dijkstra(self):       
        if not self.check_nodes() : 
            return
        G, elevation_adjust, shortest, elevation_type = self.G, self.elevation_adjust, self.shortest_dist, self.elevation_type
        start_node, end_node = self.start_node, self.end_node

        temp = [(0.0, 0.0, start_node)]
        seen = set()
        prior_info = {start_node: 0}
        parent_node = defaultdict(int)
        parent_node[start_node] = -1

        while temp:
            curr_priority, curr_distance, curr_node = heappop(temp)
            
            if curr_node not in seen:
                seen.add(curr_node)
                if curr_node == end_node:
                    break

                for n in G.neighbors(curr_node):
                    if n in seen: 
                        continue
                    
                    prev = prior_info.get(n, None) # get past priority of the node
                    edge_len = self.get_cost(curr_node, n, "normal")
                    
                    # Update distance btw the nodes depending on maximize(subtract) or minimize elevation(add)
                    if elevation_type == "maximize":
                        if elevation_adjust <= 0.5:
                            nxt = edge_len*0.1 + self.get_cost(curr_node, n, "elevation_drop")
                            nxt += curr_priority
                        else:
                            nxt = (edge_len*0.1 - self.get_cost(curr_node, n, "elevation_difference"))* edge_len*0.1
                    else:
                        nxt = edge_len*0.1 + self.get_cost(curr_node, n, "elevation_gain")
                        nxt += curr_priority
                    
                    nxt_distance = curr_distance + edge_len
                    
                    if nxt_distance <= shortest*(1.0+elevation_adjust) and (prev is None or nxt < prev):
                        parent_node[n] = curr_node
                        prior_info[n] = nxt
                        heappush(temp, (nxt, nxt_distance, n))        
        
        if not curr_distance: 
            return

        route = self.get_route(parent_node, end_node)
        elevation_dist, dropDist = self.get_Elevation(route, "elevation_gain"), self.get_Elevation(route, "elevation_drop")
        self.best = [route[:], curr_distance, elevation_dist, dropDist]
        print("best", self.best)
        return


    def retrace_path(self, from_node, curr_node):
        # Reconstructs the path and plots it.
        if not from_node or not curr_node : return
        total = [curr_node]
        while curr_node in from_node:
            curr_node = from_node[curr_node]
            total.append(curr_node)
        
        self.best = [total[:], self.get_Elevation(total, "normal"), self.get_Elevation(total, "elevation_gain"), self.get_Elevation(total, "elevation_drop")]
        return



    def a_star(self):
        # Implements A* algorithm for calculating distances. 
        evaluated = set() #evaluated node set      
        toEval = set() # nodes that are not evaluated
        best_node = {} # best cost to end
        costToStart = {} # cost of node to start node
        costToStart1 = {}
        final_score = {} # dist between start node and end node thru a particular node


        if not self.check_nodes() : 
            return
        G, min_dist = self.G, self.shortest_dist
        elevation_adjust, elevation_type = self.elevation_adjust, self.elevation_type
        start_node= self.start_node
        end_node = self.end_node
        
        toEval.add(start_node)
   
        for node in G.nodes():
            costToStart[node] = float("inf")
        
        costToStart[start_node] = 0 

        for node in G.nodes():
            costToStart1[node] = float("inf")
        costToStart1[start_node] = 0

        final_score[start_node] = G.nodes[start_node]['dist_from_dest']*0.1
        
        while len(toEval):
            curr_node = min([(node,final_score[node]) for node in toEval], key=lambda t: t[1])[0]            
            if curr_node == end_node:
                self.retrace_path(best_node, curr_node)
                return
            
            toEval.remove(curr_node)
            evaluated.add(curr_node)
            for n in G.neighbors(curr_node):
                if n in evaluated: 
                    continue 
                if elevation_type == "minimize":
                    pred_costToStart = costToStart[curr_node] + self.get_cost(curr_node, n, "elevation_gain")
                elif elevation_type == "maximize":
                    pred_costToStart = costToStart[curr_node] + self.get_cost(curr_node, n, "elevation_drop")

                pred_costToStart1 = costToStart1[curr_node] + self.get_cost(curr_node, n, "normal")

                if n not in toEval and pred_costToStart1<=(1+elevation_adjust)*min_dist:# Discover a new node
                    toEval.add(n)
                else: 
                    if (pred_costToStart >= costToStart[n]) or (pred_costToStart1>=(1+elevation_adjust)*min_dist):
                        continue 

                best_node[n] = curr_node
                costToStart[n] = pred_costToStart
                costToStart1[n] = pred_costToStart1
                final_score[n] = costToStart[n] + G.nodes[n]['dist_from_dest']*0.1




    def get_shortest_path(self, startpt, endpt, elevation_adjust, elevation_type = "maximize", log=True):
        
        # Calculates shortest path
        G = self.G
        self.elevation_adjust = elevation_adjust/100.0
        self.elevation_type = elevation_type
        self.start_node, self.end_node = None, None

        #self.best = [path, totalDist, totalElevGain, totalElevDrop]
        if elevation_type == "maximize": 
            self.best = [[], 0.0, float('-inf'), float('-inf')]
        else:
            self.best = [[], 0.0, float('inf'), float('-inf')]

        #get shortest path
        self.start_node, d1 = ox.get_nearest_node(G, point=startpt, return_dist = True)
        self.end_node, d2   = ox.get_nearest_node(G, point=endpt, return_dist = True)

        # returns the shortest route from start to end based on distance
        self.shortest_route = nx.shortest_path(G, source=self.start_node, target=self.end_node, weight='length')
        
        # ox.get_route function returns list of edge length for above route
        self.shortest_dist  = sum(ox.get_route_edge_attributes(G, self.shortest_route, 'length'))
        
        shortest_route_latlong = [[G.nodes[route_node]['x'],G.nodes[route_node]['y']] for route_node in self.shortest_route] 
        
        shortestPathStats = [shortest_route_latlong, self.shortest_dist, \
                            self.get_Elevation(self.shortest_route, "elevation_gain"), self.get_Elevation(self.shortest_route, "elevation_drop")]
        print(shortestPathStats)
        if(elevation_adjust == 0):
            return shortestPathStats, shortestPathStats

        start_time = time.time()
        self.dijkstra()
        end_time = time.time()
        dijkstra_route = self.best
        if log:
            print()
            print("Dijkstra route statistics")
            print(dijkstra_route[1])
            print(dijkstra_route[2])
            print(dijkstra_route[3])
            print("--- Time taken = %s seconds ---" % (end_time - start_time))

        if elevation_type == "maximize": 
            self.best = [[], 0.0, float('-inf'), float('-inf')]
        else:
            self.best = [[], 0.0, float('inf'), float('-inf')]

        start_time = time.time()
        self.a_star()
        end_time = time.time()
        a_star_route = self.best
        if log:
            print()
            print("A star route statistics")
            print(a_star_route[1])
            print(a_star_route[2])
            print(a_star_route[3])
            print("--- Time taken = %s seconds ---" % (end_time - start_time))

            print()

        if self.elevation_type == "maximize":
            if (dijkstra_route[2] > a_star_route[2]) or (dijkstra_route[2] == a_star_route[2] and dijkstra_route[1] < a_star_route[1]):
                self.best = dijkstra_route
                if log:
                    print("Dijkstra chosen as best route")
                    print()
            else:
                self.best = a_star_route
                if log:
                    print("A star chosen as best route")
                    print()
        else:
            if (dijkstra_route[2] < a_star_route[2]) or (dijkstra_route[2] == a_star_route[2] and dijkstra_route[1] < a_star_route[1]):
                self.best = dijkstra_route
                if log:
                    print("Dijkstra chosen as best route")
                    print()
            else:
                self.best = a_star_route
                if log:
                    print("A star chosen as best route")
                    print()

        # If dijkstra or A-star doesn't return a shortest path based on elevation requirements
        if (self.elevation_type == "maximize" and self.best[2] == float('-inf')) or (self.elevation_type == "minimize" and self.best[3] == float('-inf')):            
            return shortestPathStats, [[], 0.0, 0, 0]
        
        self.best[0] = [[G.nodes[route_node]['x'],G.nodes[route_node]['y']] for route_node in self.best[0]]

        # If the elevation path does not match the elevation requirements
        if((self.elevation_type == "maximize" and self.best[2] < shortestPathStats[2]) or (self.elevation_type == "minimize" and self.best[2] > shortestPathStats[2])):
            self.best = shortestPathStats

        return shortestPathStats, self.best





