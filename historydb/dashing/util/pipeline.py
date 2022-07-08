
import os
import numpy as np
import csv
from collections import defaultdict
from copy import deepcopy
from numpy import inf, nan
from dashing.util.os_utils import get_all_files
from dashing.util.h5_utils import multi_merge_h5_data, merge_h5_data, \
    validate_region_events, get_event_subset, clean_and_get_regions
from dashing.util.UtilityClass import Utility
import importlib
from sklearn.preprocessing import MinMaxScaler

class DataLoader(dict):

    def __init__(self):
        target=""
        pass
    
    @classmethod
    def init_from_h5(self, config_name, data_path, proc_configs, arch_file,
            event_file, exclude_file, counter_file, target="Runtime"):
        
        print("Initializing with h5")
        
        self = DataLoader()
        self.config_name = config_name
        #self.proc_configs = proc_configs
        self.target = target
        self.h5_map, self.raw_h5_map, self.events, self.regions \
            = self.parse_data(data_path, self.target)
        self._setup(arch_file, event_file, exclude_file, counter_file)
        
        return self
    

    @classmethod
    def init_from_csv(self, config_name, csv_path, proc_configs, arch_file,
            event_file, exclude_file, counter_file, target="Runtime", compute_target="None"):

        print("Initializing with csv")
        
        self = DataLoader()
        self.config_name = config_name
        self.proc_configs = proc_configs
        self.target = target
        self.compute_target = compute_target
        
        self.h5_map, self.raw_h5_map, self.events, self.regions \
            = self.parse_csv_data(csv_path, self.target)
        self._setup(arch_file, event_file, exclude_file, counter_file)

        return self

    @classmethod
    def init_from_dataframe(self, config_name, dataframe, proc_configs, arch_file,
            event_file, exclude_file, counter_file, target="Runtime", compute_target="None"):

        print("Initializing from dataframe")
        
        self = DataLoader()
        self.config_name = config_name
        self.proc_configs = proc_configs
        self.target = target
        self.compute_target = compute_target
        
        self.h5_map, self.raw_h5_map, self.events, self.regions \
            = self.parse_dataframe(dataframe, self.target)
        self._setup(arch_file, event_file, exclude_file, counter_file)

        return self

    
    def _setup(self, arch_file, event_file, exclude_file, counter_file):

        self.events = sorted(self.events, key=lambda x: x.lower())
        self.regions = sorted(self.regions, key=lambda x: x.lower())

        # Gets information on what events belong to which resources
        # As well as which resources are uncore
        self.res_to_ev_map, self.ev_to_res_map, self.uncore_flags = \
            self.parse_resources(arch_file, event_file, exclude_file, counter_file)

        self.resources = sorted(list(self.res_to_ev_map.keys()))
        self.assign_resource_colors()
        
        # Convert flags from ints to booleans
        for key in self.uncore_flags:
            self.uncore_flags[key] = (self.uncore_flags[key] == 1)

        # Internal dictionary used to have data flow through dataloader
        self.options = {}

    # Replace internal functions to access our backend dictionary
    ############################################################
    
    def __getitem__(self, x):
        return self.options[x]

    def __setitem__(self, k, v):
        self.options[k] = v

    def __contains__(self, x):
        return x in self.options
    
    def update_options(self, new_options):
        '''Simply copies a dictionary into ours
        '''
        for key in new_options:
            self.options[key] = new_options[key]
    
    def get_option(self, x, default=None):
        return self[x] if x in self else default

    def parse_data(self, data_path, target='Runtime'):
        '''Handles parsing all of an applications data given a path to its h5 files
        '''

        # Look for all h5 files associated with a job configuration
        # This will be a list of lists where each internal list has all the h5 file paths
        # for a specific configuration
        h5_file_path_tasks = []
        for proc_count in self.proc_configs: 
            contains_str = 'perf-dump.%d.h5' % proc_count
            h5_file_path_tasks.append(get_all_files(data_path, contains=contains_str))
        
        # We remove any proc configs where there was nothing found
        filtered_tasks = []
        for i, h5_task in enumerate(h5_file_path_tasks):
            if len(h5_task) == 0:
                print("WARNING: %d reported 0 files found." % self.proc_configs[i])
                print("This configuration will be removed and ignored.")
                del self.proc_configs[i]
            else:
                filtered_tasks.append(h5_task)

        # We request all paths to be loaded and parse
        # We then get our events and regions as well
        merged_h5_dicts, raw_h5_dicts = multi_merge_h5_data(filtered_tasks)
        event_set = get_event_subset(merged_h5_dicts, self.proc_configs)
        ## This is where self.proc_configs gets modified, where
        reg_set, self.proc_configs = clean_and_get_regions(merged_h5_dicts, self.proc_configs)

        event_set = list(event_set)
        reg_set = list(reg_set)

        # Final mapping is reg->event->data (mx1) where m is # of procs
        m = len(merged_h5_dicts)
        h5_map = {}
        raw_h5_map = {}
        for reg in reg_set:
            h5_map[reg] = {}
            raw_h5_map[reg] = {}
            for event in event_set:
                h5_map[reg][event] = np.zeros((m,1))
                raw_h5_map[reg][event] = [None] * m

                for i in range(m):
                    h5_map[reg][event][i] = merged_h5_dicts[i][reg][event]
                    raw_h5_map[reg][event][i] = raw_h5_dicts[i][reg][event]

        # Runtime should not be considered a "event" beyond pre-processing
        event_set.remove(target)
	
        return h5_map, raw_h5_map, event_set, reg_set
    
    def parse_csv_data(self, csv_path, target='Runtime'):
        event_set = set()
        reg_set = set()
        with open(csv_path, 'r') as csv_file:
            dict_reader = csv.DictReader(csv_file)
            h5_map = defaultdict(dict)
            
            for row in dict_reader:
                key_val_pairs = list(row.items())
                ev = key_val_pairs[0][1]
                event_set.add(ev)
                proc_configs = defaultdict()
                for reg,v in key_val_pairs[1:]:
                    reg_set.add(reg)
                    values = [float(val) for val in v.split(',')]
                    h5_map[reg][ev] = np.asarray(values).reshape((-1, 1))
                    if not self.proc_configs: #If proc configs is not defined
                        proc_configs[reg] = np.arange(len(h5_map[reg][ev]))
                    else: #If it is defined, just make sure to copy the defined proc_configs to all regions
                        proc_configs[reg] = self.proc_configs
                        
        event_set.remove(target)
        event_set = list(event_set)
        reg_set = list(reg_set)
        ## Make sure to rewrite the proc_configs so that each region gets a copy of the configurations
        self.proc_configs = proc_configs
        return h5_map, None, event_set, reg_set


    def parse_dataframe(self, dataframe, target='Runtime'):
        event_set = set()
        reg_set = set()
        h5_map = defaultdict(dict)
        
        for index, row in dataframe.iterrows():
            key_val_pairs = list(row.items())
            ev = key_val_pairs[0][1]
            event_set.add(ev)
            proc_configs = defaultdict()
            for reg,v in key_val_pairs[1:]:
                reg_set.add(reg)
                values = [float(val) for val in v.split(',')]
                h5_map[reg][ev] = np.asarray(values).reshape((-1, 1))
                if not self.proc_configs: #If proc configs is not defined
                    proc_configs[reg] = np.arange(len(h5_map[reg][ev]))
                else: #If it is defined, just make sure to copy the defined proc_configs to all regions
                    proc_configs[reg] = self.proc_configs

        event_set.remove(target)
        event_set = list(event_set)
        reg_set = list(reg_set)
        ## Make sure to rewrite the proc_configs so that each region gets a copy of the configurations
        self.proc_configs = proc_configs
        return h5_map, None, event_set, reg_set

    def parse_json_data(self, csv_path, target='Runtime'):
        event_set = set()
        reg_set = set()
        with open(csv_path, 'r') as csv_file:
            dict_reader = csv.DictReader(csv_file)
            h5_map = defaultdict(dict)
            
            for row in dict_reader:
                key_val_pairs = list(row.items())
                ev = key_val_pairs[0][1]
                event_set.add(ev)
                proc_configs = defaultdict()
                for reg,v in key_val_pairs[1:]:
                    reg_set.add(reg)
                    values = [float(val) for val in v.split(',')]
                    h5_map[reg][ev] = np.asarray(values).reshape((-1, 1))
                    if not self.proc_configs: #If proc configs is not defined
                        proc_configs[reg] = np.arange(len(h5_map[reg][ev]))
                    else: #If it is defined, just make sure to copy the defined proc_configs to all regions
                        proc_configs[reg] = self.proc_configs
                        
        event_set.remove(target)
        event_set = list(event_set)
        reg_set = list(reg_set)
        ## Make sure to rewrite the proc_configs so that each region gets a copy of the configurations
        self.proc_configs = proc_configs
        return h5_map, None, event_set, reg_set



    def parse_resources(self, arch_path, event_path, exclude_path, counter_path):
        '''Interacts with Utility class to generate a mapping between
        resources and events
        '''
        util = Utility(arch_path, event_path, exclude_path)
        a_groups, uncore_flags, arch_dict = util.set_arch_groups()
        event_list = util.get_event_list(counter_path)
        res_to_event_map = util.assign_event_list_to_eventGroups(event_list, a_groups)

        undefined_events = []
        if 'UNDEFINED' in res_to_event_map:
            undefined_events = res_to_event_map['UNDEFINED']
            del res_to_event_map['UNDEFINED']
            print("Removing undefined")
        
        # this provide a event->resource lookup
        event_to_res_map = {}
        for res_key in res_to_event_map:
            for ev_key in res_to_event_map[res_key]:
                if ev_key not in event_to_res_map:
                    event_to_res_map[ev_key] = []
                event_to_res_map[ev_key].append(res_key)
        
        for event in undefined_events:
            if event not in event_to_res_map and event in self.events:
                print("Removing %s for not having a valid resource" % event)
                del self.events[self.events.index(event)]
        
        return res_to_event_map, event_to_res_map, uncore_flags

    
    def dict_to_array(self, data_dict, reg):
        '''Parses a dictionary into a numpy array

        Inputs:
            data_dict: Dictionary in format of event_key->value
                where value is mx1 where m is the number of configurations
        
        Output:
            mxn array where n is the number of counters
        '''
        m = len(self.proc_configs[reg])
        n = len(data_dict)
               
        data = np.zeros((m,n))
