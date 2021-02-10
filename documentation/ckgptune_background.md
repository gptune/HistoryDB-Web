# CK-GPTune

In this section, we introduce CK-GPTune which is a workflow automation framework for GPTune.
CK-GPTune helps users install GPTune and provides an interface to run GPTune using simple commands.
CK-GPTune also provides some example programs that users can install/run/autotune using the workflow automation technology.
CK-GPTune is built based on the [Collective Knowledge (CK)](https://cknowledge.org) technology [1] that provides a lot of useful functions to automate (experiment) workflows and to define/detect software dependencies to compile and run applications automatically.

---
## Background of CK

CK is a tool which helps organize research workflows.
CK can manage many different things, such as research data, programs or scripts analyzing this data, as well as the research data. In our CK-GPTune, it is used for recording and  organizing the history data of simulations. 

In CK, there are three important concepts: *entries*, *repositories*, *modules*. Here, we provide a brief introduction of these concepts.

* CK Entries: Each entry represents a research component (e.g. data, program, script) that you want to manage. Each entry has *meta.json* that contains meta information (e.g. run command, compiler/runtime dependencies) about the entry.

* CK Repositories: Each CK repository is a collection of entries which are meant to be shared with other people. For example, to install a CK repository *ck-autotuning*, we can use the following commands:
    
    ```
    $ ck pull repo:ck-autotuning
    ```
    <br>
    ```
    $ ck pull repo --url=https://github.com/ctuning/ck-autotuning
    ```

* CK Modules: Modules group entries with "actions" to operate on these entries. Each module has *module.py* in that we can define its customized actions.
    
    ```
    $ ck [action] [module:entry]
    ```

CK provides many useful modules such as "program", "package", and "experiment". For example, the program module [CK Problem Module](https://cknowledge.io/c/module/program/) offers actions to compile and run programs.
    
```
$ ck compile program:gemm
$ ck run program:gemm
```

For more information, [the CTuning community](https://ctuning.org) provides a lot of documentation about CK including a detailed user manual [CK:Manual](https://ck.readthedocs.io/_/downloads/en/latest/pdf/).
Also, there is a blog at [https://github.com/michel-steuwer/About-CK](https://github.com/michel-steuwer/About-CK) that provides a good overview of CK.

---
## References

[1] L.  S.  Blackford,  J.  Choi,  A.  Cleary,  E.  D’Azevedo,  J.  Demmel,  I.  Dhillon,  J.  Don-garra, S. Hammarling, G. Henry, A. Petitet, K. Stanley, D. Walker, and R. C. Whaley.ScaLAPACK Users’ Guide.  Society for Industrial and Applied Mathematics, 1997.

[2] L. D. Dalcin, R. R. Paz, P. A. Kler, and A. Cosimo.  Parallel distributed computingusing python.Advances in Water Resources, 34(9):1124 – 1139, 2011.  New Computa-tional Methods and Software Tools.

[3] Scikit-Optimize.   Scikit-optimize.https://scikit-optimize.github.io/stable/,2020

[4] Autotune.  Autotune.https://pypi.org/project/autotune/, 2018.

[5] W. M. Sid-Lakhdar, J. W. Demmel, X. S. Li, Y. Liu, and O. Marques. Gptune UserGuide, 2020.

[6] X. S. Li and J. W. Demmel. Superludist:  A scalable distributed-memory sparse directsolver for unsymmetric linear systems.ACM Trans. Math. Softw., 29(2):110–140, June2003.

[7] R. D. Falgout and U. M. Yang.  hypre:  A library of high performance preconditioners.In P. M. A. Sloot, A. G. Hoekstra, C. J. K. Tan, and J. J. Dongarra, editors,Com-putational  Science  —  ICCS  2002,  pages 632–641,  Berlin,  Heidelberg,  2002. SpringerBerlin Heidelberg.
