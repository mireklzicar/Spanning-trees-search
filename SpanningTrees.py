
import networkx as nx
import numpy as np
from GraphMatrix import GraphMatrix
import random
import matplotlib.pyplot as plt

class SpanningTrees:
    """ Class for searching and visualising spanning trees"""
    
    def __init__(self, nx_graph, seed=42):
        self.nx_graph = nx_graph
        self.seed = seed
        self.graph_matrix = GraphMatrix()
        self.graph_matrix.adjacency_matrix = nx.adjacency_matrix(self.nx_graph)
        self.my_pos = nx.spring_layout(self.nx_graph)
        
    def spanning_trees_count(self):
        """
        Counts number of spanning trees in the graph via Kirchoff's theorem
        """
        self.graph_matrix.compute_remaining_matrices()
        return self.graph_matrix.adjugate_subdeterminant
        
        
    def preview(self):
        nx.draw(self.nx_graph, with_labels=True, node_color='pink', pos = self.my_pos)
        
    
    def check_cycle(self, edges_list):
        """Checking if there is a cycle in the graph by traversing list of edges"""
        start = edges_list[0]
        e1 = start
        c = 0
        while True:
            next_edge_index = [i for i, e in enumerate(edges_list) if e[0] == e1[1]]
            if len(next_edge_index) == 1:
                e1 = edges_list[next_edge_index[0]]
                c+=1
            else:
                return False, 0
            if e1 == start:
                return True, c

    def is_tree(self, G):
        """Checking if graph is tree"""
        e = G.number_of_edges()
        v = G.number_of_nodes()
        return e == v - 1

    def are_tree_edges(self, edges_list):
        """Checking is edges are tree edges"""
        G = nx.Graph()
        G.add_edges_from(edges_list)
        e = G.number_of_edges()
        v = G.number_of_nodes()
        return e == v - 1

    def is_connected(self, edges_list):
        """Checking if graph is connected"""
        G = nx.Graph()
        G.add_edges_from(edges_list)
        return nx.is_connected(G)


    def process(self):
        """Recursively searching and visualising spanning trees
        Spanning tree is induced subgraph of the given graph, that is connected and has no cycles, therefore it is a tree.

        Function works as binary tree, where each node is an induced subgraph and in each level we are selecting and removing one edge.
        Leaves of the tree are spanning trees (where every possible edge was removed).
            In every iteration we are choosing edge for removal and fixation with following conditions:
                - edge should be new (not previously chosen)
                - its removal should not affect connectedness
                - its fixation should not create cycle of fixed edges
            Then we are fixing the edge (creating left children) and removing it from the graph (creating right children)
            In next iteration we repeat the same procedure for left and right children, until we reach the leaves of the tree.
            (We are using recursion and passing fixed edges and number of iteration)
        """
        G = self.nx_graph
        # Inner recursive function
        def fnc(G, fixed_edges=[], result_trees = [], iter_count = 0, itermax = 100):
            # Limiting iterations to not exhaust memory
            if iter_count > itermax:
                return
            # Every node is a copy of previous graph
            G = G.copy()
            edges = list(G.edges())
            # If graph is connected and tree, we have found a spanning tree and can draw it
            if nx.is_connected(G) and self.is_tree(G):
                if not set(G.edges) in result_trees:
                    result_trees.append(set(G.edges))
                    plt.figure(figsize=(2, 2))
                    nx.draw(G, pos = self.my_pos, with_labels=True, node_color='pink', node_size=100)
            
            # Edges to choose are all remaining edges - fixed_edges
            # If there is nothing left to choose, we exhausted all possible edges, return
            edges_to_choose = list(set(edges) - set(fixed_edges))
            if len(edges_to_choose) == 0:
                return
            
            # Choosing edge for removal and fixation
            choice_is_ok = False
            tries = 0 
            while not choice_is_ok:
                # Choosing random edge
                e = random.choice(list(edges_to_choose)) #FIXME systematic choice might be more efficient and better
                H = G.copy()
                H.remove_edge(e[0], e[1])
                # Checking if removal of chosen edge doesnt disconnect the graph and its fixation doesnt create cycle
                choice_is_ok = (not self.check_cycle(fixed_edges + [e])[0]) and nx.is_connected(H)
                tries += 1
                # If we have tried too many times and cannot found good edge, we are giving up
                if tries > G.number_of_edges():
                    return
            
            # If we found good possible edge
            if choice_is_ok:
                # Fixing the edge in left branch
                fnc(G, fixed_edges + [e], iter_count=iter_count + 1)
                # Removig the edge in right branch
                G.remove_edge(e[0], e[1])
                fnc(G, iter_count=iter_count + 1)
        fnc(G)
        plt.show()