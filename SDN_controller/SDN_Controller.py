# HASH: 12c5feeeb506f73797014803639f013df8005c7d02c294b1574b3fed230732eb


import networkx as nx
import hashlib
import matplotlib.pyplot as plt
from collections import defaultdict
import heapq

class SDNController:
    def __init__(self):
        self.graph = nx.Graph()
        self.flow_table = defaultdict(dict)
        self.backup_paths = {}
        self.link_utilization = defaultdict(int)

    def add_node(self, node):
        self.graph.add_node(node)

    def add_link(self, src, dst, weight=1):
        self.graph.add_edge(src, dst, weight=weight)

    def remove_link(self, src, dst):
        if self.graph.has_edge(src, dst):
            self.graph.remove_edge(src, dst)
            print(f"Link {src}-{dst} removed.")
        self.recompute_paths()

    def inject_traffic(self, src, dst, flow_id, priority=1):
        if nx.has_path(self.graph, src, dst):
            paths = list(nx.all_shortest_paths(self.graph, src, dst, weight='weight'))
            path = paths[hash(flow_id) % len(paths)] #this load balances across paths
            self.flow_table[flow_id] = {'path': path, 'priority': priority, 'src': src, 'dst': dst}
            for i in range(len(path) - 1):
                self.link_utilization[(path[i], path[path[i+1]])] +=1
            print(f"Flow {flow_id} injected from {src} to {dst} via {path}.")
            #Backup path
            try:
                backup = self.get_backup_path(src, dst, exclude=path)
                self.backup_paths[flow_id] = backup
            except:
                self.backup_paths[flow_id] = []
        else:
            print(f"No path found between {src} and {dst}.")

    def get_backup_path(self, src, dst, exclude=[]):
        G_copy = self.graph.copy()
        for i in range(len(exclude) - 1):
            if G_copy.has_edge(exclude[i], exclude[i + 1]):
                G_copy.remove_edge(exclude[i], exclude[i + 1])
        return nx.shortest_path(G_copy, src, dst, weight='weight')

    def query_routing(self, flow_id):
        if flow_id in self.flow_table:
            print(f"Flow {flow_id} -> Path: {self.flow_table[flow_id]['path']}, Priority: {self.flow_table[flow_id]['priority']}")
            if self.backup_paths[flow_id]:
                print(f"Backup path: {self.backup_paths[flow_id]}")
        else:
            print("Flow ID not found.")

    def recompute_paths(self):
        print("Recomputing flow paths after change...")
        for flow_id, flow in self.flow_table.items():
            self.inject_traffic(flow['src'],flow['dst'], flow_id, flow['priority'])

    def visualize(self):
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=True, node_color='lightblue')
        edge_labels = {(u, v): f"{self.link_utilization[(u, v)]}" for u, v in self.graph.edges() if
                       (u, v) in self.link_utilization}
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)
        plt.title("SDN Network Topology and Link Utilization")
        plt.show()

    



