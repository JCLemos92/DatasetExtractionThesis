# -*- coding: utf-8 -*-
"""
Created on Tue Jun  8 11:06:15 2021

@author: Leonardo Ferreira
@goal: Analyses the real dataset provided by a cybersecurity company
"""


import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime
from numpy import array
from matplotlib import pyplot as plt

import seaborn as sns
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import LabelEncoder
import scipy.cluster.hierarchy as sch
import pygraphviz as pgv

np.set_printoptions(threshold=sys.maxsize)

from Code.Graphs.GraphPlot import GraphPlot
from Code.Utils import Utils

def datasetToFile(data, path):
        
    output = path + ".xlsx"
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    data.to_excel(writer, sheet_name='Preprocessing', index = False)  
    writer.save()

def cleanTimestamps(list_):
    
    if type(list_) != float:
        list_ = list_.replace('[', '')
        list_ = list_.replace(']', '')
        
        x = list_.split(", ")
        temp = []
        temp = convertTimeStamps(x)
    else:
        temp.append("")

    return temp

def convertTimeStamps(list_):
    
    temp = []
    #print(list_)
    for k in list_:
        #print("object", k)
        dt_object = datetime.fromtimestamp(int(k))
        temp.append(dt_object.strftime('%d-%m-%Y %H:%M:%S'))
        
    return temp

def calculateTotalTime(list_):
        
    d1 = datetime.strptime(list_[0], "%d-%m-%Y %H:%M:%S")
    d2 = datetime.strptime(list_[-1], "%d-%m-%Y %H:%M:%S")
    time_diff = d2 - d1
    
    return round(time_diff.total_seconds() / 60)

def calculateDiffDate(date_1, timestamp_2):
        
    d1 = datetime.strptime(date_1, "%Y-%m-%d %H:%M:%S")
    d2 = datetime.fromtimestamp(int(timestamp_2))
    time_diff = d2 - d1
    
    return round(time_diff.total_seconds() / 60)
    #return time_diff
    
def calculateDiffTimeFromTimestamp(time_1, time_2):
        
    time_1 = datetime.fromtimestamp(int(time_1))
    time_2 = datetime.fromtimestamp(int(time_2))
    time_diff = time_2 - time_1
    
    #print(round(time_diff.total_seconds() / 60, 1))
    #return int(time_diff.total_seconds())
    return abs(round(time_diff.total_seconds() / 60, 1))
    #return time_diff
    
def findNegativeTimestamps(timestamps):
    
    #print("Aqui", timestamps)
    temp = ""
    for k in timestamps:
        if temp == "":
            temp = k 
        else:
            if calculateDiffTimeFromTimestamp(temp, k) < 0:
                #print("Negative found")
                return False
            
    return True

def findUnclosedTickets(transitions):
    
    #print("Aqui", transitions)
    temp = ""
    if transitions[-1] != "CL":
        return False
    else:
        return True

def cleanDataset(data):
    #print(len(data))
    data = data[data['ID'].notna()]
    #print(len(data))
    data = data[data['discovered_date'].notna()]
    #print(len(data))
    data = data[data['Transitions'].notna()]
    data = data[data['Transitions'].str.contains("policy_name")==False]
    #data = data[data['description'].notna()]
    
    #print(len(data))
    #data = data[(data['Status'] == "Closed") | (data['Status'] == "Transfer") | (data['Status'] == "Open") | (data['Status'] == "In Progress")]
    #data = data[~data['description'].str.contains("SOC Service Operation")]
    
    # Surpasses the limit of excel cell character
    data = data[data['ID'] != 2402822]
    data = data[data['ID'] != 2405189]
    data = data[data['ID'] != 2406761]
    
    data["time_stamp_converted"] = data["operator_action_timestamps"].apply(cleanTimestamps)

    #data["discovered_date"] = pd.to_datetime(data["discovered_date"])
    #data["discovered_date"] = data["discovered_date"].dt.strftime('%Y-%m-%d %H:%M:%S')
    data["discovered_date"] = [datetime.fromtimestamp(int(x)) for x in data["discovered_date"]]
   
    #data["end_date"] = pd.to_datetime(data["end_date"])
    #data["end_date"] = data["end_date"].dt.strftime('%Y-%m-%d %H:%M:%S')
    data["end_date"] = [datetime.fromtimestamp(int(x)) for x in data["end_date"]]
    
    data["Transitions"] = data["Transitions"].apply(lambda x: x.replace("'", ""))
    data["Transitions"] = data["Transitions"].apply(lambda x: x.strip())
    data['Transitions'] = data['Transitions'].apply(lambda x: x[1:-1].split(', '))
    data['operator_action_timestamps'] = data['operator_action_timestamps'].apply(lambda x: x[1:-1].split(', '))
   
