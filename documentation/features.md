# History Database Features

Users can invoke the history database either by manual Python coding in the application-GPTune driver code or by using a command line interface provided by the workflow automation tool called CK-GPTune (for the sake of simplicity, the detailed user guide~\cite{CKGPTune} is not presented in this document).
If the history database is invoked, GPTune can store and load performance data to and from performance data files in the user's local storage; each application (code) will have a data file that contains all performance data (obtained by the user and/or downloaded from the shared public database) of the application.
The performance data is saved as dictionaries in JavaScript Object Notation ([JSON](https://www.json.org/json-en.html)) format.
JSON is becoming more popular and easy to add/remove data fields, so it is easy for us to organize data for database queries and gradually improve the data format.
In what follows, we present the features provided by the GPTune history database.

---
### Re-using Function Evaluation Data

Users can allow GPTune to store function evaluation data obtained from autotuning into data files.
Each data file contains the function evaluation results obtained from the GPTune's Bayesian optimization model.
The multitask learning autotuning (MLA) of GPTune relies on three information spaces: \textit{input space} (IS), \textit{parameter space} (PS), and \textit{output space} (OS)~\cite{Sid-Lakhdar:2019:arXiv}.
IS contains all the input problems (i.e.\ tasks) that the application may encounter (e.g. the sizes of matrices, pointers to input files) and PS contains all the tuning parameter configurations to be optimized (e.g. size of row/column blocks).
OS is the output space for each of the scalar objective functions (e.g. measured runtime).
GPTune saves the function evaluation result  for each parameter configuration.
The history database stores these performance data into the JSON file right after evaluating each parameter configuration.
This practice ensures that no data is lost, in the case where  a long run with many parameter configurations does not complete.
If GPTune is run in parallel and multiple processes need to update performance data simultaneously, to keep the consistency of the data, the history database allows one process to update the data file at a time based on simple file access control.
GPTune users can choose to load the previous function evaluation data when starting a new autotuning.
This feature will be useful whether or not a user wants to share data to or from other users.

### Re-using GP Surrogate Model

GPTune uses Bayesian optimization to iteratively build a Gaussian Process (GP) surrogate model~\cite{gramacy2020surrogates}~\footnote{Refer to Section 3 in the GPTune UserGuide~\cite{GPTuneUserGuide} for more details about how GPTune builds surrogate models.}, by running the application at carefully chosen tuning parameter values.
In addition to the ability to reuse previous function evaluation data, the history database also supports storing and loading trained GP surrogate models; users can use this feature to save the GP surrogate model after finishing some autotuning and load a trained model to continue autotuning afterward (with no additional model updates or fewer updates).
Again, this feature will be useful whether or not a user wants to share data to or from other users.
GPTune provides a Python interface to run MLA after loading a GP surrogate model from the database.
While it supports several model selection criterion to select the model such as MLE (Maximum Likelihood Estimation), AIC (Akaike Information Criterion), and BIC (Bayesian Information Criterion), users can also select a model based on their own method based on the provided statistics information; the history database provides some statistics (e.g. likelihood, gradients) of the model.

### Machine/Software Dependencies When Re-using Autotuning Data

In addition to performance data obtained from autotuning, the history database also records the machine configuration (e.g. the number of nodes/cores used) and software information (e.g. which software libraries are used for that application) into the JSON file.
Users can provide this information manually when calling GPTune, but they can also leverage a workflow automation tool called CK-GPTune~\cite{CKGPTune} to manage the information automatically.
With CK-GPTune, users need to define the application's software dependencies with a meta-description file, then CK-GPTune detects the software packages/libraries that have dependencies, based on the Collective Knowledge (CK) technology~\cite{Fursin:2020}.
Users can therefore determine which performance data are relevant for re-using (learning) from a possibly different machine or software versions or configurations.

### Workflow Automation for Reproducing Performance Data

CK-GPTune not only provides automatic software detection, but also allows you to define/run automated workflows (e.g. experiment, analysis) using a command line interface and meta description files.
In CK-GPTune, we currently provide workflow automation for four example codes (e.g. ScaLAPACK's PDGEQRF~\cite{Blackford:1997:Scalapack}) that users can install/run/autotune using simple commands, and plan to provide more examples.
Users can also automate their program workflows and share them with other users with the public database.
This will allow users to reproduce performance data from the same and different users.
For more information about CK-GPTune, please refer to our Github web pages~\cite{CKGPTune}.

### Using the Public Shared Database

The currently working version of the history database already supports the aforementioned features, however, it only supports storing/loading performance data of each user separately (on the local storage).
To harness the power of crowdtuning, we are now focusing on developing a public shared database to allow users to upload their performance data or download performance data provided by other users.

Here are the main design points for building our public database:

* Storage: To store all performance data from multiple sites, we plan to use Cori's storage system provided by NERSC.

* Web service: The public repository will use web resources provided by NERSC (also known as [Science Gateways](https://www.nersc.gov/assets/Uploads/19-Science-Gateways.pdf) for user-DB connection.
We will provide the web service at *https://portal.nersc.gov/...* to access the public database.

* DBMS: Since our performance data is managed as JSON files, we will use MongoDB~\cite{Chodorow:2013} internally to manage performance data.

* User interface: Users will be able to download/upload performance data from/to the public repository either using a command line interface or directly from a web browser.
For example, users may use a command like *$ historydb\_manager upload --user GPTune-Dev --application PDGEQRF* to submit a performance data file.

* User identification: The public database may require login credentials for users to submit their performance data.
%Users therefore need to provide the user login credentials (e.g. email) to upload data.
However, we could allow anyone to browse and download data without providing any user information.

* Visualization/statistics: We plan to provide some visualizations (e.g. plots/statistics of function evaluation data) of performance data on the web page.

Providing the shared public database is still work in progress.
If you have any requirements or comments, please tell us and we can consider them in the design.

