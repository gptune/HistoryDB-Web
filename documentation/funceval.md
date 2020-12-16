# User Guide: Re-using Function Evaluation Data

This section describes how users can use previous function evaluation data for their optimization problem.
GPTune users first need to write a Python code for their optimization problem, as explained in the GPTune UserGuide manual~\cite{GPTuneUserGuide}.
Then, users can invoke the history database in one of two ways.
The first way is manually invoking the history database from the Python code.
The other way is adding the user's program and the Python code into the CK-GPTune's program list to take advantage of the CK-GPTune workflow automation.
One of the main differences between the manual and the CK-GPTune approach is that users who are using the manual approach need to pass information about software dependencies and machine configuration by hand.

---
## Performance Data

Listing~\ref{listing:pdqrdriver.json} shows a performance data file for the QR factorization routine of ScaLAPACK [3] for two different tasks \{m: 816, n: 599\} and \{m: 669, n: 164\}.
In this example, we evaluated runtime of one parameter configuration for each task (two parameter configurations in total).
In Listing~\ref{listing:pdqrdriver.json}, \texttt{I} contains the information about each task parameter, and all the performance data of that task are stored in \texttt{func\_eval} as an array where each array item contains the tuning parameter configuration \texttt{P} and its evaluation result \texttt{O}.
In GPTune, there is a Python class named \texttt{data} to store sampled tasks, tuning parameters and outputs~\cite{GPTuneUserGuide}.
After finishing each function evaluation, the history database queries the contents of the \texttt{data} class and updates the performance data file.

Each function evaluation data in *func\_eval* can also contain the information about the machine and software configuration to run the application.
The information related to the machine configuration includes the machine name (e.g. Cori) and the number of cores/nodes used.
The software information contains the versions of software packages that are used for compiling/installing the application.
The machine and software configurations are stored in *machine\_deps* and *compile\_deps*, respectively.
Unlike task and tuning parameters, the machine and software information is not available in GPTune and needs to be given by the user.
Users can use CK-GPTune to automatically detect the software dependencies or provide the information manually in the application-GPTune driver code.

<details>
<summary>Example JSON performance data</summary>
<div markdown="1">
```Json
{
  "name": "pdqrdriver",
  "perf_data": [
    {
      "I": {
        "m": 816,
        "n": 599
      },
      "func_eval": [
        {
          "P": {
            "mb": 6,
            "nb": 16,
            "nproc": 3,
            "p": 2
          },
          "machine_deps": {
            "machine": "intel72",
            "nodes": 1,
            "cores": 1
          },
          "compile_deps": {
            "openmpi": {
              "version": "40",
              "version_split": [
                40
              ]
            },
            "scalapack": {
              "version": "2.1.0",
              "version_split": [
                2,
                1,
                0
              ]
            }
          },
          "O": {
            "r": 0.132027
          }
        }
      ]
    },
    {
      "I": {
        "m": 669,
        "n": 164
      },
      "func_eval": [
        {
          "P": {
            "mb": 2,
            "nb": 5,
            "nproc": 2,
            "p": 1
          },
          "machine_deps": {
            "machine": "intel72",
            "nodes": 1,
            "cores": 1
          },
          "compile_deps": {
            "openmpi": {
              "version": "40",
              "version_split": [
                40
              ]
            },
            "scalapack": {
              "version": "2.1.0",
              "version_split": [
                2,
                1,
                0
              ]
            }
          },
          "O": {
            "r": 0.0154
          }
        }
      ]
    }
  ]
}
```
</div>
</details>

<br>
## Python Interface for History Database

We first describe how to modify the Python code to call the history database.
To do so, users need to add several lines of code to define the history database setting and send the machine/software information.
Listing~\ref{listing:python_interface} shows an example.
First, users need to create an instance of the history database module \texttt{HistoryDB} (lines 8 and 30) and turn on the history database mode (line 31).
Users also need to set \texttt{application\_name} as the program name (line 32); the database will create a database file using this name.
It is also possible to optionally define the path of the database file by setting \texttt{history\_db\_path} (line 33).

As shown in lines 35--49, users can optionally send the information about their machine and software configuration.
For the machine configuration, users can send the machine name and the number of nodes/cores used (lines 36--40).
%, and the versions of software packages that have compile and runtime-level software dependencies.
As shown in lines 41--49, the software versions are passed as dictionaries which can contain a string of the software version and an array of the version split numbers (e.g. major, minor, and revision numbers).
While version split numbers are used by default, as shown in line 49, users can also use a different identifier such as Git commit information.
This can be helpful if the software does not have a specific version number.
As shown in lines 51--78, users can define conditions (\texttt{load\_deps}) using dictionaries to selectively load previous performance data.
For each load condition, the user may use an array to allow multiple configurations for loading.
For example, line 56 allows to load performance data obtained when using 15, 16, and 17 core counts.
Finally, users need to register the history database instance when creating the GPTune instance (line 81).
GPTune will then run with the history database mode while loading/storing the performance data from/into the user's local storage.

