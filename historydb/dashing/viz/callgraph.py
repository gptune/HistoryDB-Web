import os
import glob
import numpy as np
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler


##For reading json
import json
import plotly.graph_objects as go
from collections import OrderedDict
from dash_bootstrap_templates import load_figure_template
# from util.utility_functions import *
from datetime import datetime as dt
# import networkx as nx
# from viz.addEdge import addEdge

import hashlib
from collections import Counter
def chimbuko_callgraph3D(data_loader):
    ids = []
    labels = []
    parents = []
    values = []
    hover_labels = []
    pairs = []
    dataframe = data_loader.dict_entries
    obj = data_loader.dataFrameObj
    PERCENT_OFFSET = 1.00001
    name = data_loader.get_option('name', 'untitled sunburst')
    save_sunburst = data_loader.get_option('save_sunburst', False)
    
    ############################################################################
    dimension = 3
    func_name =     name = data_loader.get_option('callgraph_root', '')
    G = nx.DiGraph()
    ###
    callgraph_edgelist = obj.get_callgraph_edgelist_for_function(func_name)
    if callgraph_edgelist == None:
        print('No function with that name')
        return
    G.add_weighted_edges_from(callgraph_edgelist)
    Num_nodes = len(G.nodes)
    colors = nx.get_edge_attributes(G,'color').values()
    weights = nx.get_edge_attributes(G,'weight').values()
    nodeColor = 'Blue'
    nodeSize = 20
    lineWidth = 2
    lineColor = '#000000'
    node_labels = list(G.nodes)
    root = node_labels.index(func_name)
    ###
    #spring_3D = nx.spring_layout(G, dim=dimension, seed=218)#nx.spring_layout(G, seed=8)
    #spring_3D = nx.fruchterman_reingold_layout(G, dim=dimension, k=5, seed=517)
    #spring_3D = nx.bipartite_layout(G, pos.keys())
    #spring_3D = nx.circular_layout(G)
    #spring_3D = nx.kamada_kawai_layout(G, dim=dimension, scale=1)
    #spring_3D = nx.planar_layout(G)
    #spring_3D = nx.random_layout(G, dim=dimension)
    #spring_3D = nx.rescale_layout_dict(spring_3D)
    #spring_3D = nx.shell_layout(G)
    spring_3D = nx.spectral_layout(G, dim=dimension, scale=3) #Good one
    #spring_3D = nx.spiral_layout(G, resolution=0.5, equidistant=True)

    #we need to seperate the X,Y,Z coordinates for Plotly
    x_nodes = [spring_3D[func][0] for func in G.nodes]# x-coordinates of nodes
    y_nodes = [spring_3D[func][1] for func in G.nodes]# y-coordinates
    z_nodes = [spring_3D[func][2] for func in G.nodes]# z-coordinates

    #we  need to create lists that contain the starting and ending coordinates of each edge.
    # x_edges=[]
    # y_edges=[]
    # z_edges=[]      
    community_label = []
    node_size = []
    trace_edges=[]

    ### Min-max scaling of the edge weights
    edge_weights = []
    for edge in G.edges():
        edge_weights.append(round(G.get_edge_data(*edge)['weight'], 2))

    edge_data=np.array(edge_weights).reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    data=list(scaler.fit_transform(edge_data))

    
    edge_idx = 0
    for edge in G.edges():
        x_edges=[]
        y_edges=[]
        z_edges=[]      
        x_coords = [spring_3D[edge[0]][0],spring_3D[edge[1]][0],None]
        x_edges += x_coords

        y_coords = [spring_3D[edge[0]][1],spring_3D[edge[1]][1],None]
        y_edges += y_coords

        z_coords = [spring_3D[edge[0]][2],spring_3D[edge[1]][2],None]
        z_edges += z_coords

        edge_weight = edge_data[edge_idx][0]
        size_factor = 1000
        small_size_factor = 700
        width_factor = 550
        community_label.append(edge_weight*size_factor)

        edge_style = 'solid'
        if edge_weight < 0.7:
            edge_style = 'solid'#'dash'
            node_size.append(edge_weight*small_size_factor)
        else:
            node_size.append(edge_weight*size_factor)
            
        trace_edges.append(go.Scatter3d(name=func_name, x=x_edges,
                            y=y_edges,
                            z=z_edges,
                            mode='lines',
                            text=str(edge_weight),
                            line=dict(
                                color=community_label[edge_idx],
                                width=edge_weight * width_factor,
                                #dash='solid',
                                dash=edge_style,
                                showscale=True),
                            hoverinfo='text'))
    #create a trace for the edges
    
    # trace_edges = go.Scatter3d(name=func_name, x=x_edges,
    #                         y=y_edges,
    #                         z=z_edges,
    #                         mode='lines',
    #                         text=edge_width,
    #                         line=dict(color=community_label, width=1, dash='longdash', showscale=True),
    #                         hoverinfo='text')
    #create a trace for the nodes
    trace_nodes = go.Scatter3d(name=func_name, x=x_nodes,
                             y=y_nodes,
                            z=z_nodes,
                            mode='markers+text',
                            marker=dict(symbol='circle',
                                        size=node_size,
                                        color=community_label, #color the nodes according to their community
                                        #colorscale=['lightgreen','magenta'], #either green or mageneta
                                        line=dict(color='black', width=0.5)),
                            text=node_labels,
                            textfont=dict(size=12),
                            hoverinfo='text')    # nodes trace
    
    ## We need to redraw the root (anomalous function) one more time in red
    trace_root = go.Scatter3d(x=[x_nodes[root]],
                    y=[y_nodes[root]],
                    z=[z_nodes[root]],
                    mode='markers',
                    name=func_name,
                    marker=dict(symbol='circle',
                                size=node_size[root],
                                color='red',
                                line=dict(color='black', width=0.5)
                                ),
                    text = [func_name],
                    textfont=dict(size=12),
                    hoverinfo = 'text')    #we need to set the axis for the plot 
    
    #we need to set the axis for the plot 
    axis = dict(showbackground=False,
            showline=False,
            zeroline=False,
            showgrid=False,
            showticklabels=False,
            title='')
    #also need to create the layout for our plot
    layout = go.Layout(title="Call path of: " + func_name,
                width=650,
                height=625,
                showlegend=False,
                scene=dict(xaxis=dict(axis),
                        yaxis=dict(axis),
                        zaxis=dict(axis),
                        ),
                margin=dict(t=100),
                hovermode='closest')

    ############################################################################
    # fig.update_layout(
    #     xaxis=dict(
    #         rangeslider=dict(
    #             visible=True,
    #             range = [0, len(ranklist)]
    #         ),
    #         type ="category"
    #     )
    # )
    # layout = go.Layout(
    #     margin = go.layout.Margin(t=0, l=0, r=0, b=0),
    # )
    # #also need to create the layout for our plot
    # layout = go.Layout(title="Call path of: " + func_name,
    #             # width=650,
    #             # height=625,
    #             showlegend=False,
    #             scene=dict(xaxis=dict(axis),
    #                     yaxis=dict(axis),
    #                     zaxis=dict(axis),
    #                     ),
    #             margin=dict(t=100),
    #             hovermode='closest')
            
