# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 15:38:12 2020

@author: Leonado Ferreira
@goal: Main class of the project where the tickets are created and handled by the operators
"""

from Code.Variables import Variables
from Code.Utils import Utils

import pandas as pd
import random
import string
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import calendar
import time
import _pickle as cPickle

class TicketGenerator:    

    def __init__(self):
        # Dictionaries and basic data
        self.family_pool = {}
        self.subfamily_pool = {}
        self.subfamily_actions_taken = {}
        self.family_time_probability_pool = {}
        self.family_week_probability_pool = {}
        self.family_month_probability_pool = {}
        self.family_steps_pool = {}
        self.analysts_info = {}
        self.analysts_availability = {}
        self.tickets_info = {}
        self.tickets_replicated = {}
        self.subfamily_analysts_action = {}
        self.family_area = {}
        self.clients_info = {}
        self.tickets_inheritance = {}

        # List
        self.ticket_ids = []
        self.ticket_priority = []
        self.ticket_escalate = []
        self.similar_tickets = [] 
        self.coord_tickets = [] 
        self.ticket_inherited_elapsed_time = [] 
        self.clients = []
        self.locations = []
        self.locations_time = []
        self.locations_time_diff = []
        self.locations_time_day = []
        self.locations_time_stage_day = []
        self.locations_time_weekday = []
        self.locations_time_month = []
        self.location_utc_date = []
        self.locations_utc_date_minimized = []
        self.ticket_unfixed_time = []
        self.ticket_timestamps = []
        self.ticket_fixed_time = []
        self.ticket_src_ip = []
        self.ticket_dst_ip = []
        self.ticket_src_port = []
        self.ticket_dst_port = []
        self.alert_area = []
        self.alert_family = []
        self.alert_subfamily = []
        self.alert_subfamily_coordinated = []
        self.alert_subfamily_duration = []
        self.family_actions = []
        self.subfamily_actions = []
        self.ticket_teams = []
        self.ticket_teams_users = []
        self.all_analysts = []
        self.analysts_actions = []
        self.analysts_actions_status = []
        self.analysts_actions_duration = []
        self.analysts_actions_duration_outlier = []
        self.ticket_duration = []
        self.analysts_available = []
        self.analysts_chosen = []
        self.analysts_chosen_action = []
        self.analysts_chosen_action_status = []
        self.ticket_status = []
        self.ticket_suspicious = []
        self.action_verified = []
        self.alert_outliers = []
        self.alert_shifted = []
        self.user_shifts = []
        self.off_days = []
        self.ticket_id = 0
        
    # Calculates the difference between similar ticket (time in min)
    def getFirstOccurence(self, curr_ticket, first_ticket):
        
        last_occurence = ""
        #curr_ticket_time = datetime.strptime(self.tickets_info[curr_ticket]['unsolved'], '%d-%m-%Y %H:%M:%S')
        curr_ticket_time = self.tickets_info[curr_ticket]['unsolved datetime']
        #first_ticket_time = datetime.strptime(self.tickets_info[first_ticket]['unsolved'], '%d-%m-%Y %H:%M:%S')
        first_ticket_time = self.tickets_info[first_ticket]['unsolved datetime']
        
        time_diff = curr_ticket_time - first_ticket_time

        minutes = round(time_diff.total_seconds() / 60)
        last_occurence = "The same problem happened " + str(minutes) +  " minutes ago"
        self.ticket_inherited_elapsed_time.append(last_occurence)
        
    # Get first user available 
    def getFirstAnalyst(self, team_analysts):
        
        temp = ""
        user = "None"
        for i in team_analysts:
            #print(i)
            user_time = self.getUserEndTime(i)
            #print("User " + str(i) + " ends the treatment " + str(user_time))
            if temp == "":
                temp = user_time
                user = i
            else:
                if temp > user_time:
                    temp = user_time
                    user = i
                    #print("Current first user " + str(i) + " ends the treatment " + temp)
                    
        #print("First user:", user)
        return user
    
    # Get when the user is available
    def getUserEndTime(self, user):

        if self.analysts_availability[user]['ticket endtime'] != "None":
            return self.analysts_availability[user]['ticket endtime']

    # Removes user from Queue
    def removeUserFromQueue(self, user):
        
        for i in self.analysts_info.keys():
            if user in self.analysts_info[i]['queue']:
                #print(user + " was removed from the queue of team " + str(i))
                self.analysts_info[i]['queue'].remove(user)
       
    # Add user to Team Queues
    def addToteamsQueue(self, user):
    
        for team in self.analysts_info.keys():
            for users in Variables.teams_info_pool[team]:
                if user in users:
                    self.analysts_info[team]["queue"].append(user)
                
    # Get client
    def getClient(self):
        
        client_id = random.randint(1, Variables.clients_number)
        client = "Client_" + str(client_id)
        
        return client
            
    # Sort tickets_info
    def sortTickets(self, to_sort):

        #print(to_sort)
        temp_dict = sorted(to_sort.items(), key=lambda x: x[1]['unsolved datetime'])
        ordered_tickets_info = {}
        
        for i in range(len(temp_dict)):
            #print("Aqui",temp_dict[i])
            #temp_id = str(i) 
            temp_id = i 
            ordered_tickets_info[temp_id] = temp_dict[i][1]
        
        #print(ordered_tickets_info)
        self.tickets_info = ordered_tickets_info
        
    # Generates sets of subtechniques for each technique used in the family
    def processActionStep(self, family, step, sub_techniques_range):
        
        init, final, transfer = Utils.getLockedTechniques()
    
        #print("Special Operations:", Variables.actions_checkpoints)
        sub_techniques = []
        self.family_steps_pool[family][step] = {}
        sub_techniques_num = random.randint(sub_techniques_range[0], sub_techniques_range[1])
        #print("Subtechniques number", sub_techniques_num)
        locked_techniques = list(Variables.actions_checkpoints["init_op"].keys()) + list(Variables.actions_checkpoints["end_op"].keys()) + list(Variables.actions_checkpoints["transfer_sub_op"].keys()) + init + final
        #print("Locked techniques", locked_techniques)
        build_subtechniques = True

        if step in locked_techniques:
            if step in Variables.actions_checkpoints["init_op"].keys():
                act_type = "init_op"
                #print("In main init")
            elif step in Variables.actions_checkpoints["end_op"].keys():
                act_type = "end_op"
                #print("In main end")
            else:
                act_type = "transfer_sub_op"
            
            if bool(Variables.actions_checkpoints[act_type][step]):
                #print("Step " + step + " already analysed")
                self.family_steps_pool[family][step] = Variables.actions_checkpoints[act_type][step]
                build_subtechniques = False
# =============================================================================
#         else:
#             print("Step " + step + " is not locked")
# =============================================================================
                
        if build_subtechniques:
            for i in range (sub_techniques_num):
                int_technique = random.randint(0, 255)
                #This will break for negative values -> consider[3:]
                hex_technique = hex(int_technique)[2:]
                #print("sub_techniques state", sub_techniques)
                #print("New technique", hex_technique)
                locked_techniques_pool = sub_techniques + locked_techniques
                    
                while str(hex_technique) in locked_techniques_pool:
                    if Variables.debug:
                        print("The technique: " + str(hex_technique) + " already exists. Try another")
                    int_technique = random.randint(0, 255)
                    hex_technique = hex(int_technique)[2:]
            
                sub_techniques.append(hex_technique)
                #print("Subtechnique accepted", hex_technique)

                step_cost = random.randint(Variables.min_subtechnique_cost, Variables.max_subtechnique_cost)
                multiplier = random.randint(Variables.min_subtechnique_rate, Variables.max_subtechnique_rate)
                self.family_steps_pool[family][step][hex_technique] = int(step_cost * multiplier/100)
            
                if Variables.debug:
                    print("Step cost:", step_cost)
                    print("Multiplier:", multiplier)
                    print("Multiplier converted:", int(step_cost * multiplier/100))
                    print("Result:", self.family_steps_pool[family][step][hex_technique])
        
            #if Variables.debug:
            if step in locked_techniques:
                if not bool(Variables.actions_checkpoints[act_type][step]):
                    #print("Step " + step + " added")
                    Variables.actions_checkpoints[act_type][step] = self.family_steps_pool[family][step]
            
            #print("The step " + str(step) + " has the following techniques: ", self.family_steps_pool[family][step])
            #print("State of locked techniques", Variables.actions_checkpoints)
    
    # Based on probabilities, each technique is assigned a set of subtechniques
    def processAction(self, family, action, sub_techniques_range):
    
        #techniques_used = []
        self.family_steps_pool[family] = {}
        for step in action:
            if Variables.debug:
                print("Step " + str(step) + " is being analysed")
            if step not in self.family_steps_pool[family].keys():
                if Variables.debug:
                    print("Step " + str(step) + " has a group of techniques with the length of " + str(sub_techniques_range))
                self.processActionStep(family, step, sub_techniques_range)
        
    # Generates a random string with specific length
    def randomStringGenerator(self, family, length, techniques_num, sub_techniques_range):
        
        techniques_pool = string.ascii_letters + string.digits    
        #print("\nTechniques pool:", techniques_pool)
    
        init_technique_chosen = random.choice(list(Variables.actions_checkpoints["init_op"].keys()))
        #print("First technique:", init_technique_chosen)
        end_technique_chosen = random.choice(list(Variables.actions_checkpoints["end_op"].keys()))
        #print("Final technique:", end_technique_chosen)
        init, final, transfer = Utils.getLockedTechniques()
        locked = list(Variables.actions_checkpoints["init_op"].keys()) + list(Variables.actions_checkpoints["end_op"].keys()) + list(Variables.actions_checkpoints["transfer_sub_op"].keys()) + init + final
        
        if length > 1:
            techniques_selected = random.sample([tec for tec in techniques_pool if tec not in locked], k = (techniques_num-2))
        else:
            #print("Length less than 2!")
            techniques_selected = random.sample([tec for tec in string.ascii_letters if tec not in locked], k = (techniques_num-2))
            
        if Variables.debug:
            print("Techniques selected: ", techniques_selected)
            print("Techniques num: ", techniques_num)
            print("length: ", length)
    
        action_result = str(init_technique_chosen)
        if length > techniques_num:
            if Variables.debug:
                print("Repetead steps included since length is greater than the number of techniques available")
                middle_actions = random.choice(techniques_selected, k = (length-2))
        else:  
            middle_actions = random.sample(techniques_selected, k = (length-2))
        
        #print("Middle Actions:", middle_actions)
        action_result += ''.join(middle_actions)
        action_result += str(end_technique_chosen)
        
        if Variables.debug:
            print("The family " + str(family) + " has the action: " + str(action_result))
        self.processAction(family, action_result, sub_techniques_range)

        return action_result

    # Fills the family actions and if they are important for outside hours analysis
    def familyActionGenerator(self, family, techniques_num, sub_techniques_range):
    
        #print("Techniques number", techniques_num)
        length_min = 0
        length_max = 0
    
        if techniques_num < 10:
            length_min = random.randint(3,4)
            length_max = random.randint(4,5)
        else:
            length_min = random.randint(2,4)
            length_max = random.randint(5,8)
          
        length = random.randint(length_min, length_max)
        #print("Action Length", length)
        action = self.randomStringGenerator(family, length, techniques_num, sub_techniques_range)
        self.family_pool[family]["action"] = action
        
        if Variables.debug:
            print("Action of each family assigned")
        
        return action
         
    # Gives the duration of a certain action
    def actionDuration(self, family, action, team, user):
        
        sub_method_found = False
        sub_method = ""
        dur = 0
        family_techniques = self.family_steps_pool[family]
        transitions = []
        
        if Variables.debug:
            print("Family", family)
            print("Action:", action)

        for i in range(len(action)):
            ch = action[i]
            if Variables.debug:
                print("Current character: ", ch)
            if ch == "'" and sub_method_found is False:
                sub_method_found = True
                if Variables.debug:
                    print("Sub method is now True")
            elif ch !="'" and sub_method_found is True:
                sub_method = sub_method + ch
                if Variables.debug:
                    print("Sub method keeps growing")
            elif ch == "'" and sub_method_found is True:
               
                #print(Variables.actions_checkpoints["transfer_sub_op"].keys())
                if sub_method in list(Variables.actions_checkpoints["transfer_sub_op"].keys()):
                    subtech_dur = Variables.actions_checkpoints["transfer_sub_op"][sub_method]
                    #print("Last step is a transfer operation")
                else:
                    subtech_dur = [sub[sub_method] for sub in family_techniques.values() if sub_method in sub.keys()][0]
                
                if Variables.debug:
                    print("Family techniques", family_techniques)
                    print("sub method: ", sub_method)
                    print("Sub method ended and is reset")
                    print("Duration:", subtech_dur)
                    
                if user != "None":  
                    speed = float(Variables.analysts_skills[team][user]["speed"])
                    if Variables.debug:
                        print("Sub method", sub_method)
                        print("User", user)
                        print("Speed", speed)
                    
                    ## rounds 
                    step_cost = subtech_dur / speed
                    if step_cost == 0:   
                        print("Step cost", step_cost)
                        step_cost = 1
                        
                    #print("Step cost", step_cost)
                    dur = dur + step_cost
                    transitions.append(step_cost)
                    #print("Duration", int(step_cost))
                else:
                    dur = dur + subtech_dur
                
                sub_method_found = False
                sub_method = ""
        if Variables.debug:
            print("Final Duration: ", dur)
            
        return dur, transitions

    # Creates replicated tickets   
    def replicateTicket(self, list_ids, to_replicated, ticket_id, tickets_ids_to_replicate, pending_replicated_tickets, replicated_ids, reason):                                

        list_ids.insert(ticket_id, ticket_id)
        list_ids = Utils.updateIDs(list_ids, ticket_id)
        
        pending_replicated_tickets[ticket_id] = to_replicated
        pending_replicated_tickets[ticket_id]["id"] = ticket_id
        #new_date = datetime.strptime(to_replicated["fixed"], '%d-%m-%Y %H:%M:%S')
        new_date = Utils.convertStrToDatetime(to_replicated["fixed"])
        pending_replicated_tickets[ticket_id]["unsolved"] = to_replicated["fixed"]
        pending_replicated_tickets[ticket_id]["unsolved datetime"] = new_date
        pending_replicated_tickets[ticket_id]["time min"] = '{:02d}:{:02d}:{:02d}'.format(new_date.hour, new_date.minute, new_date.second)
        pending_replicated_tickets[ticket_id]["day"] = calendar.day_name[new_date.weekday()]
        pending_replicated_tickets[ticket_id]["month"] = calendar.month_name[new_date.month]
        pending_replicated_tickets[ticket_id]["allocated"] = ""
        pending_replicated_tickets[ticket_id]["fixed"] = "" 
        pending_replicated_tickets[ticket_id]["replicated from"] = ticket_id - 1
        pending_replicated_tickets[ticket_id]["duration"] = ""
        pending_replicated_tickets[ticket_id]["duration with outlier"] = ""
        pending_replicated_tickets[ticket_id]["shifted"] = False
        pending_replicated_tickets[ticket_id]["reason"] = reason
        del pending_replicated_tickets[ticket_id]["analysts available"]
        del pending_replicated_tickets[ticket_id]["status"]
        del pending_replicated_tickets[ticket_id]["distance"]
        del pending_replicated_tickets[ticket_id]["solutions status"]
        del pending_replicated_tickets[ticket_id]["solutions available"]
        del pending_replicated_tickets[ticket_id]["analyst"]
        del pending_replicated_tickets[ticket_id]["action"]
        del pending_replicated_tickets[ticket_id]["action changes"]
        del pending_replicated_tickets[ticket_id]['analysts working'] 
        
        if "similar" in pending_replicated_tickets[ticket_id].keys() and "similar ids" in pending_replicated_tickets[ticket_id].keys():
            del pending_replicated_tickets[ticket_id]["similar"]
            del pending_replicated_tickets[ticket_id]["similar ids"]
        
        teams = list(Variables.teams_info_pool.keys())
        index = teams.index(pending_replicated_tickets[ticket_id]["team"])

        if index <= 2:
            next_team = teams[index + 1]            
            pending_replicated_tickets[ticket_id]["team"] = next_team

            if next_team == "L4":
                pending_replicated_tickets[ticket_id]["escalate"] = False
            else:
                #print("Ticket will escalate")
                #print("Next team", next_team)
                pending_replicated_tickets[ticket_id]["escalate"] = random.choices([True, False], weights=[((Variables.escalate_rate_percentage/(index + 1))/100), 1 - ((Variables.escalate_rate_percentage/(index + 1))/100)], k = 1)[0]  
        
        curr_team = pending_replicated_tickets[ticket_id]["team"]

        #pending_replicated_tickets_ids = sorted(pending_replicated_tickets, key = lambda x: pending_replicated_tickets[x]["unsolved datetime"])
        pending_replicated_tickets_ids = Utils.sortReplicatedIDs(ticket_id, new_date, replicated_ids, pending_replicated_tickets, True)
        self.allAnalysts(curr_team, Variables.teams_info_pool[curr_team], pending_replicated_tickets[ticket_id]["time min"], pending_replicated_tickets[ticket_id]["family"], pending_replicated_tickets[ticket_id]["subfamily"], ticket_id, pending_replicated_tickets[ticket_id]["unsolved"], pending_replicated_tickets, False)
        #print("Replicated ticket:", pending_replicated_tickets[ticket_id])
        
        return list_ids, pending_replicated_tickets_ids

    # Updates the list of similar ticket ids for each ticket
    def updateSimilarIDS(self, i, tickets_info, number_replicated_tickets):
    
        if isinstance(tickets_info[i]["similar ids"], list):

            temp_number = cPickle.loads(cPickle.dumps(number_replicated_tickets))
            similar_tickets = cPickle.loads(cPickle.dumps(tickets_info[i]["similar ids"]))
            similar_tickets_inverted = similar_tickets
            similar_tickets_inverted.reverse()
            #print("Similar tickets", similar_tickets)
            #print("Similar tickets inverted", similar_tickets_inverted)
            
            similar_fixed = []
            ids_mapping = {}
            n_replicated = 0
            for l in range(len(similar_tickets_inverted)):
                #print("Prev Similar analysed:", similar_tickets[l])
                curr_ticket = similar_tickets[l] + temp_number
                #print("After Similar analysed:", curr_ticket)
                diff = i - curr_ticket
                n_replicated = 0
                temp = i-1
                while diff > 0:
                    #print("K", temp)
                    if "replicated from" in tickets_info[temp].keys(): #and (k not in analysed):
                        #print("replicated found")
                        #temp_number -=1
                        n_replicated += 1
                    else:
                        diff -= 1
                    #print("Curr diff:", diff)
                    temp = temp - 1
                ids_mapping[similar_tickets[l]] = curr_ticket - n_replicated
                similar_fixed.append(curr_ticket - n_replicated)
                #print("Element added:", curr_ticket - n_replicated)

            similar_fixed.reverse()
            #print("Result:", similar_fixed)
            tickets_info[i]["similar"] = similar_fixed
            tickets_info[i]["similar ids"] = similar_fixed  
            
            if isinstance(tickets_info[i]["coordinated"], list):
                coordinated_tickets = cPickle.loads(cPickle.dumps(tickets_info[i]["coordinated"]))
                #print("Coordinated list found:", coordinated_tickets)
                coordinated_fixed = []
                for p in coordinated_tickets:
                    #print("P:", p)
                    coordinated_fixed.append(ids_mapping[p])
                #print("Coordinated updated:", coordinated_fixed)
                tickets_info[i]["coordinated"] = coordinated_fixed

    # Check if replication is possible
    def checkReplication(self, team, i, list_ids, original_ticket, n_replicated_tickets, tickets_ids_to_replicate, pending_replicated_tickets, pending_replicated_tickets_ids, reason):
    
        if team != "L4":
            n_replicated_tickets += 1
            list_ids, pending_replicated_tickets_ids = self.replicateTicket(list_ids, original_ticket, i + 1, tickets_ids_to_replicate, pending_replicated_tickets, pending_replicated_tickets_ids, reason)
        else:
            print("Can't be replicated because it is already on the top team")
            
        return n_replicated_tickets, pending_replicated_tickets_ids
    
    # Finds the Similar and Coordinated Tickets
    def findSimilarAndCoordinatedTickets(self, thread, weight):
        
        ids_to_replicate = []
        reasons_for_replication = []
        tickets_inheritance = {}
        
        for i in range(len(self.tickets_info)):
            #print("Ticket id", i)
            team = self.tickets_info[i]["team"]
            subfamily = self.tickets_info[i]["subfamily"]
            client = self.tickets_info[i]["client"]
            country = self.tickets_info[i]["country"]
            #time_raised = self.tickets_info[i]["unsolved"]
            escalated_status = self.tickets_info[i]["escalate"]
            datetime_raised = self.tickets_info[i]["unsolved datetime"] 

            self.tickets_info[i]["id"] = i
            
            if escalated_status:
                #print("escalated")
                self.tickets_info[i]["similar"] = "---"
                self.tickets_info[i]["coordinated"] = "---"
                #print("Ticket " + str(i) + " with id " + str(curr_id) + " must be replicated due to escalation status")
                if team != "L4":
                    ids_to_replicate.append(i)
                    reasons_for_replication.append("Escalation")
                else:
                    print("Can't be replicated because it is already on the top team")        
            else:
                if client not in tickets_inheritance:
                    tickets_inheritance[client] = {}
            
                if subfamily not in tickets_inheritance[client]:
                    tickets_inheritance[client][subfamily] = {}
                    tickets_inheritance[client][subfamily]["start"] = datetime_raised
                    tickets_inheritance[client][subfamily]["end"] = datetime_raised + timedelta(minutes = self.subfamily_pool[subfamily]["timerange"])
                    tickets_inheritance[client][subfamily]["curr counter"] = 1
                    tickets_inheritance[client][subfamily]["similar"] = []
                    tickets_inheritance[client][subfamily]["similar"].append(i)
                    tickets_inheritance[client][subfamily]["similar ids"] = []
                    tickets_inheritance[client][subfamily]["similar ids"].append(i)
                    self.tickets_info[i]["similar"] = "---"
                    self.tickets_info[i]["coordinated"] = "---"
                else:
                    if tickets_inheritance[client][subfamily]["start"] <= datetime_raised <= tickets_inheritance[client][subfamily]["end"]:
                        self.tickets_info[i]["similar"] = cPickle.loads(cPickle.dumps(tickets_inheritance[client][subfamily]["similar"]))
                        self.tickets_info[i]["similar ids"] = cPickle.loads(cPickle.dumps(tickets_inheritance[client][subfamily]["similar ids"]))
                    
                        coordinated_tickets = []
                        for l in tickets_inheritance[client][subfamily]["similar"]:
                            if country == self.tickets_info[l]["country"]:
                                coordinated_tickets.append(self.tickets_info[l]["id"])
                    
                        if not coordinated_tickets:
                            self.tickets_info[i]["coordinated"] = "---"
                        else:
                            self.tickets_info[i]["coordinated"] = coordinated_tickets
                        
                        tickets_inheritance[client][subfamily]["similar"].append(i)
                        tickets_inheritance[client][subfamily]["similar ids"].append(i)
                        tickets_inheritance[client][subfamily]["curr counter"] += 1
                    else:
                        tickets_inheritance[client][subfamily]["start"] = datetime_raised
                        tickets_inheritance[client][subfamily]["end"] = datetime_raised + timedelta(minutes = self.subfamily_pool[subfamily]["timerange"])
                        tickets_inheritance[client][subfamily]["curr counter"] = 1 
                        tickets_inheritance[client][subfamily]["curr ticket"] = i
                        tickets_inheritance[client][subfamily]["similar"] = []
                        tickets_inheritance[client][subfamily]["similar"].append(i)
                        tickets_inheritance[client][subfamily]["similar ids"] = []
                        tickets_inheritance[client][subfamily]["similar ids"].append(i)
                        self.tickets_info[i]["similar"] = "---"
                        self.tickets_info[i]["coordinated"] = "---"    
 
                    if tickets_inheritance[client][subfamily]["curr counter"] == self.subfamily_pool[subfamily]["max counter"]:
                        #print("Ticket " + str(i) + " with id " + str(i) + " must be replicated due to max similarity")
                        ids_to_replicate.append(i)
                        reasons_for_replication.append("Max similarity")
                        del tickets_inheritance[client][subfamily]

        replication_tickets = list(zip(ids_to_replicate,reasons_for_replication))
        print("Number of replicated tickets:", len(replication_tickets))
        
        return replication_tickets

    # Main action generator
    def actionsGenerator(self, thread, weight, techniques_num, sub_techniques_num_min, sub_techniques_num_max):

        for i in self.tickets_info.keys():
            #print("Ticket id", i)
            if Variables.debug:
                print("\nActions Generation. Ticket id: ", i)
        
            family = self.tickets_info[i]["family"]
            subfamily = self.tickets_info[i]["subfamily"]
            sub_techniques_range = []
            sub_techniques_range.append(sub_techniques_num_min)
            sub_techniques_range.append(sub_techniques_num_max)
            self.actionChecker(family, subfamily, techniques_num, sub_techniques_range)

        if Variables.debug:  
            print("All actions assigned")

    # Checks if a subfamily has an already allocated. If not it generates a new one
    def actionChecker(self, family, subfamily, techniques_num, sub_techniques_range):  
    
        family_action = ""
        if "action" not in self.family_pool[family].keys():
            if Variables.debug:
                print("Family " + str(family) + " doesn't have an action")
            family_action = self.familyActionGenerator(family, techniques_num, sub_techniques_range)
        else:
            if Variables.debug:
                print("Family " + str(family) + " action already exists")
            family_action = self.family_pool[family]["action"]

        #print("Aqui", self.subfamily_pool)
        
        if subfamily in self.subfamily_pool:
            if "action" in self.subfamily_pool[subfamily].keys():
                #action = self.subfamily_pool[sub]["action"]
                if Variables.debug:
                    print("Sub action of " + str(subfamily) + " aldready exists")
            else:
                if Variables.debug:  
                    print("Sub action of " + str(subfamily) + " doesn't exist")
                self.subfamilyActionBuild(family, subfamily, family_action)
            
    # Build subfamily action
    def subfamilyActionBuild(self, family, subfamily, action):
        
        if Variables.debug:
            print("Special Operations:", Variables.actions_checkpoints)
            print("Generate action for the subfamily")
            print("Family: " + str(family))
            print("Subfamily: " + str(subfamily))
            print("Family Action: " + str(action))
    
        updated_action = ""
        if Variables.debug:
            print("Before converting: ", str(action)) 
        for i in range(len(action)):
            ch = action[i]
            if ch in self.family_steps_pool[family].keys() and self.family_steps_pool[family][ch] != "None":
                if Variables.debug:
                    print("Step " + str(ch) + " has techniques to replace with.") 
                transformations = list(self.family_steps_pool[family][ch].keys())

                if Variables.debug:
                    print("Transformations available: ", list(transformations))
                new_ch = "'" + str(random.choices(transformations, k = 1)[0]) + "'"

                if Variables.debug:
                    print("Step " + str(ch) + " will be replace by " + str(new_ch)) 
                updated_action = updated_action + new_ch
            else:
                updated_action =  updated_action + ch
    
        if Variables.debug:
            print("After converting: ", str(updated_action)) 
 
        self.subfamily_pool[subfamily]["action"] = updated_action 

    # Assigns the teams to each ticket (teams take care of x% of the subfamilies)
    def teamsAssignment(self, thread, weight):

        Utils.teamsDivider(self.subfamily_pool)

        for i in self.tickets_info.keys():
            #print("Ticket id", i)
            family = self.tickets_info[i]["family"]
            subfamily = self.tickets_info[i]["subfamily"]
            utc_complete = self.tickets_info[i]["unsolved"]
            utc_min = self.tickets_info[i]["time min"]
            #utc_localized = self.tickets_info[i]["local time"]
            self.tickets_info[i]['team'] = self.subfamily_pool[subfamily]["team"]   
            #Assigns the team to each ticket
            self.teamBuild(subfamily, family, utc_min, i, utc_complete)

        if Variables.debug:
            print("All tickets have teams assigned")
    
    # Generates the teams and allocates the tickets to them
    def teamBuild(self, subfamily, family, ticket_time, ticket_id, utc_complete):
    
        if Variables.debug:
            print("Family: " + str(family))
            print("Subfamily: " + str(family))
            print("Ticket Time minimized: " + str(ticket_time))
        
        assigned_team = self.tickets_info[ticket_id]['team']
        
        if assigned_team == "L4":
            self.ticket_priority.append(Variables.priority_levels[3])
            if self.tickets_info[ticket_id]['escalate']:
                self.tickets_info[ticket_id]['escalate'] = False
                #print("Can't escalate since L4 is the top team!")
        elif assigned_team == "L3":
            self.ticket_priority.append(Variables.priority_levels[2])
        elif assigned_team == "L2":
            self.ticket_priority.append(Variables.priority_levels[1])
        else:
            self.ticket_priority.append(Variables.priority_levels[0])

        if Variables.debug:
            print("The assigned team was " + str(assigned_team))
    
        team_users = Variables.teams_info_pool[assigned_team]
        
        self.allAnalysts(assigned_team, team_users, ticket_time, family, subfamily, ticket_id, utc_complete, self.tickets_info, False)

    # Get all the analysts available to fix a ticket
    def allAnalysts(self, team, team_users, ticket_time, family, subfamily, ticket_id, utc_complete, tickets_info, debug):

        analysts = {}
        
        ticket_shift = Utils.getTicketShift(ticket_time)
        #time_datetime = datetime.strptime(utc_complete, '%d-%m-%Y %H:%M:%S')
        time_datetime = Utils.convertStrToDatetime(utc_complete)
        ticket_day = calendar.day_name[time_datetime.weekday()]
        shifts_ordered = Utils.getAnalystsNextShift(ticket_time, Variables.shifts)
        if debug:
            print("Ticket id:", ticket_id)
            print("Ticket date:", utc_complete)
            print("Shifts ordered:", shifts_ordered)
            print("Ticket day", ticket_day)
            print("Team:", team)
            print("Team users:", team_users)
            
        #Verifies if there are any analysts available when the ticket is raised
        for shifts in range(len(shifts_ordered)):
            if debug:
                print("Shift:", shifts_ordered[shifts])
            for i in team_users:
                user_shift = self.analysts_info[team][i]['shift']
                if user_shift == shifts_ordered[shifts]:
                    if debug:
                        print("User:", i)
                        print("User shift:", user_shift)
                        print("Off days:", self.analysts_info[team][i]['days off'])
                        print("Ticket day", ticket_day)
                        print("Off days:", self.analysts_info[team][i]['days off'])
                    if ticket_day not in self.analysts_info[team][i]['days off']:
                        if user_shift not in analysts:
                            analysts[user_shift] = []
                        if i not in analysts[user_shift]:
                            analysts[user_shift].append(i)
                    if debug:
                        print("analysts shift:", analysts)
            #print("Check next shift")
            if shifts < len(shifts_ordered) - 1:
                if shifts_ordered[shifts + 1] == 0:
                    time_datetime = time_datetime + timedelta(1, 0, 0, 0)
                    ticket_day = calendar.day_name[time_datetime.weekday()]
                    if debug:
                        print("Next Ticket day", ticket_day)
                
        # All shifts occupied option, guarantees there is always someone on the ticket shift (By Default is True). Unless off days contradicts
        tickets_info[ticket_id]['analysts working'] = analysts
        
    # Checks which analysts are available in the next day
    def checkAnalystsNextDay(self, ticket_id, ticket_date, ticket_time, family, subfamily, team, shift, outlier):
        
        print("Ticket Weekday:", str(calendar.day_name[ticket_date.weekday()]))
        res = ticket_date + timedelta(1)
        next_ticket_day = calendar.day_name[res.weekday()]
        print("Next Ticket Weekday:", str(next_ticket_day))
        
        shifts_ordered = Utils.getAnalystsNextShift(ticket_time, Variables.shifts)
        #print("Shifts ordered:", shifts_ordered)
        team_users = Variables.teams_info_pool[team]

        for shifts in range(len(shifts_ordered)):
            print("Shift:", shifts_ordered[shifts])
            users_available = []
            analyst_sol = []
            analyst_sta = []
            for i in team_users:
                user_shift = self.analysts_info[team][i]['shift']
                if user_shift == shifts_ordered[shifts]:
                    #print("User:", i)
                    #print("User shift:", user_shift)
                    #print("Off days:", self.analysts_info[team][i]['days off'])
                    if next_ticket_day not in self.analysts_info[team][i]['days off']:
                        users_available.append(i)
                        analyst_solution, analyst_status, valid_user = self.checkRepeatedAnalystAction(family, subfamily, team, i, ticket_id, ticket_date, outlier, False)
                        analyst_sol.append(analyst_solution)
                        analyst_sta.append(analyst_status)
            #print("Check Next shift")
            if shifts < len(shifts_ordered) - 1:
                if shifts_ordered[shifts + 1] == 0:
                    time_datetime = res + timedelta(1, 0, 0, 0)
                    next_ticket_day = calendar.day_name[time_datetime.weekday()]
                        
            if users_available:
                break

        print("Analysts available:", users_available)
        #print("Analysts solutions:", analyst_sol)
        #print("Analysts solutions status:", analyst_sta)
        return users_available, analyst_sol, analyst_sta
    
    # Get analysts form current or next shift
    def getAnalysts(self, ticket):
        
        curr_analysts = []
        
        if (ticket['analysts in shift'] == "No users available. Check next shift!") or (ticket['analysts in shift'] == "Time to fix will surpass the analyst's maximum shift!"):
            #ticket['analysts available'] = ticket['analysts next shift']
            print("Users are from the next shift")
            curr_analysts = ticket['analysts next shift']
        else:
            #ticket['analysts available'] = ticket['analysts in shift']
            print("Users are from the same shift of the ticket")
            curr_analysts = ticket['analysts in shift']
            
        return curr_analysts

    # Checks if analyst action surpasses their shift
    def checkAnalyst(self, ticket_date, subfamily, member, action_duration, outlier):
        
        #print("Date considered:", ticket_date)
        if outlier:
            #print("Outlier")
            action_duration = action_duration + Variables.outlier_cost * action_duration
        else:
            action_duration = action_duration
         
        date_considered = ticket_date
        if not self.analysts_availability[member]['free']:
            #print("Member is occupied:", self.analysts_availability[member]['ticket endtime'])
            #user_end = datetime.strptime(self.analysts_availability[member]['ticket endtime'], '%d-%m-%Y %H:%M:%S')
            #considered_date = datetime.strptime(date_considered, '%d-%m-%Y %H:%M:%S')
            if self.analysts_availability[member]['ticket endtime'] > ticket_date:
                date_considered = self.analysts_availability[member]['ticket endtime']
                #print("Date Superior " + str(date_considered) + " dur - " + str(action_duration))
            
        if not Utils.checkNearNextShiftAction(date_considered, action_duration):
            #print(member + " is ok " + str(action_duration))
            user_status = True
        else:
            #if date_considered != ticket_date:
            #    print("Dates were changed:", date_considered)
            user_status = False
            #print(member + " is surpassing his shift with " +str(action_duration))
            #print("Action duration:", action_duration)
            
            #print("Date", ticket_date)
            
        return user_status
        
    # Verifies if a subfamily already has a member allocated to a ticket with a specific action
    def checkRepeatedAnalystAction(self, family, subfamily, team, member, i, ticket_date, outlier, check_valid_user):

        if Variables.debug:  
            print("Ticket:", i)
            print("Family:", family)
            print("Subfamily:", subfamily)
            print("Analyst:", member)
        analyst_sol = ""
        actions_status = ""
        valid_user = True
    
        # Analyst already solved the family
        if subfamily in self.subfamily_analysts_action.keys() and member in self.subfamily_analysts_action[subfamily].keys():  
            if Variables.debug:  
                print("action with subfamily and member already exists!")
            same_action = random.choices([True, False], weights=[Variables.analyst_same_action_probability, 1 - Variables.analyst_same_action_probability], k=1)[0]
            if same_action:
                analyst_sol =  self.subfamily_analysts_action[subfamily][member]['action']
                if Variables.debug:  
                    print("Member " + member + " is going to use the prev action " + analyst_sol)  
                actions_status = str(member) +  " is using the same action"
            else:
                analyst_sol = Utils.userActionBuild(family, subfamily, team, member, self.subfamily_pool[subfamily]["action"], self.family_steps_pool, Variables.actions_operations, Variables.debug, True)
                if Variables.debug:  
                    print("Member " + member + " is performing a new action:" + analyst_sol)  
                actions_status = str(member) +  " is using a new action"
                
                action_dur, transitions = self.actionDuration(family, analyst_sol, team, member)
                self.subfamily_analysts_action[subfamily][member]["action"] = analyst_sol
                self.subfamily_analysts_action[subfamily][member]['duration'] = action_dur
        else:
            if Variables.debug:  
                print("action with subfamily and member doesn't exists!")
            use_subfamily_action = random.choices([True, False], weights=[Variables.analyst_subfamily_action_probability, 1 - Variables.analyst_subfamily_action_probability], k=1)[0]
            
            #Uses the subfamily action
            if use_subfamily_action:
                analyst_sol = self.subfamily_pool[subfamily]["action"]
                if Variables.debug:  
                    print("Member " + member + " is going to use the subfamily action: " + analyst_sol)
                actions_status = str(member) +  " is using the subfamily action"
            #Creates a new action based on the family
            else:
                analyst_sol = Utils.userActionBuild(family, subfamily, team, member, self.subfamily_pool[subfamily]["action"], self.family_steps_pool, Variables.actions_operations, Variables.debug, True)

                if Variables.debug:      
                    print("Subfamily action:", self.subfamily_pool[subfamily]["action"])   
                    print("Member " + member + " is going to use a new action: " + analyst_sol)
                actions_status = str(member) +  " is going to use new action"
                       
                #action_dur, transitions = self.actionDuration(family, analyst_sol, team, member)
                
            action_dur, transitions = self.actionDuration(family, analyst_sol, team, member)
            
            if subfamily in self.subfamily_analysts_action.keys():
                self.subfamily_analysts_action[subfamily][member] = {}
                self.subfamily_analysts_action[subfamily][member]["action"] = analyst_sol
                self.subfamily_analysts_action[subfamily][member]['duration'] = action_dur
            else:
                self.subfamily_analysts_action[subfamily] = {}
                self.subfamily_analysts_action[subfamily][member] = {}
                self.subfamily_analysts_action[subfamily][member]["action"] = analyst_sol
                self.subfamily_analysts_action[subfamily][member]['duration'] = action_dur
                
        if check_valid_user:
            act_dur = self.subfamily_analysts_action[subfamily][member]['duration'] 
            valid_user = self.checkAnalyst(ticket_date, subfamily, member, act_dur, outlier)
        
        return analyst_sol, actions_status, valid_user
    
    # Get the first pending replicated ticket (they are ordered when one is added to the queue)
    def getEarliestReplicatedTicket(self, pending_tickets_ids, pending_tickets):
              
        #print("Length ids:", len(pending_tickets_ids))
        #print("Pending ids:", pending_tickets_ids)
        #print("length:", len(pending_tickets))
        #print("Pending tickets:", pending_tickets)
        best_key = pending_tickets_ids[0]

        return best_key
    
    # Assigns the action and user for each ticket
    def analystsAssignment(self, thread, similar_escalated_tickets, weight):

        list_ids = list(self.tickets_info.keys())
        temp_dict = cPickle.loads(cPickle.dumps(self.tickets_info))
        #print("Geral", temp_dict)
        
        n_replicated_tickets = 0
        i = 0
        original_dict_idx = 0
        mode = 0

        tickets_info_updated = {}
        tickets_info_updated[i] = temp_dict[i]
        pending_replicated_tickets = {}
        pending_replicated_tickets_ids = []
        #print("Reading from tickets_info. Index:", i - n_replicated_tickets)
        tickets_ids_to_replicate = [k[0] for k in similar_escalated_tickets]
        #print("Tickets to replicate:", tickets_ids_to_replicate)
        
        
        while i < len(list_ids): 
            #print("Original ids to replicate:", tickets_ids_to_replicate)
            #print("Ticket id:", i)
            #print("Original idx:", original_dict_idx)
            #print("Replicated tickets number:", n_replicated_tickets)
            
            family = tickets_info_updated[i]["family"]
            subfamily = tickets_info_updated[i]["subfamily"]
            datetime_raised = tickets_info_updated[i]["unsolved datetime"]
            #print("Week day:", tickets_info_updated[i]['day'])
            datetime_min = tickets_info_updated[i]['time min']
            team = tickets_info_updated[i]["team"]
            outlier = tickets_info_updated[i]["outlier"]
            
            tickets_info_updated[i]["solutions available"] = []
            tickets_info_updated[i]["solutions status"] = []
            tickets_info_updated[i]["action changes"] = []
            tickets_info_updated[i]["id"] = i
            special = False
            
            if i != 0:
                #print("Check for free users...")
                self.freeAnalysts(tickets_info_updated[i]["unsolved datetime"], tickets_info_updated, mode)
            
            #print("Pending tickets size:", len(pending_replicated_tickets))  
            if "similar ids" in tickets_info_updated[i]:
                self.updateSimilarIDS(i, tickets_info_updated, n_replicated_tickets - len(pending_replicated_tickets))     
                
            ticket_shift = Utils.getTicketShift(datetime_min)
            #print("Ticket shift:", ticket_shift)
                
            # All shifts occupied option, guarantees there is always someone on the ticket shift (By Default is True). Unless off days contradicts
            all_analysts =  tickets_info_updated[i]['analysts working']

            shifts_ordered = Utils.getAnalystsNextShift(datetime_min, Variables.shifts)
            if ticket_shift not in list(all_analysts.keys()):
                #print("Ticket shift " + str(ticket_shift) + " doesn't exist")
                shifts_ordered.remove(ticket_shift)
            #else:
                #print("Ticket shift " + str(ticket_shift) + " exists")

            shifts_updated = []
            for shift in shifts_ordered:
                if shift in list(all_analysts.keys()):
                    #print("Doesn't exist")
                    shifts_updated.append(shift)
            
            #print("Shifts to analyse:", shifts_updated)
            #print("All users:", all_analysts)
            team_analysts_available = []
            temp_date = cPickle.loads(cPickle.dumps(tickets_info_updated[i]["unsolved datetime"]))
            #Get the actions for the analysts available
            for shift_idx in range(len(shifts_updated)):
                #print("Idx:", shifts_updated[shift_idx])
                if (ticket_shift not in shifts_updated) or (shift_idx != 0):
                    if shifts_updated[shift_idx] == 0:
                        temp_date = temp_date.replace(minute = 00, hour = 00, second = 00, year = temp_date.year, month = temp_date.month, day = temp_date.day)
                    elif shifts_updated[shift_idx] == 1:
                        temp_date = temp_date.replace(minute = 00, hour = 8, second = 00, year = temp_date.year, month = temp_date.month, day = temp_date.day)
                    else:
                        temp_date = temp_date.replace(minute = 00, hour = 16, second = 00, year = temp_date.year, month = temp_date.month, day = temp_date.day)
# =============================================================================
#                     print("Updated date:", temp_date)
#                 else:
#                     print("Temp date:", temp_date)
# =============================================================================
                
                team_analysts_to_verify = all_analysts[shifts_updated[shift_idx]]
                #print("The users to verify on shift " + str(shifts_updated[shift_idx])  + " are " + str(team_analysts_to_verify))

                team_analysts_available = []
                for analyst in team_analysts_to_verify: 
                    #analyst_sol, sol_status, sol_dur, valid_user = self.checkRepeatedAnalystAction(family, subfamily, team, analyst, i, datetime_raised, outlier, True)
                    analyst_sol, sol_status, valid_user = self.checkRepeatedAnalystAction(family, subfamily, team, analyst, i, temp_date, outlier, True)
                    if valid_user:
                        team_analysts_available.append(analyst)
                        tickets_info_updated[i]["solutions available"].append(analyst_sol) 
                        tickets_info_updated[i]["solutions status"].append(sol_status) 

                if team_analysts_available:                    
                    #print("Users available:", team_analysts_available)
                    tickets_info_updated[i]["analysts available"] = team_analysts_available
                    temp_date = cPickle.loads(cPickle.dumps(tickets_info_updated[i]["unsolved datetime"]))
                    break
                else:
                    #print("Users actions durations surpass their time shift. Check next shift")
                    tickets_info_updated[i]["solutions available"] = []
                    tickets_info_updated[i]["solutions status"] = []
                    tickets_info_updated[i]["shifted"] = True  
                    tickets_info_updated[i]["jump"] = 0
                    
            if not team_analysts_available:
                print("Ticket id:", i)
                print("Special cases")
                special = False
                tickets_info_updated[i]["shifted"] = True
                tickets_info_updated[i]["jump"] = 1
                #print("Prev users:", all_analysts[shifts_updated[0]])
                temp_users, temp_sol, temp_status = self.checkAnalystsNextDay(i, datetime_raised, datetime_min, family, subfamily, team, ticket_shift, outlier)
                tickets_info_updated[i]["solutions available"] = temp_sol
                tickets_info_updated[i]["solutions status"] = temp_status
                tickets_info_updated[i]["analysts available"] = temp_users
                team_analysts_available = temp_users

            #print("Queue Before:", self.analysts_info[team]["queue"])
            replicate_ticket = self.findBestAnalyst(tickets_info_updated[i], i, datetime_raised, team_analysts_available, mode, team, subfamily, thread, tickets_ids_to_replicate, original_dict_idx, special, 15)
            #print("Queue After:", self.analysts_info[team]["queue"])
            if original_dict_idx in tickets_ids_to_replicate:
                #print("Replication")
                #print("To copy:", temp_dict[original_dict_idx])
                original_ticket = cPickle.loads(cPickle.dumps(temp_dict[original_dict_idx]))
                n_replicated_tickets, pending_replicated_tickets_ids = self.checkReplication(team, i, list_ids, original_ticket, n_replicated_tickets, tickets_ids_to_replicate, pending_replicated_tickets, pending_replicated_tickets_ids, "similarity_escalation")
                if tickets_ids_to_replicate:
                        tickets_ids_to_replicate.pop(0)
            elif replicate_ticket:
                #print("Verification")
                #print("To verify", tickets_info_updated[i])
                original_ticket = cPickle.loads(cPickle.dumps(tickets_info_updated[i]))
                n_replicated_tickets, pending_replicated_tickets_ids = self.checkReplication(team, i, list_ids, original_ticket, n_replicated_tickets, tickets_ids_to_replicate, pending_replicated_tickets, pending_replicated_tickets_ids, "verification")
                      
            i += 1
            if i < len(list_ids):
                if pending_replicated_tickets:
                    #print("Pending tickets number:", len(pending_replicated_tickets))
                    #print("Pending tickets:", (pending_replicated_tickets))
                    if original_dict_idx >= len(temp_dict) - 1:
                        #print("Max reached:", original_dict_idx)
                        #print("length reached:", len(temp_dict))
                        earlier_replicated_ticket = self.getEarliestReplicatedTicket(pending_replicated_tickets_ids, pending_replicated_tickets)
                        tickets_info_updated[i] = pending_replicated_tickets[earlier_replicated_ticket]
                        del pending_replicated_tickets[earlier_replicated_ticket]
                        pending_replicated_tickets_ids.pop(0)
                        read_original_dict = False
                    else:
                        earlier_replicated_ticket = self.getEarliestReplicatedTicket(pending_replicated_tickets_ids, pending_replicated_tickets)
                        pending_ticket_date = pending_replicated_tickets[earlier_replicated_ticket]["unsolved datetime"]
                        next_normal_ticket = temp_dict[original_dict_idx + 1]["unsolved datetime"]
                        #print("PENDING DATE", pending_ticket_date)
                        #print("Next Normal DATE", next_normal_ticket)
                        if pending_ticket_date < next_normal_ticket:
                            tickets_info_updated[i] = pending_replicated_tickets[earlier_replicated_ticket]
                            #print("Next ticket:", tickets_info_updated[i])
                            del pending_replicated_tickets[earlier_replicated_ticket]
                            pending_replicated_tickets_ids.pop(0)
                            read_original_dict = False
                            #print("Next ticket id " + str(i) + " is read from pending tickets")
                        else:
                            #print("Normal ticket comes first")
                            read_original_dict = True
                else:
                    read_original_dict = True
                    
                if read_original_dict:
                    original_dict_idx += 1
                    #print("Next ticket id " + str(i) + " is read from tickets_info. Index:" + str(original_dict_idx))
                    tickets_info_updated[i] = temp_dict[original_dict_idx]
                    read_original_dict = False

        if Variables.debug:  
            print("All the tickets have actions that may solve the ticket")
        self.tickets_info = tickets_info_updated
        #print("len",  len(self.tickets_info))
        print("Number of Replicated Tickets", n_replicated_tickets)
    
    # Gets the timestamps of each action step
    def getTimestamps(self, ticket, date, family, action, team, user, outlier):
        
        #print("Outlier:", outlier)
        transition_dates = []
        action_user, transition_user = self.actionDuration(family, action, team, user)
        if outlier:
            #print("Prev", transition_user) 
            transition_user = Utils.updateStepOutlier(transition_user)
        #print("After", transition_user) 
        #transition_dates.append(int(datetime.timestamp(datetime.strptime(date, '%Y-%m-%d %H:%M:%S'))))
        
        #curr_date = datetime.strptime(date, '%d-%m-%Y %H:%M:%S')
        curr_date = Utils.convertStrToDatetime(date)
        transition_dates.append('{:02d}/{:02d}/{:02d} {:02d}:{:02d}:{:02d}'.format(curr_date.day, curr_date.month, curr_date.year, curr_date.hour, curr_date.minute, curr_date.second))

        for i in transition_user:
            curr_date +=  timedelta(0, 0, 0, 0, i)
            #transition_dates.append(int(datetime.timestamp(curr_date)))
            transition_dates.append('{:02d}/{:02d}/{:02d} {:02d}:{:02d}:{:02d}'.format(curr_date.day, curr_date.month, curr_date.year, curr_date.hour, curr_date.minute, curr_date.second))
            
        #print("Transition dates:", transition_dates)
        return transition_dates

    # Fills relevant data to the tickets
    def trainTicketAdvancedInfo(self, thread, weight):

        for i in self.tickets_info.keys():
            #print("id", i)
            ticket = self.tickets_info[i]
            #print("Aqui", ticket['unsolved'])
            country = ticket['country']
            action = ticket['action']
            family = ticket['family']
            subfamily = ticket['subfamily']
            user = ticket['analyst']
            team = ticket['team']
            client = ticket['client']
            subfamily_action = self.subfamily_pool[subfamily]["action"]
            dur = self.tickets_info[i]['duration']
            #print("Dur", dur)

            subfamily_dur, transitions = self.actionDuration(family, subfamily_action, "None", "None")

            replicated = False
            if "replicated from" in ticket.keys():
                replicated = True
            
            self.ticket_ids.append(i)    
            self.alert_family.append(family)
            self.family_actions.append(self.family_pool[family]["action"])
            self.alert_subfamily.append(subfamily)
            self.subfamily_actions.append(subfamily_action)
            self.alert_subfamily_duration.append(subfamily_dur)
            self.ticket_teams.append(team) 
            self.ticket_teams_users.append(Variables.teams_info_pool[team])
            self.analysts_actions.append(str(ticket["solutions available"])[1:-1])
            self.analysts_actions_status.append(ticket["solutions status"])
            self.ticket_status.append(ticket["status"])  

            self.analysts_chosen_action.append(action)
            self.analysts_available.append(str(ticket["analysts available"])[1:-1]) 
            self.ticket_escalate.append(ticket["escalate"])    
            
            self.locations.append(country)
            #self.locations_time_stage_day.append(ticket['stage day'])
            #self.locations_time.append(ticket['local time'])
            #self.locations_time_diff.append(ticket['local time diff']) 
            #self.locations_time_day.append(ticket['local time day'])
            #self.locations_time_weekday.append(ticket['day'])    
            self.locations_time_weekday.append(calendar.day_name[(Utils.convertStrToDatetime(ticket["allocated"])).weekday()]) 
            
            #self.locations_time_month.append(ticket['month'])     
            self.locations_utc_date_minimized.append(ticket['time min'])  
            #self.alert_area.append(ticket['area']) 
            self.clients.append(client)
            self.off_days.append(self.analysts_info[team][user]['days off'])
            
            self.location_utc_date.append(ticket['unsolved'])
            self.ticket_unfixed_time.append(ticket['allocated'])
            self.ticket_duration.append(Utils.calculateDateDiff(ticket['unsolved'], ticket['allocated']))
            self.ticket_fixed_time.append(ticket['fixed'])    
            self.analysts_chosen.append(user)
            self.user_shifts.append(ticket["user shift"])
            if "source ip" in ticket.keys():
                self.ticket_src_ip.append(ticket['source ip'])
                self.ticket_src_port.append(ticket['source port'])
                self.ticket_dst_ip.append(ticket['destination ip'])
                self.ticket_dst_port.append(ticket['destination port'])
                self.clients_info[client][country]["ips"][i] = ticket['destination ip']

            else: 
                self.ticket_src_ip.append("")
                self.ticket_src_port.append("")
                self.ticket_dst_ip.append("")
                self.ticket_dst_port.append("")
                self.clients_info[client][country]["ips"][i] = ""
                
            #suspicious = Utils.checkTicketSuspicious(ticket, self.subfamily_pool[ticket['subfamily']]['suspicious'])
            self.ticket_suspicious.append(ticket["suspicious"])  
            
            if replicated:
                similar = "Replicated from ticket " + str(ticket["replicated from"])
                self.similar_tickets.append(similar) 
                self.ticket_inherited_elapsed_time.append("---")
                self.coord_tickets.append("---")
            else:
                if ticket["similar"] != "---":
                    #print("i", i)
                    self.similar_tickets.append(ticket["similar ids"]) 
                    self.getFirstOccurence(i,ticket["similar ids"][-1])
                else:
                    self.similar_tickets.append("---")
                    self.ticket_inherited_elapsed_time.append("--")
                    
                if ticket["coordinated"] != "---":
                    #print("i", i)
                    self.coord_tickets.append(ticket["coordinated"]) 
                else:
                    self.coord_tickets.append("---")
                    
            if ticket["status"] == "Transfer":
                #print("Ticket", ticket)
                if ticket['escalate']:
                    if replicated:
                        self.analysts_chosen_action_status.append("Action updated due to ESCALATION Status")
                    else:
                        self.analysts_chosen_action_status.append("Last step removed due to ESCALATION Status")
                else: 
                    if ticket["distance"] >= Variables.actions_similarity: 
                        self.analysts_chosen_action_status.append("Distance GREATER than " + str(Variables.actions_similarity))
                    else:
                        self.analysts_chosen_action_status.append("Max similarity reached")
            else:
                   self.analysts_chosen_action_status.append("Distance LESS " + str(Variables.actions_similarity))
            
            self.analysts_actions_duration.append(dur)
            if ticket['outlier']:
                self.alert_outliers.append(True)
                self.analysts_actions_duration_outlier.append(self.tickets_info[i]['duration with outlier'])
            else: 
                self.alert_outliers.append(False)
                self.analysts_actions_duration_outlier.append(dur)
                
            if ticket['shifted']:
                self.alert_shifted.append(True)
            else: 
                self.alert_shifted.append(False)
                                    
            self.ticket_timestamps.append(self.getTimestamps(i, ticket['allocated'], family, action, team, user, ticket['outlier']))
            
            if subfamily not in self.subfamily_actions_taken.keys():
                self.subfamily_actions_taken[subfamily] = {}
                self.subfamily_actions_taken[subfamily]["actions"] = []
                self.subfamily_actions_taken[subfamily]["nodes info"] = {}
                self.subfamily_actions_taken[subfamily]["transitions"] = {}
                #self.subfamily_actions_taken[subfamily]["transitions occurences"] = {}
                
            action = action.replace("''", ",")
            action = action.replace("'", "")
            action_divided = action.split(",")
            action_str = [str(x) for x in action_divided]
            #action_str.insert(0, "init")
            if action_str not in self.subfamily_actions_taken[subfamily]["actions"]:    
                #print("New Action:", action_str)
                #actions_cleaned.append(action_str)
                self.subfamily_actions_taken[subfamily]["actions"].append(action_str)
        #print("Aqui", self.subfamily_actions_taken)
            
        if Variables.debug:
            print("Advanced ticket data assigned")
            
    # Frees all analysts
    def freeAllAnalysts(self):
        
        for x in self.analysts_availability.keys():
            self.analysts_availability[x]['free'] = True
            self.analysts_availability[x]['ticket endtime'] = "None"
            self.analysts_availability[x]['queue'] = []
              
    # Frees the analyst when ticket is fixed
    def freeAnalysts(self, ticket_init, tickets_info, mode):
        
        for x in self.analysts_availability.keys():
            #print("Member:", str(x))
            if self.analysts_availability[x]['free'] == False:
                #print("Member " + str(x) + " is occupied")
                #print("Ticket queue:", self.analysts_availability[x]['queue'])
                #if Variables.debug:
                #print("ticket init:", ticket_init)
                updated_queue = []
                #print("First ticket endtime:", self.analysts_availability[x]['ticket endtime'])
                
                for ticket in self.analysts_availability[x]['queue']:
                    #print("Ticket allocated id:", ticket)
                    #first_ticket_end = tickets_info[ticket]["fixed datetime"]
                    #print("First ticket end:", first_ticket_end)
                    ticket_end = tickets_info[ticket]["fixed datetime"]
                    if ticket_init < ticket_end:
                        updated_queue.append(ticket)
                    #else:
                        #print("ticket removed:", ticket)
                
                if not updated_queue:
                    #print("Analyst " + str(x) + " was freed")
                    self.analysts_availability[x]['free'] = True
                    self.analysts_availability[x]['ticket endtime'] = "None"
                    self.analysts_availability[x]['queue'] = []
                else:
                    self.analysts_availability[x]['queue'] = updated_queue
                    last_ticket_end = self.analysts_availability[x]['queue'][-1]
                    self.analysts_availability[x]['ticket endtime'] = tickets_info[last_ticket_end]["fixed datetime"]
                    #print("First Ticket endtime updated:", self.analysts_availability[x]['ticket endtime'])
                    
    def addToAnalystSummary(self, curr_team, user, subfamily, action_dur):
    
        #print(type(action_dur))
        #print(action_dur)
        if subfamily not in self.analysts_info[curr_team][user]["summary"].keys():
            self.analysts_info[curr_team][user]["summary"][subfamily] = {}
            self.analysts_info[curr_team][user]["summary"][subfamily]["occurences"] = 1
            self.analysts_info[curr_team][user]["summary"][subfamily]["Time spent"] = action_dur
            self.analysts_info[curr_team][user]["summary"][subfamily]["average"] = action_dur        
        else:
            self.analysts_info[curr_team][user]["summary"][subfamily]["occurences"] += 1
            self.analysts_info[curr_team][user]["summary"][subfamily]["Time spent"] += action_dur
            self.analysts_info[curr_team][user]["summary"][subfamily]["average"] = self.analysts_info[curr_team][user]["summary"][subfamily]["Time spent"] / self.analysts_info[curr_team][user]["summary"][subfamily]["occurences"]
# =============================================================================
#             print("Subfamily:", subfamily)
#             print("User:", user)
#             print("Occurences", self.analysts_info[curr_team][user]["summary"][subfamily]["occurences"])
#             print("Time", self.analysts_info[curr_team][user]["summary"][subfamily]["Time spent"])
# =============================================================================
    # Get user from team queue
    def findAnalystQueue(self, team, team_analysts):
        
        user = "None"
        # This prevents from assigning always the same user
        temp = random.sample(team_analysts,len(team_analysts))
        for i in temp:
            if self.analysts_availability[i]["free"] == True:
                #if Variables.debug:
                user = i
                break
        
        #if user == "None":
        #    print("Aqui")
        #    user = self.getFirstAnalyst(team_analysts)
            
        return user
              
    # Finds the next fastest analyst   
    def findNextAnalyst(self, ticket, team, team_analysts, subfamily, ticket_id):
        
        free_users = []
        
        for x in team_analysts:
            if self.analysts_availability[x]['free']:
                free_users.append(x)
                
        #print("Free Users", free_users)
        if len(free_users) == 1:
            return free_users[0]
        else:
            user = "None"
            time = 0
            for i in self.analysts_info[team]:
                if i in free_users:
                    #print("User:", i)
                    if subfamily not in self.analysts_info[team][i]["summary"].keys():
                        #print("User " + str(i) + " didn't handle this subfamily!")
                        time_spent = 0
                    else:
                        time_spent = self.analysts_info[team][i]["summary"][subfamily]["Time spent"]
                        #print(str(i) + " spent " + str(time_spent) +  " in the subfamily")
                        #print("Number of occurences", self.analysts_info[team][i]["summary"][subfamily]["occurences"])
                        
                    if ticket['outlier']:
                        action_dur = self.subfamily_analysts_action[subfamily][i]['duration'] + Variables.outlier_cost * self.subfamily_analysts_action[subfamily][i]['duration']
                    else:
                        action_dur = self.subfamily_analysts_action[subfamily][i]['duration']
                    
                    time_temp = time_spent + action_dur
                    #print("Action Duration:", action_dur)
                    #print("Total Time:", time_temp)
                    
                    if time == 0:
                        time = time_temp
                        user = i
                    elif time_temp < time:
                        time = time_temp
                        user = i
            
            #print("User", user)
            return user
            
    # Find the fastest analyst
    def findFastestAnalyst(self, team, team_analysts, subfamily, ticket_id):
        
        user = "None"
        time = 0
        
        #print("Team Info", self.analysts_info[team])
        for i in self.analysts_info[team]:
            if i in team_analysts:
                #print("User:", i)
                if subfamily not in self.analysts_info[team][i]["summary"].keys():
                    #print("User " + str(i) + " didn't handle this subfamily!")
                    time_spent = 0
                else:
                    time_spent = self.analysts_info[team][i]["summary"][subfamily]["Time spent"]
                    #print(str(i) + " spent " + str(time_spent) +  " in the subfamily")
                    #print("Number of occurences", self.analysts_info[team][i]["summary"][subfamily]["occurences"])
                    
                if self.tickets_info[ticket_id]['outlier']:
                    action_dur = self.subfamily_analysts_action[subfamily][i]['duration'] + Variables.outlier_cost * self.subfamily_analysts_action[subfamily][i]['duration']
                else:
                    action_dur = self.subfamily_analysts_action[subfamily][i]['duration']
                
                time_temp = time_spent + action_dur
                #print("Action Duration:", action_dur)
                #print("Total Time:", time_temp)
                
                if time == 0:
                    time = time_temp
                    user = i
                elif time_temp < time:
                    time = time_temp
                    user = i
                
        return user
    
    # Updates the action and its duration according to its escalation status
    def updateActionEscalation(self, ticket, ticket_id, team, user, action):
        
        subtechniques = action.split("'")
        subtechniques_cleaned = [x for x in subtechniques if x]
        #print("Subtechniques", subtechniques_cleaned)
        #print("Transfer action", list(Variables.actions_checkpoints["transfer_sub_op"].keys())[0])
        subtechniques_cleaned[-1] = list(Variables.actions_checkpoints["transfer_sub_op"].keys())[0]
        if len(subtechniques_cleaned) > 2:
            subtechniques_cleaned.pop(len(subtechniques_cleaned) - 2 )
        #subtechniques_cleaned = subtechniques_cleaned[:-1]
        #print("Subtechniques cleanted", subtechniques_cleaned)

        action_updated = ""
        for l in range(len(subtechniques_cleaned)):
            action_updated += "'" + subtechniques_cleaned[l] + "'"
                    
        #print("Action updated", action_updated)
        ticket['action'] = action_updated
        action_updated_dur, transitions = self.actionDuration(ticket["family"], action_updated, team, user)
        action_dur = action_updated_dur
        #self.subfamily_analysts_action[subfamily][user]['action'] = action_updated
        #self.subfamily_analysts_action[subfamily][user]['duration'] = action_updated_dur
        #print("The action updated was updated to " + str(action_updated) + " with a new duration " + str(action_dur))
        
        return action_updated, action_dur
                    
    # Fills some general data regarding the train tickets
    def trainTicketInfoGenerator(self, thread, weight, ticket_number):
        
        unsorted_tickets_info = {}
        networks_used = []
        countries_chosen = random.choices(list(Variables.countries.keys()), k = ticket_number)
        #print("Countries chosen:", countries_chosen)
        area_chosen = random.choices(list(self.family_area.keys()), weights=self.family_area.values(), k = ticket_number)
        #print("Areas chosen:", area_chosen)
        escalate_chosen = random.choices([True, False], weights=[Variables.escalate_rate_percentage/100, 1 - Variables.escalate_rate_percentage/100], k = ticket_number)
        #print("Escalate chosen:", escalate_chosen)
        outlier_chosen = random.choices([True, False], weights=(Variables.outlier_rate/100, (1 - Variables.outlier_rate/100)), k = ticket_number)
        #print("Outlier chosen:", outlier_chosen)
        
        frmt = '%d-%m-%Y %H:%M:%S'
    
        stime = time.mktime(time.strptime(Variables.start_date, frmt))
        etime = time.mktime(time.strptime(Variables.end_date, frmt))
    
        for i in range(ticket_number):
            if 1 == True: #if not thread.canceled:
                #print("Ticket id", i)
                country = countries_chosen[i]
                #local_time, local_time_min, diff, utc_time, utc_minimized, local_day, local_weekday, local_month = Utils.randomDateCountry(country)
                local_time, local_time_min, utc_datetime, utc_time, utc_minimized, utc_time_min, utc_weekday, utc_month = Utils.randomDateCountry(country, stime, etime)
                #stage_day = Utils.getStageDay(local_time_min)      
                #print(utc_minimized)
                #print(local_time_min)
                family, subfamily = Utils.getFamilyAndSubfamily(self.family_pool, self.subfamily_pool, self.family_time_probability_pool, self.family_week_probability_pool, utc_time_min, utc_weekday, utc_month, ticket_number)
                #Fills some info to the ticket dictionary for further analysis
                unsorted_tickets_info[i] = {}
                unsorted_tickets_info[i]['unsolved'] = utc_time
                unsorted_tickets_info[i]['unsolved datetime'] = utc_datetime
                unsorted_tickets_info[i]['country'] = country
                unsorted_tickets_info[i]['time min'] = utc_minimized
                #unsorted_tickets_info[i]['local time'] = local_time
                #unsorted_tickets_info[i]['local time min'] = local_time_min
                #unsorted_tickets_info[i]['local time diff'] = diff
                #unsorted_tickets_info[i]['local time day'] = local_day.lstrip('0')
                unsorted_tickets_info[i]['day'] = utc_weekday
                #unsorted_tickets_info[i]['stage day'] = stage_day
                unsorted_tickets_info[i]['month'] = utc_month
                unsorted_tickets_info[i]['fixed'] = "" 
                unsorted_tickets_info[i]['allocated'] = "" 
                
                client = self.getClient()
                unsorted_tickets_info[i]['client'] = client
                    
                if area_chosen[i] == "No Area":
                    unsorted_tickets_info[i]['area'] = ""
                else:
                    unsorted_tickets_info[i]['area'] = area_chosen[i]
                    
                unsorted_tickets_info[i]['family'] = family
                unsorted_tickets_info[i]['subfamily'] = subfamily
                unsorted_tickets_info[i]['team'] = "" 
                unsorted_tickets_info[i]['analyst'] = "None"
                unsorted_tickets_info[i]['shifted'] = False
                unsorted_tickets_info[i]['jump'] = 0
                unsorted_tickets_info[i]['action'] = "None"
                unsorted_tickets_info[i]['duration'] = "None"
                unsorted_tickets_info[i]['duration with outlier'] = "None"
                unsorted_tickets_info[i]['escalate'] = escalate_chosen[i]
                unsorted_tickets_info[i]['outlier'] = outlier_chosen[i]
                unsorted_tickets_info[i]['suspicious'] = Utils.isTicketSuspicious(i, unsorted_tickets_info[i], self.subfamily_pool[subfamily]['suspicious'])
                
                #Different Clients may share the netwrok
                if client not in self.clients_info.keys():
                    self.clients_info[client] = {}
                
                if country not in self.clients_info[client].keys():
                    self.clients_info[client][country] = {}    
                    self.clients_info[client][country]["networks"] = []
                    self.clients_info[client][country]["ips"] = {}
                
                network = Utils.getCountryNetwork(country, networks_used)
                networks_used.append(network)
                self.clients_info[client][country]["networks"].append(network)

                if self.family_pool[family]["ip"]:
                    source_country = Utils.randomCountry()
                    
                    src_ip, src_port = Utils.getSourceIPandPort(source_country, unsorted_tickets_info[i]['suspicious'])
                    dst_ip, dst_port = Utils.getDestinationIPandPort(self.clients_info[client][country]["networks"])
                    
                    #unsorted_tickets_info[i]['source ip']= src_ip
                    #unsorted_tickets_info[i]['source port']= src_port
                    #unsorted_tickets_info[i]['destination ip']= dst_ip
                    #unsorted_tickets_info[i]['destination port']= dst_port

                if Variables.debug:  
                    print("Ticket " + str(i) + " created")
        
        #print(unsorted_tickets_info)
        self.sortTickets(unsorted_tickets_info)
        #print(self.tickets_info)
            
        if Variables.debug:  
            print("All tickets created")      
            
    # If outlier, the ticket duration is updated
    def updateTicketDuration(self, ticket, action_dur):
        
        if ticket['outlier']:
            ticket['duration'] = action_dur 
            ticket['duration with outlier'] = action_dur + Variables.outlier_cost * action_dur
        else:
            ticket['duration'] = action_dur
        
    # Add boolean to check if replication is needed for max similarity    
    def getUserInfo(self, ticket, ticket_id, team, user, subfamily, tickets_ids_to_replicate, original_id, ticket_date):
        
        #print("User:", user)
        self.analysts_availability[user]['free'] = False
        ticket['analyst'] = user
        action = self.subfamily_analysts_action[subfamily][user]['action']
        action_dur = self.subfamily_analysts_action[subfamily][user]['duration']
        verify_ticket = False
        #print("Action dur", action_dur)
    
        #print(self.tickets_info[ticket_id]["to_replicate"])
        status = Utils.checkTicketStatus(ticket, original_id, action, self.subfamily_pool[subfamily]["action"], tickets_ids_to_replicate)
        if status == "Transfer":
            action, action_dur = self.updateActionEscalation(ticket, ticket_id, team, user, action)  
            #print("Action dur", action_dur)
            if (original_id not in tickets_ids_to_replicate) and (ticket["escalate"] == False):
                verify_ticket = True
                #print("aqui")
        
        if self.subfamily_analysts_action[subfamily][user]['action'] != action or "replicated from" in ticket.keys():
            #print("Current shifted status", ticket['shifted'])
            if Utils.checkNearNextShiftAction(ticket_date, action_dur):    
                #print("Ticket is going to be shifted")
                ticket['shifted'] = True
                
        ticket['status'] = status
        ticket['action'] = action
        
        return action, action_dur, verify_ticket
            
    # Finds the user according to the mode chosen (default is 0) and scheduling status
    def pickUser(self, ticket, mode, team, analysts, subfamily, ticket_id, schedule):
      
        if mode == 0:
            if not schedule:
                user = self.findAnalystQueue(team, analysts)
            else:
                #print("Ticket will be rescheduled")
                user = self.getFirstAnalyst(analysts)
                
            #print("User picked:", user)
            #self.removeUserFromQueue(user)
        else:
            if not schedule:
                user = self.findNextAnalyst(ticket, team, analysts, subfamily, ticket_id)
# =============================================================================
#                 if not self.analysts_availability[user]['free']:
#                     #print(str(user) + " is occupied until " + str(self.analysts_availability[user]['ticket endtime']))
#                     user = None
# =============================================================================
            else:
                #print("Ticket will be rescheduled")
                user = self.getFirstAnalyst(analysts)
                
        #print("User picked:", user)
        return user
        
    # Gets the analyst that fixes the ticket
    def findBestAnalyst(self, ticket, ticket_id, ticket_date, team_analysts, mode, team, subfamily, thread, tickets_ids_to_replicate, original_id, special, weight):
        
        replicate_ticket = False
        
        #print("Competent users: ", team_analysts)
        if Variables.debug:  
            print("Ticket id:" + str(ticket_id) + " Other Team: " + team)
            print("Team users " + str(team_analysts))
            print("Team:", team)

        user = self.pickUser(ticket, mode, team, team_analysts, subfamily, ticket_id, False)
                
        if user != "None":
            #print("Aqui")
            action, action_dur, replicate_ticket = self.getUserInfo(ticket, ticket_id, team, user, subfamily, tickets_ids_to_replicate, original_id, ticket_date)
            date = ""
                
            if ticket['shifted']:
                #print("Ticket id:", ticket_id)
                #print("Analyst shift to consider", self.analysts_info[team][user]['shift'])
                date, start_time = Utils.updateTicketTime(ticket_date, self.analysts_info[team][user]['shift'], ticket['jump'], action_dur, user, ticket['outlier'], Variables.outlier_cost, team, Variables.shifts, special)
                #self.analysts_availability[user]['ticket starttime'] = start_time
                ticket['allocated'] = start_time
                if special:
                    print("Ticket was shifted to:", str(date))
            else:
                #print("date to add ", ticket_date)
                date = Utils.addMinutesToDate(ticket_date, action_dur, ticket['outlier'], Variables.outlier_cost)
                #self.analysts_availability[user]['ticket starttime'] = ticket_date
                ticket['allocated'] = '{:02d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(ticket_date.day, ticket_date.month, ticket_date.year, ticket_date.hour, ticket_date.minute, ticket_date.second)
                if special:
                    print("Ticket fixed immediatly to:", date)

            ticket['fixed'] = '{:02d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(date.day, date.month, date.year, date.hour, date.minute, date.second)
            ticket['fixed datetime'] = date
            
            if self.analysts_availability[user]['ticket endtime'] == "None":
                self.analysts_availability[user]['ticket endtime'] = date
            self.analysts_availability[user]['queue'].append(ticket_id)
            self.updateTicketDuration(ticket, action_dur)
            ticket["user shift"] = self.analysts_info[team][user]["shift"]

        #Schedule the solving time and user when all of them are occupied
        else:
            if special:
                print("Rescheduling")
            user = self.pickUser(ticket, mode, team, team_analysts, subfamily, ticket_id, True)
            
            if Variables.debug:
                print("No users were available. Schedule ticket for when there users available")
            
            action, action_dur, replicate_ticket = self.getUserInfo(ticket, ticket_id, team, user, subfamily, tickets_ids_to_replicate, original_id, ticket_date)
    
            if self.analysts_availability[user]['ticket endtime'] != "None":
                if special:
                    print("User occupied")
                temp_date = self.analysts_availability[user]['ticket endtime']
                time = '{:02d}:{:02d}'.format(temp_date.hour, temp_date.minute)
                user_shift = self.analysts_info[team][user]['shift']
                different_shift = False
                if not Utils.isTimeBetween(Variables.shifts[user_shift]['start'], Variables.shifts[user_shift]['end'], time):
                    if special:
                        print("Ticket on different working shift")
                    different_shift = True
                
                if (Utils.checkNearNextShiftAction(self.analysts_availability[user]['ticket endtime'], action_dur)) or (different_shift == True):
                    #print("Ticket is close to end of the shift")
                    #print("User endtime", self.analysts_availability[user]['ticket endtime'])
                    date, start_time = Utils.updateTicketTime(self.analysts_availability[user]['ticket endtime'], self.analysts_info[team][user]['shift'], 0, action_dur, user, ticket['outlier'], Variables.outlier_cost, team, Variables.shifts, special)
                    #self.analysts_availability[user]['ticket starttime'] = start_time
                    ticket['allocated'] = start_time
                    #self.tickets_info[ticket_id]['allocated'] = self.analysts_availability[user]['ticket endtime']
                    if special:
                        print("User endtime:", self.analysts_availability[user]['ticket endtime'])
                        print("Solved date when user is finished with previous ticket:", str(date))
                else:
                    #print("Ticket is fixed after user is available")
                    date = Utils.addMinutesToDate(self.analysts_availability[user]['ticket endtime'], action_dur, ticket['outlier'], Variables.outlier_cost)
                    #print("Ticket fixed after user is available:", date)
                    user_endtime = self.analysts_availability[user]['ticket endtime']
                    ticket['allocated'] ='{:02d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(user_endtime.day, user_endtime.month, user_endtime.year, user_endtime.hour, user_endtime.minute, user_endtime.second)
                    if special:
                        print("User not free - Allocated date:", self.analysts_availability[user]['ticket endtime'])
                    #self.analysts_availability[user]['ticket starttime'] =  self.analysts_availability[user]['ticket endtime']
                #print("User was occupied")

            ticket['fixed'] = '{:02d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(date.day, date.month, date.year, date.hour, date.minute, date.second)
            ticket['fixed datetime'] = date
            
            if self.analysts_availability[user]['ticket endtime'] == "None":
                self.analysts_availability[user]['ticket endtime'] = date
            self.analysts_availability[user]['queue'].append(ticket_id)
            self.updateTicketDuration(ticket, action_dur)    
            ticket["user shift"] = self.analysts_info[team][user]["shift"]

        self.addToAnalystSummary(team, user, subfamily, ticket['duration'])

        #if replicate_ticket:
        #    print(str(ticket_id) + " should be replicated for verification")
            
        return replicate_ticket

   # Generates the dataset based on the information collected
    def trainDatasetOutput(self, thread, weight):
    
        data = {'ID': self.ticket_ids, 
                'Location':self.locations, 
                #'Location Time':self.locations_time, 
                #'Day': self.locations_time_day, 
                'Time Difference': self.locations_time_diff, 
                #'Time of the day':self.locations_time_stage_day, 
                'Weekday': self.locations_time_weekday, 
                'Month':self.locations_time_month,
                'Raised (UTC)': self.location_utc_date, 
                'Raised (Min)': self.locations_utc_date_minimized,
                'Allocated': self.ticket_unfixed_time, 
                'Stages': self.ticket_timestamps,
                'Fixed': self.ticket_fixed_time, 
                #'Area': self.alert_area, 
                'Client': self.clients, 
                'Family': self.alert_family, 
                'Family Action': self.family_actions, 
                'Subfamily':self.alert_subfamily, 
                'Subfamily Action': self.subfamily_actions, 
                'Subfamily Action Duration':self.alert_subfamily_duration, 
                'Team': self.ticket_teams, 
                'Team Users':self.ticket_teams_users, 
                'Users Competent': self.analysts_available, 
                'User actions': self.analysts_actions, 
                'User actions status': self.analysts_actions_status, 
                'User Chosen': self.analysts_chosen, 
                'Off Days': self.off_days,
                'User Shift': self.user_shifts,
                'Action Chosen': self.analysts_chosen_action, 
                'Action Chosen Status': self.analysts_chosen_action_status, 
                'Action Chosen Duration': self.analysts_actions_duration, 
                'Action Chosen (With Outlier)': self.analysts_actions_duration_outlier, 
                'Wait Time': self.ticket_duration, 
                'Coordinated With': self.coord_tickets,
                'Similar': self.similar_tickets, 
                'Inheritance Elapsed Time': self.ticket_inherited_elapsed_time,
                'Status': self.ticket_status, 
                'Initial Escalation': self.ticket_escalate, 
                'Suspicious': self.ticket_suspicious, 
                'Outlier': self.alert_outliers, 
                'Source IP': self.ticket_src_ip, 
                'Source PORT': self.ticket_src_port, 
                'Destination IP': self.ticket_dst_ip, 
                'Destination PORT': self.ticket_dst_port,
                'Shifted': self.alert_shifted}
 
        dataset = pd.DataFrame(data, columns=['ID', 
                                              'Location', 
# =============================================================================
#                                               'Location Time', 
#                                               'Time of the day', 
#                                               'Weekday', 
#                                               'Day', 
#                                               'Month', 
#                                               'Time Difference', 
# =============================================================================
                                              'Raised (UTC)', 
                                              #'Raised (Min)',
                                              'Allocated', 
                                              'Weekday',
                                              #'Wait Time',
                                              'Stages',
                                              'Fixed', 
                                              #'Shifted',
                                              'Client', 
                                              #'Area', 
                                              'Family', 
                                              'Family Action', 
                                              'Subfamily', 
                                              'Subfamily Action', 
                                              #'Subfamily Action Duration', 
                                              'Team', 
                                              #'Team Users', 
                                              'Users Competent', 
                                              'User actions', 
                                              'User actions status',
                                              'User Chosen', 
                                              'User Shift',
                                              'Off Days',
                                              'Action Chosen', 
                                              'Action Chosen Status',
                                              'Action Chosen Duration',
                                              'Action Chosen (With Outlier)', 
                                              'Initial Escalation',
                                              'Coordinated With',
                                              'Similar',
                                              'Inheritance Elapsed Time', 
                                              'Status',
                                              #'Suspicious', 
                                              'Outlier'])
                                              #'Source IP'])
                                              #'Source PORT',
                                              #'Destination IP', 
                                              #'Destination PORT'])
 
        #train = dataset.loc[0:change_mode_idx-1]
        #Utils.excelFormatter(train, "Queue_generation")
        #test = dataset.loc[change_mode_idx: len(dataset)]
        #Utils.excelFormatter(test, "Speed_generaton")
        Utils.excelFormatter(dataset, "trainDataset")
        #Utils.saveActionsFile(dataset, self.subfamily_actions_taken)
        #print("Last date:", dataset['Raised (UTC)'].iloc[-1])
        #dataset['Fixed'] = pd.to_datetime(dataset['Fixed'], format = "%d-%m-%Y %H:%M:%S")
        #print("Aqui:", dataset['Raised (UTC)'].iloc[-1])
        #print("Steps:", self.family_steps_pool)
        
# =============================================================================
#         for fam in self.family_steps_pool:
#             print("Family:", fam)
#             print("Family Steps", self.family_steps_pool[fam].keys())
#             for sub_step in self.family_steps_pool[fam]:
#                 print("Subfamily steps", self.family_steps_pool[fam][sub_step].keys())
# =============================================================================
        
        #return dataset['Fixed'].iloc[-1]
        
    # Prints all the variables of the tickets to ease debugging
    def printVariables(self):
        
        ticket_raised_time = {}    
        
        for i in self.tickets_info:

            fam = self.tickets_info[i]['family']
            tim = self.tickets_info[i]['time min']
            day = self.tickets_info[i]['day']
            
            if Variables.debug:
                print("Ticket id: " + str(i))
                print("Raised: ", self.tickets_info[i]['time min'])
                print("Fixed: ", self.tickets_info[i]['fixed'])
                print("Allocated: ", self.tickets_info[i]['allocated'])
                print("Family: ", self.tickets_info[i]['family'])
                print("Subfamily: ", self.tickets_info[i]['subfamily'])
                print("\n")
                print("Team: ", self.tickets_info[i]['team'])
                print("Analyst: ", self.tickets_info[i]['analyst'])
                print("Shifted: ", self.tickets_info[i]['shifted'])
                print("Action: ", self.tickets_info[i]['action'])
                print("Duration: ", self.tickets_info[i]['duration'])
                print("Outlier: ", self.tickets_info[i]['outlier'])
                print("\nTime before fix: ", tim)
                print("Day: ", day)
                print("day", day)
                print("tim", tim)
            
            if len(self.family_pool[fam]) > 4:
                print("family", self.family_pool[fam])
                fam_week_loc = self.family_pool[fam]['week loc']
                tim_fixed = Utils.centerDataPlot(fam_week_loc, day, tim)
            else:
                tim_fixed = Utils.centerDataPlot(0, day, tim)
   
            if fam not in ticket_raised_time.keys():
                ticket_raised_time[fam] = []
            ticket_raised_time[fam].append(tim_fixed)     

        for l in ticket_raised_time.keys():   
            
            if len(self.family_pool[l]) > 4:
                week_loc = self.family_pool[l]['week loc']
            else:
                week_loc = 0
                
            print("\nFamily ", l)
            print("Week loc: ", week_loc)
             
            days_list_sorted = []
            offset = week_loc

            while week_loc < len(list(Variables.week_time.keys())) + offset:
                days_list_sorted.append(week_loc % len(list(Variables.week_time.keys())))
                week_loc +=1
            
            days_list_sorted = days_list_sorted[4:]  + days_list_sorted[:4]
            print("days sorted after slicing: ", days_list_sorted)
            
            n, bins, patches = plt.hist(ticket_raised_time[l], bins = np.arange(-72, 84, 12))
            locs, labels = plt.xticks()
            lbs = ["Empty"]*13
            pos = 0
            
            colors = ["b", "g", "r", "c", "m", "y", "k"]
            random.shuffle(colors)
            color = random.choices(colors, k = 1)[0]
            
            for i in range(0, len(bins)):
                if (bins[i]/24).is_integer():
                    lbs[i] = Variables.week_time[days_list_sorted[pos]]['day']
                    pos += 1
                else:
                    lbs[i] = ""
                    
            for p in range(0, len(patches)):
                patches[p].set_facecolor(color)

            plt.suptitle("Family " + l)
            plt.xticks(bins, lbs)                        
            plt.show()

        if Variables.debug:
            print("\n")    
            for l in self.analysts_info:
                print("Analyst: ", l)
                print("Analyst Shift: ", self.analysts_info[l]['shift'])
                print("Analyst Shift Start: ", self.analysts_info[l]['init'])
                print("Analyst Shift End: ", self.analysts_info[l]['end'])
            
            print("\n")
            for j in self.family_steps_pool:
                print("Family : ", j)
                for p in self.family_steps_pool[j]:
                    print("Technique " + str(p) + str(" can be substituted by ") + str(self.family_steps_pool[j][p]))