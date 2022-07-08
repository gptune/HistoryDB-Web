import sys
import numpy as np
import pandas
import plotly.graph_objects as go
import csv
from numpy import nan
import os
import plotly.tools as tls
import plotly.graph_objects as go

colors = ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c',
	'#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5',
	'#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f',
	'#c7c7c7', '#bcbd22', '#dbdb8d', '#17becf', '#9edae5']

def load_imbalance(data_loader):
	proc_configs = data_loader.proc_configs
	for reg in data_loader.regions:	
		for ev in data_loader.events:
			ev_importance = importance(data_loader['name'], reg, ev)
			if ev_importance <= 0.005:
				continue
			
			proc_vals_across_configs = find_proc_vals_across_configs(data_loader, proc_configs, reg, ev)

			fig = go.Figure()
			for proc_i, vals_per_proc in enumerate(proc_vals_across_configs):
				fig.add_trace(go.Bar(
					name = proc_i,
					x = proc_configs,
					y = vals_per_proc))

			fig.update_layout(autosize=True, title="%s, %s"%(reg,ev), barmode="stack")
			fig.layout.xaxis.title = "Number of Processes"
			fig.layout.xaxis.tickvals = proc_configs
			fig.layout.yaxis.title = "Raw values per process"
			data_loader['charts'].append(fig)
			break
		break



def normalize_to_sum_to_1(proc_vals):
	the_sum = sum(proc_vals)
	if the_sum == 0: return proc_vals
	return [d/the_sum for d in proc_vals]
		

#returns nxm matrix where n=largest process count(32 for haswell, 68 for knl), m = number of configs 
def find_proc_vals_across_configs(data_loader, proc_configs, reg, ev):
	proc_vals_across_configs = np.zeros((proc_configs[-1], len(proc_configs)))

	for config_i, config in enumerate(proc_configs):
		config_data = data_loader.raw_h5_map[reg][ev][config_i]
		config_data = normalize_to_sum_to_1(config_data)

		for dp_i, datapoint in enumerate(config_data):
			proc_vals_across_configs[dp_i][config_i] = datapoint
		

	return proc_vals_across_configs


#def standardize_length(config_data, length):
#	standardized_array = np.zeros(length)
#	for i in range(len(config_data)):
#		standardized_array[i] = config_data[i]
#	return standardized_array
		


def create_barchart(data_loader):
    
    name = data_loader.get_option('name', 'untitled barchart')
    rsm_results = data_loader['rsm_res_errors']
    regions = [key for key in rsm_results]
    resources = [resource for key in regions for resource in rsm_results[key]]
    resources = list(set(resources))

    resources = sorted(resources)
    data = np.zeros((len(regions), len(resources)))
    for i, region in enumerate(regions):
        for j, resource in enumerate(resources):
            data[i, j] = rsm_results[region][resource]
    
    for i in range(len(resources)):
        if resources[i] == 'UNDEFINED':
            resources[i] = 'UNDEF'
        if resources[i] == 'OFFCORE':
            resources[i] = 'OFF'

    x_font_dict = {
        'rotation': 90,
        'fontweight': 'semibold'
    }

    title_font_dict = {
        'fontweight': 'bold',
        'fontsize': 18
    }

    bar_graphs = []

    title_str = "%s | %s"
    raw_data = []
    for reg_i, region in enumerate(regions):
        #print(region)
        valid_indices = []
        reg_resources = []
        for i in range(len(resources)):
            if np.isnan(data[reg_i, i]):
                pass
                #print("Removing ", resources[i])
            else:
                valid_indices.append(i)
                reg_resources.append(resources[i])
        
        raw_data.append(data[reg_i, valid_indices])

    for i, norm_data in enumerate(normalize(raw_data)):
        bar_graphs.append(go.Bar(
            x=reg_resources,
            y=norm_data,
            name=regions[i]))
     

    fig = go.Figure(bar_graphs)
    fig.update_layout(title=name, autosize=True)
    fig.layout.xaxis.title="resource"
    fig.layout.yaxis.title="rsm score"

    data_loader['charts'].append(fig)