# =============================================================================
#     with_outlier_actions = len(data)
#     data = data[data.groupby("Transitions")["Transitions"].transform('count').ge(2)]
#     without_outlier_actions = len(data)
#     print("Outlier tickets removed", str(with_outlier_actions - without_outlier_actions))
#     print(len(data))
#     data["Transitions"] = data["Transitions"].apply(lambda x: x.replace("'", ""))
#     data["Transitions"] = data["Transitions"].apply(lambda x: x.strip())
#     data['Transitions'] = data['Transitions'].apply(lambda x: x[1:-1].split(', '))
#     data['operator_action_timestamps'] = data['operator_action_timestamps'].apply(lambda x: x[1:-1].split(', '))
#     
#     with_negatives = len(data)
#     data = data[data["operator_action_timestamps"].apply(findNegativeTimestamps) != False]
#     without_negatives = len(data)
#     print("Number of tickets with negative transitions removed:", str(with_negatives - without_negatives))
#     #print(len(data))
#     unclosed_tickets = len(data)
#     data = data[data["Transitions"].apply(findUnclosedTickets) != False]
#     closed_tickets = len(data)
#     print("Number of unclosed tickets removed:", str(unclosed_tickets - closed_tickets))
# =============================================================================
    #print(len(data))
    return data

# Audtrail, ZalertNotify, ST_Attach, Attach_DOC #, SLARESUME, SLADELAY
def removeUnnecessaryTransitions(transitions, description, timestamps):
    
    necessary_transitions = []
    necessary_description = []
    necessary_timestamps = []
    
    #print("Transition:", transitions)
    for l in range(len(transitions)):
        #print("Transição", transitions[l])
        if transitions[l] != "AUDTRAIL" and transitions[l] != "ST_ATTACH" and transitions[l] != "ATTACHTDOC": #and transitions[l] != "SLADELAY" and transitions[l] != "SLARESUME":  
            #print("Transition added")
            necessary_transitions.append(transitions[l])
            necessary_description.append(description[l])
            necessary_timestamps.append(timestamps[l])
    
    #print("Transition Ok:", necessary_transitions)
            
    return necessary_transitions, necessary_description, necessary_timestamps

def checkTransitions(transitions, description):
    
    found = False
    #print("Checking transitions...")
    for l in range(len(transitions)):
        #print("index", l)
        #print("Transição", transitions[l])
        #print("Descricao", description[l])
        if transitions[l] == "LOG" and transitions[l + 1] == "LOG":
            #print("LOG found!")
            found = True
            break
        elif transitions[l] == "FLD" and (l + 1 != len(transitions) and  transitions[l + 1] == "FLD"):
            #print("FLD found!")
            found = True
            break
        elif transitions[l] == "ATTACHTDOC" and (l + 1 != len(transitions) and  transitions[l + 1] == "ATTACHTDOC"):
            #print("ATTACHTDOC found!")
            found = True
            break
            
    return found

def processTransitionsDuration(transitions, description, timestamps):
    
    #print("Aqui")
    #First is L1 (SOC Operators), L2 (SOC Analysts), and L3 (SOC Engineer)
    # index 0 -> L1, 1 -> L2, 2 -> L3
    teams_duration = [0,0,0]
    transitions_duration = []
    dur = 0
    last_team_idx = 0
    
    #print("Transitions", transitions)
    #print("Description", description)
    #print("Timestamp", timestamps)
    for l in range(len(transitions)):
        if l == 0:
            transitions_duration.append((transitions[l], dur))
        else:
            transition_dur = calculateDiffTimeFromTimestamp(timestamps[l - 1], timestamps[l])
            transitions_duration.append(((transitions[l], transition_dur)))
            
            dur = dur + transition_dur
            #print("Duration updated:", dur)
            if transitions[l] == "TR":
                #print("Descp", description[l])
                #print("State", teams_duration[0])
                #print("Transation dur", transition_dur)
                if "from 'SOC Operators'" in description[l]:
                    teams_duration[0] += teams_duration[0] + dur
                    if "to 'SOC Analyst'" in description[l]:
                        #print("Team changed to L2")
                        last_team_idx = 1
                    else:
                        #print("Team changed to L3")
                        last_team_idx = 2
                        
                elif "from 'SOC Analyst'" in description[l]:
                    teams_duration[1] += teams_duration[1] + dur
                    if "to 'SOC Engineer'" in description[l]:
                        #print("Team changed to L3")
                        last_team_idx = 2
                    else:
                        #print("Team changed to L1")
                        last_team_idx = 0
                else:
                    teams_duration[2] += teams_duration[2] + dur
                    if "to 'SOC Operators'" in description[l]:
                        #print("Team changed to L1")
                        last_team_idx = 0
                    else:
                        #print("Team changed to L2")
                        last_team_idx = 1
                #print("Teams updated", teams_duration)
                dur = 0
            elif l == len(transitions) - 1:
                #print("Final step")
                teams_duration[last_team_idx] += teams_duration[last_team_idx] + dur
                #print("Teams updated", teams_duration)
            
    #print("Duration:", duration_combo)
    return transitions_duration, teams_duration

