# Motivation and Goals

GPTune is an autotuner for high-performance computing codes, relying on multitask learning to help solve the underlying black-box optimization problem. GPTune is part of the xSDK4ECP project supported by the Exascale Computing Project (ECP).

GPTune is designed to tune high-performance application codes as "black-boxes", running them for carefully chosen tuning parameter values and building a performance model (i.e. surrogate model) based on the measured performance (i.e. function evaluation data) [1].
One of the main costs with this approach is the expensive black-box objective function (i.e. run and measure the application on a parallel machine).
To reduce this cost, the history database aims to provide the following features:

---

### Re-using autotuning data
    
The proposed history database can re-use performance data (e.g. function evaluation data and trained surrogate models) obtained from previous autotuning.
This allows the user to continue autotuning without recollecting data or rebuilding the surrogate model.

### Harnessing the power of crowdtuning

We provide a public shared database, where users can store their performance data or download the performance data provided by other users.
With the shared database, everyone can benefit from (expensive) runs of widely used high-performance computing codes.

### Reproducible autotuning

Users may want to reproduce performance data from the same or different users.
We aim to provide a portable workflow automation framework to help users reproduce performance data that exist in our shared database.

---

[1] W. M. Sid-Lakhdar,  J. W. Demmel,  X. S. Li,  Y. Liu,  and O. Marques.  Gptune user guide,2020.