<details>
<summary>Example Python application-GPTune driver code</summary>
<div markdown="1">
```Python
from autotune.search import *
from autotune.space import *
from autotune.problem import *
from gptune import GPTune
from data import Data
from options import Options
from computer import Computer
from historydb import HistoryDB

task_space = Space([Categorical(['a','b','c'], name="pb")])
input_space = Space([Integer(0, 10, name="x")])
output_space = Space([Real(0.0, inf, name="time")])

def objective(point):
    from math import exp
    return exp(point['x'])

cst1 = "x >= .5"
def cst2(point):
    return (point['x'] < 1.5)
    
constraints = {'cst1': cst1, 'cst2': cst2}

problem = TuningProblem(task_space, input_space, output_space, objective, constraints, None) # no analytical model

computer = Computer(nodes=1, cores=16)
option = Options()

# setting to use the history database
history_db = HistoryDB()
history_db.history_db = 1 # turn on the history database mode
history_db.application_name = 'scalapack-pdqrdriver' # database file name
history_db.history_db_path = './' # default location is $PWD

# optional information to store into the history database
history_db.machine_deps = {
    "machine":"cori",
    "nodes":1,
    "cores":16
}
history_db.compile_deps = {
    "openmpi":{
        "version":"4.0.0",
        "version_split":[4,0,0],
    },
    "scalapack":{
        "git":"bc6cad585362aa58e05186bb85d4b619080c45a9"
    },
}
        
# conditions for loading previous performance data
history_db.load_deps = {
    "machine_deps": {
        "machine":['cori'], # load only if the data's machine name is cori
        "nodes":[1], # load only if the data's node count is 1
        "cores":[15,16,17] # load if the data's core count is 15, 16, or 17.
    },
    "compile_deps": {
        "mpi":[
            {
                "name":"openmpi",
                "version_from":[4,0,0],
                "version_to":[5,0,0]
            },
            {
                "name":"intelmpi"
            }
        ],
        "scalapack":[
            {
                "name":"scalapack",
                "git":"bc6cad585362aa58e05186bb85d4b619080c45a9"
            }
        ]
    }
}

# add the history db module into the GPTune module
gt = GPTune(problem, computer=computer, data=data, options=options, history_db=history_db)

ntask = 2
nruns = 20
giventask = [[1],[2]]

(data, model, stats) = gt.MLA(NS=nruns, Igiven=giventask, NI=ntask, NS1=max(nruns/2, 1))

```
</div>
</details>

<br>

## Leverage Workflow Automation with CK-GPTune

In CK-GPTune, programs are managed as components of the CK's \texttt{program} module~\cite{Fursin:CKProgram} that provides a unified way for program compilation and workflows (and automatic detection of software dependencies) using a CLI and meta description files.
For these programs, CK-GPTune can automatically run GPTune with the history database.
Users therefore need to add their program and the Python interface code that calls GPTune into the CK-GPTune's program list to take advantage of CK-GPTune.

Users can create an entry of a new program using the following command.

```Bash
$ ck add ck-gptune:program:my_test_program
```

The command then prints the available templates as shown in the below, and users can select one of these template and extend it for their applications.

```Bash
0) C program "Hello world" (--template=template-hello-world-c)
1) C program "Hello world" with compile and run scripts (--template=template-hello-world-c-compile-run-via-scripts)
2) C program "Hello world" with jpeg dataset (--template=template-hello-world-c-jpeg-dataset)
3) C program "Hello world" with output validation (--template=template-hello-world-c-output-validation)
4) C program "Hello world" with xOpenME interface and pre/post processing (--template=template-hello-world-c-openme)
5) C++ program "Hello world" (--template=template-hello-world-cxx)
6) Fortran program "Hello world" (--template=template-hello-world-fortran)
7) Java program "Hello world" (--template=template-hello-world-java)
8) Python program "Hello world" (--template=template-hello-world-python)
9) bench-julia-sin (--template=bench-julia-sin)
10) cbench-automotive-susan (--template=cbench-automotive-susan)
11) milepost-codelet-mibench-automotive-susan-s-src-susan-codelet-1-1 (--template=milepost-codelet-mibench-automotive-susan-s-src-susan-codelet-1-1)
12) polybench-cpu-2mm (--template=polybench-cpu-2mm)
13) polybench-cuda-gemm (--template=polybench-cuda-gemm)
14) Empty entry

Select template for the new entry (or press Enter for 0):
```

