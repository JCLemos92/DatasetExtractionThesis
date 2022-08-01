# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 17:27:40 2021

@author: Leonardo
@goal: Testing Graphviz and Networkx Capabilities
"""

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import os
import random

import pygraphviz as pgv
from networkx.drawing.nx_agraph import graphviz_layout
from networkx.drawing.nx_pydot import to_pydot

dol = {0: [1, 2], 1:[2]}  # single edge (0,1)
my_dict_of_dicts = {0: {1: {'weight': 10}, 
                        2: {'weight': 1},
                        0: {'weight': 2}}, 
                    1: {2: {'weight': 1}}, 
                    2: {3: {'weight': 1}, 
                        1: {'weight': 1},
                        2: {'weight': 1}}}


color = ["blue", "yellow", "yellow", "blue"]

options_graph = {
    "font_size": 40,
    "font_weight": "bold",
    "node_size": 6000,
    "node_color": color,
    "edgecolors": "black",
    "linewidths": 2,
    "width": 5,
    "alpha":0.5
}

options_labels = {
    "font_size": 40,
    "font_weight": "bold",
    "font_color": 'black',
    "label_pos": 0.5
}

#G = nx.from_dict_of_lists(dol)
#create_using=nx.DiGraph(dol)

# =============================================================================
# plt.figure(figsize=(20,20))  
# plt.title("Familia X", fontsize = 40)
# 
# g = nx.DiGraph(my_dict_of_dicts)
# pos = nx.circular_layout(g)
# #pos = graphviz_layout(g, prog='dot')
# nx.draw(g, with_labels=True, pos= pos, **options_graph)
# edge_labels = dict([((n1, n2), my_dict_of_dicts['weight']) for n1, n2, my_dict_of_dicts in g.edges(data=True)])
# nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels, **options_labels)
# plt.show()
# 
# =============================================================================
#print(edge_labels)

# =============================================================================
# #nx.nx_agraph.write_dot(g,'test.dot')
# plt.figure(figsize=(20,20))  
# plt.title('With graphviz_layout', fontsize = 40)
# pos=graphviz_layout(g, prog='dot')
# nx.draw(g, pos, with_labels=True, **options_graph)
# #pos = graphviz_layout(g)
# #nx.draw_networkx(g, pos)
# edge_labels = dict([((n1, n2), my_dict_of_dicts['weight']) for n1, n2, my_dict_of_dicts in g.edges(data=True)])
# nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels, **options_labels)
# #plt.savefig('nx_test.png')
# plt.show()
# =============================================================================

# =============================================================================
# for e in g.edges(data=True):
#     print(e[0], e[1])
# =============================================================================

#nx.set_edge_attributes(g, {(e[0], e[1]): {'label': " " + str(e[2]['weight'])} for e in g.edges(data=True)})


# =============================================================================
# A = nx.nx_agraph.to_agraph(g)
# n = A.get_node('0')
# n.attr['style']="filled"
# n.attr['color']="red"
# #fillcolor=red, style=
# n.attr["shape"] = "square"
# print(n.attr)
# A.layout('dot')
# A.draw('abcd.png', prog="dot")
# =============================================================================

# =============================================================================
# G = pgv.AGraph(my_dict_of_dicts, strict=True, directed=True)
# 
# #nodelist = ["f", "g", "h"]
# #G.add_nodes_from(nodelist)
# #G.add_node(1, color="red", fontsize=32)
# 
# #n = G.get_node(1)
# #n.attr["shape"] = "diamond"
# #G.add_edge("f", "g", color="blue")
# #G.add_edge(1, 1, color="blue", label = " 2")
# edge = G.get_edge('0', '0')
# print(edge)
# #edge.attr['label'] = 10
# nodes = G.nodes()
# edges = G.edges()
# print(G)
# 
# print(nodes)
# print(edges)
# 
# G.layout(prog="dot")
# G.draw("file.png", prog="dot")
# 
# =============================================================================

# =============================================================================
# parsed_tree = [(0,1), (0,2), (1,3), (2,4), (2,5), (4,6), (5,7)]
# 
# id_to_str = {0: 'S', 1: 'NP', 2: 'VP', 3: 'I', 4: 'V', 5: 'NP', 6: "'saw'", 7: "'him'"}
# 
# tree2graph = nx.DiGraph()
# tree2graph.add_edges_from(parsed_tree)
# for node in tree2graph.nodes():
#     tree2graph.nodes[node]['label'] = id_to_str[node]
# 
# nx.draw(tree2graph)
# #G = nx.DiGraph(edges)
# 
# =============================================================================

# =============================================================================
# #G = nx.DiGraph(nx.utils.pairwise("abd"))
# #G.add_edges_from(nx.utils.pairwise("acd"))
# plt.figure(figsize=(20,20))  
# plt.title('teste', fontsize = 40)
# nx.draw(G)
# plt.show()
# =============================================================================

# =============================================================================
# plt.figure(figsize=(20,20))  
# plt.title('branching', fontsize = 40)
# B = nx.dag_to_branching(G)
# nx.draw(B)
# plt.show()
# 
# =============================================================================


# =============================================================================
# G = nx.MultiDiGraph()
# nx.add_path(G, [0, 1, 2])
# G.add_edge(2, 3, key="main", weight=5)
# G.add_edge(2, 3, key="second", weight=7)
# G.edges(data=True)
# #pos = graphviz_layout(G, "dot")
# #G_temp.get_edge_data
# #list(G.edges(data=True))
# print([e for e in G.edges(data=True, keys=True)])
# 
# G_temp = nx.nx_agraph.to_agraph(G.copy())
# print(G_temp)
# for e in G_temp.edges(keys=True):
#     print("Edge", e)
#     #print("Aqui", e.attr['label'])
# # =============================================================================
# #     print("last", e[2])
# #     if "weight" in e[2].keys():
# #         print("weigth", e[2]["weight"])
# #         e.attr['label'] = e[2]["weight"]
# # =============================================================================
# name = "teste.png"
# G_temp.layout(prog="dot")
# G_temp.draw(name, prog="dot")
# 
# =============================================================================
# =============================================================================
# G = pgv.AGraph(strict=False)
# G.add_edge("a", "b", 1)
# temp = G.add_edge("a", "b", 1)
# print(G.get_edge("a", "b", 1))
# =============================================================================