#             templates = [
#                 "bootstrap",
#                 "minty",
#                 "pulse",
#                 "flatly",
#                 "quartz",
#                 "cyborg",
#                 "darkly",
#                 "vapor",
#             ]

    data = trace_edges
    data.append(trace_nodes)
    data.append(trace_root)
    #data = [trace_edges, trace_nodes, trace_root]# trace_JohnA]
    fig = go.Figure(data=data, layout=layout)

    template = "minty"#"minty"#"ggplot2"
    load_figure_template(template)
    #fig = go.Figure([trace], layout)
    #fig.update_layout(width=500, height = 500, template=template)
    fig.update_layout(template=template)
        
    data_loader.options['charts'].append(fig)
    if save_sunburst:
        file_path = '%s_3D.pdf' % data_loader.get_config_name()
        dir_path = os.path.join('viz_output', 'callgraph')

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        
        file_path = os.path.join(dir_path, file_path)
        fig.write_image(file_path)

    return fig

def chimbuko_callgraph3D_orig(data_loader):
    ids = []
    labels = []
    parents = []
    values = []
    hover_labels = []
    pairs = []
    dataframe = data_loader.dict_entries
    obj = data_loader.dataFrameObj
    PERCENT_OFFSET = 1.00001
    name = data_loader.get_option('name', 'untitled sunburst')
    save_sunburst = data_loader.get_option('save_sunburst', False)
    
    ############################################################################
    dimension = 3
    func_name =     name = data_loader.get_option('callgraph_root', '')
    G = nx.DiGraph()
    ###
    callgraph_edgelist = obj.get_callgraph_edgelist_for_function(func_name)
    if callgraph_edgelist == None:
        print('No function with that name')
        return
    G.add_weighted_edges_from(callgraph_edgelist)
    Num_nodes = len(G.nodes)
    colors = nx.get_edge_attributes(G,'color').values()
    weights = nx.get_edge_attributes(G,'weight').values()
    nodeColor = 'Blue'
    nodeSize = 20
    lineWidth = 2
    lineColor = '#000000'
    node_labels = list(G.nodes)
    root = node_labels.index(func_name)
    ###
    #spring_3D = nx.spring_layout(G, dim=dimension, seed=218)#nx.spring_layout(G, seed=8)
    #spring_3D = nx.fruchterman_reingold_layout(G, dim=dimension, k=5, seed=517)
    #spring_3D = nx.bipartite_layout(G, pos.keys())
    #spring_3D = nx.circular_layout(G)
    spring_3D = nx.kamada_kawai_layout(G, dim=dimension, scale=1)
    #spring_3D = nx.planar_layout(G)
    #spring_3D = nx.random_layout(G, dim=dimension)
    #spring_3D = nx.rescale_layout_dict(spring_3D)
    #spring_3D = nx.shell_layout(G)
    #spring_3D = nx.spectral_layout(G, dim=dimension) #Good one
    #spring_3D = nx.spiral_layout(G, resolution=0.5, equidistant=True)

    #we need to seperate the X,Y,Z coordinates for Plotly
    x_nodes = [spring_3D[func][0] for func in G.nodes]# x-coordinates of nodes
    y_nodes = [spring_3D[func][1] for func in G.nodes]# y-coordinates
    z_nodes = [spring_3D[func][2] for func in G.nodes]# z-coordinates

    #we  need to create lists that contain the starting and ending coordinates of each edge.
    x_edges=[]
    y_edges=[]
    z_edges=[]      
    community_label = []
    node_size = []
    node_color = []
    edge_width = []
    trace_edges=[]
    for edge in G.edges():
        x_coords = [spring_3D[edge[0]][0],spring_3D[edge[1]][0],None]
        x_edges += x_coords

        y_coords = [spring_3D[edge[0]][1],spring_3D[edge[1]][1],None]
        y_edges += y_coords

        z_coords = [spring_3D[edge[0]][2],spring_3D[edge[1]][2],None]
        z_edges += z_coords
        community_label.append(G.get_edge_data(*edge)['weight']*100)
        node_size.append(G.get_edge_data(*edge)['weight']*100)
        node_color.append(G.get_edge_data(*edge)['weight']*100)
        edge_width.append(G.get_edge_data(*edge)['weight']*100)
    #create a trace for the edges
    
    trace_edges = go.Scatter3d(name=func_name, x=x_edges,
                            y=y_edges,
                            z=z_edges,
                            mode='lines',
                            text=edge_width,
                            line=dict(color=community_label, width=1, dash='longdash', showscale=True),
                            hoverinfo='text')
    #create a trace for the nodes
    trace_nodes = go.Scatter3d(name=func_name, x=x_nodes,
                             y=y_nodes,
                            z=z_nodes,
                            mode='markers+text',
                            marker=dict(symbol='circle',
                                        size=node_size,
                                        color=community_label, #color the nodes according to their community
                                        #colorscale=['lightgreen','magenta'], #either green or mageneta
                                        line=dict(color='black', width=0.5)),
                            text=node_labels,
                            textfont=dict(size=12),
                            hoverinfo='text')    # nodes trace
    
    ## We need to redraw the root (anomalous function) one more time in red
    trace_root = go.Scatter3d(x=[x_nodes[root]],
                    y=[y_nodes[root]],
                    z=[z_nodes[root]],
                    mode='markers',
                    name=func_name,
                    marker=dict(symbol='circle',
                                size=node_size[root],
                                color='red',
                                line=dict(color='black', width=0.5)
                                ),
                    text = [func_name],
                    hoverinfo = 'text')    #we need to set the axis for the plot 
    
    #we need to set the axis for the plot 
    axis = dict(showbackground=False,
            showline=False,
            zeroline=False,
            showgrid=False,
            showticklabels=False,
            title='')
    #also need to create the layout for our plot
    layout = go.Layout(title="Call path of: " + func_name,
                width=650,
                height=625,
                showlegend=True,
                scene=dict(xaxis=dict(axis),
                        yaxis=dict(axis),
                        zaxis=dict(axis),
                        ),
                margin=dict(t=100),
                hovermode='closest')

    ############################################################################

    data = [trace_edges, trace_nodes, trace_root]# trace_JohnA]
    fig = go.Figure(data=data, layout=layout)

    template = "minty"#"minty"#"ggplot2"
    load_figure_template(template)
    #fig = go.Figure([trace], layout)
    #fig.update_layout(width=500, height = 500, template=template)
    fig.update_layout(template=template)
        
    data_loader.options['charts'].append(fig)
    if save_sunburst:
        file_path = '%s_3D.pdf' % data_loader.get_config_name()
        dir_path = os.path.join('viz_output', 'callgraph')

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        
        file_path = os.path.join(dir_path, file_path)
        fig.write_image(file_path)

    return fig


