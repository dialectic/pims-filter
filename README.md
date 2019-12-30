# pims-filter

This Python package is a personal information management filter (PIMS filter) for text-based user information.

## Installation

To clone recursively all submodules, use the following command.

```bash
git clone --recursive https://github.com/ricopicone/pims-filter.git
```

## Submodules

This package uses a submodule structure as follows.

- `pims-filter` (python) computes filter from `adjacency.json` and plots output
  - `dialectica-pimsifier` (ruby) builds Dialectica class from `THESIS-code-dump` and exports graph as adjacency array in `adjacency.json`
    - `dialectica-core` (ruby) used to build Dialectica class
    - `THESIS-code-dump` (python) tagged TeX to json dictionary

## TODO

- Convert `pims-filter.py` script into a class.
  - Should have attributes:
    - Adjacency file `adjacency_file`
    - Adjacency list `adjacency_list`
    - Adjacency index `adjacency_index`
    - Adjcency sparse matrix (`A`)
    - Degree sparse matrix (`D`)
    - Laplacian sparse matrix (`L`)
    - Number of principle components (`n_PC`)
    - Eigenvalues of L+ (`evals`)
    - Eiegenvectors of L+ (`evecs`)
    - Projection matrix (`P`)
    - Scatter plot figure
  - Should have methods:
    - `load_adjacency` that loads from `adjacency_file` and populates `adjacency_file` and `adjacency_list` 
    - `build_sparse_matrices` that populates `A`, `D`, `L`
    - `eigendecomposition` that populates `evals` and `evecs`
    - `project` that projects to <a href="https://www.codecogs.com/eqnedit.php?latex=\mathbb{R}^n" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\mathbb{R}^n" title="\mathbb{R}^n" /></a> with <a href="https://www.codecogs.com/eqnedit.php?latex=n" target="_blank"><img src="https://latex.codecogs.com/gif.latex?n" title="n" /></a>` = n_PC` and populates `P`
    - `plot_it` that plots in <a href="https://www.codecogs.com/eqnedit.php?latex=\mathbb{R}^3" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\mathbb{R}^2" title="\mathbb{R}^2" /></a> and maybe <a href="https://www.codecogs.com/eqnedit.php?latex=\mathbb{R}^3" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\mathbb{R}^3" title="\mathbb{R}^3" /></a>
  - Work TODO on submodules
    - Work on submodules is outlined in each submodule's `README`