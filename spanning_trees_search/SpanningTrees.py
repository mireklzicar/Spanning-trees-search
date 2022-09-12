
import networkx as nx
import numpy as np
from spanning_trees_search.GraphMatrix import GraphMatrix
import random
import matplotlib.pyplot as plt
import os
import pandas as pd
import imageio
from tqdm import tqdm

class SpanningTrees:
    """ Class for searching and visualising spanning trees"""
    
    def __init__(self, nx_graph, seed=42):
        self.nx_graph = nx_graph
        self.seed = seed
        self.graph_matrix = GraphMatrix()
        self.graph_matrix.adjacency_matrix = np.array(nx.adjacency_matrix(self.nx_graph).todense())
        self.my_pos = nx.spring_layout(self.nx_graph)
        self.spanning_trees = []
        self.export_directory_path = None
        self.graph_png_filename = None
        self.graph_csv_filename = None
        self.csv_output_directory = None
        self.image_output_directory = None
        self.spanning_trees_exported = False
        self.spanning_trees_num = 0
        
        
    def spanning_trees_count(self):
        """Counts number of spanning trees in the graph via Kirchoff's theorem"""
        self.graph_matrix.compute_remaining_matrices()
        self.spanning_trees_num = self.graph_matrix.adjugate_subdeterminant
        return self.spanning_trees_num
        
    def preview(self):
        """Previewing a graph"""
        nx.draw(self.nx_graph, with_labels=True, node_color='pink', pos = self.my_pos)
        plt.show()
    
    def save_figure(self, filename="graph.png"):
        """Saving image of the graph"""
        nx.draw(self.nx_graph, with_labels=True, node_color='pink', pos = self.my_pos)
        plt.savefig(filename)
        plt.close()

    def save_csv(self, filename="graph.csv"):
        """Saving adjacency matrix csv of the graph"""
        if not self.graph_matrix.adjacency_set:
            raise ValueError("Adjacency matrix not set. Cannot save csv.")
        df = pd.DataFrame(self.graph_matrix.adjacency_matrix)
        df.to_csv(filename)
    
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
    
    def export_spanning_trees(self, save_path="/test/run"):
        """Exporting spanning trees to csv and images as in folder structure explained in compute_spanning_trees()
        
        Parameters
        ----------
        save_path : str, optional
            Path for saving, by default "/test/run"
        
        Output
        ------
        Example of full output directory structure:
        Assuming visualisation='plots_save', export='adjacency_csv', save_path="/test/run"):
        ├── run
            │── graph.png
            │── graph_adjacency.csv
            │── csv_output
            │   ├── spanning_tree_adjacency_001.csv
            │   ├── spanning_tree_adjacency_002.csv
            │   └── spanning_tree_adjacency_003.csv
            └── images
                ├── spanning_tree_001.png
                ├── spanning_tree_002.png
                └── spanning_tree_003.png
        
        """
        
        if len(self.spanning_trees) == 0:
            raise ValueError("No spanning trees found. Please run compute_spanning_trees() first.")
        
        if not os.path.exists(save_path):
            os.mkdir(save_path)
            self.export_directory_path = save_path
        else:
            raise OSError("Directory already exists. Creation of the directory %s failed" % save_path)
    
        self.graph_png_filename = os.path.join(save_path, "graph.png")
        self.graph_csv_filename = os.path.join(save_path, "graph_adjacency.csv")
        self.csv_output_directory = os.path.join(save_path, "csv_output")
        self.image_output_directory = os.path.join(save_path, "images")
        
        
        os.mkdir(self.csv_output_directory)
        os.mkdir(self.image_output_directory)
        
        self.save_figure(filename=self.graph_png_filename)
        self.save_csv(filename=self.graph_csv_filename)
        
        spanning_tree_objects = []
        for graph in self.spanning_trees:
            st = SpanningTrees(graph)
            st.my_pos = self.my_pos
            spanning_tree_objects.append(st)  
        
        for i, j in enumerate(spanning_tree_objects):
            filename = os.path.join(self.image_output_directory, "spanning_tree_" + str(i).zfill(3) + ".png")
            j.save_figure(filename=filename)
            filename_csv = os.path.join(self.csv_output_directory, "spanning_tree_adjacency_" + str(i).zfill(3) + ".csv")
            j.save_csv(filename=filename_csv)
        
        self.spanning_trees_exported = True
    
    def export_gif(self):
        """Exporting gif of spanning trees. Inspired by https://stackoverflow.com/a/35943809"""
        if not self.spanning_trees_exported:
            raise ValueError("Spanning trees were not exported. Please run export_spanning_trees() first.")

        images = []
        #images.append(self.graph_png_filename)
        for filename in sorted(os.listdir(self.image_output_directory)):
            images.append(imageio.imread(os.path.join(self.image_output_directory, filename)))
        imageio.mimsave(os.path.join(self.export_directory_path, "spanning_tree.gif"), images, duration=0.2)

    
    def compute_spanning_trees(self, visualisation=True, export='adjacency_csv', save_path="/test/run", progress_bar=False):
        """Recursively searching and visualising spanning trees
        Spanning tree is induced subgraph of the given graph, that is connected and has no cycles, therefore it is a tree.
        
            visualisation : str, optional
            Visualisation type, by default 'plots_inline'
            Available options: 'plots_inline', 'plots_save', 'plots_all', None
        export : str, optional
            Export type, by default 'none'
            Available options: 'adjacency_csv', 'incidence_csv', 'degree_csv', None
        
        Description
        -----------
        Function works as a binary tree, where each node is an induced subgraph and in each level we are selecting and removing one edge.
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
        if self.spanning_trees_num == 0:
            number_of_trees = self.spanning_trees_count()
        print("Number of spanning trees is: ", self.spanning_trees_num)
        bar = tqdm(total=self.spanning_trees_num)
        
        # Inner recursive function
        def fnc(G, fixed_edges=[], result_trees = [], iter_count = 0, itermax = self.spanning_trees_num):
            # Limiting iterations to not exhaust memory
            if iter_count >= itermax:
                return
            # Every node is a copy of previous graph
            G = G.copy()
            edges = list(G.edges())
            # If graph is connected and tree, we have found a spanning tree and can draw it
            if nx.is_connected(G) and self.is_tree(G):
                if not set(G.edges) in result_trees:
                    result_trees.append(set(G.edges))
                    self.spanning_trees.append(G)
                    if visualisation:
                        plt.figure(figsize=(2, 2))
                        nx.draw(G, pos = self.my_pos, with_labels=True, node_color='pink', node_size=100)
                    if progress_bar:
                        bar.update(1)
                        #print("Spanning trees found: ", iter_count, "/", itermax)
                        #print(".", end="")
            
            # Edges to choose are all remaining edges - fixed_edges
            # If there is nothing left to choose, we exhausted all possible edges, return
            edges_to_choose = list(set(edges) - set(fixed_edges))
            if len(edges_to_choose) == 0:
                return
            
            # Choosing edge for removal and fixation
            choice_is_ok = False
            tries = 0 
            
            while not choice_is_ok:
                e = random.choice(list(edges_to_choose)) #FIXME systematic choice might be more efficient
                H = G.copy()
                H.remove_edge(e[0], e[1])
                # Checking if removal of chosen edge doesnt disconnect the graph and its fixation doesnt create cycle
                choice_is_ok = (not self.check_cycle(fixed_edges + [e])[0]) and nx.is_connected(H) and (not G.copy() in self.spanning_trees)
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
        if visualisation:
            plt.show()