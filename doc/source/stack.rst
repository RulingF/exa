Full Stack Design
======================================
In the graphic below, the technical organization of the code's logic is
described. Specifically, the distribution of communication (between languages)
and structure of GUI related code is given. In a model-view-controller sense
(the model updates the view, the user sees the view, the users interacts with
the controller, the controller manipulates the model, and the cycle repeats),
the model is the (backend) **Python** code, the view is **container.js**,
and the controller is **app.js**. In some cases the controller only
performs aesthetic changes to the view and does not require communication with
the model (note that communication between the controller and model, and model
and view is the most expensive step due to transformation of objects between
languages - usually requiring in memory copies).

.. image:: _static/stack.jpg


Scalability and Compilation
================================================
Efficient distributed and parallelized calculation can be difficult to achieve
in practice. Scalable computations are organized by their ability to be distributed
across multiple (network connected) computers (real or virtual), scalable
across a multicore/multithread CPU and/or GPU, and propensity for ahead-of-time
compilation (AOT) or just-in-time compilation (JIT) to C or C++ code (for example).

From the least to the most computationally efficient, exa leverages:

- python operators, iterators, generators, etc
- numpy/pandas/scipy
- cython/numba
- ipyparallel

For out of core work, exa leverages:

- numpy memory maps

Because of the inherent inefficiency with out of core algorithms (disk is slower
than RAM), these operations are treated on different footing than in core work;
their performance should not be directly compared.

Below are some notes to consider when building scalable, parallelized functions.

- All threaded functions must release the GIL (or worker must release the GIL)
- Parallelization/distribution of the outermost loop is generally more performant because it has less communication overhead
- JIT compilation is almost always faster than AOT compilation (from a few percent to 5X+)
- Multidimensional arrays are generally slower than 1D arrays
- Reshaping/raveling is faster than concatenation
- Threading (CPU) vectorized functions is performant for arrays with length > ~5*10**5
- Threading (GPU) vectorized functions should not be done
- GPU computation is performant when the GPU has a lot of work to do but a small amount of data to transfer
