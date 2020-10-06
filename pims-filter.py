import json
import numpy as np
from scipy.linalg import eig, eigh
from scipy.sparse.linalg import eigs, eigsh
from scipy.sparse import dok_matrix, diags
from matplotlib import pyplot as plt

class PIMS_Filter:
  """

  """
  def __init__(self, adjacency_file, n_PC, plot_it=False):
    self.adjacency_file = adjacency_file
    self.n_PC = n_PC




  def load_adjacency(self):
    # Loads adjacency file and populates adjacency_list and adjacency_index
    with open(self.adjacency_file, 'rb') as adj_file:
      adjacency_dict = json.load(adj_file)

    try:
      adjacency_list = adjacency_dict["list"]
      adjacency_index = adjacency_dict["nodes"]
    except:
      ValueError("Argument 'adjacency_file' must be a dictionary w/ keys, 'list' and 'nodes'")


  def build_sparse_matrices(self):
    # populates variables A, D, L
    print('temp')

  def eigendecomposition(self):
    # populates evals and evecs
    print('temp')

  def project(self):
    # projects to R^n where n == n_PC and populates P
    print('temp')

  def plot_it(self):
    # plots in R^2, could also build to plot in R^3
    print('temp')





if __name__ == '__main__':
  PF = PIMS_Filter

  
##################################################################
####################### ORIGINAL SCRIPT ##########################
##################################################################

plot_it = True # must be n_PC = 2
n_PC = 2 # number of principle components
adjacency_file = 'dialectica-pimsifier/adjacency.json'
test_file = 'dialectica-pimsifier/THESIS-code-dump/test_data.json'

# load adjacency
with open(adjacency_file, "r") as read_file:
  adjacency = json.load(read_file)
adjacency_list = adjacency["list"]
adjacency_index = adjacency["nodes"]
n_nodes = len(adjacency_index) # number of nodes

# build sparse matrices
A = dok_matrix((n_nodes,n_nodes), dtype=np.float32) # adjacency
D = dok_matrix((n_nodes,n_nodes), dtype=np.float32) # degree
L = dok_matrix((n_nodes,n_nodes), dtype=np.float32) # Laplacian
# populate degree and adjacency
for i in range(0,n_nodes):
  adjacents = adjacency_list[i]
  D[i,i] = len(adjacents)
  for j in range(0,len(adjacents)):
    A[i,adjacents[j]] = 1
    A[adjacents[j],i] = 1
# populate Laplacian
L = D - A

# eigendecomposition
# - using ARPACK via https://docs.scipy.org/doc/scipy/reference/tutorial/arpack.html
# - we want the largest eigenvals/vecs of L^+
# - equivalently, we find the smallest eigenvals/vecs of L
# - used sigma=0 to do the shift-invert mode
evals_small, evecs_small = eigsh(L, n_PC, sigma=0, which='LM')
# evals_small, evecs_small = eigsh(L, n_PC, which='SA')
evals = 1/evals_small
evecs = evecs_small # scale by whatever
evecs_T = evecs.T
print(f"  - truncated evals: {evals}")

# TODO error checking: evals should all be positive or zero

# build projection matrix P
# - a node i vector is a unit vector e_i
# - Saerens (2004) eq 8 tells us a transformed node i vector is
# -- Lambda^(1/2) U^T e_i.
# - we needn't recompute the matrix multiplication each time
# - do it once and build lookup table
# - we'll assume n_PC is small so we can use dense matrices
# - construct U and Lambda
# -- must reshape with zero padding
U = dok_matrix((n_nodes,n_nodes), dtype=np.float32) # evec matrix
Lambda_root = dok_matrix((n_nodes,n_nodes), dtype=np.float32) # eval matrix
for i in range(0,n_PC):
  Lambda_root[i,i] = np.sqrt(evals[i])
  for j in range(0,n_nodes):
    U[j,i] = evecs[j,i]
# - construct projection matrix P
P = Lambda_root*U.T # sparse matrix mult
P = P[0:n_PC,:]
print(f"  - P shape: {P.shape}")

# plot
if plot_it:
  P = np.asarray(P.todense())
  plt.scatter(P[0,:],P[1,:])
  # plt.tight_layout()
  plt.xlim([P[0,:].min(),P[0,:].max()])
  plt.show()