def create_rsm_percent_barchart(data_loader):
    rsm_results = data_loader['rsm_res_errors']
    regions = data_loader.get_regions()
    resources = [resource for key in regions for resource in rsm_results[key]]
    resources = sorted(list(set(resources)))

    percent_dict = {}
    for reg in regions:
        percent_dict[reg] = {}
#        eff_loss = data_loader.get_app_eff_loss(reg)
        ##NOTE: TZI 09/05/2020
        eff_loss = data_loader.get_app_target(reg)
        base_error = np.linalg.norm(eff_loss)
        for res in resources:
            if np.isnan(rsm_results[reg][res]):
                percent_dict[reg][res] = np.nan
            else:
                reduction = base_error - rsm_results[reg][res]
                percent_dict[reg][res] =  (reduction / base_error) * 100.0
    
    data = np.zeros((len(regions), len(resources)))
    for i, reg in enumerate(regions):
        for j, res in enumerate(resources):
            data[i, j] = percent_dict[reg][res]
    
    for i in range(len(resources)):
        if resources[i] == 'UNDEFINED':
            resources[i] = 'UNDEF'
        if resources[i] == 'OFFCORE':
            resources[i] = 'OFF'
    
    bar_graphs = []
    for res_i, resource in enumerate(resources):
        res_data = data[:, res_i]

        if np.all(np.isnan(res_data)):
            print("Skiping %s for having nan values..." % resource)
            continue
        
        hover_labels = []
        hover_text = 'Region: %s<br>Resource: %s<br>Percent Error Reduced: %0.2f%%<br>'
        for i in range(len(regions)):
            hover_labels.append(hover_text % (regions[i], resource, res_data[i]))
        
        bar_graphs.append(go.Bar(
            name=resource,
            x=regions,
            y=res_data,
            hovertext=hover_labels,
            hoverinfo="text",
            marker_color=data_loader.get_resource_color(resource)))
    
    fig = go.Figure(bar_graphs)
    fig.update_layout(autosize=True)
    fig.layout.xaxis.title = "Region"
    fig.layout.yaxis.title = "Percent Accuracy"
    fig.update_yaxes(range=[0.0, 100.0])
    data_loader['charts'].append(fig)

def create_rsm_error_barchart(data_loader):
    rsm_results = data_loader['rsm_results']
    regions = [key for key in rsm_results]
    resources = [resource for key in regions for resource in rsm_results[key]]
    resources = sorted(list(set(resources)))
    
    data = np.zeros((len(regions), len(resources)))
    for i, reg in enumerate(regions):
        for j, res in enumerate(resources):
            data[i, j] = rsm_results[reg][res]
    
    for i in range(len(resources)):
        if resources[i] == 'UNDEFINED':
            resources[i] = 'UNDEF'
        if resources[i] == 'OFFCORE':
            resources[i] = 'OFF'
    
    bar_graphs = []
    for res_i, resource in enumerate(resources):
        res_data = data[:, res_i]

        if np.all(np.isnan(res_data)):
            print("Skiping %s for having nan values..." % resource)
            continue
        
        bar_graphs.append(go.Bar(
            name=resource,
            x=regions,
            y=res_data))
    
    fig = go.Figure(bar_graphs)
    fig.update_layout(autosize=True)
    fig.layout.xaxis.title = "Region"
    fig.layout.yaxis.title = "RSM Score"
    fig.update_yaxes(range=[0.0, 1.0])
    data_loader['charts'].append(fig)
    