def updateTransitions(transitions, transitions_description, timestamps):
    
    transitions_combo = []
    transitions_updated = []
    description_updated = []
    timestamps_updated = []
    
    #print("Transition", transitions)
    #print("Removing transitions...")
    for l in range(len(transitions)):
        #print("index", l)
        #print("Transição", transitions[l])
        #print("Descricao", transitions_description[l])
        if transitions[l] == "TR" and ("group" not in transitions_description[l] and "Group" not in transitions_description[l]):  
            print("TR removed!")
        elif transitions[l] == "LOG" and transitions[l + 1] == "LOG":
            print("LOG removed!")
        elif transitions[l] == "FLD" and (l+1 != len(transitions) and  transitions[l + 1] == "FLD"):
            print("FLD removed!")
        elif transitions[l] == "ST" and (l+1 != len(transitions) and  transitions[l + 1] == "ST"):
            print("ST removed!")
        else:
            transitions_updated.append(transitions[l])
            description_updated.append(transitions_description[l])
            timestamps_updated.append(timestamps[l])
            transitions_combo.append((transitions[l], transitions_description[l]))

    return transitions_combo, transitions_updated, description_updated, timestamps_updated

def getNodesInfo(subfamily, transitions, transitions_info):
        
    if subfamily not in transitions_info.keys():
        transitions_info[subfamily] = {}
        transitions_info[subfamily]["nodes info"] = {}
        transitions_info[subfamily]["transitions"] = {}
        transitions_info[subfamily]["actions"] = []
    else:
        transitions_info[subfamily]["actions"].append(transitions)
    
    #print("Subfamily:", subfamily)
    #print("Transition:", transitions)
    for t in range(len(transitions)):
        step = transitions[t]
        #print("Curr transition", step)
        if step != transitions[-1]:
            edge = (step, transitions[t + 1])
            #print("Edge", edge)
            if step not in transitions_info[subfamily]["nodes info"].keys():
                transitions_info[subfamily]["nodes info"][step] = {}
                transitions_info[subfamily]["nodes info"][step]["possible edges"] = []
                transitions_info[subfamily]["nodes info"][step]["edges count"] = {}
                transitions_info[subfamily]["transitions"][step] = []
            
            if transitions[t + 1] not in transitions_info[subfamily]["nodes info"][step]["possible edges"]:
                transitions_info[subfamily]["nodes info"][step]["possible edges"].append(transitions[t + 1])
                transitions_info[subfamily]["transitions"][step].append(transitions[t + 1])
                            
            if edge not in transitions_info[subfamily]["nodes info"][step]["edges count"].keys():
               transitions_info[subfamily]["nodes info"][step]["edges count"][edge] = 1
               #print("New edge added")
            else:
                transitions_info[subfamily]["nodes info"][step]["edges count"][edge] += 1
                #print("Edge updated")
                
    #print("Nodes Info", transitions_info[subfamily]["nodes info"])
    #print("Transition", actions[sub]["transitions"])
    #print("Transition values", actions[sub]["transitions"].values())
    #print("Curr transition", actions)
    