def chimbuko_callgraph2D(data_loader):
    ids = []
    labels = []
    parents = []
    values = []
    hover_labels = []
    pairs = []
    dataframe = data_loader.dict_entries
    obj = data_loader.dataFrameObj
    PERCENT_OFFSET = 1.00001
    name = data_loader.get_option('name', 'untitled sunburst')
    save_sunburst = data_loader.get_option('save_sunburst', False)
    
    ############################################################################
    func_name =     name = data_loader.get_option('callgraph_root', '')
    dimension = 2
    G = nx.DiGraph()
    ###
    callgraph_edgelist = obj.get_callgraph_edgelist_for_function(func_name)
    if callgraph_edgelist == None:
        print('No function with that name')
        return
    G.add_weighted_edges_from(callgraph_edgelist)
    Num_nodes = len(G.nodes)
    colors = nx.get_edge_attributes(G,'color').values()
    weights = nx.get_edge_attributes(G,'weight').values()
    nodeColor = 'Blue'
    nodeSize = 20
    lineWidth = 2
    lineColor = '#000000'
    node_labels = list(G.nodes)
    root = node_labels.index(func_name)

    ### Min-max scaling of the edge weights
    edge_weights = []
    for edge in G.edges():
        edge_weights.append(round(G.get_edge_data(*edge)['weight'], 2))

    edge_data=np.array(edge_weights).reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    data=list(scaler.fit_transform(edge_data))

    
    ###
    ###
    #spring_2D = nx.spring_layout(G, seed=718)#nx.spring_layout(G, seed=8)
    #spring_2D = nx.spring_layout(G, dim=dimension, seed=218)#nx.spring_layout(G, seed=8)
    #spring_2D = nx.fruchterman_reingold_layout(G, dim=dimension, k=5, seed=517)
    #spring_2D = nx.bipartite_layout(G, pos.keys())
    spring_2D = nx.circular_layout(G)
    #spring_2D = nx.kamada_kawai_layout(G, dim=dimension, scale=1)
    #spring_2D = nx.planar_layout(G)
    #spring_2D = nx.random_layout(G, dim=dimension)
    #spring_2D = nx.rescale_layout_dict(spring_3D)
    #spring_2D = nx.shell_layout(G)
    #spring_2D = nx.spectral_layout(G, dim=dimension, scale=3) #Good one
    #spring_2D = nx.spiral_layout(G, resolution=0.5, equidistant=True)
    for node in G.nodes:
        G.nodes[node]['pos'] = list(spring_2D[node])
    
    #we need to seperate the X,Y,Z coordinates for Plotly
    x_nodes = [spring_2D[func][0] for func in G.nodes]# x-coordinates of nodes
    y_nodes = [spring_2D[func][1] for func in G.nodes]# y-coordinates
    #we  need to create lists that contain the starting and ending coordinates of each edge.
    x_edges=[]
    y_edges=[]
    edge_idx = 0
    community_label = []
    node_size = []

    for edge in G.edges():
        x_coords = [spring_2D[edge[0]][0],spring_2D[edge[1]][0],None]
        x_edges += x_coords

        y_coords = [spring_2D[edge[0]][1],spring_2D[edge[1]][1],None]
        y_edges += y_coords

        edge_weight = edge_data[edge_idx][0]
        size_factor = 1000
        small_size_factor = 500
        width_factor = 150
        community_label.append(edge_weight*size_factor)

        edge_style = 'solid'
        if edge_weight < 0.7:
            edge_style = 'dash'
            node_size.append(edge_weight*small_size_factor)
        else:
            node_size.append(edge_weight*size_factor)

    # Make a list of edges for plotly, including line segments that result in arrowheads
    for edge in G.edges():
        # addEdge(start, end, edge_x, edge_y, lengthFrac=1, arrowPos = None, arrowLength=0.025, arrowAngle = 30, dotSize=20)
        start = G.nodes[edge[0]]['pos']
        end = G.nodes[edge[1]]['pos']
        x_edges, y_edges = addEdge(start, end, x_edges, y_edges, .8, 'end', .04, 30, nodeSize)

    trace_edges = go.Scatter(name=func_name, x=x_edges,
                            y=y_edges,
                            mode='lines',
                            text=community_label,
                            line=dict(
                                color='black',
                                width=2,
                                dash='solid'),
                            hoverinfo='text',
                            textfont=dict(size=12))

    # #create a trace for the edges
    # trace_edges = go.Scatter(name=func_name, x=x_edges,
    #                         y=y_edges,
    #                         mode='lines',
    #                         line=dict(color='black', width=2),
    #                         hoverinfo='none')
    #create a trace for the nodes
    trace_nodes = go.Scatter(name=func_name, x=x_nodes,
                             y=y_nodes,
                            mode='markers+text',
                            marker=dict(symbol='circle',
                                        size=node_size,
                                        color=community_label, #color the nodes according to their community
                                        #colorscale=['lightgreen','magenta'], #either green or mageneta
                                        showscale=True,
                                        line=dict(color='black', width=0.5)),
                            text=node_labels,
                            textfont=dict(size=12),
                            hoverinfo='text')    # nodes trace


    
    ## We need to redraw the root (anomalous function) one more time in red
    trace_root = go.Scatter(x=[x_nodes[root]],
                    y=[y_nodes[root]],
                    mode='markers',
                    name=func_name,
                    marker=dict(symbol='circle',
                                size=20,
                                color='red',
                                line=dict(color='black', width=0.5)
                                ),
                    text = [func_name],
                    hoverinfo = 'text')    #we need to set the axis for the plot 
    
    #we need to set the axis for the plot 
    axis = dict(showbackground=False,
            showline=False,
            zeroline=False,
            showgrid=False,
            showticklabels=False,
            title='')
    #also need to create the layout for our plot
    layout = go.Layout(title="Call path of: " + func_name,
                # width=650,
                # height=625,
                showlegend=False,
                scene=dict(xaxis=dict(axis),
                        yaxis=dict(axis),
                        zaxis=dict(axis),
                        ),
                margin=dict(t=100),
                hovermode='closest')

    ############################################################################
    # fig.update_layout(
    #     xaxis=dict(
    #         rangeslider=dict(
    #             visible=True,
    #             range = [0, len(ranklist)]
    #         ),
    #         type ="category"
    #     )
    # )
    # layout = go.Layout(
    #     margin = go.layout.Margin(t=0, l=0, r=0, b=0),
    # )
    # #also need to create the layout for our plot
    # layout = go.Layout(title="Call path of: " + func_name,
    #             # width=650,
    #             # height=625,
    #             showlegend=False,
    #             scene=dict(xaxis=dict(axis),
    #                     yaxis=dict(axis),
    #                     zaxis=dict(axis),
    #                     ),
    #             margin=dict(t=100),
    #             hovermode='closest')
            