def create_barchart_2(data_loader):
    
    name = data_loader.get_option('name', 'untitled barchart')
    rsm_results = data_loader['rsm_res_errors']
    regions = [key for key in rsm_results]
    resources = [resource for key in regions for resource in rsm_results[key]]
    resources = list(set(resources))

    resources = sorted(resources)
    data = np.zeros((len(resources), len(regions)))
    for i, resource in enumerate(resources):
        for j, region in enumerate(regions):
            data[i, j] = rsm_results[region][resource]
    
    for i in range(len(resources)):
        if resources[i] == 'UNDEFINED':
            resources[i] = 'UNDEF'
        if resources[i] == 'OFFCORE':
            resources[i] = 'OFF'
    
    # Remove () and :: from names
    for i in range(len(regions)):
        if ':' in regions[i]:
            regions[i] = regions[i].split(':')[-1]
        
        if '()' in regions[i]:
            regions[i] = regions[i].split('()')[0]

    x_font_dict = {
        'rotation': 90,
        'fontweight': 'semibold'
    }

    title_font_dict = {
        'fontweight': 'bold',
        'fontsize': 18
    }

    bar_graphs = []

    title_str = "%s | %s"
    raw_data = []
    for res_i, resource in enumerate(resources):
        #print(region)
        valid_indices = []
        reg_resources = []
        for i in range(len(regions)):
            if np.isnan(data[res_i, i]):
                pass
                #print("Removing ", resources[i])
            else:
                valid_indices.append(i)
                reg_resources.append(regions[i])
        
        raw_data.append(data[res_i, valid_indices])

    for i, norm_data in enumerate(normalize(raw_data)):
        bar_graphs.append(go.Bar(
            x=reg_resources,
            y=norm_data,
            name=resources[i]))
     

    fig = go.Figure(bar_graphs)
    fig.update_layout(title=name, autosize=True)
    fig.layout.xaxis.title="Resource"
    fig.layout.yaxis.title="RSM"

    data_loader['charts'].append(fig)



def calc_color(data_loader, event):
	res = data_loader.ev_to_res_map[event][0]
	return colors[hash(res) % len(colors)]


def importance(name, region, event):
	with open('dashing/ev_belief_perc.csv', 'r') as csvfile:
		csv_reader = csv.reader(csvfile,delimiter=',')
		for row in csv_reader:
			if row[0].strip() == name.strip() and \
				row[1].strip() == region.strip() and \
				row[3].strip() == event.strip():
				return float(row[4])
		else:
			return 0.0
	

#source: https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

#assuming that scores are either all nan, or have no nan's in them
def remove_nan(df,resources):
	valid_data = []
	for resource in resources:
		if not np.isnan(df[resource][0]):
			valid_data.append(resource)
	return valid_data


def normalize_1d(data):
	min_val = min(data)
	max_val = max(data)
	return [ (d-min_val)/(max_val-min_val) for d in data ]



#bad implementation, fix later
def normalize(data):
	norm_bars = []
	min_val = find_min(data)
	max_val = find_max(data)
	for bargraph_data in data:
		norm_data = []
		for x in bargraph_data:
			norm_data.append( (x-min_val)/(max_val-min_val) )
		norm_bars.append(norm_data)

	return norm_bars

def find_min(data):
	min_val = 9999999.9
	for bargraph_data in data:
		for x in bargraph_data:
			if x < min_val:
				min_val = x
	
	return min_val

def find_max(data):
	max_val = 0.0
	for bargraph_data in data:
		for x in bargraph_data:
			if x > max_val:
				max_val = x

	return max_val
#####%%%%%%%%%%%%%%%%%%%%%%%%%%%% TZI: New addition
def compare_rsm_barcharts(data_loaders, global_options):
    for config in global_options['compare_kernels']:
        compare_rsm_barcharts_per_block(data_loaders, global_options, global_options[config])
        