def drawGraph(transitions_info, transitions_treated):
    
    for sub in transitions_info.keys():
        #print("Subfamily:", sub)
        #Utils.printList(transitions_info[sub]["actions"])
        
        transitions = transitions_info[sub]["transitions"]
        G = pgv.AGraph(transitions,strict=True, directed=True)

        for n in G.nodes():
            #print("Curr node", n)
            if n == "INIT":
                n.attr["shape"] = "diamond"
                n.attr["color"] = "green"
                #n.attr["linewidth"] = 8
            elif n == "CL":
                n.attr["shape"] = "box"
                n.attr["color"] = "red"
                #n.attr["linewidth"] = 8
            elif n == "TR":
                n.attr["shape"] = "triangle"
                n.attr["color"] = "blue"
                #n.attr["linewidth"] = 8
            #print("Node " + str(n) + " edges: "  + str(G.out_edges(n)))

        for e in G.edges():
            #print("Curr edge", e)
            #print("Leading node", e[0])
            input_node = e[0]
            node_edges = transitions_info[sub]["nodes info"][input_node]["edges count"]
            #print("Node edges", node_edges)
            node_edge_count = transitions_info[sub]["nodes info"][input_node]["edges count"][e]
            #print("Edge count", node_edge_count)
            #print("values", sum(list(node_edges.values())))
            node_edge_prob = round((node_edge_count/sum(list(node_edges.values()))), 2)
            #print("Edge prob", node_edge_prob)
            e.attr['label'] = " " + str(node_edge_prob)
            transitions_info[sub]["nodes info"][input_node]["edges probs"] = {}
            transitions_info[sub]["nodes info"][input_node]["edges probs"][e] = node_edge_prob
            #print("Nodes info updated", actions[sub]["nodes info"][input_node])
            #print("Node " + str(n) + " edges: "  + str(G.out_edges(n)))
        
        GraphPlot.addGraphStyle(G, "Subfamily " + sub)
        
        name = "../RealDatasetCleaner/Subfamilies/" + sub + ".png"
        G.layout(prog="dot")
        G.draw(name, prog="dot")

def getOperators(ticket_id, subfamily, transitions, summary, timestamps, operators_info):
    
    if subfamily not in operators_info.keys():
        operators_info[subfamily] = {}
    
    operators = []
    curr_user = ""
    user_timestamp = -1
    print("Checking operators...")
    for k in range(len(transitions)):
        #print("index", k)
        if transitions[k] == "TR":  
            #print("TR found!")
            tr_info = summary[k]
            tr_info = tr_info.replace("\\n", "")
            #print("Transfer info:", tr_info)
            team_info = ""
            if "Transfer group" in tr_info:
                #print("Team escalation found")
                tr_info = tr_info.replace("\n", "")
                team_info = tr_info.partition("Transfer group")[-1]
                tr_info = tr_info.partition("Transfer group")[0]
                #print("Team info:", team_info)
                #print("Transfer info updated:", tr_info)
            elif "Transfer Group" in tr_info:
                #print("Team escalation found")
                tr_info = tr_info.replace("\n", "")
                team_info = tr_info.partition("Transfer Group")[-1]
                tr_info = tr_info.partition("Transfer Group")[0]
                #print("Team info:", team_info)
                #print("Transfer info updated:", tr_info)
                
            if team_info != "":
                team = team_info.partition(" to ")[2]
                team = team.replace("'", "").lstrip().rstrip()
                print("Team:", team)
            
            operator = tr_info.partition(" to ")[2]
            #print("Operator", operator)
            operator = operator.replace("'", "").lstrip().rstrip()
            #print("Operator:", operator)
            
            if curr_user != "":
                if curr_user not in operators_info[subfamily].keys():
                    operators_info[subfamily][curr_user] = {}
                    operators_info[subfamily][curr_user]["tickets"] = {}
                if ticket_id not in operators_info[subfamily][curr_user]["tickets"].keys():
                    operators_info[subfamily][curr_user]["tickets"][ticket_id] = {}
                
                operators_info[subfamily][curr_user]["tickets"][ticket_id]["init"] = str(datetime.fromtimestamp(int(user_timestamp)))
                operators_info[subfamily][curr_user]["tickets"][ticket_id]["end"] = str(datetime.fromtimestamp(int(timestamps[k])))
                
                #print("user time", datetime.fromtimestamp(int(user_timestamp)))
                #print("time", datetime.fromtimestamp(int(timestamps[k])))
                time_spent = calculateDiffTimeFromTimestamp(user_timestamp, timestamps[k])
                operators_info[subfamily][curr_user]["tickets"][ticket_id]["diff (sec)"] = time_spent
                #print("time spent", time_spent)
                operators.append((curr_user, time_spent))
                #print("OPERATOR added:", (curr_user, time_spent))
            
            curr_user = operator
            user_timestamp = timestamps[k]
            
        if k == len(transitions) - 1 and curr_user != "":
            if curr_user not in operators_info[subfamily].keys():
                operators_info[subfamily][curr_user] = {}
            if ticket_id not in operators_info[subfamily][curr_user].keys():
                operators_info[subfamily][curr_user]["tickets"] = {}
                operators_info[subfamily][curr_user]["tickets"][ticket_id] = {}

            operators_info[subfamily][curr_user]["tickets"][ticket_id]["init"] = str(datetime.fromtimestamp(int(user_timestamp)))
            operators_info[subfamily][curr_user]["tickets"][ticket_id]["end"] = str(datetime.fromtimestamp(int(timestamps[k])))
            
            time_spent = calculateDiffTimeFromTimestamp(user_timestamp, timestamps[k])
            operators_info[subfamily][curr_user]["tickets"][ticket_id]["diff (sec)"] = time_spent
            operators.append((curr_user, time_spent))
            #print("Final OPERATOR added:", (curr_user, time_spent))

    if not operators:
        operators.append("No info about opts")
        
    return operators

