![exa](doc/source/_static/logo.png)

[![Documentation Status](https://readthedocs.org/projects/exa/badge/?version=latest)](http://exa.readthedocs.io/en/latest/?badge=latest)

[![Build Status](https://travis-ci.org/avmarchenko/exa.svg?branch=master)](https://travis-ci.org/avmarchenko/exa)

[![codecov](https://codecov.io/gh/avmarchenko/exa/branch/master/graph/badge.svg)](https://codecov.io/gh/avmarchenko/exa)

# Installation
**Note** conda build coming soon!
The typical Python data stack is required (example using the **conda** package manager).
```
conda install numpy scipy pandas seaborn scikit-learn jupyter notebook ipywidgets sphinx
```
Currently there are some growing pains associated with our dependencies. Ensure that
you have identical version numbers on ipywidgets and jupyter-client (eg. ipywidgets=4.1.1
and jupyter-client=4.1.1).


# Getting Started


# Documentation
Documentation is generated using [sphinx](http://sphinx-doc.org "Sphinx")
```
cd doc
make html    # .\make.bat html # Windows
```
