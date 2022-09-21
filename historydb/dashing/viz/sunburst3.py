from ast import Delete
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go
import plotly.io as pio
import plotly
import csv
import copy
import os

import pandas as pd
import numpy as np
from numpy import inf
from difflib import get_close_matches
import re
from collections import OrderedDict 

from sklearn.preprocessing import MinMaxScaler

from numpy import asarray

def conv_str(ev):
    shortened_event_name = ''
    if (ev == 'transactions'):
        shortened_event_name += ''
    elif (ev == 'misses'):
        shortened_event_name += 'miss'
    elif (ev == 'subp0'):
        shortened_event_name += 'p0'
    elif (ev == 'subp1'):
        shortened_event_name += 'p1'
    elif (ev == 'sysmem'):
        shortened_event_name += ''
    elif (ev == 'pipe'):
        shortened_event_name += ''
    elif (ev == 'fb'):
        shortened_event_name += ''
    elif (ev == 'sector'):
        shortened_event_name += ''
    elif (ev == 'tex'):
        shortened_event_name += ''
    elif (ev == 'queries'):
        shortened_event_name += 'q'
    elif (ev == 'ld'):
        shortened_event_name += 'ld'
    elif (ev == 'st'):
        shortened_event_name += 'st'
    elif (ev == 'store'):
        shortened_event_name += 'st'
    elif (ev == 'read'):
        shortened_event_name += 'r'
    elif (ev == 'write'):
        shortened_event_name += 'w'
    elif (ev == 'fma'):
        shortened_event_name += ''
    elif (ev == 'executed'):
        shortened_event_name += 'exec'
    elif (ev == 'l2'):
        shortened_event_name += ''
    elif (ev == 'shared'):
        shortened_event_name += ''
    else:
        shortened_event_name += ev[0]
    return shortened_event_name

def shorten_event_name(event_name):    
    shortened_event_name = ''
    print('shorten_event_name: ', event_name)
    if event_name == 'l2_subp0_write_sysmem_sector_queries':
        shortened_event_name = 'p0_w_q'
    elif event_name == 'l2_subp1_write_sysmem_sector_queries':
        shortened_event_name = 'p1_w_q'
    elif event_name == 'l2_subp1_read_sysmem_sector_queries':
        shortened_event_name = 'p1_r_q'
    elif event_name == 'l2_subp1_read_sysmem_sector_queries':
        shortened_event_name = 'p1_r_q'
    elif event_name == 'fb_subp0_read_sectors':
        shortened_event_name = 'p0_r_q'
    elif event_name == 'fb_subp1_read_sectors':
        shortened_event_name = 'p1_r_q'
    elif event_name == 'fb_subp0_write_sectors':
        shortened_event_name = 'p0_w_q'
    elif event_name == 'fb_subp1_write_sectors':
        shortened_event_name = 'p1_w_q'
    elif event_name == 'shared_ld_bank_conflict':
        shortened_event_name = 'ld_conflict'
    elif event_name == 'shared_st_bank_conflict':
        shortened_event_name = 'st_conflict'
    elif event_name == 'l2_subp0_read_tex_sector_queries':
        shortened_event_name = 'p0_r_queries'
    elif event_name == 'l2_subp0_write_tex_sector_queries':
        shortened_event_name = 'p0_w_queries'
    elif event_name == 'l2_subp1_read_tex_sector_queries':
        shortened_event_name = 'p1_r_queries'
    elif event_name == 'l2_subp1_write_tex_sector_queries':
        shortened_event_name = 'p1_w_queries'
    elif event_name == 'l2_subp0_read_tex_hit_sectors':
        shortened_event_name = 'p0_r_hit'
    elif event_name == 'l2_subp0_write_tex_hit_sectors':
        shortened_event_name = 'p0_w_hit'
    elif event_name == 'l2_subp1_read_tex_hit_sectors':
        shortened_event_name = 'p0_r_hit'
    elif event_name == 'l2_subp1_write_tex_hit_sectors':
        shortened_event_name = 'p1_w_hit'

    elif event_name == 'global_store':
        shortened_event_name = 'g_st'
    elif event_name == 'shared_ld_transactions':
        shortened_event_name = 'ld_trans'
    elif event_name == 'shared_st_transactions':
        shortened_event_name = 'st_trans'
    
    else:
        flag = 0
        event_str_list = event_name.split('_')
        for i, ev in enumerate(event_str_list):
            tmp = conv_str(ev)
            if (i > 0) and (tmp != '') and (flag > 0): 
                shortened_event_name += '_'
                flag+=1
            if (tmp != ''):
                flag+=1
            shortened_event_name += tmp 
        
    return shortened_event_name