def filterL2L3Teams(user, teams):
    
    if user in teams["SOC Analyst"]["Users"] or user in teams["SOC Engineer"]["Users"]:
        #print("User is in L2 or L3")
        return False
    else:
        #print("User belongs to L1")
        return True

def getOperatorsInfo(operators_info, teams_info):
    
    for sub in operators_info.keys():
        #print("Subfamily:", sub)
        avg_values = []
        operators = []
        ticket_times = []
        for opt in operators_info[sub].keys():
            #print("Operator:", opt)
            if filterL2L3Teams(opt, teams_info):
                temp = []
                #print("Operator:", opt)
                #print("All tickets", operators_info[sub][opt]["tickets"])
                total_tickets = len(list(operators_info[sub][opt]["tickets"].keys()))
                #print("Number of tickets", total_tickets)
                time_spent = 0
                for t in operators_info[sub][opt]["tickets"].keys():
                    #print("Ticket id", t)
                    #print("Info:", operators_info[sub][opt]["tickets"][t])
                    time_spent += operators_info[sub][opt]["tickets"][t]["diff (sec)"]
                    temp.append(operators_info[sub][opt]["tickets"][t]["diff (sec)"])
                operators_info[sub][opt]["avg"] = round(float(time_spent/total_tickets))
                #print("Avg Time spent", operators_info[sub][opt]["avg"])
                avg_values.append(operators_info[sub][opt]["avg"])
                operators.append(opt.split(',')[0])
                ticket_times.append(temp)
        #print("Operators", operators)
        #print("Ticket times", ticket_times)
        plotBox(sub, operators, ticket_times)
        #print("\n")
        #plotHistogram(sub, operators, avg_values)
            
def plotHistogram(sub, x, y):
    
    fig, axs = plt.subplots(figsize=(40,15))
    sns.set(style="darkgrid")
    sns.barplot(x= x, y= y, alpha=0.9)
    axs.set_title(sub, fontsize=24)
    axs.set_xlabel('Operators', fontsize=18)
    axs.set_ylabel('Average Time (min)', fontsize=18)
    plt.savefig("../../RealDatasetCleaner/Operators/" + sub + ".png", bbox_inches='tight')
# =============================================================================
#     for tick in axs.get_xticklabels():
#         tick.set_rotation(90)
# =============================================================================
      
def plotBox(sub, x, y):
    
    fig, axs = plt.subplots(figsize=(40,15))
    plt.boxplot(y, labels=x) 
    axs.set_title(sub, fontsize=24)
    axs.set_xlabel('Operators', fontsize=18)
    axs.set_ylabel('Average Time (min)', fontsize=18)
    plt.savefig("../../RealDatasetCleaner/Operators/" + sub + ".png", bbox_inches='tight')

