
import csv
import multiprocessing
import os

import numpy as np
from scipy.optimize import nnls
from scipy.linalg import lstsq
from numpy import NaN, inf
import psutil
from sklearn.preprocessing import MinMaxScaler


def get_app_eff_loss(data_loader, reg):
    runtime = data_loader.h5_map[reg][data_loader.target].copy()
    runtime = runtime.reshape((len(runtime),))
    base_case = runtime[0]

    eff_loss = np.zeros_like(runtime)
    proc_configs = [1, 2, 4, 8]
    for i in range(len(data_loader.proc_configs[reg])):
        eff_loss[i] = 1 - (base_case / (proc_configs[i] * runtime[i]))
    
    return eff_loss
    
def compute_target(data_loader, reg):
    runtime = data_loader.h5_map[reg][data_loader.target].copy()
    runtime = runtime.reshape((len(runtime),))
    #base_case = runtime[0]
    base_case = 0

    eff_loss = np.zeros_like(runtime)
    for i in data_loader.proc_configs[reg]:
        eff_loss[i] = (runtime[i] - base_case)
    norm = np.linalg.norm(eff_loss)
    eff_loss = (eff_loss / norm)
    ## Set 0 to the nan values
    where_nans = np.isnan(eff_loss)
    eff_loss[where_nans] = 0
    return eff_loss

def compute_inverse_target(data_loader, reg):
    runtime = data_loader.h5_map[reg][data_loader.target].copy()
    runtime = runtime.reshape((len(runtime),))
    #base_case = runtime[0]
    base_case = 0
    eff_loss = np.zeros_like(runtime)
    for i in data_loader.proc_configs[reg]:
        eff_loss[i] = (runtime[i] - base_case)
    norm = np.linalg.norm(eff_loss)
    eff_loss = eff_loss / norm
    for i in data_loader.proc_configs[reg]:
        if eff_loss[i] != 0:
            eff_loss[i] = 1.0 / eff_loss[i]
    ## Set 0 to the nan values
    where_nans = np.isnan(eff_loss)
    eff_loss[where_nans] = 0
    return eff_loss

def compute_one_minus_target(data_loader, reg):
    runtime = data_loader.h5_map[reg][data_loader.target].copy()
    runtime = runtime.reshape((len(runtime),))
    #base_case = runtime[0]
    base_case = 0
    eff_loss = np.zeros_like(runtime)
    for i in data_loader.proc_configs[reg]:
        eff_loss[i] = (runtime[i] - base_case)
    norm = np.linalg.norm(eff_loss)
    eff_loss = 1.0 - (eff_loss / norm)
    ## Set 0 to the nan values
    where_nans = np.isnan(eff_loss)
    eff_loss[where_nans] = 0
    return eff_loss


def compute_standard_target(data_loader, reg):
    runtime = data_loader.h5_map[reg][data_loader.target].copy()
    runtime = runtime.reshape((len(runtime),))
    #base_case = runtime[0]
    base_case = 0
    scaler = MinMaxScaler()
    norm_runtime = scaler.fit_transform(runtime.reshape(-1,1))
    return norm_runtime.reshape(runtime.shape)


def compute_standard_one_minus_target(data_loader, reg):
    runtime = data_loader.h5_map[reg][data_loader.target].copy()
    runtime = runtime.reshape((len(runtime),))
    #base_case = runtime[0]
    scaler = MinMaxScaler()
    norm_runtime = scaler.fit_transform(runtime.reshape(-1,1))
    return (1.0-norm_runtime.reshape(runtime.shape))

def compute_one_minus_runtime(data_loader, reg):
    runtime = data_loader.h5_map[reg][data_loader.target].copy()
    runtime = runtime.reshape((len(runtime),))
    #base_case = runtime[0]
    base_case = 0

    eff_loss = np.zeros_like(runtime)
    for i in data_loader.proc_configs[reg]:
        eff_loss[i] = (1.0 / (runtime[i] - base_case))
    norm = np.linalg.norm(eff_loss)
    eff_loss = 1.0 - (eff_loss / norm)
    ## Set 0 to the nan values
    where_nans = np.isnan(eff_loss)
    eff_loss[where_nans] = 0

    return eff_loss

def compute_one_minus_standard_runtime(data_loader, reg):
    runtime = data_loader.h5_map[reg][data_loader.target].copy()
    runtime = runtime.reshape((len(runtime),))
    #base_case = runtime[0]
    base_case = 0

    scaler = MinMaxScaler()
    norm_runtime = scaler.fit_transform(runtime.reshape(-1,1))
    return (1.0-norm_runtime.reshape(runtime.shape))

def compute_runtime(data_loader, reg):
    runtime = data_loader.h5_map[reg][data_loader.target].copy()
    runtime = runtime.reshape((len(runtime),))
    #base_case = runtime[0]
    base_case = 0

    eff_loss = np.zeros_like(runtime)
    for i in data_loader.proc_configs[reg]:
        eff_loss[i] = (runtime[i] - base_case)
    norm = np.linalg.norm(eff_loss)
    eff_loss = (eff_loss / norm)
    ## Set 0 to the nan values
    where_nans = np.isnan(eff_loss)
    eff_loss[where_nans] = 0

    return eff_loss

def compute_standard_runtime(data_loader, reg):
    runtime = data_loader.h5_map[reg][data_loader.target].copy()
    runtime = runtime.reshape((len(runtime),))
    #base_case = runtime[0]
    base_case = 0

    base_case = 0
    scaler = MinMaxScaler()
    norm_runtime = scaler.fit_transform(runtime.reshape(-1,1))
    return norm_runtime.reshape(runtime.shape)