The command will create a directory for the program at \texttt{\$}\path{HOME/CK/ck-gptune/program/my_test_program}.
Instead of using these templates, users can also copy content from an existing program and modify/extend the content for their program.

```Bash
$ ck copy ck-gptune:program:scalapack-pdqrdriver ck-gptune:program:my_test_program
```

After creating the entry, users may add source codes, run/compile scripts, and datasets into the program's directory.
Then, users need to define their actions (e.g.\ how to compile and run, what are the required software packages, etc.) in the meta description file (\texttt{\$}\path{HOME/CK/ck-gptune/program/my_test_program/.cm/meta.json}).

Listing~\ref{listing:meta_description_example} shows an example meta description file.
In lines 4--22, the meta description file describes how to compile the program and its compile-level dependencies.
The software packages needed by the program are automatically detected based on their tags during program compilation.
CK internally uses the CK \texttt{soft} module~\cite{Fursin:CKSoft} which is able to detect many software packages.
However, if CK does not support detecting a certain software package, the user has to add a new detection plugin by following the CK manuals~\cite{CK:UserGuide:Automating,CK:Manual}.
CK-GPTune automatically stores the detected software versions into the history database.
As shown in lines 23--30, the user can also define runtime-level dependencies.
Lines 53--66, on the other hand, define how to run their program for autotuning.
The user probably just needs to set *run\_cmd\_main* as a runnable command; the command should run the Python interface code which calls GPTune for for the user's optimization probelm (there is no need to manually invoke the history database).
Also, as shown in lines 31--52, the user can define some rules using JSON format to selectively load previous performance data.

After completing the meta description file, the user can run the program with the history database using CK-GPTune commands, as shown in the examples in Section~\ref{sec:ck-gptune:gptune_examples}.
First, the user needs to compile and install the program using the following command.
```Bash
$ ck compile program:my_test_program
```
The command detects software dependencies defined in the meta description file and stores the detected software information in the program's working directory.
CK-GPTune will send the detected software versions to the history database and stores the information into the performance data file.
After installing the program, the following command runs GPTune with history database.
```Bash
$ ck crowdtune gptune --bench=my_test_program
```
The line executes the command described in the meta description file and automatically invokes the history database.
GPTune loads existing performance data from the performance data file according to the load rules in the meta description file.
The machine related information (machine name, number of cores/nodes) can be passed as arguments, as follows.
```Bash
$ ck crowdtune gptune --bench=my_test_program --machine=cori --nodes=1 --cores=16
```
In addition to the purpose of passing machine information to CK-GPTune, the user may require additional arguments to pass to user programs or scripts.
Arguments of the above command line are treated as environment variables.
Hence, to receive arguments through the command line, the user needs to modify the user program to get the argument values through environment variables.

<details>
<summary>Example meta description file</summary>
<div markdown="1">
```Json
{
  "backup_data_uid": "8bf9aa0ad04427bb",
  "build_compiler_vars": {},
  "use_compile_script": "yes"
  "compile_cmds": {
    "default": {
      "cmd": "bash ../install_scalapack$#script_ext#$"
    }
  },
  "compile_deps": {
    "openmpi": {
      "local": "yes",
      "name": "OpenMPI library",
      "tags": "lib,mpi,openmpi",
      "version_from": [4,0,1]
    },
    "scalapack": {
      "local": "yes",
      "name": "SCALAPACK",
      "tags": "lib,scalapack"
    }
  },
  "run_deps": {
    "lib-gptune": {
      "local": "yes",
      "name": "GPTune library",
      "tags": "lib,gptune",
      "version_from": [1,0,0]
    }
  },
  "load_deps": {
    "machine_deps": {
        "machine":['cori'],
        "nodes":[1],
        "cores":[15,16,17]
    },
    "compile_deps": {
        "mpi":[
            {
                "name":"openmpi",
                "version_from":[4,0,0],
                "version_to":[5,0,0]
            }
        ],
        "scalapack":[
            {
                "name":"scalapack",
                "version_to":[2,1,0]
            }
        ]
    }
  },
  "run_cmds": {
    "default": {
      "ignore_return_code": "no",
      "run_time": {
        "run_cmd_main": "$MPIRUN -n 1 $<<CK_ENV_COMPILER_PYTHON_FILE>>$ ..$#dir_sep#$run_autotuner.py",
        "run_cmd_out1": "stdout.log",
        "run_cmd_out2": "stderr.log",
        "run_output_files": [
          "stdout.log",
          "stderr.log"
        ]
      }
    }
  },
  "process_in_tmp": "yes"
}
```
</div>
</details>

<br><br>