def sunburst(data_loader):
    # print("Zayed Here but why")

    rsm_ev_errors = data_loader['rsm_ev_errors']
    rsm_alphas = data_loader['rsm_alphas']
    rsm_norm_data = data_loader['rsm_norm_data']
    rsm_results = data_loader['rsm_results']
    name = data_loader.get_option('name', 'untitled sunburst')
    save_sunburst = data_loader.get_option('save_sunburst', False)
    PERCENT_OFFSET = 1.00001
    BELIEF_THRESHOLD = 0.003

    clean_dict(rsm_ev_errors)
    clean_dict(rsm_alphas)
    clean_dict(rsm_results)

    # print("Zayed Checking: ", rsm_ev_errors)
    # rsm_results = copy.deepcopy(rsm_results)
    # resources = set()
    # for reg in rsm_results:
    #     for res in rsm_results[reg]:
    #         resources.add(res)
    #         if rsm_results[reg][res] < 0.0:
    #             rsm_results[reg][res] = 0.0

    rsm_results = copy.deepcopy(rsm_results)
    resources = set()
    for reg in rsm_results:
        base_error = np.linalg.norm(np.array(list(rsm_results[reg].values())))
        for res in rsm_results[reg]:
            resources.add(res)
            rsm_results[reg][res] = (base_error - rsm_results[reg][res]) / base_error
            if rsm_results[reg][res] < 0.0:
                rsm_results[reg][res] = 0.0

    regions = data_loader.get_regions()
    config_name = data_loader.get_config_name()
    regions.sort()
    # print(regions)
    resources = sorted(list(resources))
    app_name = name

    ids = []
    labels = []
    parents = []
    values = []
    hover_labels = []
    pairs = []

    descriptions = {}
    with open(data_loader['desc_path'], 'r') as f:
        reader = csv.reader(f)
        descriptions = {}
        for rows in reader:
            val = ""
            key = rows[0]
            for r in range(1, len(rows)):
                val += rows[r]
            descriptions[key] = val
                
    runtimes = OrderedDict() #{}
    for reg in regions:
        runtime = data_loader.get_app_target(reg)
        
        ## The following will only work if we have ts or Runtime in the dataset
        #runtime = data_loader.get_sunburst_level1_target(reg)
        runtime_sum = np.sum(runtime)
        runtimes[reg] = runtime_sum
    

    normed_runtime = OrderedDict() #{}
    # Assures the sum of normed_runtime is less than 1
    runtime_sum = sum(runtimes.values()) * PERCENT_OFFSET
    for reg in regions:
        normed_runtime[reg] = runtimes[reg] / runtime_sum

    # print("Zayed normed runtime")
    # print(runtimes)

    # First layer
    # Add the app name and its value is the sum of the normed runtime
    ids.append(app_name)
    pairs.append([app_name])
    labels.append(app_name)
    hover_labels.append(app_name)
    parents.append('')
    values.append(sum(normed_runtime.values()))

    #Fourth Layer Calculation
    #########################################################################
    ev_percent_error = {}
    for reg in regions:
        #base_error = np.linalg.norm(data_loader.get_app_eff_loss(reg))
        base_error = np.linalg.norm(data_loader.get_app_target(reg))
        ev_percent_error[reg] = {}
        for event, ev_err in rsm_ev_errors[reg].items():
            diff_error = base_error - ev_err
            ev_percent_error[reg][event] = diff_error / base_error
            if ev_percent_error[reg][event] < 0.0:
                ev_percent_error[reg][event] = 0.0

    # print("Zayed Checking2: ", ev_percent_error)

    # print("Zayed ev_to_gro")
    # print(data_loader.ev_to_res_map)
    # mapping = dict()
    # with open('counter_map.txt', 'a') as txtfile:
    #     for counter in data_loader.ev_to_res_map:
    #         for group in data_loader.ev_to_res_map[counter]:
    #             if group not in mapping:
    #                 mapping[group] = []
    #             mapping[group].append(counter)

    #     for group in mapping:
    #         for counter in mapping[group]:
    #             txtfile.write(counter + '=>' + group + '\n')

    # lam = 0.0005
    # lam = 1

    belief_ev_map = OrderedDict() #{}
    for reg in regions:
        belief_ev_map[reg] = OrderedDict() #{}
        for event, percent_error in ev_percent_error[reg].items():
            belief_ev_map[reg][event] = percent_error
            # belief_ev_map[reg][event] = np.exp(-lam * percent_error)
    # Parse the map into a region->res->event->belief layout
    belief_res_ev_map = OrderedDict() #i{}
    for reg in regions:
        belief_res_ev_map[reg] = OrderedDict()
        for event, event_belief in belief_ev_map[reg].items():
            event_resource = data_loader.ev_to_res_map[event][0]
            
            if event_resource not in belief_res_ev_map[reg]:
                belief_res_ev_map[reg][event_resource] = OrderedDict()
            belief_res_ev_map[reg][event_resource][event] = event_belief

    original_belief_res_ev_map = copy.deepcopy(belief_res_ev_map)
    # print("Zayed here", belief_res_ev_map)

    #TZI: Debug: Output the event percentages in a csv file for ease of use.
    # csv_file = open('dashing/ev_belief_perc.csv', 'a')
    # csv_writer = csv.writer(csv_file,delimiter=',')
    # for reg in belief_res_ev_map:
    #     resources_to_remove = []
    #     for resource in belief_res_ev_map[reg]:
    #         belief_min = min(belief_res_ev_map[reg][resource].values())
    #         belief_max = max(belief_res_ev_map[reg][resource].values())
    #         keys_to_remove = []

    #         if belief_min == belief_max:
    #             resources_to_remove.append(resource)
    #             continue

    #         for event, event_belief in belief_res_ev_map[reg][resource].items():

    #             belief_res_ev_map[reg][resource][event] = (event_belief - belief_min) / (belief_max - belief_min)

    #             if belief_res_ev_map[reg][resource][event] < BELIEF_THRESHOLD:
    #                 keys_to_remove.append(event)
    #             # if belief_res_ev_map[reg][resource][event] > BELIEF_THRESHOLD:
    #             #     # csv_writer.writerow([app_name, reg, resource, event, belief_res_ev_map[reg][resource][event]])
            
    #         for key in keys_to_remove:
    #             del belief_res_ev_map[reg][resource][key]
        
    #     for resource in resources_to_remove:
    #         # print("Deleting %s from %s" % (resource, reg))
    #         del belief_res_ev_map[reg][resource]
    
    for reg in belief_res_ev_map:
        resources_to_remove = []
        for resource in belief_res_ev_map[reg]:
            belief_min = min(belief_res_ev_map[reg][resource].values())
            belief_max = max(belief_res_ev_map[reg][resource].values())
            keys_to_remove = []

            bels = list(belief_res_ev_map[reg][resource].values())
            mean = sum(bels) / len(bels)
            variance = sum([((x - mean) ** 2) for x in bels]) / len(bels)
            res = variance ** 0.5

            if belief_min == belief_max:
                resources_to_remove.append(resource)
                continue

            for event, event_belief in belief_res_ev_map[reg][resource].items():

                # belief_res_ev_map[reg][resource][event] = abs((event_belief - mean) / res)
                # print("Zayed ", reg, resource, event, belief_res_ev_map[reg][resource][event])

                if belief_res_ev_map[reg][resource][event] < BELIEF_THRESHOLD:
                    keys_to_remove.append(event)
                # if belief_res_ev_map[reg][resource][event] > BELIEF_THRESHOLD:
                #     # csv_writer.writerow([app_name, reg, resource, event, belief_res_ev_map[reg][resource][event]])
            
            for key in keys_to_remove:
                del belief_res_ev_map[reg][resource][key]
        
        for resource in resources_to_remove:
            # print("Deleting %s from %s" % (resource, reg))
            del belief_res_ev_map[reg][resource]
    

    # csv_file.close()
    normed_belief_res_ev_map = {}
    for reg in belief_res_ev_map:
        normed_belief_res_ev_map[reg] = {}
        for resource in belief_res_ev_map[reg]:
            normed_belief_res_ev_map[reg][resource] = {}
            belief_sum = sum(belief_res_ev_map[reg][resource].values()) * PERCENT_OFFSET
            for event, belief in belief_res_ev_map[reg][resource].items():
                normed_belief_res_ev_map[reg][resource][event] = belief / belief_sum

    ##############################################################################################


    #############################################################################################
    # Third Layer Calculations

    # print("Zayed belief_map_before ", rsm_results)

    # lam = 0.005
    lam = 1
    belief_map = OrderedDict() #{}
    for reg in regions:
        belief_map[reg] = {}
        for resource, res_percent_err in rsm_results[reg].items():
            # print ("Not is: ", reg, resource, res_percent_err)
            if resource in normed_belief_res_ev_map[reg]:
                # print ("Is: ", reg, resource, res_percent_err)
                belief_map[reg][resource] = res_percent_err
                belief_map[reg][resource] = np.exp(-lam * res_percent_err)
            # print("%s : %s : %s" % (resource, res_percent_err, belief_map[reg][resource]))
    
    # print("Zayed belief_map ", belief_map)
    original_normed_belief_map = copy.deepcopy(belief_map)
    # Normalize between 0 and 1 removing any small values
    for reg in regions:
        if(not belief_map[reg]):
            continue
        # print ('...........', reg, belief_map[reg])
        belief_min = min(belief_map[reg].values())
        belief_max = max(belief_map[reg].values())
        belief_sum = sum(belief_map[reg].values())


        keys_to_remove = []
        for resource in belief_map[reg]:
            # if (belief_max - belief_min) != 0:
            #     # belief_map[reg][resource] = (belief_map[reg][resource] - belief_min) / (belief_max - belief_min)
                # belief_map[reg][resource] = belief_map[reg][resource] / belief_sum

            if belief_map[reg][resource] < BELIEF_THRESHOLD or len(list(belief_res_ev_map[reg][resource].keys())) == 0:
            # if belief_map[reg][resource] < BELIEF_THRESHOLD:

                #print("Removing %s from %s" % (resource, reg))
                keys_to_remove.append(resource)
        
        for key in keys_to_remove:
            del belief_map[reg][key]

    # for reg in regions:
    #     if(not belief_map[reg]):
    #         continue
    #     # print ('...........', reg, belief_map[reg])
    #     belief_min = min(belief_map[reg].values())
    #     belief_max = max(belief_map[reg].values())
    #     belief_sum = sum(belief_map[reg].values())

    #     bels = list(belief_res_ev_map[reg][resource].values())
    #     mean = sum(bels) / len(bels)
    #     variance = sum([((x - mean) ** 2) for x in bels]) / len(bels)
    #     res = variance ** 0.5
    #     keys_to_remove = []
    #     for resource in belief_map[reg]:
    #         # if (belief_max - belief_min) != 0:
    #             # belief_map[reg][resource] = (belief_map[reg][resource] - belief_min) / (belief_max - belief_min)
    #         belief_map[reg][resource] = ((belief_map[reg][resource] - mean) / res)

    #         if belief_map[reg][resource] < BELIEF_THRESHOLD:
    #             #print("Removing %s from %s" % (resource, reg))
    #             keys_to_remove.append(resource)
        
    #     for key in keys_to_remove:
    #         del belief_map[reg][key]

    # Next step is with these belief values, normalized them such that
    # the sum of all beliefs is equal to the regions normalized value
    # We do this by first dividing all values by the sum
    # This assures that the sum of these values equals 1
    normed_belief_map = {}
    for reg in regions:
        normed_belief_map[reg] = {}
        belief_sum = sum(belief_map[reg].values()) * PERCENT_OFFSET
        for resource, belief in belief_map[reg].items():
            normed_belief_map[reg][resource] = belief / belief_sum

    #######################################################################################################

    # Second layer calculation and appending to sunburst
    # Consists of each region whose value is their runtime percentage
    hover_label = '%s<br>Runtime: %0.2f%%'
    is_empty = True
    for reg in regions:
        #data_loader.set_region(reg)
        if normed_belief_map[reg]:
            is_empty = False
            ids.append(reg)
            pairs.append([reg])
            labels.append(reg)
            hover_labels.append(hover_label % (reg, normed_runtime[reg] * 100.0))
            parents.append(app_name)
            values.append(normed_runtime[reg])


    # Third Layer appending to the sunburst
    hover_label = '%s<br>Percent Error Reduced: %0.2f%%'
    # csv_file = open('dashing/res_imp.csv', 'a')
    # csv_writer = csv.writer(csv_file,delimiter=',')
    for reg in regions:
        for resource, belief in belief_map[reg].items():
            ids.append(reg+resource)
            pairs.append([reg, resource])
            labels.append(resource)
            # hover_labels.append(hover_label % (resource, rsm_results[reg][resource]*100.0))
            hover_labels.append(hover_label % (resource, normed_belief_map[reg][resource]*100.0))
            # csv_writer.writerow([config_name, reg, resource, "#", rsm_results[reg][resource]*100.0])
            parents.append(reg)
            values.append(normed_belief_map[reg][resource] * normed_runtime[reg])
    # csv_file.close()

    # Fourth layer appending to the sunburst
    hover_label = '%s<br>Percent Error Reduced: %0.2f%%<br>%s'
    for reg in normed_belief_res_ev_map:
        for resource in normed_belief_res_ev_map[reg]:
            for event, belief in normed_belief_res_ev_map[reg][resource].items():
                if resource in normed_belief_map[reg]:
                    ids.append(reg+resource+event)
                    pairs.append([reg, resource, event])
                    #labels.append(event) --> TZI: modify
                    #labels.append(shorten_event_name(event))
                    labels.append(event)
                    # value = ev_percent_error[reg][event]*100.0
                    value = normed_belief_res_ev_map[reg][resource][event] * 100

                    closest_event_names = get_close_matches(event, descriptions.keys(), cutoff=.8)
                    if closest_event_names: # if there was a match at all
                        this_description = '<br>'.join(line.strip() for line in re.findall(r'.{1,40}(?:\s+|$)', descriptions[closest_event_names[0]] ))
                        hover_labels.append(hover_label % (event, value, this_description))
                    else:
                        hover_labels.append(hover_label % (event, value, ""))

                    parents.append(reg+resource)
                    
                    values.append(normed_belief_res_ev_map[reg][resource][event] * normed_belief_map[reg][resource] * normed_runtime[reg])

    sunburst_colors = ['#FFFFFF']
    default_color = '#babbca' #'#636efa'
    pairs.pop(0)
    for pair in pairs:
        if len(pair) == 1:
            sunburst_colors.append(default_color)
        else:
            res = pair[1]
            sunburst_colors.append(data_loader.get_resource_color(res))

    new_orig = copy.deepcopy(original_belief_res_ev_map)
    data_loader['raw_importance'] = new_orig
    # Recreating the toatal data
    for reg in original_belief_res_ev_map:
        for resource in original_belief_res_ev_map[reg]:
            for event, value in original_belief_res_ev_map[reg][resource].items():
                try:
                    original_belief_res_ev_map[reg][resource][event] = normed_belief_res_ev_map[reg][resource][event]
                except:
                    original_belief_res_ev_map[reg][resource][event] = 0.0

    for region in regions:
        for resource in original_normed_belief_map[region]:
            try:
                original_normed_belief_map[region][resource] = normed_belief_map[region][resource]
            except:
                original_normed_belief_map[region][resource] = 0.0


    # data_loader['group_reg_pair'] = normed_belief_map
    # data_loader['group_reg_pair_vlaues'] = normed_belief_res_ev_map
    # print("Zayed Here but why " , original_normed_belief_map)
    data_loader['group_reg_pair'] = original_normed_belief_map
    data_loader['group_reg_pair_vlaues'] = original_belief_res_ev_map

    if is_empty:
        data_loader.options['charts'].append(None)
        return


    # template = "minty"
    # load_figure_template(template)
    trace = go.Sunburst(
        ids=ids,
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        hovertext=hover_labels,
        hoverinfo="text",
	    insidetextfont = {"size": 20, "color": "#000000"},
        outsidetextfont = {"size": 30, "color": "#377eb8"},
#        outsidetextfont = {"size": 20, "color": "#377eb8"},
        marker = {"line": {"width": 2}},
        marker_colors=sunburst_colors
    )

    layout = go.Layout(
        margin = go.layout.Margin(t=0, l=0, r=0, b=0),
    )
    
    fig = go.Figure([trace], layout)
    # fig.update_layout(width = 700, height = 700, template=template)
    fig.update_layout(width = 700, height = 700)

    data_loader.options['charts'].append(fig)
    if save_sunburst:
        file_path = '%s.pdf' % data_loader.get_config_name()
        dir_path = os.path.join('viz_output', 'sunburst')

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        
        file_path = os.path.join(dir_path, file_path)
        fig.write_image(file_path)

def clean_dict(rsm_dict):
    for key1 in rsm_dict:
        remove_keys = []

        for key2 in rsm_dict[key1]:
            if np.isnan(rsm_dict[key1][key2]):
                remove_keys.append(key2)

        for key2 in remove_keys:
            del rsm_dict[key1][key2]