#        for j, event_key in enumerate(data_dict):
#            data[:, j] = data_dict[event_key].reshape((m,))
        ##NOTE":TZI
        for j, event_key in enumerate(data_dict):
            ev_values = data_dict[event_key]
            data[:, j] = data_dict[event_key].reshape((m,))

        return data

    def rescale_dict(self, data_dict):
        '''Handles normalizing data between 0 and 1
        '''
        for key in data_dict:
            # Extract min, max, and rescale
            data_min = min(data_dict[key])
            data_max = max(data_dict[key])

            with np.errstate(divide='ignore', invalid='ignore'):
                new_data = (data_dict[key] - data_min) / (data_max - data_min)
            
            # Fix any damages
            new_data[new_data == inf] = 0
            new_data[new_data == -inf] = 0
            new_data = np.nan_to_num(new_data)

            data_dict[key] = new_data

        return data_dict
    
    ##This function is only called to get get_app_data, which in turn is called by linechart.py
    
    def copy_app_data(self, reg, keys):
        # Prepare to divide counter values by their processor count
        divide_vec = np.array(self.proc_configs[reg]).reshape((len(self.proc_configs[reg]),1))

        # Iterate over our keys and copies data
        data_dict = {}
        for key in keys:
            data_dict[key] = self.h5_map[reg][key].copy()
            print (reg, key)
            # If any resource associated with an event is uncore, we divide it by its
            # processor count
            is_uncore = list(map(lambda x : self.uncore_flags[x],
                self.ev_to_res_map[key]))
            #### TZI: Oct 2020: Commenting out the following to use the uncore flag to indicate good resource vs bad resource. TODO: we need to add a separate indicator for uncore or good/bad resources.
            # if any(is_uncore):
            #     data_dict[key] /= divide_vec

        return data_dict

    # Getters
    ## Only called from linechart.py.
    def get_app_data(self, reg, rescale=False, keys=None):
        # Copies a subset of the h5 data using a list of keys
        # We then parse this dictionary into a array and return it
        data_dict = self.get_app_dict(reg, rescale=rescale, keys=keys)
        #NOTE: Find the region ID:
        return self.dict_to_array(data_dict, reg)
    
    def get_app_dict(self, reg, rescale=False, keys=None):
        if keys is None:
            keys = self.events

        # Gets a copy with only the keys specified
        data_dict = self.copy_app_data(reg, keys)
        if rescale:
            data_dict = self.rescale_dict(data_dict)
        
        return data_dict

    def get_app_runtime(self, reg, rescale=False):
        runtime = self.h5_map[reg]['Runtime'].copy()
        runtime = runtime.reshape((len(runtime),))
        if rescale:
            runtime = (runtime - min(runtime)) / (max(runtime) - min(runtime))
        
        return runtime

    def get_app_target(self, reg):
        module_name, func_name = self.compute_target.rsplit('.', 1)
        module = importlib.import_module(module_name)
        func = getattr(module, func_name)
        # We provide all data loaders and the config for this global task
        computed_target = func(self, reg)

        return computed_target

    def get_app_target_standard_raw(self, reg):
        #max_runtime = max(self.h5_map, key= lambda x: self.h5_map[x][self.target])
        runtime = self.h5_map[reg][self.target].copy()
        runtime = runtime.reshape((len(runtime),))

        scaler = MinMaxScaler()
        norm_runtime = scaler.fit_transform(runtime.reshape(-1,1))
        return norm_runtime.reshape(runtime.shape)


    def get_app_target_normalized_raw2(self, reg):
        #max_runtime = max(self.h5_map, key= lambda x: self.h5_map[x][self.target])
        runtime = self.h5_map[reg][self.target].copy()
        runtime = runtime.reshape((len(runtime),))

        norm = np.linalg.norm(runtime)
        norm_runtime = runtime/norm
        return norm_runtime

    def get_app_target_normalized_raw(self, reg):
        runtime = self.h5_map[reg][self.target].copy()
        runtime = runtime.reshape((len(runtime),))

        for r_i, r in enumerate(self.regions):
            if r_i == 0:
                max_val = np.amax(self.h5_map[r][self.target])
                min_val = np.amin(self.h5_map[r][self.target])
            else:
                if (max_val < np.amax(self.h5_map[r][self.target])):
                    max_val = np.amax(self.h5_map[r][self.target])
                if (min_val < np.amin(self.h5_map[r][self.target])):
                    min_val = np.amin(self.h5_map[r][self.target])
        norm_runtime = (runtime - min_val) / (max_val - min_val)
        return norm_runtime

    def get_app_target_raw(self, reg):
        runtime = self.h5_map[reg][self.target].copy()
        runtime = runtime.reshape((len(runtime),))
        return (runtime)

    ##The following will be used by the sunburst visualization
    
    def get_sunburst_level1_target(self, reg):
