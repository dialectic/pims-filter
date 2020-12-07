import json
import numpy as np
from scipy.linalg import eig, eigh
from scipy.sparse.linalg import eigs, eigsh
from scipy.sparse import dok_matrix, diags
from matplotlib import pyplot as plt
from matplotlib import rc
import tikzplotlib
import pickle

plot_it = True # must be n_PC = 2
plot_labeled = False # must be n_PC = 2
pickle_it = True # pickle projection matrix
n_PC = 2 # number of principle components
adjacency_file = '../dialectica-pimsifier/adjacency_train.json'

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
print(f"  - A:\n{A}")
# populate Laplacian
L = D - A

# print(f"  - Lapacian:\n{L.todense()}")

# print(f"  - Lapacian eig:\n{eig(L.todense())[0]}")

# eigendecomposition
# - using ARPACK via https://docs.scipy.org/doc/scipy/reference/tutorial/arpack.html
# - we want the largest eigenvals/vecs of L^+
# - equivalently, we find the smallest eigenvals/vecs of L
# - used sigma=0 to do the shift-invert mode
try:
  evals_small, evecs_small = eigsh(L, n_PC+1, sigma=0, which='LM')
except RuntimeError:
  evals_small, evecs_small = eigsh(L, n_PC+1, which='SA')
evals = 1/evals_small[1:None] # exclude smallest because it's approximating the zero eigenvalue
evecs = evecs_small[:,1:None] # exclude smallest because it's approximating the zero eigenvalue
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

print(f"  - P: {P.todense()}")

# pickle
if pickle_it:
  pickle.dump(
    P.todense(),
    open("../Data/Projection.pkl", "wb")
  )

# plot scatter 
if plot_it:
  P = np.asarray(P.todense())
  plt.scatter(P[0,:],P[1,:])
  # plt.tight_layout()
  plt.xlim([P[0,:].min(),P[0,:].max()])
  plt.show()

# plot labeled scatter 
if plot_labeled:
  # rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
  rc('text', usetex=True)
  fig, ax = plt.subplots()
  labels = ["\\bigcup","A_1","A_{12}","A_{13}","A_{123}","B_1","B_{12}","B_{13}","B_{134}","B_1 C_1","C_1","C_{12}","C_{13}","C_{134}"]
  labels = ["$"+s+"$" for s in labels]
  colors = ['black',"green","green","green","green","blue","blue","blue","blue","purple","red","red","red","red"]
  for i in range(0,n_nodes):
    ax.plot(P[0,i],P[1,i], marker='o',color=colors[i])
    ax.text(P[0,i]+.02,P[1,i]+.02, 
      labels[i], color='black', 
      ha='left', va='bottom'
    )
  plt.xlim([-2,1])
  plt.ylim([-1.5,1.5])
  tikzplotlib.save("scatter_tikz.tex")
  plt.show()