#             templates = [
#                 "bootstrap",
#                 "minty",
#                 "pulse",
#                 "flatly",
#                 "quartz",
#                 "cyborg",
#                 "darkly",
#                 "vapor",
#             ]

    data = [trace_edges, trace_nodes, trace_root]# trace_JohnA]
    fig = go.Figure(data=data, layout=layout)

    template = "minty"#"minty"#"ggplot2"
    load_figure_template(template)
    #fig = go.Figure([trace], layout)
    #fig.update_layout(width=500, height = 500, template=template)
    fig.update_layout(template=template)
    fig.update_layout(yaxis = dict(scaleanchor = "x", scaleratio = 1), plot_bgcolor='rgb(255,255,255)')
        
    data_loader.options['charts'].append(fig)
    if save_sunburst:
        file_path = '%s.pdf' % data_loader.get_config_name()
        dir_path = os.path.join('viz_output', 'callgraph')

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        
        file_path = os.path.join(dir_path, file_path)
        fig.write_image(file_path)

    return fig


def gptune_callgraph3D(sobol_analysis):
    type_of_scores = sobol_analysis.keys()
    cols = ['param_name', 'X', 'Y']
    cols.extend(type_of_scores)
    df = pd.DataFrame(columns=cols)
    names = sobol_analysis['ST']
    row = []
    for name in names:


    print(df.head())
