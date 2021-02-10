# CK-GPTune

---
## CK-GPTune Setup

***Installation of CK-GPTune.***
To use CK-GPTune, users first need to install the CK framework using the following command.
```Bash
$ pip install ck --user
```
This will create a directory named *CK* in the home directory and install the CK framework.

We provide a repository of CK-GPTune on Github ([https://github.com/yhcho614/ck-gptune](https://github.com/yhcho614/ck-gptune)).
Users can install CK-GPTune using the following command.

```Bash
$ ck pull repo --url=https://github.com/yhcho614/ck-gptune
```

CK-GPTune will be installed in *$HOME/CK/ck-gptune*.
CK-GPTune relies on several other CK repositories (e.g. ck-autotuning, ctuning-programs).
These repositories will be automatically installed when installing CK-GPTune.

***Installation and Detection of GPTune.***
With CK-GPTune, users have the option to install GPTune ([https://github.com/gptune/GPTune/tree/history_db](https://github.com/gptune/GPTune/tree/history_db)) automatically using the following command.

```Bash
$ ck install ck-gptune:package:gptune
```

GPTune relies on several software packages such as OpenMPI, BLAS, LAPACK, Scalapack [1], MPI4PY [2], Scikit-optimize [3], and Autotune [4].
The command automatically detects if these software packages are available on your system.
If there are missing software packages, CK-GPTune will print out a message to let you know which software packages need to be installed. If there are multiple software versions in your computer, CK-GPTune will ask you to choose one.
After resolving all the dependencies, CK-GPTune installs the GPTune library in *$HOME/CK-TOOLS*
(e.g. *$HOME/CK-TOOLS/lib-gptune-1.0.0-gcc-9.3.0-compiler.python-3.8.5-linux-64*).

To use CK-GPTune, users need to detect the installed GPTune software with the following command.
The command detects the GPTune installation path and prepares an executable environment by setting all the environment variables needed by GPTune.

```Bash
$ ck detect soft:lib.gptune
```

Some users may want to use already installed GPTune or install GPTune manually by following the GPTune UserGuide [5].
In this case, users can simply use the above command to detect the installed GPTune and continue using CK-GPTune.

---
## Run GPTune Examples

CK-GPTune currently provides four example programs including *gptune-demo*, *scalapack\-pdqrdriver* [1], *superlu-pddspawn* [6], and *hypre-ij* [7].
Each program has its own working directory (e.g. *$HOME/CK/ck-gptune/program/scalapack-pdqrdriver/)*.

These example programs are managed as components (i.e. CK entries) of [the CK's program module](https://cknowledge.io/c/module/program/) that provides a unified way for program compilation and execution workflow.
With the CK program module, for example, you can compile and run these benchmarks with a simple command line interface (CLI).
To compile the scalapack-pdqrdriver example, you can use the following command.

```Bash
$ ck compile ck-gptune:program:scalapack-pdqrdriver
```

This will compile and install the software for the scalapack-pdqrdriver example in *$HOME/CK/ck-gptune/program/scalapack-pdqrdriver/tmp*.
While installing the software, CK-GPTune will detect the installation paths and the versions of the required software packages (e.g. OpenMPI, scalapack).
These software dependencies are defined in *meta.json* in the *.cm* directory of each benchmark program, and the detected versions of software dependencies are stored in the *tmp-deps.json* file in the same directory.

Then, you can also run the example using the following command.

```Bash
$ ck run ck-gptune:program:scalapack-pdqrdriver
```

This command will run the example as defined by the *run\_cmd* in the *meta.json* file.
Each of our four example programs has a Python script to run autotuning with GPTune.
The run command will execute the Python script and stores the output into the *stdout.out* file in the *tmp* directory.
Currently the run command does not pass additional arguments to the script, and the Python script runs with a default setting.

CK-GPTune provides a CK module called *gptune* to run these examples with more functionalities (e.g. run with history database, passing additional arguments).
In CK modules, we can define and implement our own actions using Python.
The *gptune* module currently offers two actions *autotune* and *crowdtune*.
The *autotune* action will run GPTune for the example without using the history database, which is equivalent to command *$ ck run ck-gptune:program:[example]*.

```Bash
$ ck autotune gptune --bench=scalapack-pdqrdriver
```

With the *gptune* module, we can also pass additional arguments as shown in the below command; the module internally uses environment variables to pass the arguments values.
If the argument values are not given by this command line, the example will run with the default setting.
```Bash
$ ck autotune gptune --bench=scalapack-pdqrdriver --ntask=10 --nruns=10
```

The *crowdtune* action, on the other hand, automatically invokes the history database while running autotuning.

```Bash
$ ck crowdtune gptune --bench=scalapack-pdqrdriver --ntask=10 --nruns=10 --machine=cori
```

With this command, the scalapack pdqrdriver example loads existing performance data from the performance data file.
The output and the performance data file are stored in the working directory (*tmp* directory) of the example.
CK-GPTune supports storing the information about machine specifications and the software dependencies.
The machine related information (e.g. machine name, number of cores/nodes) needs to be passed as arguments.
```Bash
$ ck crowdtune gptune --bench=scalapack-pdqrdriver --ntask=10 --nruns=10 --machine=cori -nnodes=1 -ncores=16
```
The software dependency information, on the other hand, is automatically parsed from the example program directory (there is tmp-deps.json file that stores the information about software dependencies).

---
## References

[1] L.  S.  Blackford,  J.  Choi,  A.  Cleary,  E.  D’Azevedo,  J.  Demmel,  I.  Dhillon,  J.  Don-garra, S. Hammarling, G. Henry, A. Petitet, K. Stanley, D. Walker, and R. C. Whaley.ScaLAPACK Users’ Guide.  Society for Industrial and Applied Mathematics, 1997.

[2] L. D. Dalcin, R. R. Paz, P. A. Kler, and A. Cosimo.  Parallel distributed computingusing python.Advances in Water Resources, 34(9):1124 – 1139, 2011.  New Computa-tional Methods and Software Tools.

[3] Scikit-Optimize.   Scikit-optimize.https://scikit-optimize.github.io/stable/,2020

[4] Autotune.  Autotune.https://pypi.org/project/autotune/, 2018.

[5] W. M. Sid-Lakhdar, J. W. Demmel, X. S. Li, Y. Liu, and O. Marques. Gptune UserGuide, 2020.

[6] X. S. Li and J. W. Demmel. Superludist:  A scalable distributed-memory sparse directsolver for unsymmetric linear systems.ACM Trans. Math. Softw., 29(2):110–140, June2003.

[7] R. D. Falgout and U. M. Yang.  hypre:  A library of high performance preconditioners.In P. M. A. Sloot, A. G. Hoekstra, C. J. K. Tan, and J. J. Dongarra, editors,Com-putational  Science  —  ICCS  2002,  pages 632–641,  Berlin,  Heidelberg,  2002. SpringerBerlin Heidelberg.
