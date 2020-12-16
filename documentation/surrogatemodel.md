# Re-using Pre-Trained Surrogate Models

In addition to the ability to reuse previous function evaluation data, the history database also supports storing and loading trained GP surrogate models.
Reusing pre-trained surrogate models can be useful for autotuning users because the modeling phase of GPTune can require a significant amount of time.
Users can use this feature to save the GP surrogate model after some autotuning and load a trained model to continue autotuning afterward.
Note that trained surrogate models may not be meaningful for different problem spaces.
The history database therefore loads trained models only if they match the problem space of the given optimization problem.


---
## Database Format

<details>
<summary>Example JSON model data</summary>
<div markdown="1">
```Json
{
  "name": "scalapack-pdqrdriver",
  "model_data": [
    {
      "hyperparameters": [
        1.0527605312568593,
        1.2715212554472748,
        1.2027294004347358,
        1.0517280135928133,
        1.1546119453408696,
        1.6413469213310425,
        1.5014948881756074,
        1.173993679837753,
        1.0,
        1.0,
        0.0023860485299051046,
        0.7600658732999609,
        0.0023860485299051046,
        0.7600658732999609,
        0.0031522461753559637,
        0.5901041554798607,
        0.14585622912945412,
        0.30551505890586245,
        0.17549255744288955,
        1.0808067485372712
      ],
      "model_stats": {
        "log_likelihood": -3.929220353125104,
        "neg_log_likelihood": 3.929220353125104,
        "gradients": [
          0.010411706436844118,
          0.012425768275627823,
          0.018340984906837037,
          0.01629360938204379,
          0.1079192443019152,
          0.059066991217628824,
          0.15281815815889632,
          0.19917686118958441,
          -0.04909524106806599,
          -0.4823841175020911,
          -12.039883262484398,
          -0.5320359818332572,
          -12.039883262484398,
          -0.5320359818332572,
          -11.431384333937665,
          -0.2983087111862601,
          -0.4503630784220767,
          -0.2074801503943561,
          -5.214696462276302,
          0.17629266890684875
        ],
        "gradients_sum_abs": 44.030296576198346,
        "gradients_average_abs": 2.201514828809917,
        "gradients_hmean_abs": 0.053634902189785866,
        "gradients_gmean_abs": 0.260899623554923,
        "iteration": 82
      },
      "func_eval": [
        "a9012a0a-2a4b-11eb-a97e-c93b9c1adf71",
        "a9012a0b-2a4b-11eb-a97e-c93b9c1adf71",
        "be4f71be-2a4b-11eb-a97e-c93b9c1adf71",
        "be4f71bf-2a4b-11eb-a97e-c93b9c1adf71"
      ],
      "task_parameters": [
        [
          1024,
          1024
        ],
        [
          2048,
          2048
        ]
      ],
      "problem_space": {
        "IS": [
          {
            "lower_bound": 128,
            "upper_bound": 16000,
            "type": "int"
          },
          {
            "lower_bound": 128,
            "upper_bound": 16000,
            "type": "int"
          }
        ],
        "PS": [
          {
            "lower_bound": 1,
            "upper_bound": 16,
            "type": "int"
          },
          {
            "lower_bound": 1,
            "upper_bound": 16,
            "type": "int"
          },
          {
            "lower_bound": 1,
            "upper_bound": 3,
            "type": "int"
          },
          {
            "lower_bound": 0,
            "upper_bound": 3,
            "type": "int"
          }
        ],
        "OS": [
          {
            "lower_bound": -Infinity,
            "upper_bound": Infinity,
            "type": "real"
          }
        ]
      },
      "modeler": "Model_LCM",
      "objective_id": 0,
      "time": {
        "tm_year": 2020,
        "tm_mon": 11,
        "tm_mday": 19,
        "tm_hour": 18,
        "tm_min": 43,
        "tm_sec": 57,
        "tm_wday": 3,
        "tm_yday": 324,
        "tm_isdst": 0
      },
      "uid": "be4f71c0-2a4b-11eb-a97e-c93b9c1adf71"
    }
  ]
}
```
</div>
</details>


In this example, we have assumed only the LCM approach used in the default GPTune setting.
Different modeling approaches may require different data format.

Storing model data is done automatically by GPTune history database if the user runs GPTune with the history database mode as described in Section~\ref{sec:userguide:func_eval}.
By default, the history database stores every modeling data during the optimization process into the database.

## Run MLA with Pre-Trained Surrogate Models