def compare_rsm_barcharts_per_block(data_loaders, global_options, compat_pair_strings):
    bar_graphs = []
    hover_text = 'Region: %s<br>Resource: %s<br>Importance: %0.4f%%<br>'
    key_reg_list = []
    save_figure = True
    fig = go.Figure()
    for compat_pair_str in compat_pair_strings:
        key_reg1, key_reg2 = compat_pair_str.split(',')
        dl1_name, reg1 = key_reg1.split(':', 1)
        dl2_name, reg2 = key_reg2.split(':', 1)
        print ('---ddd----------o', compat_pair_str, 'o-----ddd-----------')

        dl1 = data_loaders[dl1_name]
        dl2 = data_loaders[dl2_name]
        save_figure = dl1.get_option('save_barchart', True)
        show_title = dl1.get_option('show_barchart', False)

        print("%s regions: %s" % (dl1_name, dl1.get_regions()))
        print("%s regions: %s" % (dl2_name, dl2.get_regions()))

        print("Starting %s vs. %s\n---------------------------------"
            % (key_reg1, key_reg2))
        key_reg_list.append(key_reg1)
        if set(dl1.proc_configs[reg1]) != set(dl2.proc_configs[reg2]):
            print("ERROR: proc configurations aren't the same")
            continue
        rsm_results = dl1['rsm_results'][compat_pair_str]
        regions = [reg1]
        resources = [resource for resource in rsm_results[reg1]]
        resources = sorted(list(set(resources)))

        percent_dict = {}
        for reg in regions:
            percent_dict[reg] = {}
            for res in resources:
                if np.isnan(rsm_results[reg][res]):
                    percent_dict[reg][res] = 0
                else:
                    percent_dict[reg][res] =  rsm_results[reg][res]
                    print('RSM:', reg, res, '-->', rsm_results[reg][res])
        data = np.zeros((len(regions), len(resources)))
        for i, reg in enumerate(regions):
            for j, res in enumerate(resources):
                data[i, j] = percent_dict[reg][res]
    
        for i in range(len(resources)):
            if resources[i] == 'UNDEFINED':
                resources[i] = 'UNDEF'
            if resources[i] == 'OFFCORE':
                resources[i] = 'OFF'
    
        clean_dl1_name = key_reg1
        clean_dl2_name = key_reg2
        title = '%s (%s) vs. %s (%s)' % (reg1, clean_dl1_name, reg2, clean_dl2_name)
        res_data = []
        hover_labels = []
        for res_i, resource in enumerate(resources):
            #res_data = data[:, res_i]
            print('DEBUG: ', resource, data[:, res_i])
            res_data.append(data[:, res_i][0])

            if np.all(np.isnan(res_data)):
                print("Skiping %s for having nan values..." % resource)
                continue
        
            #for i in range(len(regions)):
            hover_labels.append(hover_text % (reg1, resource, res_data[res_i]))
        # fig.add_trace(bar_graphs.append(go.Bar(
        #     name=key_reg1,
        #     x=resources,
        #     y=res_data,
        #     hovertext=hover_labels,
        #     hoverinfo="text",
        #     marker_color=dl1.get_region_color(reg1))))
        tmp_regname = key_reg1.split(':')[1] + ':' + key_reg2.split(':')[1]
        fig.add_trace(go.Bar(
            name=tmp_regname,#key_reg1,
            x=resources,
            y=res_data,
            hovertext=hover_labels,
            hoverinfo="text",
            marker_color=dl1.get_region_color(reg1)))

    #fig = go.Figure(bar_graphs)
    #fig.update_layout(autosize=True)
    fig.layout.xaxis.tickvals = resources
    fig.layout.xaxis.title = "Resources"
    fig.layout.yaxis.title = "Resource Importance"
    fig.update_yaxes(range=[0.0, 0.6])
    fig.update_layout(    font={'size': 28})
    dl1['charts'].append(fig)

    if save_figure:
        confname = ""
        for cs in compat_pair_strings:
            key_reg1, key_reg2 = cs.split(',')
            dl1_name, reg1 = key_reg1.split(':', 1)
            confname += reg1
        print('Barchart filename: ', confname)
        file_path = '%s_%s.pdf' % (dl1_name, confname)
        dir_path = os.path.join('viz_output', 'barchart')
        dir_path = os.path.join('viz_output', 'barchart')
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        file_path = os.path.join(dir_path, file_path)
        fig.write_image(file_path, width=1000, height=500)

