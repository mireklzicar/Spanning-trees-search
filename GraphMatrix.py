import numpy as np
from sympy.matrices import Matrix

class GraphMatrix:
    """
    Class for storing and computing matrices of graph. 
    Setting of adjacency or incidence matrix (as type numpy array) is mandatory. The rest is computed automatically.
    """
    
    def __init__(self):
        
        self.adjacency_set = False
        self.incidence_set = True
        self.adjugate_subdeterminant = None
        self.definition_complete = False
    
    def incidence2adjacency(self, incidence_matrix):
        # compute adjacency matrix from incidence matrix
        I = np.array(incidence_matrix)
        adj = (np.dot(I, I.T) > 0).astype(int)
        np.fill_diagonal(adj, 0)
        A = adj
        return A
    
    def adjacency2incidence(self, adjacency_matrix):
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
            I[:,i] = [1 if k in edges[i] else 0 for k in range(I.shape[0])]
        I = I.T
        return I
    
    def degree_matrix(self, adjacency_matrix):
        # compute degree matrix from adjacency matrix
        A = adjacency_matrix
        D = np.zeros(shape = (np.shape(A)[0], np.shape(A)[0]))
        for i in range(A.shape[0]):
            D[i, i] = np.sum(A[i])
        return D
    
    def laplacian_matrix(self, adjacency_matrix, degree_matrix):
        A = adjacency_matrix
        D = degree_matrix
        return D - A
    
    def laplacian_adjugate_matrix(self, laplacian_matrix):
        return np.array(Matrix(laplacian_matrix).adjugate())
    
    def compute_remaining_matrices(self):
        if not self.definition_complete:
            raise Exception("Definition of matrices is not complete.")
        elif self.adjacency_set:
            self.incidence_matrix = self.adjacency2incidence(self.adjacency_matrix)
            self.degree_matrix = self.degree_matrix(self.adjacency_matrix)
            self.laplacian_matrix = self.laplacian_matrix(self.adjacency_matrix, self.degree_matrix)
            self.laplacian_adjugate_matrix = self.laplacian_adjugate_matrix(self.laplacian_matrix)
            self.adjugate_subdeterminant = int(self.laplacian_adjugate_matrix[0, 0])
        elif self.incidence_set:
            self.adjacency_matrix = self.incidence2adjacency(self.incidence_matrix)
            self.degree_matrix = self.degree_matrix(self.adjacency_matrix)
            self.laplacian_matrix = self.laplacian_matrix(self.adjacency_matrix, self.degree_matrix)
            self.laplacian_adjugate_matrix = self.laplacian_adjugate_matrix(self.laplacian_matrix)
            self.adjugate_subdeterminant = int(self.laplacian_adjugate_matrix[0, 0])
    
    @property
    def adjacency_matrix(self):
        "Adjacency matrix property for graph matrix"
        return self._adjacency_matrix
    
    @adjacency_matrix.setter
    def adjacency_matrix(self, value):
        "Adjacency matrix property setter and computation of the rest for graph matrix"
        self._adjacency_matrix = value
        self.adjacency_set = True
        self.definition_complete = True
        
    @property
    def incidence_matrix(self):
        "Incidence matrix property for graph matrix"
        return self._incidence_matrix
    
    @incidence_matrix.setter
    def incidence_matrix(self, value):
        "Incidence matrix property setter and computation of the rest for graph matrix"
        self._incidence_matrix = value
        self.incidence_set = True
        self.definition_complete = True
