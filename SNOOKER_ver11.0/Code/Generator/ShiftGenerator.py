# -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 14:29:15 2020

@author: Leonardo Ferreira
@goal: Creates the working shifts of the analysts
"""
from Code.Variables import Variables 
from Code.Configurator import Configurator 

import random
import _pickle as cPickle

class ShiftGenerator:

    # Generates the analysts shifts
    def pickShifts(shifts_used, allshifts_occupied):
    
        shift_index = -1
        #print("shifts used:", shifts_used)
        if allshifts_occupied:
            shifts_remaining = []
            for i in Variables.shifts.keys():
                if i not in shifts_used:
                    shifts_remaining.append(i)
            if Variables.debug:
                print("Remaining Shifts: ", shifts_remaining)
            if not shifts_remaining:
                shift_index = min(shifts_used, key=shifts_used.get)
                #shift_index = random.randint(0, len(Variables.shifts.keys())-1)
            else:
                shift_index = random.choices(shifts_remaining, k = 1)[0]
        else:
            shift_index = random.randint(0, len(Variables.shifts.keys())-1)
    
        if Variables.debug:
            print("Shift index picked: ", shift_index)
        return shift_index
    
    # Generates the analysts shifts
    def pickDayOff(days_used, days_list):
    
        day = -1
        #print("Days off used:", days_used)
        days_remaining = []
        for i in days_list:
            if i not in days_used:
                days_remaining.append(i)
        #if Variables.debug:
        #print("Remaining Shifts: ", days_remaining)
        if not days_remaining:
            day = min(days_used, key=days_used.get)
            #shift_index = random.randint(0, len(Variables.shifts.keys())-1)
        else:
            day = random.choices(days_remaining, k = 1)[0]
    
        if Variables.debug:
            print("Day picked: ", day)
        return day
    
    # Fills some relevant data to the analysts dictionary
    def resetShiftsDaysOff(domain, allshifts_occupied, analyst_shifts):
    
        shifts_picked = {}
        days_picked = {}
        save_info = {}
        
        days = []
        users_treated = {}
        existent_users = []
        
        for i in Variables.week_time.keys():
            days.append(Variables.week_time[i]['day'])       
    
        for team in Variables.teams_info_pool:
            analyst_shifts[team] = {}
            #analyst_shifts[team]["queue"] = []
            save_info[team] = {}
            
            temp_team_users = cPickle.loads(cPickle.dumps(Variables.teams_info_pool[team]))
            if existent_users:
                #print("Existent users:", existent_users)
                temp_users =  list(set(temp_team_users) - set(existent_users))
                #print("New users:", temp_users)
                for i in temp_users:
                    temp_team_users.remove(i)
                
                team_shuffled = random.sample(temp_team_users, len(temp_team_users))
                team_shuffled = team_shuffled + temp_users
            else:
                team_shuffled = random.sample(temp_team_users, len(temp_team_users))
            if Variables.debug:
                print("Team: ", team)
                print("Team members: ", team_shuffled)
            
            for member in team_shuffled:
                if member not in analyst_shifts[team].keys():
                    existent_users.append(member)
                    if member not in users_treated:
                        #print(member + " has no shift assigned nor days off")
                        users_treated[member] = {}
                        shift_index = ShiftGenerator.pickShifts(shifts_picked, allshifts_occupied)
                        users_treated[member]["shift"] = shift_index
                        
                        day_off = ShiftGenerator.pickDayOff(days_picked, days)
                        users_treated[member]["days off"] = day_off
                    else:
                        #print(member + " already with shift assigned and day off")
                        shift_index = users_treated[member]["shift"]
                        day_off = users_treated[member]["days off"]
                        
                    if shift_index not in shifts_picked:
                        shifts_picked[shift_index] = 1
                    else:
                        shifts_picked[shift_index] += 1
                        
                    if day_off not in days_picked:
                        days_picked[day_off] = 1
                    else:
                        days_picked[day_off] += 1
                        
                    analyst_shifts[team][member] = {}
                    #analyst_shifts[team][member]['speed'] = existent_user_info[team][member]["speed"]
                    #analyst_shifts[team][member]['speed'] = round(random.uniform(0.5, 2), 2)
                    analyst_shifts[team][member]['shift'] = shift_index
                    analyst_shifts[team][member]['init'] = Variables.shifts[shift_index]['start']
                    analyst_shifts[team][member]['end'] = Variables.shifts[shift_index]['end']
                    analyst_shifts[team][member]['summary'] = {}
                    analyst_shifts[team][member]['days off'] = day_off
                    #analyst_shifts[team]["queue"].append(member)
                    
                    save_info[team][member] = {}
                    save_info[team][member]['shift'] = shift_index
                    save_info[team][member]['days off'] = day_off
                    
                    if Variables.debug:
                        print("Shifts used: ", shifts_picked)
                        print("Days off used: ", days_picked)
                else:
                    shifts_picked[analyst_shifts[team][member]['shift']] += 1
                    days_picked[analyst_shifts[team][member]['days_off']] += 1
                    if Variables.debug:
                        print("Analyst shift already assigned!")
                        print("Shifts used: ", shifts_picked)
                        print("Days used: ", days_picked)
            if Variables.debug:
                print("Shifts being used: ", shifts_picked)
        
            shifts_picked = {}
            days_picked = {}
                
        if Variables.debug:
            print("All analysts shifts assigned")
        #print("Shifts info", analyst_shifts)
        Configurator.updateConfigFile("analysts_skills", save_info, domain, "./Configurations/" + domain + "/Init_cfg.yaml" )
        Variables.analysts_skills = analyst_shifts
# =============================================================================
#         path = "./Configurations/" + domain + "/Init_cfg.yaml"
#         teste = Configurator.readConfigFile(domain, path)
#         print(teste["analysts_skills"])
#         for team in teste["analysts_skills"]:
#             print("Team:", team)
#             print("Team type:", type(team))
#             print(teste["analysts_skills"][team])
#             for user in teste["analysts_skills"][team]:
#                 if user != "queue":
#                     print("User:", user)
#                     print("User type:", type(user))
#                     print(teste["analysts_skills"][team][user])
#                     for user_info in teste["analysts_skills"][team][user]:
#                         temp = teste["analysts_skills"][team][user]
#                         print(user_info)
#                         print("content:", temp[user_info])
#                         print("content type:", type(temp[user_info]))
# =============================================================================

    def setRemainingUserInfo(analysts_info):
        
        for team in analysts_info:    
            #print("Team", team)
            #analysts_info[team]["queue"] = []
            for user in analysts_info[team]:
                #if user != "queue":
                #print("User:", user)
                #print("User info:", analysts_info[team][user])
                #print("Aqui:", user_info)
                shift = analysts_info[team][user]["shift"]
                #print("Shift:", analysts_info[team][user]["shift"])
                analysts_info[team][user]['init'] = Variables.shifts[shift]['start']
                analysts_info[team][user]['end'] = Variables.shifts[shift]['end']
                analysts_info[team][user]['summary'] = {}
                    
                if user not in analysts_info[team]["queue"]:
                    analysts_info[team]["queue"].append(user)
                    
        #print("Aqui:", analysts_info)
                
    def setAnalystsAvailability(analysts_info, analysts_availability):
        
        for team in analysts_info:
            #print("Team", team)
            for user in analysts_info[team]:
                #if user != "queue":
                #print("User", user)
                #temp = teste["analysts_skills"][team][user]
                analysts_info[team][user]['speed'] = round(random.uniform(0.5, 2), 2)
                if user not in analysts_availability.keys():
                    analysts_availability[user] = {}
                    analysts_availability[user]["teams"] = []
                    analysts_availability[user]["teams"].append(team)
                    analysts_availability[user]['free'] = True
                    analysts_availability[user]['ticket endtime'] = "None"
                    analysts_availability[user]['queue'] = []
                    
                if team not in analysts_availability[user]["teams"]:
                    analysts_availability[user]["teams"].append(team)
                        
# =============================================================================
#         #print("Aqui")
#         for team in analysts_info:
#             print("Team:", team)
#             #print("Team type:", type(team))
#             for user in analysts_info[team]:
#                 print("User:", user)
#                 #print("User type:", type(user))
#                 #print(Variables.analysts_skills[team])
#                 for user_info in analysts_info[team][user]:
#                     temp = analysts_info[team][user]
#                     #if user_info == "days off" or user_info == "shift":
#                     #print(user_info)
#                     print(str(user_info) + ": " + str(temp[user_info]))
#                     #print("Content type:", type(temp[user_info]))
#                         
#                 #print("Analyst availability:", analysts_availability[user])
# =============================================================================