#%%%%%%%%%%%%%%%%%%%%%%%%%%%% TZI: For showing both increase in resource usage and decrease in resource usage
def compare_rsm_barcharts_both(data_loaders, global_options):
#    for config in global_options['compare_kernels']:
#    compare_rsm_barcharts_per_block_both(data_loaders, global_options, global_options[config])      
    compare_rsm_barcharts_per_block_both(data_loaders, global_options)
    
def compare_rsm_barcharts_per_block_both(data_loaders, global_options):
    bar_graphs = []
    hover_text = 'Region: %s<br>Resource: %s<br>Importance: %0.4f%%<br>'
    key_reg_list = []
    save_figure = True
    fig = go.Figure()
    # resources = []
    from collections import defaultdict
    dict_data = defaultdict(defaultdict)
    # hover_labels = []
    for config in global_options['compare_kernels']:
        compat_pair_strings = global_options[config]
        print('---------xxxxx-------------o', compat_pair_strings, 'o------xxxx---------')
        tmp_compat_pair_strings = []
        ## Add duals
        for tmp in compat_pair_strings:
            tmp_compat_pair_strings.append(tmp)
            key_reg1, key_reg2 = tmp.split(',')
            dual = key_reg2+','+key_reg1
            tmp_compat_pair_strings.append(dual)
            
        for compat_pair_str in tmp_compat_pair_strings:
            key_reg1, key_reg2 = compat_pair_str.split(',')
            #print (compat_pair_str)
        
            if "max" in config:
                tmp = key_reg1
                key_reg1 = key_reg2
                key_reg2 = tmp
           
                dl2_name, reg2 = key_reg1.split(':', 1)
                dl1_name, reg1 = key_reg2.split(':', 1)
                #print(compat_pair_strings, " --> ", dl1_name, dl2_name)
            else:
                dl1_name, reg1 = key_reg1.split(':', 1)
                dl2_name, reg2 = key_reg2.split(':', 1)
            
            dl1 = data_loaders[dl1_name]
            dl2 = data_loaders[dl2_name]
            save_figure = dl1.get_option('save_barchart', True)
            show_title = dl1.get_option('show_barchart', False)
                
            #print("%s regions: %s" % (dl1_name, dl1.get_regions()))
            #print("%s regions: %s" % (dl2_name, dl2.get_regions()))

            print("Starting %s vs. %s\n---------------------------------"
                      % (key_reg1, key_reg2))
            key_reg_list.append(key_reg1)

            print('666666666 ', dl1.proc_configs[reg1], dl2.proc_configs[reg2],' 666666666')
            if set(dl1.proc_configs[reg1]) != set(dl2.proc_configs[reg2]):
                print("ERROR: proc configurations aren't the same")
                continue
            print(dl1['rsm_results'], compat_pair_str)
            rsm_results = dl1['rsm_results'][compat_pair_str]
            #print(rsm_results)
            regions = [reg1]
            resources = [resource for resource in rsm_results[reg1]]
            resources = sorted(list(set(resources)))

            percent_dict = {}
            for reg in regions:
                percent_dict[reg] = {}
                for res in resources:
                    if np.isnan(rsm_results[reg][res]):
                        percent_dict[reg][res] = 0
                    else:
                        if "max" in config:
                            percent_dict[reg][res] = rsm_results[reg][res]
                            #print(config, ' RSM:', reg, res, '-->', percent_dict[reg][res])
                        else:
                            percent_dict[reg][res] = -1.0 * rsm_results[reg][res]
                            #print(config, ' RSM:', reg, res, '-->', percent_dict[reg][res])
                        
            data = np.zeros((len(regions), len(resources)), dtype=float)
            for i, reg in enumerate(regions):
                for j, res in enumerate(resources):
                    data[i, j] = percent_dict[reg][res]
                    #print ('DATA-DEBUG: ', reg, res, percent_dict[reg][res], ' became ', data[i, j])
    
            for i in range(len(resources)):
                if resources[i] == 'UNDEFINED':
                    resources[i] = 'UNDEF'
                if resources[i] == 'OFFCORE':
                    resources[i] = 'OFF'
    
            clean_dl1_name = key_reg1
            clean_dl2_name = key_reg2
            title = '%s (%s) vs. %s (%s)' % (reg1, clean_dl1_name, reg2, clean_dl2_name)
            res_data = []
            hover_labels = []
            for res_i, resource in enumerate(resources):
                #res_data = data[:, res_i]
                #print(res_i, 'DEBUG: ', resource, data[:, res_i], data[:, res_i][0], data)
                res_data.append(data[:, res_i][0])

                if np.all(np.isnan(res_data)):
                    print("Skiping %s for having nan values..." % resource)
                    continue
        
                #for i in range(len(regions)):
                hover_labels.append(hover_text % (reg1, resource, res_data[res_i]))
                # fig.add_trace(bar_graphs.append(go.Bar(
                #     name=key_reg1,
                #     x=resources,
                #     y=res_data,
                #     hovertext=hover_labels,
                #     hoverinfo="text",
                #     marker_color=dl1.get_region_color(reg1))))
            dict_data[compat_pair_str] = res_data
            # tmp_regname = key_reg1.split(':')[1] + ':' + key_reg2.split(':')[1]
            # fig.add_trace(go.Bar(
            #         name=compat_pair_str,#key_reg1,
            #         x=resources,
            #         y=res_data,
            #         hovertext=hover_labels,
            #         hoverinfo="text",
            #         marker_color=dl1.get_region_color(reg1)))
        #print(resources, res_data)

    ################################33
    for config in global_options['compare_kernels']:
        if "max" in config:
            continue
        fig = go.Figure()

        compat_pair_strings = global_options[config]
        for compat_pair_str in compat_pair_strings:
            key_reg1, key_reg2 = compat_pair_str.split(',')
            dual = key_reg2+','+key_reg1
            res1 = dict_data[compat_pair_str]
            res2 = dict_data[dual]
            print("<DEBUG> ", compat_pair_str, dual, res1, res2)
            #val = [ res1[i] if abs(res1[i]) > abs(res2[i]) else res2[i] for i in range(0, len(res1)) ]
            val = [ (res1[i] + res2[i]) for i in range(0, len(res1)) ]
            tmp_regname = key_reg1.split(':')[1]# + ':' + key_reg2.split(':')[1]
            fig.add_trace(go.Bar(
                name=tmp_regname,#key_reg1,
                x=resources,
                y=val,
                hovertext=hover_labels,
                hoverinfo="text",
                marker_color=dl1.get_region_color(key_reg1)))

        #fig = go.Figure(bar_graphs)
        #fig.update_layout(autosize=True)
        fig.layout.xaxis.tickvals = resources
        fig.layout.xaxis.title = "Resources"
        fig.layout.yaxis.title = "Relative Change in Importance"
        fig.update_yaxes(range=[-0.5, 0.5])
        fig.update_xaxes(showline=True, linewidth=2, linecolor='black')
        fig.update_yaxes(showline=True, linewidth=2, linecolor='black')
        fig.update_layout(    font={'size': 18})
        #fig.update_layout(legend=dict(
        #orientation="h",
        #yanchor="bottom",
        #y=1,
        #xanchor="left",
        #x=1.02))
        dl1['charts'].append(fig)
            
        if save_figure:
            confname = "__"
            for cs in compat_pair_strings:
                key_reg1, key_reg2 = cs.split(',')
                dl1_name, reg1 = key_reg1.split(':', 1)
                confname += reg1
            file_path = '%s_%s.pdf' % (dl1_name, confname)
            dir_path = os.path.join('viz_output', 'barchart')
            dir_path = os.path.join('viz_output', 'barchart')
            print('Filename: ', file_path, confname)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            file_path = os.path.join(dir_path, file_path)
            #fig.write_image(file_path, width=100, height=50)
            fig.write_image(file_path)