def cleanTransitions(ticket_id, subfamily, transitions, summary, timestamps, operators_info):
    
    summary = summary.strip('][')
    #print(summary)
    
    main_field = False
    sub_field = False
    special_field = False
    field = ""
    transitions_description = []

    for i in range(len(summary)):
        ch = summary[i]
        #print("Curr character:", ch)
        
        if not sub_field:
            if not main_field:
                if ch == "'"  or ch == '"':
                    main_field = True
                    #print("\nNormal case")
                elif ch != "," and ch != " " and ch != "'" and ch != '"':
                    special_field = True
                    #print("\nSpecial Case")
            else:
                if i == len(summary) - 1:
                    #print("Main Field: ", field)
                    transitions_description.append(field)
                    main_field = False
                    field = ""
                elif (ch == "'" or ch == '"') and (summary[i+1] == "," and summary[i+2] == " "):
                    #print("Main Field: ", field)
                    transitions_description.append(field)
                    main_field = False
                    field = ""
                    #print("Check next field")
                else:
                    field += ch
                    if field == "Log entry added":
                        sub_field = True
                        main_field = False
                        #print("Subfield started")
        
            if special_field:
                if ch == "," and summary[i+1] == " ":
                    #print("Special Field: ", field)
                    transitions_description.append(field)
                    special_field = False
                    field = ""
                    #print("Check next field")
                else:
                    if ch != ",":
                        field += ch
        else:
            if summary[i+1] == "," and summary[i+2] == " " and summary[i+4] == 'A' and summary[i+5] == 't' and summary[i+6] == 't':   
                transitions_description.append(field)
                #print("Sub Field:", field)
                #print("Sub Field")
                sub_field = False
                field = ""
            elif summary[i+1] == "," and summary[i+2] == " "  and summary[i+4] == 'U' and summary[i+5] == 'p' and summary[i+6] == 'd':   
                transitions_description.append(field)
                #print("Sub Field:", field)
                #print("Sub Field")
                field = ""
            else:
                if field == "":
                    if ch != "," and ch != " " and ch != "'":
                        field += ch
                else:
                    field += ch
                        
    #print("Ticket", ticket_id)
    #print(len(transitions_description))
    #print("Transitions:", transitions)
    #print("Description:", transitions_description)
    #print("Timestamps:", timestamps)
    
    operators = getOperators(ticket_id, subfamily, transitions, transitions_description, timestamps, operators_info)
    print("Operators:", operators)
    #print("Prev:", timestamps)
    trans, description, timestps = removeUnnecessaryTransitions(transitions, transitions_description, timestamps)
    #print("After:", timestps)
    transitions_combined, transitions_updated, description_updated, timestamps_updated = updateTransitions(trans, description, timestps)
        
    while checkTransitions(transitions_updated, description_updated):
        transitions_combined, transitions_updated, description_updated, timestamps_updated = updateTransitions(transitions_updated, description_updated, timestps)
        
    return transitions_combined, transitions_updated, description_updated, timestamps_updated, operators
        
def processTeams(data):
    
    teams_information = {}
    
    for k in data:
        for p in k:
            if p[0] == "TR":
                #print("Main:", p[1])
                transfer_info = p[1].replace("\\n", "")
                transfer_info = transfer_info.replace("Transfer assignee from ", "")
                transfer_info = transfer_info.replace("Transfer Assignee from ", "")
                
                #print("assignee replaced:", transfer_info)
                transfer_info = transfer_info.replace("Transfer group from ", " - ")
                transfer_info = transfer_info.replace("Transfer Group from ", " - ")
                #print("group replaced:", transfer_info)
                transfer_info = transfer_info.split(' - ')
                #print("Transfer info:", transfer_info)
                
                users = [x.strip(" '") for x in transfer_info[0].split(' to ')]
                if len(users) == 1:
                    users = [x for x in users if x]
                #print("Users:", users)
                
                teams = [x.strip("'") for x in transfer_info[1].split(' to ')]
                if len(teams) == 1:
                    teams = [x for x in users if x]
                #print("Teams:", teams)
                #print("\n")
                
                if len(users) and len(teams):
                    for t in range(len(teams)):
                        #print("Curr team", teams[t])
                        if teams[t] not in teams_information.keys():
                            #print("New team:", teams[t])
                            teams_information[teams[t]] = {}
                            teams_information[teams[t]]["Users"] = []
                        if users[t] != "" and users[t] not in teams_information[teams[t]]["Users"]:
                            #if teams[t] == "SOC Analyst" and users[t] == "Herraez Thyaru, Thyaru ":
                                #print("Aqui", transfer_info)
                            teams_information[teams[t]]["Users"].append(users[t])

    #print("Team information:", teams_information)
    return teams_information    

