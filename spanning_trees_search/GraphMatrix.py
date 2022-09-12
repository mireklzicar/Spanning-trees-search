import numpy as np
from sympy.matrices import Matrix
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


class GraphMatrix:
    """
    A class for storing and computing matrices of graph.
    Setting of adjacency or incidence matrix (as type numpy array) is mandatory. The rest is computed automatically.
    """

    def __init__(self):

        self.adjacency_set = False
        self.incidence_set = True
        self.adjugate_subdeterminant = None
        self.definition_complete = False
        self.matrices_computed = False
        self.graph_created = False

    def incidence2adjacency(self, incidence_matrix):
        """Compute adjacency matrix from incidence matrix

        Parameters
        ----------
        incidence_matrix : numpy array
        """
        I = np.array(incidence_matrix)
        adj = (np.dot(I, I.T) > 0).astype(int)
        np.fill_diagonal(adj, 0)
        A = adj
        return A

    def adjacency2incidence(self, adjacency_matrix):
        """Compute incidence matrix from adjacency matrix

        Parameters
        ----------
        adjacency matrix : numpy array
        """
        # compute incidence matrix from adjacency matrix
        A = adjacency_matrix
        edges = []
        for i in range(A.shape[0]):
            for j in range(A.shape[1]):
                if A[i, j] == 1 and ((i, j) not in edges) and ((j, i) not in edges):
                    edges.append((i, j))
        # indexing connections for each edge
        I = np.zeros((A.shape[0], len(edges)))
        for i in range(I.shape[1]):
            I[:, i] = [1 if k in edges[i] else 0 for k in range(I.shape[0])]
        #I = I.T
        return I

    def degree_matrix(self, adjacency_matrix):
        """Compute degree matrix from adjacency matrix

        Parameters
        ----------
        adjacency matrix : numpy array
        """
        # compute degree matrix from adjacency matrix
        A = adjacency_matrix
        D = np.zeros(shape=(np.shape(A)[0], np.shape(A)[0]))
        D = D.astype(np.int32)
        for i in range(A.shape[0]):
            D[i, i] = np.sum(A[i])
        return D

    def laplacian_matrix(self, adjacency_matrix, degree_matrix):
        """Compute Laplacian matrix from adjacency matrix and degree matrix

        Parameters
        ----------
        adjacency matrix : numpy array
        degree matrix : numpy array
        """
        A = adjacency_matrix
        D = degree_matrix
        return D - A

    def laplacian_adjugate_matrix(self, laplacian_matrix):
        """Compute Laplacian adjugate matrix from Laplacian matrix

        Parameters
        ----------
        Laplacian matrix : numpy array
        """
        # L = laplacian_matrix
        # L_adj = np.zeros(shape=(np.shape(L)[0], np.shape(L)[0]))
        # for i in range(L.shape[0]):
        #     for j in range(L.shape[1]):
        #         if i != j:
        #             L_adj[i, j] = (-1) ** (i + j) * L[j, i]
        # return L_adj

        return np.array(Matrix(laplacian_matrix).adjugate(), dtype=np.int32)
    
    def compute_graph(self):
        if not self.adjacency_set:
            raise Exception("Adjacency matrix not set. Cannot create graph.")
        graph = nx.from_numpy_matrix(self.adjacency_matrix)
        return graph

    def compute_remaining_matrices(self):
        """Compute remaining matrices if adjacency matrix or incidence matrix is set and graph definition is thus complete"""

        if self.matrices_computed:
            print("Matrices already computed. No need to compute again. Skipping.")
            return
        if not self.definition_complete:
            raise Exception("Definition of matrices is not complete.")
        elif self.adjacency_set:
            self.incidence_matrix = self.adjacency2incidence(self.adjacency_matrix)
            self.degree_matrix = self.degree_matrix(self.adjacency_matrix)
            self.laplacian_matrix = self.laplacian_matrix(
                self.adjacency_matrix, self.degree_matrix
            )
            self.laplacian_adjugate_matrix = self.laplacian_adjugate_matrix(
                self.laplacian_matrix
            )
            self.adjugate_subdeterminant = int(self.laplacian_adjugate_matrix[0, 0])
        elif self.incidence_set:
            self.adjacency_matrix = self.incidence2adjacency(self.incidence_matrix)
            self.degree_matrix = self.degree_matrix(self.adjacency_matrix)
            self.laplacian_matrix = self.laplacian_matrix(
                self.adjacency_matrix, self.degree_matrix
            )
            self.laplacian_adjugate_matrix = self.laplacian_adjugate_matrix(
                self.laplacian_matrix
            )
            self.adjugate_subdeterminant = int(self.laplacian_adjugate_matrix[0, 0])
            
        self.graph = self.compute_graph()
        self.graph_created = True
        self.matrices_computed = True
        

    @property
    def adjacency_matrix(self):
        """Adjacency matrix property for graph matrix"""
        return np.array(self._adjacency_matrix, dtype=np.int32)

    @adjacency_matrix.setter
    def adjacency_matrix(self, value):
        """Adjacency matrix property setter and computation of the rest for graph matrix"""
        self._adjacency_matrix = value
        self.adjacency_set = True
        self.definition_complete = True

    @property
    def incidence_matrix(self):
        """Incidence matrix property for graph matrix"""
        return np.array(self._incidence_matrix, dtype=np.int32)

    @incidence_matrix.setter
    def incidence_matrix(self, value):
        """Incidence matrix property setter and computation of the rest for graph matrix"""
        self._incidence_matrix = value
        self.incidence_set = True
        self.definition_complete = True
        
    @property
    def graph(self):
        return self._graph
    
    @graph.setter
    def graph(self, value):
        self._graph = value
        self.my_pos = nx.spring_layout(self._graph)
        self.graph_created = True
    
    def load(self, filename, mode="adjacency"):
        """Load adjacency or incidence matrix from .csv file

        Parameters
        ----------
        filename : str
        mode : str
        """
        if mode == "adjacency":
            self.adjacency_matrix = pd.read_csv(filename, header=0, index_col=0).to_numpy(dtype=np.int32)
            print("1) Adjacency matrix loaded.")
        elif mode == "incidence":
            self.incidence_matrix = pd.read_csv(filename, header=0, index_col=0).to_numpy(dtype=np.int32)
            print("1) Incidence matrix loaded.")
        else:
            raise Exception("Mode not supported.")
        try:
            self.compute_remaining_matrices()
            print("2) Remaining matrices computed.")
        except Exception as e:
            print(f"Input in {filename} with input mode {mode} is not valid or cannot be computed. Raising error: {e}")

    def preview(self):
        """Previewing a graph"""
        g = nx.from_numpy_matrix(self.adjacency_matrix)
        nx.draw(g, with_labels=True, node_color='pink')
    
    def save_figure(self, filename="graph.png", pos = 'default'):
        """Saving image of the graph"""
        if not self.graph_created:
            self.graph = self.compute_graph()
        if pos == 'default':
            nx.draw(self.graph, with_labels=True, node_color='pink', pos = self.my_pos)
        else:
            nx.draw(self.graph, with_labels=True, node_color='pink', pos = pos)
        plt.savefig(filename)
        plt.close()

    def save_csv(self, filename="graph.csv"):
        """Saving adjacency matrix csv of the graph"""
        if not self.adjacency_set:
            raise ValueError("Adjacency matrix not set. Cannot save csv.")
        df = pd.DataFrame(self.adjacency_matrix)
        df.to_csv(filename)