#     ids = []
#     labels = []
#     parents = []
#     values = []
#     hover_labels = []
#     pairs = []
#     dataframe = data_loader.dict_entries
#     obj = data_loader.dataFrameObj
#     PERCENT_OFFSET = 1.00001
#     name = data_loader.get_option('name', 'untitled sunburst')
#     save_sunburst = data_loader.get_option('save_sunburst', False)
    
#     ############################################################################
#     func_name =     name = data_loader.get_option('callgraph_root', '')
#     dimension = 2
#     G = nx.DiGraph()
#     ###
#     callgraph_edgelist = obj.get_callgraph_edgelist_for_function(func_name)
#     if callgraph_edgelist == None:
#         print('No function with that name')
#         return
#     G.add_weighted_edges_from(callgraph_edgelist)
#     Num_nodes = len(G.nodes)
#     colors = nx.get_edge_attributes(G,'color').values()
#     weights = nx.get_edge_attributes(G,'weight').values()
#     nodeColor = 'Blue'
#     nodeSize = 20
#     lineWidth = 2
#     lineColor = '#000000'
#     node_labels = list(G.nodes)
#     root = node_labels.index(func_name)

#     ### Min-max scaling of the edge weights
#     edge_weights = []
#     for edge in G.edges():
#         edge_weights.append(round(G.get_edge_data(*edge)['weight'], 2))