The (current) modeling method does not leverage any previous modeling information (e.g. pre-trained models) to (efficiently) update the surrogate model.
One possible and useful user scenario is to find out if there is a good enough surrogate model and use the model for optimization (with no additional updates or fewer updates).
Here, we explain how users can run MLA with pre-trained surrogate model data.
Similar to when loading history database, there are two ways to load a trained model for MLA: one is using manual Python coding and the other is using CK-GPTune's command line interface.

### Python Interface

GPTune provides a method called \texttt{MLA\_LoadModel} which runs MLA after loading a GP surrogate model from the database.
Users can invoke \texttt{MLA\_LoadModel} as follows.

```Python
`# create a history db module instance
history_db = HistoryDB(machine_deps, compile_deps, load_deps)
```

```Python
`# add the history db module into the GPTune module
gt = GPTune(problem, computer, data, options, history_db)
`# new method named "Load Model" in the GPTune module
`#gt.MLA(NS=nruns, Igiven=giventask, NI=ntask, NS1=max(nruns/2, 1))
gt.MLA_LoadModel(NS=nruns, Igiven=giventask)
```
Unlike the \texttt{MLA} method, \texttt{MLA\_LoadModel} does not require the information about the number of initial samples (\texttt{NS1}).
\texttt{MLA\_LoadModel} only requires the number of additional samples to be tuned after loading the model (\texttt{NS}) and the task parameter information (\texttt{Igiven}).
In \texttt{MLA\_LoadModel}, it is important to select the best model data from all available model data.
By default, \texttt{MLA\_LoadModel} selects the model data that contains most function evaluation results, assuming that we can build a better model with more function evaulation data.
\texttt{MLA\_LoadModel} also provides several more model selection methods, and users can choose one model selection method when calling \texttt{MLA\_LoadModel}, as follow.
\begin{lstlisting}[language=Python]
gt.MLA_LoadModel(NS=nruns, Igiven=giventask, method="max_evals"))
\end{lstlisting}
\textit{\textbf{Model selection parameters:}}
{\color{blue}method="max\_evals"}: choose the model that has most function evaluation data.
{\color{blue} method="MLE"} or {\color{blue} "mle"}: choose the model that has the highest likelihood.
{\color{blue} method="AIC"} or {\color{blue} "aic"}: choose the model based on Akaike Information Criterion (AIC).
{\color{blue} method="BIC"} or {\color{blue} "bic"}: choose the model based on Bayesian Information Criterion (BIC).
%[YC: it might be interesting to see how good these different model selection methods are; my current/previous experiments were too simple to see differences]

As shown in Figure~\ref{fig:reusing_surrogate_model}, once the surrogate model is loaded, by default \texttt{MLA\_LoadModel} does not update the model.
However, some users may want to update the model again after collecting a number of additional samples.
\texttt{MLA\_LoadModel} therefore provides an additional argument \texttt{update:int} which represents the number of additional samples needed for the model to be updated further.

```Python
gt.MLA_LoadModel(NS=nruns, Igiven=giventask, update=5)
```

With the above command, after loading the initial surrogate model, GPTune updates the model every time it gets five more samples.
If users want to update the model with other patterns, they can use both MLA\_LoadModel and MLA\_HistoryDB to reuse and update the model according to the user-defined pattern.

Although the provided model selection methods are easy to use, some users probably want to use more sophisticated methods based on the model statistics information.
Therefore, the GPTune history database provides a method called \texttt{ReadModelData} that reads all model data (that match the given tuning problem) as an array of dictionaries.

```Python
`# Read all model data as an array of dictionaries
model_data = history_db.ReadModelData(problem=problem, Igiven=Igiven)
```

As shown in Listing~\ref{listing:model_json}, the loaded model data contains the model statistics (e.g. (neg) log likelihood, last gradients, the number of iterations of the modeling algorithm, and the number of function evaluation data).
Users can define their own method to select the best model data (or discard the model data) based on the loaded model data.
Then, users can invoke \texttt{MLA\_LoadModel} by specifying the selected surrogate model using its unique ID (UID), as follows.

```Python
model_index = UserDefinedCriterion(model_data)
model_uid = model_data[model_index]["uid"]
gt.MLA_LoadModel(NS=nruns, Igiven=giventask, model_uid=model_uid))
```

### CK-GPTune Interface

Users can also use CK-GPTune to invoke \texttt{MLA\_LoadModel} automatically.
Users can use the following command to run MLA with pre-trained surrogate models.

```Bash
$ ck MLA_LoadModel gptune --bench=scalapack-pdqrdriver --method="max_evals" --nruns=50 --machine=cori --nodes=1 --cores=16
```


