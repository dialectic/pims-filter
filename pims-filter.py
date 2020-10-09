import json
import numpy as np
from scipy.linalg import eig, eigh
from scipy.sparse.linalg import eigs, eigsh
from scipy.sparse import dok_matrix, diags
from matplotlib import pyplot as plt

class PIMS_Filter:
    """
    TODO: finish commenting class
    TODO: plot in 3 dimensions
    TODO: better error checking?
    TODO:

    """
    def __init__(self, adjacency_file, n_PC, plot_it=False, plot_dim=2):
        self.adjacency_file = adjacency_file
        self.n_PC = n_PC
        self.plot_it = plot_it
        self.plot_dim = plot_dim

        self.n_nodes = 0
        self.adjacency_index = []
        self.adjacency_list = []

        self.L = []
        self.P = []
        self.evals = []
        self.evecs = []
        self.evecs_T = []

    def load_adjacency(self):
        # Loads adjacency file and populates adjacency_list and adjacency_index
        with open(self.adjacency_file, 'rb') as adj_file:
            adjacency_dict = json.load(adj_file)

        try:
            self.adjacency_list = adjacency_dict["list"]
            self.adjacency_index = adjacency_dict["nodes"]
        except:
            ValueError("Argument 'adjacency_file' must be a dictionary w/ keys, 'list' and 'nodes'")


    def build_sparse_matrices(self):
        # populates variables A, D, L
        self.n_nodes = len(self.adjacency_index)  # number of nodes

        # build sparse matrices
        A = dok_matrix((self.n_nodes, self.n_nodes), dtype=np.float32)  # adjacency
        D = dok_matrix((self.n_nodes, self.n_nodes), dtype=np.float32)  # degree
        self.L = dok_matrix((self.n_nodes, self.n_nodes), dtype=np.float32)  # Laplacian
        # populate degree and adjacency
        for i in range(0, self.n_nodes):
            adjacents = self.adjacency_list[i]
            D[i, i] = len(adjacents)
            for j in range(0, len(adjacents)):
                A[i, adjacents[j]] = 1
                A[adjacents[j], i] = 1
        # populate Laplacian
        self.L = D - A


    def eigendecomposition(self):
        # populates evals and evecs
        # eigendecomposition
        # - using ARPACK via https://docs.scipy.org/doc/scipy/reference/tutorial/arpack.html
        # - we want the largest eigenvals/vecs of L^+
        # - equivalently, we find the smallest eigenvals/vecs of L
        # - used sigma=0 to do the shift-invert mode


        evals_small, evecs_small = eigsh(self.L, self.n_PC, sigma=0, which='LM')
        # evals_small, evecs_small = eigsh(L, n_PC, which='SA')

        if any(evals_small <= 0):
            raise ValueError(f'evals_small <= 0') # TODO add a more helpful error message
        self.evals = 1 / evals_small

        self.evecs = evecs_small  # scale by whatever
        self.evecs_T = self.evecs.T
        print(f"  - truncated evals: {self.evals}")




        # error checking: evals should all be positive or zero

    def project(self):
        # projects to R^n where n == n_PC and populates P
        # build projection matrix P
        # - a node i vector is a unit vector e_i
        # - Saerens (2004) eq 8 tells us a transformed node i vector is
        # -- Lambda^(1/2) U^T e_i.
        # - we needn't recompute the matrix multiplication each time
        # - do it once and build lookup table
        # - we'll assume n_PC is small so we can use dense matrices
        # - construct U and Lambda
        # -- must reshape with zero padding
        U = dok_matrix((self.n_nodes, self.n_nodes), dtype=np.float32)  # evec matrix
        Lambda_root = dok_matrix((self.n_nodes, self.n_nodes), dtype=np.float32)  # eval matrix
        for i in range(0, self.n_PC):
            Lambda_root[i, i] = np.sqrt(self.evals[i])
            for j in range(0, self.n_nodes):
                U[j, i] = self.evecs[j, i]
        # - construct projection matrix P
        self.P = Lambda_root * U.T  # sparse matrix mult
        self.P = self.P[0:self.n_PC, :]
        print(f"  - P shape: {self.P.shape}")

    def plot(self):
        # plots in R^2, could also build to plot in R^3

        self.P = np.asarray(self.P.todense())
        plt.scatter(self.P[0, :], self.P[1, :])
        # plt.tight_layout()
        plt.xlim([self.P[0, :].min(), self.P[0, :].max()])
        plt.show()



    def main(self):
        self.load_adjacency()
        self.build_sparse_matrices()
        self.eigendecomposition()
        self.project()
        if self.plot_it:
            self.plot()


if __name__ == '__main__':
    file_path = r'C:\Users\liqui\PycharmProjects\THESIS\venv\Lib\pims-filter\adjacency_train.json'
    PF = PIMS_Filter(file_path, 2, plot_it=True)

    PF.main()


##################################################################
####################### ORIGINAL SCRIPT ##########################
##################################################################

