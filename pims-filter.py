import json
import numpy as np
from scipy.linalg import eig, eigh
from scipy.sparse.linalg import eigs, eigsh
from scipy.sparse import dok_matrix, diags
from matplotlib import pyplot as plt
from mpl_toolkits import mplot3d

class PIMS_Filter:
    """
    TODO: finish commenting class
    TODO: plot in 3 dimensions
    TODO: better error checking?
    TODO:

    """
    def __init__(self, adjacency_file, n_PC, plot_it=False, plot_dim=2, save_path=''):
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

        self.save_path = save_path

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


        try:
          evals_small, evecs_small = eigsh(self.L, self.n_PC+1, sigma=0, which='LM')
        except RuntimeError:
          evals_small, evecs_small = eigsh(self.L, self.n_PC+1, which='SA')
        
        if any(evals_small <= 0):
            raise ValueError(f'evals_small <= 0') # TODO add a more helpful error message
        
        self.evals = 1/evals_small[1:None] # exclude smallest because it's approximating the zero eigenvalue
        self.evecs = evecs_small[:,1:None] # exclude smallest because it's approximating the zero eigenvalue
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
        P = np.asarray(self.P.todense())
        if self.n_PC == 1:
          print(f'TODO: Cannot plot {self.n_PC} dimensions.')
        elif self.n_PC == 2:
          fig = plt.figure()
          ax = fig.add_subplot(111)
          plt.scatter(P[0, :], P[1, :])
          plt.xlim([P[0, :].min(), P[0, :].max()])
        elif self.n_PC == 3:
          fig = plt.figure()
          ax = plt.axes(projection='3d')
          ax.scatter3D(
            P[0, :], P[1, :], P[2, :]
          )
          plt.xlim([P[0, :].min(), P[0, :].max()])
          plt.ylim([P[1, :].min(), P[1, :].max()])
          ax.set_zlim([P[2, :].min(), P[2, :].max()])
        else:
          print(f'Cannot plot {self.n_PC} dimensions.')
          return 1
        plt.show()


    def save_projection(self):
        import pickle
        proj = dok_matrix.toarray(self.P)
        proj = proj.T
        with open(self.save_path, 'wb') as f:
            pickle.dump(proj, f)


    def main(self):
        self.load_adjacency()
        self.build_sparse_matrices()
        self.eigendecomposition()
        self.project()
        if self.plot_it:
            self.plot()
        if self.save_path != '':
            self.save_projection()


if __name__ == '__main__':
    file_path = r'C:\Users\liqui\PycharmProjects\THESIS\venv\Lib\pims-filter\adjacency_train.json'
    save_path = r'C:\Users\liqui\PycharmProjects\Generation_of_Novel_Metastimulus\Lib\Misc_Data\Projection_10dims.pkl'
    PF = PIMS_Filter(file_path, 10, save_path=save_path, plot_it=False)

    PF.main()


##################################################################
####################### ORIGINAL SCRIPT ##########################
##################################################################