#     edge_data=np.array(edge_weights).reshape(-1, 1)
#     scaler = MinMaxScaler(feature_range=(0, 1))
#     data=list(scaler.fit_transform(edge_data))

    
#     ###
#     ###
#     #spring_2D = nx.spring_layout(G, seed=718)#nx.spring_layout(G, seed=8)
#     #spring_2D = nx.spring_layout(G, dim=dimension, seed=218)#nx.spring_layout(G, seed=8)
#     #spring_2D = nx.fruchterman_reingold_layout(G, dim=dimension, k=5, seed=517)
#     #spring_2D = nx.bipartite_layout(G, pos.keys())
#     spring_2D = nx.circular_layout(G)
#     #spring_2D = nx.kamada_kawai_layout(G, dim=dimension, scale=1)
#     #spring_2D = nx.planar_layout(G)
#     #spring_2D = nx.random_layout(G, dim=dimension)
#     #spring_2D = nx.rescale_layout_dict(spring_3D)
#     #spring_2D = nx.shell_layout(G)
#     #spring_2D = nx.spectral_layout(G, dim=dimension, scale=3) #Good one
#     #spring_2D = nx.spiral_layout(G, resolution=0.5, equidistant=True)
#     for node in G.nodes:
#         G.nodes[node]['pos'] = list(spring_2D[node])
    
#     #we need to seperate the X,Y,Z coordinates for Plotly
#     x_nodes = [spring_2D[func][0] for func in G.nodes]# x-coordinates of nodes
#     y_nodes = [spring_2D[func][1] for func in G.nodes]# y-coordinates
#     #we  need to create lists that contain the starting and ending coordinates of each edge.
#     x_edges=[]
#     y_edges=[]
#     edge_idx = 0
#     community_label = []
#     node_size = []

#     for edge in G.edges():
#         x_coords = [spring_2D[edge[0]][0],spring_2D[edge[1]][0],None]
#         x_edges += x_coords

#         y_coords = [spring_2D[edge[0]][1],spring_2D[edge[1]][1],None]
#         y_edges += y_coords

#         edge_weight = edge_data[edge_idx][0]
#         size_factor = 1000
#         small_size_factor = 500
#         width_factor = 150
#         community_label.append(edge_weight*size_factor)

#         edge_style = 'solid'
#         if edge_weight < 0.7:
#             edge_style = 'dash'
#             node_size.append(edge_weight*small_size_factor)
#         else:
#             node_size.append(edge_weight*size_factor)

#     # Make a list of edges for plotly, including line segments that result in arrowheads
#     for edge in G.edges():
#         # addEdge(start, end, edge_x, edge_y, lengthFrac=1, arrowPos = None, arrowLength=0.025, arrowAngle = 30, dotSize=20)
#         start = G.nodes[edge[0]]['pos']
#         end = G.nodes[edge[1]]['pos']
#         x_edges, y_edges = addEdge(start, end, x_edges, y_edges, .8, 'end', .04, 30, nodeSize)

