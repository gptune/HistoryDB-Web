import math
import warnings
from copy import deepcopy

import numpy as np
import scipy
from scipy import linalg
from scipy.stats import entropy
from sklearn import decomposition
from sklearn.preprocessing import StandardScaler
from sklearn.utils.extmath import svd_flip

from util.dKL import dKL
from util.pcaOrig import pcaOrig

from modules.resource_score import *
from sklearn.preprocessing import MinMaxScaler

#NOTES:
#Single features passed in to the program always return a value of 0.

def compare_kernels_ts(data_loaders, global_options):
    compat_pair_strings = global_options['compare_kernels_ts']
    compare_kernels(data_loaders, global_options, compat_pair_strings)
    if 'compare_kernels' not in global_options:
        global_options['compare_kernels'] = []
    global_options['compare_kernels'].append('compare_kernels_ts')

def compare_kernels_util(data_loaders, global_options):
    compat_pair_strings = global_options['compare_kernels_util']
    compare_kernels(data_loaders, global_options, compat_pair_strings)
    if 'compare_kernels' not in global_options:
        global_options['compare_kernels'] = []
    global_options['compare_kernels'].append('compare_kernels_util')

def compare_kernels_score(data_loaders, global_options):
    compat_pair_strings = global_options['compare_kernels_score']
    compare_kernels(data_loaders, global_options, compat_pair_strings)
    if 'compare_kernels' not in global_options:
        global_options['compare_kernels'] = []
    global_options['compare_kernels'].append('compare_kernels_score')

def compare_kernels_ts_max(data_loaders, global_options):
    compat_pair_strings = global_options['compare_kernels_ts_max']
    compare_kernels(data_loaders, global_options, compat_pair_strings)
    if 'compare_kernels' not in global_options:
        global_options['compare_kernels'] = []
    global_options['compare_kernels'].append('compare_kernels_ts_max')

def compare_kernels_util_max(data_loaders, global_options):
    compat_pair_strings = global_options['compare_kernels_util_max']
    compare_kernels(data_loaders, global_options, compat_pair_strings)
    if 'compare_kernels' not in global_options:
        global_options['compare_kernels'] = []
    global_options['compare_kernels'].append('compare_kernels_util_max')

def compare_kernels_score_max(data_loaders, global_options):
    compat_pair_strings = global_options['compare_kernels_score_max']
    compare_kernels(data_loaders, global_options, compat_pair_strings)
    if 'compare_kernels' not in global_options:
        global_options['compare_kernels'] = []
    global_options['compare_kernels'].append('compare_kernels_score_max')

def compare_kernels(data_loaders, global_options, compat_pair_strings):
    for compat_pair_str in compat_pair_strings:
        key_reg1, key_reg2 = compat_pair_str.split(',')
        dl1_name, reg1 = key_reg1.split(':', 1)
        dl2_name, reg2 = key_reg2.split(':', 1)

        dl1 = data_loaders[dl1_name]
        dl2 = data_loaders[dl2_name]

        print("%s regions: %s" % (dl1_name, dl1.get_regions()))
        print("%s regions: %s" % (dl2_name, dl2.get_regions()))

        print("Starting %s vs. %s\n---------------------------------"
            % (key_reg1, key_reg2))

        if set(dl1.proc_configs[reg1]) != set(dl2.proc_configs[reg2]):
            print("ERROR: proc configurations aren't the same")
            continue
        
        ev1 = set(dl1.get_events())
        ev2 = set(dl2.get_events())

        ev_diff = ev1.difference(ev2)
        events = ev1.intersection(ev2)
        
        if len(ev_diff) != 0:
            print("Removed %d events for not being present in both datasets" % len(ev_diff))
        data1 = dl1.get_app_data(reg1, keys=events, rescale=True)
        data2 = dl2.get_app_data(reg2, keys=events, rescale=True)

        target1 = dl1.get_app_target(reg1)
        target2 = dl2.get_app_target(reg2)
        results = {}
        errors = {}
        ev_errors = {}
        alphas = {}
        ### Both
        # Find out which resources are maximized. So correlate <app-base : base-app>, which ones were bigger in app. So, pass <target2, target1>. Here, target2 is the TS for optimal_Version, which is the first argument to: opt:base pair in max. Correlating things baseline did less of (optimization did more of) to its inflated time.
        ## data1 --> optimized version, data2 == baseline version
        rsm_score1, error1, ev_error1, alpha1 = compat_score2(dl1, data1, data2, target1, target2, reg1, reg2, events)
        #NOTE: +ve value between baseline(data2)-optimized(data1) means what has decreased. This should be represented in the barchart using -ve value. This is why rsm_score1 value is negated below.
        
        # Find out which resources are minimized. So correlate <base-app : base-app>, which ones were smaller in app. So, pass <target1, target2>. Correlating thigs that baseline did more of to its inflated execution time.
        rsm_score2, error2, ev_error2, alpha2 = compat_score2(dl1, data2, data1, target1, target2, reg1, reg2, events)
        ##NOTE: +ve value between optimized(data1)-baseline(data2) means things have increased after optimization. This value is shown as a +ve barchart in the barchart_both graph. This is why this value is NOT negated.

        print("<DEBUG> BEFORE: compare_kernels_both: ", rsm_score1, " AND ", rsm_score2, "\n")
        rsm_score = {}
        for k, v in rsm_score1.items():
            if math.isnan(rsm_score1[k]):
                rsm_score1[k] = 0
            if math.isnan(rsm_score2[k]):
                rsm_score2[k] = 0
                
        for k, v in rsm_score2.items():
        #computing the overall increase or decrease in RSM value.
            rsm_score1[k] = rsm_score2[k] - rsm_score1[k]
            
        print("<DEBUG> AFTER: compare_kernels_both: ", rsm_score1, "\n")
        results[reg1] = rsm_score1
        alphas[reg1] = alpha1
        errors[reg1] = error1
        ev_errors[reg1] = ev_error1

        
        results[reg2] = rsm_score1
        alphas[reg2] = alpha1
        errors[reg2] = error1
        ev_errors[reg2] = ev_error1

       
        dl1['rsm_results'][compat_pair_str] = deepcopy(results)
        dl1['rsm_res_errors'][compat_pair_str] = errors
        dl1['rsm_ev_errors'][compat_pair_str] = ev_errors
        dl1['rsm_alphas'][compat_pair_str] = alphas

        dl2['rsm_results'][compat_pair_str] = deepcopy(results)
        dl2['rsm_res_errors'][compat_pair_str] = errors
        dl2['rsm_ev_errors'][compat_pair_str] = ev_errors
        dl2['rsm_alphas'][compat_pair_str] = alphas
        
        data_loaders[dl1_name] = deepcopy(dl1)
        
        key_reg1, key_reg2 = compat_pair_str.split(',')
        dual = key_reg2+','+key_reg1
        print('<DEBUG> compare_kernels_both.py--> ', compat_pair_str, dual, reg1, reg2, rsm_score1, rsm_score2)

        dl1['rsm_results'][dual] = deepcopy(results)
        dl1['rsm_res_errors'][dual] = errors
        dl1['rsm_ev_errors'][dual] = ev_errors
        dl1['rsm_alphas'][dual] = alphas

        dl2['rsm_results'][dual] = deepcopy(results)
        dl2['rsm_res_errors'][dual] = errors
        dl2['rsm_ev_errors'][dual] = ev_errors
        dl2['rsm_alphas'][dual] = alphas

