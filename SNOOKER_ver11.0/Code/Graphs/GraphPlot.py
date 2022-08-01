# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 11:53:25 2022

@author: Leonardo Ferreira
@goal: Plots in graphs the actions available for each subfamily
"""

import pygraphviz as pgv
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout

class GraphPlot:
    
    def addGraphStyle(graph, name):
        
        operations = ["transfer", "close", "init"]
        graph.graph_attr["label"] = name
        graph.graph_attr["labelloc"]= "top"
        graph.graph_attr["fontsize"]= 24
        graph.graph_attr["nodesep"]= 0.5
        
        for i in operations:
            graph.add_node(i)
            n = graph.get_node(i)
            #print("n", i)
            #n.attr["linewidth"] = 8
            if i == "transfer":
                n.attr["shape"] = "triangle"
                n.attr["color"] = "blue"
            elif i == "close":
                n.attr["shape"] = "box"
                n.attr["color"] = "red"
            else:
                n.attr["shape"] = "diamond"
                n.attr["color"] = "green"
            #print("shape", n.attr["shape"])
            #print("color", n.attr["color"])
        
        #print(graph.nodes())
        
        b = graph.add_subgraph(operations, name='cluster3', label='Legend', rank='same')
        b.graph_attr["labelloc"]= "top"
        b.graph_attr["fontsize"]= 12
        
    def processTransitions(actions):
        
        for sub in actions.keys():
            #if len(actions[sub]) > 30:
            #print("Subfamily:", sub)
            #print("Actions:", len(actions[sub]["actions"]))
            for action in actions[sub]["actions"]:
                #print("Curr action:", action)
                for i in range(len(action)):
                    step = action[i]
                    #print("Curr step", step)
                    if step != action[-1]:
                        edge = (step, action[i + 1])
                        #print("Edge", edge)
                        if step not in actions[sub]["nodes info"].keys():
                            actions[sub]["nodes info"][step] = {}
                            actions[sub]["nodes info"][step]["possible edges"] = []
                            actions[sub]["nodes info"][step]["edges"] = {}
                            actions[sub]["transitions"][step] = []
                            #actions[sub]["transitions"][step] = {}
                        if action[i + 1] not in actions[sub]["nodes info"][step]["possible edges"]:
                            actions[sub]["nodes info"][step]["possible edges"].append(action[i + 1])
                            actions[sub]["transitions"][step].append(action[i + 1])
                            #actions[sub]["transitions"][step][action[i + 1]] = {}
                            #actions[sub]["transitions"][step][action[i + 1]]["type"] = "main"
                            
                        if edge not in actions[sub]["nodes info"][step]["edges"].keys():
                            actions[sub]["nodes info"][step]["edges"][edge] = {}
                            actions[sub]["nodes info"][step]["edges"][edge]["count"] = 1
                            #print("New edge added")
                        else:
                            actions[sub]["nodes info"][step]["edges"][edge]["count"] += 1
                            #print("Edge updated")
                
            #print("Nodes Info", actions[sub]["nodes info"])
            #print("Transition", actions[sub]["transitions"])
            #print("Transition values", actions[sub]["transitions"].values())
            #print("Curr transition", actions)
        
    def processGraphs(actions, path,  init, final, transfer):
        
        GraphPlot.processTransitions(actions)
        
        for sub in actions.keys():
            #print("\nSubfamily:", sub)
            #Utils.printList(actions[sub]["actions"])
            #print("Transition values", actions[sub]["transitions"])
            GraphPlot.buildGraphTransitions(actions, path, sub, init, final, transfer)
            #GraphPlot.buildGraphActions(actions, sub, init, final, transfer)

    def buildGraphTransitions(actions, path, subfamily, init, final, transfer):
        
        #print("Subfamily:", subfamily)
        transitions = actions[subfamily]["transitions"]
         
        #print("Transitions:", transitions)
        G_nx = nx.MultiDiGraph(transitions)
        
        cycles = []
        for cycle in nx.simple_cycles(G_nx):
            cycles.append(cycle)    
        #print("Loop edges", cycles)
        
        #print("Aqui", list(nx.find_cycle(G_nx, orientation="ignore")))
        
# =============================================================================
#         for e in G_nx.edges(keys= True):
#             print("Edge", e)
# =============================================================================
        
        nx_graph = GraphPlot.outputSubfamilies(G_nx, path, subfamily, actions, init, final, transfer, cycles)
        
# =============================================================================
#         plt.figure(figsize=(20,20))  
#         plt.title(subfamily, fontsize = 40)
#         pos = graphviz_layout(nx_graph, prog='dot')
#         options_graph = {
#             "font_size": 40,
#             "font_weight": "bold",
#             "node_size": 6000,
#             "node_color": "blue",
#             "edgecolors": "black",
#             "linewidths": 2,
#             "width": 5,
#             "alpha":0.5
#             }
#         
#         options_labels = {
#             "font_size": 40,
#             "font_weight": "bold",
#             "font_color": 'black',
#             "label_pos": 0.5
#         }
#         
#         edge_labels = dict([((n1, n2), dict_of_dicts['label']) for n1, n2, dict_of_dicts in nx_graph.edges(data=True)])
#         nx.draw(nx_graph, with_labels=True, pos= pos, **options_graph)
#         nx.draw_networkx_edge_labels(nx_graph, pos, edge_labels=edge_labels, **options_labels)
#         plt.show()
#                 
# =============================================================================
    def buildGraphActions(actions, subfamily, init, final, transfer):

        sub_actions = actions[subfamily]["actions"]
        
        G = pgv.AGraph(strict=True, directed=True)
        #print("Action list:", sub_actions)
        
        for i in range(len(sub_actions)):
            #print("Curr action:", sub_actions[i])
            for p in sub_actions[i]:
                curr_id = p + "_" + str(i)
                #print("Curr id:", curr_id)
                G.add_node(curr_id, label = p)
                node = G.get_node(curr_id)
                #print("Node", node)
                if p in init:
                    node.attr["shape"] = "diamond"
                    node.attr["color"] = "green"
                    node.attr["linewidth"] = 8
                elif p in final:
                    node.attr["shape"] = "box"
                    node.attr["color"] = "red"
                    node.attr["linewidth"] = 8
                elif p in transfer:
                    node.attr["shape"] = "triangle"
                    node.attr["color"] = "blue"
            
            tuple_list = GraphPlot.convertListoTupleList(i, sub_actions[i])
            G.add_edges_from(tuple_list)
    
        name = "./Output/SubfamiliesActions/Subfamily_" + subfamily + ".png"
        G.layout(prog="dot")
        G.draw(name, prog="dot")
        
    def outputSubfamilies(graph, path, subfamily, actions, init, final, transfer, loops):
        
        G = nx.nx_agraph.to_agraph(graph.copy())
        #G = pgv.AGraph(transitions,strict=True, directed=True)
        
        #print("G", G)
        for n in G.nodes():
            #print("Curr node", n)
            n.attr["fontsize"]= 16
            if n in init:
                n.attr["shape"] = "diamond"
                n.attr["color"] = "green"
                n.attr["linewidth"] = 8
            elif n in final:
                n.attr["shape"] = "box"
                n.attr["color"] = "red"
                n.attr["linewidth"] = 8
            elif n in transfer:
                n.attr["shape"] = "triangle"
                n.attr["color"] = "blue"
                n.attr["linewidth"] = 8
                
        #print("Node " + str(n) + " edges: "  + str(G.out_edges(n)))
        #print("Edges:",  G.edges())
        for e in G.edges():
            #print("Curr edge", e)
            #print("Leading node", e[0])
            input_node = e[0]
            node_edges = actions[subfamily]["nodes info"][input_node]["edges"]
            #print("Node edges", node_edges)
            node_edge_count = actions[subfamily]["nodes info"][input_node]["edges"][e]["count"]
            #print("Edge count", node_edge_count)
            #print("values", sum(list(node_edges.values())))
            #print("Number of occurences", GraphPlot.getNumberEdges(node_edges))
            node_edge_prob = round((node_edge_count/GraphPlot.getNumberEdges(node_edges)), 2)
            #print("Edge prob", node_edge_prob)
            e.attr['label'] = " " + str(node_edge_prob)
            e.attr['color'] = GraphPlot.getEdgeColor(node_edge_prob)
            e.attr['decorate'] = True
            e.attr['fontsize'] = 12
            actions[subfamily]["nodes info"][input_node]["edges"][e]["prob"] = node_edge_prob
            #print("Type", type(actions[subfamily]["nodes info"][input_node]["edges"][e]["prob"]))
            #print("Nodes info updated", actions[sub]["nodes info"][input_node])
            #print("Node " + str(n) + " edges: "  + str(G.out_edges(n)))
        
        for curr_loop in loops:
            #print("Curr loop", curr_loop)
            if len(curr_loop) == 1:
                GraphPlot.addDuplicateEdge(G, curr_loop[0], curr_loop[0])
            else:
                for idx in range(len(curr_loop)):
                    #print("Index:", idx)
                    if idx < (len(curr_loop)-1):
                        GraphPlot.addDuplicateEdge(G, curr_loop[idx], curr_loop[idx + 1])
                    else:
                        GraphPlot.addDuplicateEdge(G, curr_loop[-1], curr_loop[0])
                        
                
# =============================================================================
#         for e in G.edges(keys=True):
#             print("Edges", e)
# =============================================================================
    
        GraphPlot.addGraphStyle(G, "Subfamily " + subfamily)

        name = path + subfamily + ".png"
        G.layout(prog="dot")
        G.draw(name, prog="dot")
        
        nx_graph = nx.nx_agraph.from_agraph(G)
        #print("New graph", temp)
        #print("Nodes number:", len(temp.nodes()))
        #print("Nodes:", temp.nodes(data = True))
        #print("Edges number:", len(temp.edges()))
        #print("Edges:", nx_graph.edges(data = True))
        
        return nx_graph
    
    def addDuplicateEdge(graph, init, target):
        
        edge_str = "Edge (" + str(init) + ", " + str(target) + ")"
        try:
            edge = graph.get_edge(init, target, 1)
            #print(edge_str + " already exists")
        except:
            #print("Edge is going to be added")
            graph.add_edge(init, target, 1)
            #if graph.get_edge(init, target, 1):
            #    print(edge_str + " added to graph")
            
            main_edge =  graph.get_edge(init, target, 0)
            #print("main edge", main_edge)
            sec_prob = round(float(main_edge.attr['label'])/3, 2)
            #print("New prob", sec_prob)
            sec_edge = graph.get_edge(init, target, 1)
            #print("New edge", sec_edge)
            sec_edge.attr['fontsize'] = 12
            sec_edge.attr['label'] = "  " + str(sec_prob)
            color = GraphPlot.getEdgeColor(sec_prob)
            #print("Color", color)
            sec_edge.attr['color'] = color
            sec_edge.attr['style'] = "dashed"
            sec_edge.attr['decorate'] = True
        
    
    def getEdgeColor(prob):
        
        color_list = "/ylgnbu9/"
        color = -1
        
        if prob < 0.25:
            color = 3
        elif 0.25 <= prob < 0.5:
            color = 5
        elif 0.5 <= prob < 0.75:
            color = 7
        elif 0.75 <= prob < 1:
            color = 8
        else:
            color = 9
                
        return color_list + str(color)
    
    def getNumberEdges(edges):
        
        total = 0
        for e in edges:
            #print("Aqui", e)
            total += edges[e]["count"]
            
        return total
    
    def convertListoTupleList(action_idx, list_):
            
        new_list = []
        for i in range(len(list_)):
            step = list_[i] + "_" + str(action_idx)
            if list_[i] != list_[-1]:
                next_step = list_[i + 1] + "_" + str(action_idx)
                edge = (step, next_step)
                new_list.append(edge)
                
        #print("Tuple List:", new_list)
        return new_list