#     trace_edges = go.Scatter(name=func_name, x=x_edges,
#                             y=y_edges,
#                             mode='lines',
#                             text=community_label,
#                             line=dict(
#                                 color='black',
#                                 width=2,
#                                 dash='solid'),
#                             hoverinfo='text',
#                             textfont=dict(size=12))

#     # #create a trace for the edges
#     # trace_edges = go.Scatter(name=func_name, x=x_edges,
#     #                         y=y_edges,
#     #                         mode='lines',
#     #                         line=dict(color='black', width=2),
#     #                         hoverinfo='none')
#     #create a trace for the nodes
#     trace_nodes = go.Scatter(name=func_name, x=x_nodes,
#                              y=y_nodes,
#                             mode='markers+text',
#                             marker=dict(symbol='circle',
#                                         size=node_size,
#                                         color=community_label, #color the nodes according to their community
#                                         #colorscale=['lightgreen','magenta'], #either green or mageneta
#                                         showscale=True,
#                                         line=dict(color='black', width=0.5)),
#                             text=node_labels,
#                             textfont=dict(size=12),
#                             hoverinfo='text')    # nodes trace


    
#     ## We need to redraw the root (anomalous function) one more time in red
#     trace_root = go.Scatter(x=[x_nodes[root]],
#                     y=[y_nodes[root]],
#                     mode='markers',
#                     name=func_name,
#                     marker=dict(symbol='circle',
#                                 size=20,
#                                 color='red',
#                                 line=dict(color='black', width=0.5)
#                                 ),
#                     text = [func_name],
#                     hoverinfo = 'text')    #we need to set the axis for the plot 
    
#     #we need to set the axis for the plot 
#     axis = dict(showbackground=False,
#             showline=False,
#             zeroline=False,
#             showgrid=False,
#             showticklabels=False,
#             title='')
#     #also need to create the layout for our plot
#     layout = go.Layout(title="Call path of: " + func_name,
#                 # width=650,
#                 # height=625,
#                 showlegend=False,
#                 scene=dict(xaxis=dict(axis),
#                         yaxis=dict(axis),
#                         zaxis=dict(axis),
#                         ),
#                 margin=dict(t=100),
#                 hovermode='closest')

#     ############################################################################
#     # fig.update_layout(
#     #     xaxis=dict(
#     #         rangeslider=dict(
#     #             visible=True,
#     #             range = [0, len(ranklist)]
#     #         ),
#     #         type ="category"
#     #     )
#     # )
#     # layout = go.Layout(
#     #     margin = go.layout.Margin(t=0, l=0, r=0, b=0),
#     # )
#     # #also need to create the layout for our plot
#     # layout = go.Layout(title="Call path of: " + func_name,
#     #             # width=650,
#     #             # height=625,
#     #             showlegend=False,
#     #             scene=dict(xaxis=dict(axis),
#     #                     yaxis=dict(axis),
#     #                     zaxis=dict(axis),
#     #                     ),
#     #             margin=dict(t=100),
#     #             hovermode='closest')
            
# #             templates = [
# #                 "bootstrap",
# #                 "minty",
# #                 "pulse",
# #                 "flatly",
# #                 "quartz",
# #                 "cyborg",
# #                 "darkly",
# #                 "vapor",
# #             ]

#     data = [trace_edges, trace_nodes, trace_root]# trace_JohnA]
#     fig = go.Figure(data=data, layout=layout)

#     template = "minty"#"minty"#"ggplot2"
#     load_figure_template(template)
#     #fig = go.Figure([trace], layout)
#     #fig.update_layout(width=500, height = 500, template=template)
#     fig.update_layout(template=template)
#     fig.update_layout(yaxis = dict(scaleanchor = "x", scaleratio = 1), plot_bgcolor='rgb(255,255,255)')
        
#     data_loader.options['charts'].append(fig)
#     if save_sunburst:
#         file_path = '%s.pdf' % data_loader.get_config_name()
#         dir_path = os.path.join('viz_output', 'callgraph')

#         if not os.path.exists(dir_path):
#             os.makedirs(dir_path)
        
#         file_path = os.path.join(dir_path, file_path)
#         fig.write_image(file_path)

#     return fig