def compat_score2(data_loader, app_data, proxy_data, app_target, proxy_target, reg1, reg2, events):
    ''' compat_score2(data_loader, optimized_version, baseline_version, optimized_runtime, baseline_runtime, ....'''
    OPT_THRESHOLD = 0.4
    app_data = app_data.copy()

    proxy_data = proxy_data.copy() #The baseline
    diff_data1 = proxy_data - app_data #np.concatenate((app_data, proxy_data), axis=1)
#    diff_data1 = app_data - proxy_data #np.concatenate((app_data, proxy_data), axis=1)
    ###### TZI: Experimental: Only consider those events that were minimized. A negative value means, that event was NOT minimized.
    diff_data1[diff_data1<0] = 0.0
    diff_data = diff_data1
    #min_data = np.amin(diff_data)
    #diff_data += min_data
    # scaler = MinMaxScaler()
    # diff_data = scaler.fit_transform(diff_data)
    # print(diff_data.shape, diff_data)
    
    diff_target1 = proxy_target - app_target #signal is the same as target
    diff_target1[diff_target1<0] = 0.0
    diff_target = diff_target1
    # diff_target2 = scaler.fit_transform(diff_target.reshape(-1,1))
    # diff_target = diff_target2.reshape(app_target.shape)
    #min_target = np.amin(diff_target)
    #diff_target += min_target

    num_samples, num_features = app_data.shape

    app_data = diff_data.copy()
    eff_loss = diff_target.copy()
    results = {}
    errors = {}
    ev_errors = {}
    alphas = {}
    norm_data = {}

    rsm_score, error, ev_error, alpha, norm_d = compute_rsm_with_data(data_loader, app_data, eff_loss)
    rsm_dict = {}
    err_dict = {}
    for i in range(len(rsm_score)):
        rsm_dict[data_loader.resources[i]] = rsm_score[i]
        err_dict[data_loader.resources[i]] = error[i]

    alpha_dict = {}
    ev_err_dict = {}
    for i in range(len(data_loader.events)):
        alpha_dict[data_loader.events[i]] = alpha[i]
        ev_err_dict[data_loader.events[i]] = ev_error[i]

    return rsm_dict, err_dict, ev_err_dict, alpha_dict

def get_principal_angles(basis_1, basis_2):
    _, sig, _ = get_svd(np.dot(basis_1.T, basis_2))
    # Fix bad values
    sig[sig>1.0] = 1.0
    sig[sig<0.0] = 0.0
    theta = np.arccos(sig)
    
    return theta

def get_svd(X):
    U, S, V = np.linalg.svd(X, full_matrices=False)
    U, V = svd_flip(U, V)

    return U, S, V

def kl(mu0, mu1, sigma0, sigma1):
    # https://stats.stackexchange.com/questions/234757/how-to-use-kullback-leibler-divergence-if-mean-and-standard-deviation-of-of-two
    return abs(np.log(sigma1/sigma0) + (sigma0**2 + (mu0-mu1)**2)/(2*(sigma1**2)) - 0.5)