def analyseDataset(data):
    
    transition_states = {}
    transitions_info = {}
    operators_info = {}
    
    transitions_combined = []
    transitions_treated = []
    timestamps_treated = []
    duration_combined = []
    wait_time = []
    l1_time = []
    l2_time = []
    l3_time = []
    team_operators = []
        
    for index, row in data.iterrows():
        ticket_id =  row['ID']
        print("Ticket id:", ticket_id)
        subfamily = row['Subfamily']
        transitions = row['Transitions']
        #print("Transition", transitions)
        timestamps = row['operator_action_timestamps']
        #print("Timestamps", timestamps)
        #print("Timestamps type", type(timestamps))
        description = row['description']
        
        transitions_comb, transitions_updated, description_updated, timestamps_updated, operators = cleanTransitions(ticket_id, subfamily, transitions, description, timestamps, operators_info)
        transitions_duration_comb, teams_solving_time = processTransitionsDuration(transitions_updated, description_updated, timestamps_updated)
        transitions_combined.append(transitions_comb)
        transitions_treated.append(transitions_updated)
        timestamps_treated.append(timestamps_updated)
        duration_combined.append(transitions_duration_comb)
        l1_time.append(teams_solving_time[0])
        l2_time.append(teams_solving_time[1])
        l3_time.append(teams_solving_time[2])
        team_operators.append(operators)
        
        getNodesInfo(subfamily, transitions, transitions_info)
        
        #print("Discovered date:", row['discovered_date'])
        #print("Timestamp 0:", timestamps_updated[0])
        #wait_time.append(calculateDiffDate(row['discovered_date'], timestamps_updated[0]))
        
        for i in range(len(transitions)-1):
            pair = (transitions[i], transitions[i+1])
            #print('Pair: ', pair)
            
            if subfamily not in transition_states.keys():
                transition_states[subfamily] = {}
                
            if pair not in transition_states[subfamily].keys():
                transition_states[subfamily][pair] = 1
            else:
                transition_states[subfamily][pair] += 1

    #print("All", transitions_info)
    #drawGraph(transitions_info, transitions_treated)
    #print("All operators", operators_info)
    
    teams_info = processTeams(transitions_combined)
    print(teams_info)
    #getOperatorsInfo(operators_info, teams_info)
    
    data["Operators"] = team_operators
    data["Transitions Updated"] = transitions_treated
    data["time_stamp_updated_converted"] = timestamps_treated
    data["Timestamps updated converted"] = data["time_stamp_updated_converted"].apply(convertTimeStamps)
    data['Transitions Updated (comments)'] = transitions_combined
    data["Resolution Time (min)"] = data["Timestamps updated converted"].apply(calculateTotalTime)
    #data["Wait Time (min)"] = wait_time
    #data["L1 (min)"] = l1_time
    #data["L2 (min)"] = l2_time
    #data["L3 (min)"] = l3_time
    data["Transitions Duration"] = duration_combined
    
    data = data[data['Resolution Time (min)'] >= 0]
    
    #family_distribution = data.groupby(['Subfamily', data['Transitions Updated'].map(tuple)]).size().reset_index(name="count")
    transitions_info = data.groupby(['Subfamily', data['Transitions Updated'].map(tuple)]).agg(count = ('Transitions Updated', 'size'), average_time = ('Resolution Time (min)', 'mean')).reset_index()
    transitions_info = transitions_info.round(0)
    transitions_info = transitions_info[transitions_info['count'] >= 5]
    #print(mean)
    transitions_info.to_csv("../../RealDatasetCleaner/NoResilient/transitions_info.csv", sep=";", index = False)
    #os.system('start excel.exe ../RealDatasetCleaner/Resilient/transitions_info.csv')

    #print(family_distribution[family_distribution['Subfamily'] == 'FW-003'])
    #print(family_distribution)
    #print("type", type(family_distribution))

    return data

def encondeTransitions(data):
    
    all_states = []
    
    for l in data['Transitions Updated']:
        for state in l:
            if state not in all_states:
                all_states.append(state)
    
    #print(all_states)
    label_encoder = LabelEncoder()
    integer_encoded = label_encoder.fit_transform(all_states)
    #print(integer_encoded)
    mapping = dict(zip(label_encoder.classes_, range(len(label_encoder.classes_))))
    
    for i in mapping:
        mapping[i] += 1
    #print(mapping)
    
    transition_list_encoded = []
    transitions_encoded = []
    transitions_encoded_occurences = []
    transitions_list_encoded_occurences = []
    
    for l in data['Transitions Updated']:
        #print("Transition", l)
        for state in l:
            #print("State")
            transitions_encoded.append(mapping[state])
            #if not (any(state in i for i in transitions_encoded_occurences)):
            transitions_encoded_occurences.append((state, l.count(state)))
            
            #print("List status", transitions_encoded_occurences)
        #print("Transition encoded", transitions_encoded)
        transition_list_encoded.append(list(transitions_encoded))
        transitions_list_encoded_occurences.append(list(transitions_encoded_occurences))
        transitions_encoded = []
        transitions_encoded_occurences = []
        
    #print(transition_list_encoded)
    #print(transitions_encoded_occurences)
        
    #print("Max length:", Utils.findMaxLength(transition_list_encoded))
        
    #X = np.array([[1, 2], [1, 4], [1, 0], [4, 2], [4, 4], [4, 0]])
    normalized = np.zeros([len(transition_list_encoded),len(max(transition_list_encoded,key = lambda x: len(x)))])
    for i,j in enumerate(transition_list_encoded):
        normalized[i][0:len(j)] = j
    #print("Aqui", normalized)
    
    normalized = normalized.astype(int)
    transitions_normalized = list()
    for row in normalized:
        transitions_normalized.append(row.tolist())
        
    #print(normalized)