#        module_name, func_name = self.compute_target.rsplit('.', 1)
#        module = importlib.import_module(module_name)
#        func = getattr(module, func_name)
#        # We provide all data loaders and the config for this global task
#        computed_target = func(self, reg)
        key = ''
        if 'Runtime' in self.events:
            key = 'Runtime'
        elif 'ts' in self.events:
            key = 'ts'
        runtime = self.h5_map[reg][key].copy()
        return runtime

    def get_app_eff_loss(self, reg):
        runtime = self.h5_map[reg]['Runtime'].copy()
        runtime = runtime.reshape((len(runtime),))
        base_case = runtime[0]

        eff_loss = np.zeros_like(runtime)
        for i in range(len(self.proc_configs[reg])):
            eff_loss[i] = 1 - (base_case / (self.proc_configs[reg][i] * runtime[i]))
        
        return eff_loss
    
    def assign_resource_colors(self):
        d20_pallet = ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c',
            '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#41159d',
            '#98df8a', '#ea1e1a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5',
            '#9583b9', '#bcbd22', '#dbdb8d', '#17becf', '#9edae5', '#06cbef']
        
        self.color_map = {}
        pallet_len = len(d20_pallet)

        for i, resource in enumerate(self.resources):
            self.color_map[resource] = d20_pallet[i % pallet_len]
    
    def get_resource_color(self, res):
        return self.color_map.get(res, None)


    def get_region_color(self, res):
        d20_pallet = ['#696969', '#d3d3d3', '#8b4513', '#006400', '#808000',
            '#483d8b', '#3cb371', '#008b8b', '#4682b4', '#000080',
            '#800080', '#b03060', '#ff0000', '#ff8c00', '#ffd700', '#40e0d0', '#8a2be4',
            '#00ff00', '#00fa9a', '#8a2be2', '#f4a460', '#f08080', '#1e90ff', '#f0e68c', '#1e90ff', '#dda0dd', '#ff00ff', '#7b68ee']
        
        self.color_map_reg = {}
        pallet_len = len(d20_pallet)
        for i, reg in enumerate(self.regions):
            self.color_map_reg[reg] = d20_pallet[i % pallet_len]
            
        return self.color_map_reg.get(res, None)

    
    def get_events_from_resource(self, res):
        return self.res_to_ev_map[res]

    def get_events(self):
        # Makes a copy
        return list(self.events)

    def get_regions(self):
        # Makes a copy
        return list(self.regions)
    
    def get_config_name(self):
        return self.config_name