# =============================================================================
#     plt.rcParams["figure.figsize"] = [7.50, 3.50]
#     plt.rcParams["figure.autolayout"] = True
#     fig = plt.figure()
#     ax = fig.add_subplot(1, 1, 1)
#     Z = sch.linkage(normalized, method='ward')
#     print(Z)
#     dendrogram = sch.dendrogram(Z, leaf_rotation = 90., leaf_font_size = 12., ax = ax)
#     plt.show()
# =============================================================================
    
    #cluster = AgglomerativeClustering(n_clusters=5, affinity='euclidean', linkage='ward')
    #cluster.fit(normalized)
    #print(cluster.labels_)
    
    #data["Transitions count"] = transitions_list_encoded_occurences
    data["Transitions encoded"] = transition_list_encoded
    #data.insert(loc=10, column='Transitions encoded', value=transition_list_encoded)
    #data["Transitions normalized"] = transitions_normalized
    #data["clusters"] = cluster.labels_
    
    family_distribution = data.groupby(['Subfamily', data['Transitions encoded'].map(tuple)]).size().reset_index(name="count")
    #family_distribution = data.groupby(['Subfamily', 'Transitions normalized']).size().reset_index(name="count")
    #print(family_distribution[family_distribution['count'] > 2])
    #print(family_distribution)
    #print(family_distribution[family_distribution['Subfamily'] == 'FW-003'])
    
    family_dict = {}
    for index, row in family_distribution.iterrows():
        subfamily = row['Subfamily']
        transitions = row['Transitions encoded']
        count = row['count']
        if subfamily not in family_dict.keys():
            family_dict[subfamily] = {}
        
        family_dict[subfamily][transitions] = count
        
        
    #print(family_dict)
    
    return data
    

print("\014")
Utils.closeExcel()
os.chdir("../../")
pd.set_option("display.max_rows", None, "display.max_columns", None)

Utils.resetOutputFolder("../../RealDatasetCleaner/Subfamilies")
Utils.resetOutputFolder("../../RealDatasetCleaner/Operators")

#df = pd.read_csv('../RealDatasetCleaner/temp.csv', sep=";", index_col=0)
df = pd.read_excel(r'../../RealDatasetCleaner/NoResilient/RealDataset.xlsx')
#print(df.columns)
keep_col = ['ref_num', 'client_name', 'FAMILY', 'alert_code', 'open_date', 'close_date', 'priority', 'operator_action_types', 'operator_action_descriptions', 'operator_action_timestamps'] 

df = df[keep_col]
df = df.rename(columns={'ref_num': 'ID', 
                   'open_date': 'discovered_date',
                   'close_date': 'end_date', 
                   'FAMILY': 'Family',
                   'client_name': 'Client',
                   'alert_code': 'Subfamily',
                   'operator_action_descriptions': 'description',
                   'operator_action_types': 'Transitions'
                   })
#print(df.columns)

df = cleanDataset(df)    
#datasetToFile(df, '../../RealDatasetCleaner/NoResilient/RealDataset_updated')
df = analyseDataset(df)
#df = encondeTransitions(df)

#df = df.drop(['Status', "time_stamp_updated_converted", "Transitions encoded", "Resolution Time (min)"], axis = 1)
#df.drop(list(df.filter(regex = 'Unnamed')), axis = 1, inplace = True)
#df = df.drop(['description', 'qradar_id', 'description (actions + comments by operators)', 'org_id', 'resilient_incident_id'], axis = 1)

df.to_csv("../../RealDatasetCleaner/NoResilient/real_dataset_updated_cleaned.csv", sep=";", index = False)

#os.system('start excel.exe ../RealDatasetCleaner/Resilient/realDataset_updated_cleaned.csv')