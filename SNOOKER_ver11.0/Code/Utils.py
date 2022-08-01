# -*- coding: utf-8 -*-
"""
Created on Tue Dec 15 12:42:45 2020

@author: leonardo Ferreira
@goal: Has several useful functions applied through out the project
"""
from Code.Variables import Variables
#from Code.Configurator import Configurator

import psutil
import subprocess
import pandas as pd
import datetime
import pytz
import random
import numpy as np
import time
import os, shutil
from datetime import timedelta

#import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from statistics import NormalDist
import ipaddress
import itertools
import calendar

class Utils:
    
    # Generates the pool of families to reduce the execution time
    def familyProbability(thread, weight, families_number, family_types, min_subfamilies_number, max_subfamilies_number, ticket_generator):
    
        alert_pool = {}
        family_time_prob = ticket_generator.family_time_probability_pool
        family_week_prob = ticket_generator.family_week_probability_pool
        family_area = ticket_generator.family_area
        
        if family_types == "Random":
            families_selected = random.sample(list(Variables.default_alert_pool.keys()), k = families_number)  
        else:
            families_selected = family_types.split(" - ")
            #print("Teste", families_selected)
            #Variables.family_weights = random.choices(range(1, 100), k=len(families_selected))
            #families = string.ascii_uppercase
            #families_selected = random.sample(families, k = families_number)  

        #print(families_selected)
        family_time_shifts = Variables.family_time_4h.keys()
        family_time_shifts_probs = []
        family_week_shifts = Variables.week_time.keys()
        family_week_shifts_probs = []
        for i in family_time_shifts:
            family_time_shifts_probs.append(Variables.family_time_4h[i]['prob'])
            
        for l in family_week_shifts:
            family_week_shifts_probs.append(Variables.week_time[l]['prob'])
              
        for k in Variables.incident_area.keys():
            for j in Variables.incident_area[k].keys():
                family_area[Variables.incident_area[k][j]['type']] = Variables.incident_area[k][j]['prob']
        
        weekday_shifts = [0, 1, 2, 3, 4]
        weekend_shifts = [5, 6]
        weekday_probs = family_week_shifts_probs[0] + family_week_shifts_probs[1] + family_week_shifts_probs[2] + family_week_shifts_probs[3] + family_week_shifts_probs[4]
        weekend_probs = float (1 - weekday_probs)
        
        time_daylight_shifts = [2, 3, 4]
        time_night_shifts = [0, 1, 5]
        time_light_probs = family_time_shifts_probs[2] + family_time_shifts_probs[3] + family_time_shifts_probs[4]
        time_night_probs = float (1 - time_light_probs)
        
        if Variables.debug:
            print("Time day probs:", time_light_probs)
            print("Time night probs:", time_night_probs)
            print("Week probs:", weekday_probs)
            print("Weekend probs:", weekend_probs)
        
        if Variables.family_default_mode:
            real_families = list(Variables.family_seasonality["January"].keys())
            #print("Real Families:", Variables.family_seasonality)
            for fam in ticket_generator.family_pool.keys():
                if fam in families_selected:
                    alert_pool[fam] = ticket_generator.family_pool[fam]
                    #print("Family", fam)
                    #print("Fam:",  alert_pool[fam])
                    if Variables.family_seasonality_selector:
                        corresponding_family = random.choice(real_families)
                        real_families.remove(corresponding_family)
                        alert_pool[fam]["real_family"] = corresponding_family
                        #print("Family probability", alert_pool[fam])
                        #print(fam + " corresponds to " + corresponding_family)
                        #print(real_families)
        else:
            for fam in families_selected:
                if 1 == True:#not thread.canceled: 
                    if fam not in alert_pool.keys():   
                        #print("Family", fam)
                        alert_pool[fam] = {}
                        alert_pool[fam]["subtypes"] = random.randint(min_subfamilies_number, max_subfamilies_number)
                        if not Variables.time_probabilities_mode:
                            timehour = random.choices([True, False], weights=[time_light_probs, time_night_probs], k=1)[0]
                            if timehour:
                                time_shift = random.choices(time_daylight_shifts)[0]
                            else:          
                                time_shift = random.choices(time_night_shifts)[0]
                        else:
                            time_shift = random.choices(list(family_time_shifts), family_time_shifts_probs)[0]  
                        
                        if Variables.distribution_mode == "normal":
                            alert_pool[fam]["time shift"] = time_shift
                            alert_pool[fam]["time dev"] = 3
                
                            if not Variables.week_equal_probabilities:
                                weekday = random.choices([True, False], weights=[weekday_probs, weekend_probs], k=1)[0]
                                if weekday:
                                    week_shift = random.choices(weekday_shifts)[0]
                                else:          
                                    week_shift = random.choices(weekend_shifts)[0]
                            else:
                                week_shift = random.choices(list(family_week_shifts), family_week_shifts_probs)[0]  
                            alert_pool[fam]["week shift"] = week_shift
                            alert_pool[fam]["week loc"] = week_shift
                            alert_pool[fam]["week dev"] = 1
                    
                            shift_time = Variables.family_time_4h[time_shift]
                            shift_time_init = shift_time['start']
                            
                            shift_time_end = shift_time['end']
                            
                            hours_init, minutes_init = map(int, shift_time_init.split(':'))
                            hours_end, minutes_end = map(int, shift_time_end.split(':'))
                    
                            x = random.uniform(hours_init, hours_end + (minutes_end/60))

                            temp = str(x).split('.')
                            loc = float(temp[0] + "." + temp[1])
                            alert_pool[fam]['time loc'] = loc
                            
                            if Variables.debug:
                                print(shift_time_init)
                                print(shift_time_end)
                                print("Hour start:", hours_init)
                                print("Hour end:", hours_end + (minutes_end/60))
                                print("Time loc:", alert_pool[fam]['time loc'])
                                print("Week loc:", alert_pool[fam]['week loc'])
                            
                            alert_pool[fam]['ip'] = random.choices([True, False], weights=(40, 60), k=1)[0]
        
        #print("Alert pool", alert_pool)
        time_slots = (60/5) * 24 
        for k in alert_pool.keys():
            if 1 == True: #if not thread.canceled:
                family_week_prob[k] = {}
                family_time_prob[k] = {}
                if  Variables.family_seasonality_selector:
                    num_params = 3
                else:
                    num_params = 2
                if len(alert_pool[k]) > num_params:
                    #print("Family " + str(k) + " follows a normal distribution.")
                    week_loc = alert_pool[k]['week loc']
                    week_dev = alert_pool[k]['week dev']
                #else:
                    #print("Family " + str(k) + " follows a uniform distribution.")
                
                for day_shift in Variables.week_time.keys():
                    if len(alert_pool[k]) > num_params:
                        prob_day = NormalDist(mu = week_loc, sigma = week_dev).pdf(day_shift)
                        prob_before_day = NormalDist(mu = week_loc, sigma = week_dev).pdf(day_shift - 7)
                        prob_after_day = NormalDist(mu = week_loc, sigma = week_dev).pdf(day_shift + 7)
                        family_week_prob[k][Variables.week_time[day_shift]['day']] =  prob_day + prob_before_day + prob_after_day 
                    else:
                        family_week_prob[k][Variables.week_time[day_shift]['day']] =  np.random.uniform(0,1,1)[0]
                
                minute = 5
                hour = 0
                if len(alert_pool[k]) > num_params:
                    time_loc = alert_pool[k]['time loc']
                    time_dev = alert_pool[k]['time dev']
                    
                for slots in range(int(time_slots)):
                    if hour == 24:
                        time_string = "23:59"
                        hour = 23
                        minute = 59
                    else:
                        curr_time = datetime.time(hour, minute)    
                        time_string = curr_time.strftime('%H:%M')             
                
                    if len(alert_pool[k]) > num_params:
                        temp_time = float(hour + (minute/60))
                        prob_time = NormalDist(mu = time_loc, sigma = time_dev).pdf(temp_time)
                    
                        temp_before_time = float(hour + (minute/60)) - 24   
                        prob_before_time = NormalDist(mu = time_loc, sigma = time_dev).pdf(temp_before_time)

                        temp_after_time = float(hour + (minute/60)) + 24
                        prob_after_day = NormalDist(mu = time_loc, sigma = time_dev).pdf(temp_after_time)
                    
                        family_time_prob[k][time_string] =  prob_time + prob_before_time + prob_after_day 
                    else:      
                        family_time_prob[k][time_string] =  np.random.uniform(0,1,1)[0]
                
                    #if Variables.debug:
                        #temp_time = float(hour + (minute/60))
                        #family_time_prob[k][time_string] = stats.norm.pdf(temp_time, loc=alert_pool[k]['time loc'], scale=alert_pool[k]['time dev'])   
                    #print("Time: " + str(time_string) + " has a prob of " +  str(family_time_prob[k][time_string]))  
                    #print("Hour: " + str(hour) + " minute: " + str(minute))
                    
                    minute = minute + 5
                    if minute == 60:
                        minute = 0
                        hour = hour + 1 
                    
        ticket_generator.family_pool = alert_pool
        #print("Alert pool", alert_pool)
        
    # Gets the family and subfamily of of the ticket according to its time and weekday
    def getFamilyAndSubfamily(alert_pool, sub_alert_pool, family_time, family_week, time, weekday, month, ticket_number):
        
        family = ""
        subfamily = -1
        ticket_time_probs = {}
        ticket_week_probs = {}
        ticket_family_probs = {}
        family_cumulative = {}
        
        hours, minutes = map(int, time.split(':'))
        
        if Variables.debug:
            print("\nWeek day: ", weekday)
            print("Local time: ", time)
            time_fixed = float(hours + (minutes/60))
            print("Time fixed: ", time_fixed)

        for q in family_week.keys():
            for day in family_week[q].keys():
                if weekday == day:
                    ticket_week_probs[q] = family_week[q][day]
                    break        
        
        for k in family_time.keys():
            for curr_time in family_time[k].keys():
                if time <= curr_time:
                    ticket_time_probs[k] = family_time[k][curr_time]
                    break
                
        if Variables.family_seasonality_selector:
            for k in alert_pool.keys():
                for mon in Variables.family_seasonality.keys():
                    if mon == month:
                        month_ticket_sazonality = Variables.family_seasonality[month]
                        ticket_family_probs[k] = month_ticket_sazonality[alert_pool[k]["real_family"]]
                        
        #print("Family time options: ", ticket_family_probs)
        
        ticket_probs_total = {x: ticket_time_probs.get(x) * ticket_week_probs.get(x) for x in ticket_time_probs}
        #print("Time and Week: ", ticket_probs_total)
        
        if Variables.family_seasonality_selector:
            ticket_probs_total = {x: ticket_probs_total.get(x) * ticket_family_probs.get(x) for x in ticket_probs_total}
        
        #print("All of them: ", ticket_probs_total)
        ticket_probs_sorted = sorted(ticket_probs_total.items(), key=lambda x: x[1])
        #print("All of them sorted: ", ticket_probs_sorted)
        #ticket_probs_sorted = sorted(ticket_family_probs.items(), key=lambda x: x[1])
        ticket_random = random.uniform(0,  sum([pair[1] for pair in ticket_probs_sorted]))
        
        if Variables.debug:
            print("Family time options: ", ticket_time_probs)
            print("\nFamily week options: ", ticket_week_probs)
            print("\nMultiply: ", ticket_probs_total)
            print("\nFamily time options sorted: ", ticket_probs_sorted)
            print("\nFamily time options sorted sum: ", sum([pair[1] for pair in ticket_probs_sorted]))
            print("\nRandom prob: ", ticket_random)  
        
        prev = 0
        for l in range(0, len(ticket_probs_sorted)):
            fam = ticket_probs_sorted[l][0]
            if l == 0:
                prev = ticket_probs_sorted[0][1]
                family_cumulative[fam] = prev
            else:
                prev = prev + ticket_probs_sorted[l][1]
                family_cumulative[fam] = prev 
    
        for t in family_cumulative.keys():
            if ticket_random < family_cumulative[t]:
                family = t
                break
            
        #print("Family chosen:", family)
        subfamily = random.randint(1, alert_pool[family]["subtypes"])
        subfamily_updated = str(family) + "_" + str(subfamily)
        
        if subfamily_updated not in sub_alert_pool:
            
            sub_alert_pool[subfamily_updated] = {}
            sub_alert_pool[subfamily_updated]['suspicious'] = random.choices([True, False], weights=(Variables.suspicious_subfamily, 1 - Variables.suspicious_subfamily), k=1)[0]
# =============================================================================
#             if ticket_number > 100000:
#                 #print("Subfamily:", subfamily_updated)
#                 increment = ticket_number//100000
#                 #print("Increment:", increment)
#                 sub_alert_pool[subfamily_updated]['max counter'] = random.randint(Variables.min_coordinated_attack + increment, Variables.max_coordinated_attack + increment)
#                 sub_alert_pool[subfamily_updated]['timerange'] = random.randint(Variables.min_coordinated_attack_minutes - (10 * increment), Variables.max_coordinated_attack_minutes - (10 * increment))
#             else:   
# =============================================================================
            sub_alert_pool[subfamily_updated]['max counter'] = random.randint(Variables.min_coordinated_attack, Variables.max_coordinated_attack)
            sub_alert_pool[subfamily_updated]['timerange'] = random.randint(Variables.min_coordinated_attack_minutes, Variables.max_coordinated_attack_minutes)
        
        return family, subfamily_updated

    # Generates a random location (country)
    def randomCountry():

        country_selected = random.choice(list(Variables.countries.keys()))

        if Variables.debug:
            print("Country of each ticket assigned")
    
        return str(country_selected)
    
    # Generates a random date in a certain place
    def randomDateCountry(country, stime, etime):  
                
        ptime = stime + random.random() * (etime - stime)
        date = datetime.datetime.fromtimestamp(time.mktime(time.localtime(ptime))) 
        #print("Date:", date)
        if Variables.ticket_seasonality_selector:
            season = Variables.ticket_seasonality
            #print("season:", season)
            season_selected = np.random.choice(list(season.keys()), p = [season["high_season"]["prob"], season["off_season"]["prob"]])
            #print("season selected:", season_selected)
            months_available = season[season_selected]["months"]
        
            while date.month not in months_available:
                ptime = stime + random.random() * (etime - stime)
                date = datetime.datetime.fromtimestamp(time.mktime(time.localtime(ptime))) 
                #print("Date rejected:", date)
        
        #print("Date accepted:", date)
        #Get the country object
        country_timezone = random.choice(Variables.countries[country]['timezones'])
        local = pytz.timezone(country_timezone)
        #Get the country time
        local_dt = local.localize(date)
        #print("Local:", local_dt)
        #Converts the time to UTC
        utc_dt = (local_dt.astimezone(pytz.utc)).replace(tzinfo=None)
        #local_time = local_dt.strftime('%Y-%m-%d %H:%M:%S|%z')
        #print("UTC", utc_dt.replace(tzinfo=None))
        if Variables.debug:
            print("Timezone selected:", country_timezone)
            print("Date 1", local)
            print("Date 2", local_dt)
            print("Date 3", utc_dt)
        #print(utc_dt)
        #print(type(utc_dt))
        
# =============================================================================
#         time_difference = local_time.split('|')[1]
#         if time_difference == "+0000":
#             time_difference = "In UTC"
#         else:
#             time_difference = time_difference[:3] + ':' + time_difference[3:]
#         
# =============================================================================
        #return local_dt.strftime('%d-%m-%Y %H:%M:%S'), local_dt.strftime('%H:%M'), utc_dt.strftime('%d-%m-%Y %H:%M:%S'),  utc_dt.strftime('%H:%M'), calendar.day_name[utc_dt.weekday()], calendar.month_name[utc_dt.month], utc_dt.replace(tzinfo=None)
        return '{:02d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(local_dt.day, local_dt.month, local_dt.year, local_dt.hour, local_dt.minute, local_dt.second), '{:02d}:{:02d}'.format(local_dt.hour, local_dt.minute), utc_dt, '{:02d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(utc_dt.day, utc_dt.month, utc_dt.year, utc_dt.hour, utc_dt.minute, utc_dt.second), '{:02d}:{:02d}:{:02d}'.format(utc_dt.hour, utc_dt.minute, utc_dt.second), '{:02d}:{:02d}'.format(utc_dt.hour, utc_dt.minute), calendar.day_name[utc_dt.weekday()], calendar.month_name[utc_dt.month]

    # Generates a random date in a certain place
    def randomDateCountryTestTicket(country, stime, etime):  
                
        ptime = stime + random.random() * (etime - stime)
        date = datetime.datetime.fromtimestamp(time.mktime(time.localtime(ptime))) 

        #print("Date accepted:", date)
        #Get the country object
        country_timezone = random.choice(Variables.countries[country]['timezones'])
        local = pytz.timezone(country_timezone)
        #Get the country time
        local_dt = local.localize(date)
        #Converts the time to UTC
        utc_dt = (local_dt.astimezone(pytz.utc)).replace(tzinfo=None)  
        #print("Utc:", utc_dt)
        #local_time = local_dt.strftime('%Y-%m-%d %H:%M:%S|%z')

        if Variables.debug:
            print("Timezone selected:", country_timezone)
            print("Date 1", local)
            print("Date 2", local_dt)
            print("Date 3", utc_dt)
            #print("Time", local_time)

        #return local_dt.strftime('%Y-%m-%d %H:%M:%S'), local_dt.strftime('%H:%M'), time_difference, utc_dt.strftime('%Y-%m-%d %H:%M:%S'),  utc_dt.strftime('%H:%M'), local_dt.strftime('%d'),  local_dt.strftime('%A'), local_dt.strftime('%B')
        return '{:02d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(local_dt.day, local_dt.month, local_dt.year, local_dt.hour, local_dt.minute, local_dt.second), '{:02d}:{:02d}'.format(local_dt.hour, local_dt.minute), utc_dt, '{:02d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(utc_dt.day, utc_dt.month, utc_dt.year, utc_dt.hour, utc_dt.minute, utc_dt.second),  '{:02d}:{:02d}'.format(utc_dt.hour, utc_dt.minute), calendar.day_name[local_dt.weekday()], calendar.month_name[local_dt.month], date

    # Checks if a date is between other two dates
    def isTimeBetween(begin_time, end_time, check_time=None):
    
        # If check time is not given, default to current UTC time
        check_time = check_time or datetime.utcnow().time()
        if begin_time < end_time:
            return check_time >= begin_time and check_time <= end_time
        else: # crosses midnight
            return check_time >= begin_time or check_time <= end_time   
        
    # Get the shift where the ticket date is located
    def getTicketShift(curr_time):
            
        if Utils.isTimeBetween("00:00:00", "08:00:00", curr_time):
            return 0
        elif Utils.isTimeBetween("08:00:00", "16:00:00", curr_time):
            return 1
        else:
            return 2
        
    # Updates the duration of a step from the transition steps
    def updateStepOutlier(transitions_dur):
            
        transitions_dur_updated = []
        
        for i in transitions_dur:
            dur_updated = i + Variables.outlier_cost * i
            transitions_dur_updated.append(dur_updated)
            
        return transitions_dur_updated
        
    # Verifies if a ticket is suspicious or not    
    def isTicketSuspicious(ticket_id, ticket, suspicious):
        
        ticket_time = ticket['time min']
        country = ticket['country']
        day = ticket['day']
        
        if suspicious:
            #print(Variables.suspicious_countries)
            if country in Variables.suspicious_countries:
                day_off_list = Variables.suspicious_countries[country]["widget day off"].text()
                if (day_off_list.find(day) == -1):
                    if Utils.isTimeBetween(Variables.suspicious_countries[country]["widget start date"].text(), Variables.suspicious_countries[country]["widget end date"].text(), ticket_time):
                        #print("Ticket id suspicious", ticket)
                        return True
# =============================================================================
#                 ### Used for profiling of the project
#                 day_off_list = Variables.suspicious_countries[country]["dayoff"]
#                 if day not in day_off_list:
#                     if Utils.isTimeBetween(Variables.suspicious_countries[country]["start"], Variables.suspicious_countries[country]["end"], ticket_time):
#                         #print("Ticket id suspicious", ticket)
#                         return True
# =============================================================================
        return False
    
    # Analyses the ticket date, the user shift and the time it takes to fix it and schedules its solving
    def updateTicketTime(date, shift, jump, action_dur, user, outlier, outlier_cost, team, shifts, special):
    
        #date = datetime.datetime.strptime(ticket_date, '%d-%m-%Y %H:%M:%S')
        #date = Utils.convertStrToDatetime(ticket_date)
        #time = '{:02d}:{:02d}'.format(date.hour, date.minute)
        analyst_ticket_start = date
    
        if outlier:
            action_dur = action_dur + outlier_cost * action_dur
    
# =============================================================================
#         if Variables.debug:  
#             print("Ticket date: ", date)
#             print("User shift start: ", shift)
# =============================================================================
    
        if shift == 0:
            date = date.replace(minute = 00, hour = 00, second = 00, year = date.year, month = date.month, day = date.day)
            analyst_ticket_start = date + timedelta(1, 0, 0, 0, 0)
            date = date + timedelta(1, 0, 0, 0, action_dur)
        elif shift == 1:    
            temp_date = date + timedelta(0, 0, 0, 0, action_dur)
            temp_time = '{:02d}:{:02d}'.format(temp_date.hour, temp_date.minute)
            #print("Shift", shift)
            #print("Temp_time:", temp_time)
            if Utils.isTimeBetween(shifts[2]['start'], shifts[2]['end'], temp_time):
                date = date.replace(minute = 00, hour = 8, second = 00, year = date.year, month = date.month, day = date.day)
                analyst_ticket_start = date + timedelta(1, 0, 0, 0, 0)
                date = date + timedelta(1, 0, 0, 0, action_dur)
                if special:
                    print("next day")
            else:
                date = date.replace(minute = 00, hour = 8, second = 00, year = date.year, month = date.month, day = date.day)
                analyst_ticket_start = date 
                date = date + timedelta(0, 0, 0, 0, action_dur)
                if special:
                    print("same day")
                
                if jump >= 1:
                    print("Aqui")
                    analyst_ticket_start = analyst_ticket_start + timedelta(jump, 0, 0, 0, 0)
                    date = date + timedelta(jump, 0, 0, 0, 0)
        else:
            temp_date = date + timedelta(0, 0, 0, 0, action_dur)
            temp_time = '{:02d}:{:02d}'.format(temp_date.hour, temp_date.minute)
            #print("Shift", shift)
            #print("Temp_time:", temp_time)
            if Utils.isTimeBetween(shifts[0]['start'], shifts[0]['end'], temp_time):
                date = date.replace(minute = 00, hour = 16, second = 00, year = date.year, month = date.month, day = date.day)
                analyst_ticket_start = date + timedelta(1, 0, 0, 0, 0)
                date = date + timedelta(1, 0, 0, 0, action_dur)
                if special:
                    print("next day")
            else:
                date = date.replace(minute = 00, hour = 16, second = 00, year = date.year, month = date.month, day = date.day)
                analyst_ticket_start = date 
                date = date + timedelta(0, 0, 0, 0, action_dur)
                if special:
                    print("same day")
                if jump >= 1:
                    print("Aqui")
                    analyst_ticket_start = analyst_ticket_start + timedelta(jump, 0, 0, 0, 0)
                    date = date + timedelta(jump, 0, 0, 0, 0)
    
# =============================================================================
#         if Variables.debug:  
#             print("Ticket Date Updated")
# =============================================================================
            
        start_time = '{:02d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(analyst_ticket_start.day, analyst_ticket_start.month, analyst_ticket_start.year, analyst_ticket_start.hour, analyst_ticket_start.minute, analyst_ticket_start.second)
        #print("date aqui", date)
        return date, start_time
    
    # Converts string date to datetime (saves a lot of time compared to datetime function)
    def convertStrToDatetime(datestr):
        day = int(datestr[:2])
        #print("day:", day)
        month = int(datestr[3:5]) 
        #print("month:", month)
        year = int(datestr[6:10])
        #print("year:", year)
        hour = int(datestr[11:13])
        #print("Hour:", hour)
        minute = int(datestr[14:16]) 
        #print("Minute:", minute)
        seconds = int(datestr[17:19])
        #print("Second:", seconds)

        return datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=seconds)
    
    # Updates the list of ticket ids when a replicated ticket is created
    def updateIDs(list_ids, position):
    
        position_list = []
        position_list.append(position)
        #print("Start:", list_ids[:position])
        #print("New:", position_list)
        temp = np.arange(position + 1, len(list_ids), 1, dtype=int).tolist()
        #print("After:", temp)
        #list_updated = list_ids[:position] + position_list + list(range(position + 1, len(list_ids)))
    
        list_updated = list_ids[:position] + position_list + temp
        return list_updated
    
    # Sorts the replicated IDS according to their creation date
    def sortReplicatedIDs(ticket_id, new_date, pending_replicated_tickets_ids, pending_replicated_tickets, generation):

        #print("Ticket id to add:", ticket_id)
        #print("Ticket date:", new_date)
        #print("Before adding:", pending_replicated_tickets_ids)
        
        if not pending_replicated_tickets_ids:
            pending_replicated_tickets_ids.append(ticket_id)
        else:
            position = -1
            for i in range(len(pending_replicated_tickets_ids)):
                #print("Index:", i)
                replicated_id = pending_replicated_tickets_ids[i]
                #print("Replicated ID", replicated_id)
                if generation:
                    replicated_date = pending_replicated_tickets[replicated_id]["unsolved datetime"]
                else:
                    replicated_date = pending_replicated_tickets[replicated_id]["Raised (UTC)"]
                #print("Date", replicated_date)
                if new_date < replicated_date:
                    position = i
                    break
            if position == -1:
                pending_replicated_tickets_ids.append(ticket_id)
            else:
                #print("Best position:", position)
                pending_replicated_tickets_ids.insert(position, ticket_id)
                
        #print("After adding:", pending_replicated_tickets_ids)
        #print("Length:", len(pending_replicated_tickets_ids))
        return pending_replicated_tickets_ids
    
    # Get the analysts from the next shift
    def getAnalystsNextShift(ticket_time, shifts):

        next_shift_index = 0
        next_shifts = []
    
        #Get the next time (currently  there are 3 shifts - 0, 1 and 2)
        for i in shifts.keys():
            if Utils.isTimeBetween(shifts[i]['start'], shifts[i]['end'], ticket_time):
                if Variables.debug:
                    print("Curr Shift", i)
                    print("Shift start: ", shifts[i]['start'])
                    print("Shift end: ", shifts[i]['end'])
                next_shifts.append(i)
                next_shift_index = i
                for p in range(len(shifts.keys()) - 1):
                    next_shift_index = next_shift_index + 1  
                    if Variables.debug:
                        print("Next shift: ", next_shift_index)
                        print("Last shift: ", list(shifts.keys())[-1] )
                    if list(shifts.keys())[-1] < next_shift_index:
                        next_shift_index = 0
                
                    if Variables.debug:
                        print("next_shift_index: ", next_shift_index)
                    next_shifts.append(next_shift_index)
                break
    
        if Variables.debug:
            print("\nNext shifts options: ", next_shifts)
            
        return next_shifts
    
    # Generates actions for subfamilies and users
    def userActionBuild(family, subfamily, team, member, action, steps_info, operation_types, debugging, generation):
    
        #print("Special Operations:", Variables.actions_checkpoints)
# =============================================================================
#         if debugging:
#             print("Generate action for user")
#             print("Family: " + str(family))
#             print("Subfamily: " + str(subfamily))
# =============================================================================
        
        subtechniques = action.split("'")
        subtechniques_cleaned = [x for x in subtechniques if x]
        
        if debugging:
            #print("SubTechniques:", subtechniques)
            print("Action List", subtechniques_cleaned)
        
        operations_number = random.randint(2, 3)
        operations = random.choices(operation_types, (0.7, 0.1, 0.1, 0.1), k = operations_number)
        
        while ('+' or '-' or '%') not in operations:
            operations = random.choices(operation_types, (0.7, 0.1, 0.1, 0.1), k = operations_number)
        
        #operations = random.choices(Variables.actions_operations, (0.30, 0.36, 0.35), k = operations_number)
        #print("Operations:", operations)
        
        for opt in operations:
            if debugging:
                print("Operation: " + opt)
            if opt == '+':
                if generation:
                    subtechniques_available = Utils.getSubTechniques(family, steps_info, "--")
                else:
                    subtechniques_available = steps_info
                add_subtechnique = random.choices(subtechniques_available, k = 1)[0]
                pos = random.randint(1, len(subtechniques_cleaned) - 1)
                subtechniques_cleaned = subtechniques_cleaned[:pos] + [add_subtechnique] + subtechniques_cleaned[pos:]
                
                if debugging:
                    print("Position to add sub:", pos)
                    print("Subtechnique to add:", add_subtechnique)
                    print("After operation + the action is " + str(subtechniques_cleaned))  
            elif opt == '-':
                if len(subtechniques_cleaned) > 2:
                    pos = random.randint(1, len(subtechniques_cleaned) - 2)
                    subtechniques_cleaned = subtechniques_cleaned[:pos] + subtechniques_cleaned[pos + 1:]
                    if debugging:
                        print("Position to remove sub:", pos)
                        #print("Subtechnique remove:", subtechniques_cleaned)
                else:
                    operation_added = random.choices(operation_types, (0.7, 0.1, 0.1, 0.1), k = 1)[0]
                    operations.append(operation_added)

                    if debugging:
                        print("cannot remove open and close steps!")                    
                        print("Operation added:", operation_added)
                        print("Operation update:", operations)
                if debugging:
                    print("After operation - the action is " + str(subtechniques_cleaned))
            elif opt == '%':
                if len(subtechniques_cleaned) > 2:
                    pos = random.randint(1, len(subtechniques_cleaned) - 2)
                    if generation:
                        subtechniques_available = Utils.getSubTechniques(family, steps_info, subtechniques_cleaned[pos])
                    else:
                        subtechniques_available = steps_info
                    to_update_subtechnique = random.choices(subtechniques_available, k = 1)[0]
                
                    subtechniques_cleaned = subtechniques_cleaned[:pos] + [to_update_subtechnique] + subtechniques_cleaned[pos+1:]
                
                    if debugging:
                        print("Position changed:", pos)
                        print("The subtechnique included:", to_update_subtechnique)
                        print("After the operation % the action is " + str(subtechniques_cleaned))
                else:
                    operation_added = random.choices(Variables.actions_operations, (0.7, 0.1, 0.1, 0.1), k = 1)[0]
                    operations.append(operation_added)

                    if debugging:
                        print("cannot change since only open and close steps!")                    
                        print("Operation added:", operation_added)
                        print("Operation update:", operations)
            else:
                if debugging:
                    print("No changes to the action since the operation is " + str(opt))

        action_updated = ""
        for i in range(len(subtechniques_cleaned)):
            action_updated += "'" + subtechniques_cleaned[i] + "'"
            
        #print("Final user action:", action_updated)
        if generation:
            return action_updated
        else:
            return subtechniques_cleaned
    
    # Adds the duration of an action to a date
    def addMinutesToDate(time_datetime, action_duration, outlier, outlier_cost):
        
        #time_datetime = Utils.convertStrToDatetime(datestring)
    
        #Adds outlier effect on the dataset (adds more time to fix a ticket)
        if outlier:
            action_duration = action_duration + outlier_cost * action_duration
    
        return time_datetime + timedelta(0, 0, 0, 0, action_duration)
    
    # Verifies if the time that it takes to fix a ticket surpasses the user shift
    def checkNearNextShiftAction(ticket_time_complete, action_dur):
        
        #time_datetime = Utils.convertStrToDatetime(ticket_time_complete)
        current_hour = ticket_time_complete.hour
    
        next_time = ticket_time_complete + timedelta(0, 0, 0, 0, action_dur)
        next_hour = next_time.hour
        
        if (current_hour == 6 and next_hour == 8) or (current_hour == 7 and next_hour == 8) or (current_hour == 7 and next_hour == 9) or (current_hour == 14 and next_hour == 16) or (current_hour == 15 and next_hour == 16) or (current_hour == 15 and next_hour == 17) or (current_hour == 22 and next_hour == 0) or (current_hour == 23 and next_hour == 0) or (current_hour == 23 and next_hour == 1):
            if Variables.debug:
                print("Action will surpass the analyst's shift")
            return True
        else:
            return False
    
    # Levenshtein distance
    def levenshtein(a,b):
        
        n, m = len(a), len(b)
        if n > m:
            a,b = b,a
            n,m = m,n
        
        current = range(n+1)
        for i in range(1,m+1):
            previous, current = current, [i]+[0]*n
            for j in range(1,n+1):
                add, delete = previous[j]+1, current[j-1]+1
                change = previous[j-1]
                if a[j-1] != b[i-1]:
                    change = change + 1
                current[j] = min(add, delete, change)
            
        return current[n]
    
    # Calculate similarity between picked action and subfamily action
    def calculateDistance(action_chosen, subfamily_action):
        
        user_action = action_chosen.split("'")
        user_action = [x for x in user_action if x]
        #print("user action", user_action)
        
        subfam_action = subfamily_action.split("'")
        subfam_action = [x for x in subfam_action if x]
        #print("subfamily action", subfam_action)
        
        distance = Utils.levenshtein(user_action, subfam_action)
        #print("Distance", distance)
        
        return distance
           
    # Check ticket status
    def checkTicketStatus(ticket, ticket_id, user_action, subfamily_action, tickets_ids_to_replicate):
        
        team = ticket["team"]
        distance = Utils.calculateDistance(user_action, subfamily_action)
        ticket["distance"] = distance

# =============================================================================
#         print("ID", ticket_id)
#         print("Team:", team)
#         print("Escalate:", escalate)
#         print("Distance:", distance)
# =============================================================================
        #print("Ids to replicate:", tickets_ids_to_replicate)
        if (ticket_id in tickets_ids_to_replicate) or (distance >= Variables.actions_similarity) or (ticket["escalate"]):
            teams = list(Variables.teams_info_pool.keys())
            index = teams.index(team)
            if index <= 2:
                return "Transfer"
        return "Closed"
    
    # Generates a random location (country)
    def getCountryNetwork(country, networks_used):

        networks = Variables.countries[country]['ips']
        #print("Networks", networks)
        
        random_network = random.choices(networks)[0]
        #print("Network picked", random_network)
# =============================================================================
#         while random_network in networks_used:
#             print("Aqui")
#             #print("networks used", networks_used)
#             random_network = random.choices(networks)[0]
#             #print("New Network picked", random_network)
# =============================================================================

        if Variables.debug:
            print("Country of each ticket assigned")
        #print("Network chosen", random_network)
    
        return random_network

    # Generates the IP and Port of Source Country
    def getSourceIPandPort(country, suspicious):
        # Port 0-1023 – Well known ports (server services by the Internet)
        # Ports 1024-49151 - Registered Port (semi-served ports)
        # Ports 49152-65535 - free to use by client programs (ephemeral ports)
        # Source nos ultimos
        # Generates the Ports  
    
        if not suspicious:
            ips_network_available = Variables.countries[country]["ips"]
            random_network = random.choice(ips_network_available)
            net = ipaddress.IPv4Network(random_network)
            random_ip_index = random.randint(0, net.num_addresses -1)
            random_ip = net[random_ip_index]
        else:
            random_ip = random.choice(list(Variables.suspicious_ips))

        #print("Source ip:", random_ip)
        src_port = random.randint(49152, 65535)    

        if Variables.ips_pool[Variables.ip_selected_idx] == "IPv6Address":
            random_ip = ipaddress.IPv6Address('2002::' + str(random_ip)).compressed
            #print("Ip converted to IPv6")
            
        return random_ip, src_port

    # Generates the IP and Port of Destination Country
    def getDestinationIPandPort(client_network):
        
        random_network = random.choices(client_network)[0]
        net = ipaddress.IPv4Network(random_network)
        
        random_ip_index = random.randint(0, net.num_addresses -1)
        random_ip = net[random_ip_index]
        
        if Variables.debug:
            print("Network", net)
            for i in net:
                print(i)
                
            print("Range", net.num_addresses)
            print("Ip index", random_ip_index)
        #print("Ip", random_ip)
        
        if Variables.ips_pool[Variables.ip_selected_idx] == "IPv6Address":
            random_ip = ipaddress.IPv6Address('2002::' + str(random_ip)).compressed
            #print("Ip converted to IPv6")
            
        dst_port_type = random.choices(["well-known", "registered"], weights=[0.5, 0.5], k=1)[0]
        #print("Destination Port Type:", dst_port_type)
        
        if dst_port_type == "well-known":
            dst_port = random.randint(0, 1023)
            #print("Destination Port:", dst_port)
        else:
            dst_port = random.randint(1024, 49151)
            #print("Destination Port:", dst_port)
        return random_ip, dst_port
        
    #Get the analysts from all teams
    def getAllAnalysts(all_analysts):
    
        for team in Variables.teams_info_pool.keys():
            for user in Variables.teams_info_pool[team]:
                if user not in all_analysts:
                    all_analysts.append(user)
                
        all_analysts.sort()
        
    #Get the subtechniques of each step of the family action
    def getSubTechniques(family, steps_pool, step):
    
        subtechniques = []
        
        init, final, transfer = Utils.getLockedTechniques()
        locked = list(Variables.actions_checkpoints["init_op"].keys()) + list(Variables.actions_checkpoints["end_op"].keys()) + list(Variables.actions_checkpoints["transfer_sub_op"].keys()) + init + final
        
        family_techniques = steps_pool[family]
        #print("Family techniques", family_techniques)
        
        for i in family_techniques.keys():
            if i not in locked:
                for l in family_techniques[i].keys():
                    if l not in locked:
                        if step != l:
                            subtechniques.append(l)
        
        #print("Family subtechniques", subtechniques)
        return subtechniques
        
    # Divides the tickets for all teams
    def teamsDivider(subfamilies_pool):
        
        teams = {}
        tickets_copy = (list(subfamilies_pool.keys())).copy()
        random.shuffle(tickets_copy)
        #print("Subfamilies shuffled", tickets_copy)
        
        print("Prioritize Lower teams", Variables.lower_teams)
        if not Variables.lower_teams: 
            # Convert percentages to float
            for i in Variables.teams_frequency.keys():
                if isinstance(Variables.teams_frequency[i], int):
                    Variables.teams_frequency[i] = Variables.teams_frequency[i]/100

            l1_percentage = Variables.teams_frequency['L1']
            l2_percentage = l1_percentage + Variables.teams_frequency['L2']
            l3_percentage = l2_percentage + Variables.teams_frequency['L3']
            #l4_percentage = Variables.teams_frequency['L1'] + Variables.teams_frequency['L2'] + Variables.teams_frequency['L3'] + Variables.teams_frequency['L1']

            l1, l2, l3, l4 = np.split(tickets_copy, [int(len(tickets_copy)*l1_percentage), int(len(tickets_copy)*l2_percentage), int(len(tickets_copy)*l3_percentage)])
            teams["L1"] = l1
            teams["L2"] = l2
            teams["L3"] = l3
            teams["L4"] = l4
            #print("Teams", teams)
        
            for team in teams.keys():
                for subfamily in teams[team]:
                    subfamilies_pool[subfamily]["team"] = team
        else:
            for subfamily in tickets_copy:
                subfamilies_pool[subfamily]["team"] = "L1"
            
    
    # Get the stage of the day (morning, afternoon, evening and night)
    def getStageDay(ticket_time):
    
        for i in Variables.day_stages.keys():
            if Utils.isTimeBetween(Variables.day_stages[i]['start'], Variables.day_stages[i]['end'], ticket_time):
                return i

    # Closes any excel file opened (prevents output wrinting fail)
    def closeExcel():
    
        #print("Aqui")
        excel_found = False
        for proc in psutil.process_iter():
            if proc.name() == "EXCEL.EXE": 
                print("Excel instances found!")
                excel_found = True
                subprocess.call(["taskkill", "/f", "/im", "EXCEL.EXE"])            
        if not excel_found:
            print("Excel instances not found!")
    
    # The plot data is centered aroun the loc
    def centerDataPlot(loc, day, time):
        
        for j in Variables.week_time.keys():
            if Variables.week_time[j]['day'] == day:
                day_mult = j    

        if Variables.debug:
            print("Loc", loc)
            print("Day", day_mult)
            print("Time", time)
        
        days_list_sorted = {}
        offset = loc
        mult = 0

        while loc < len(list(Variables.week_time.keys())) + offset:
            if loc > offset + 3:
                days_list_sorted[loc % len(list(Variables.week_time.keys()))] = mult
                mult += 1
            elif loc == offset + 3:
                days_list_sorted[loc % len(list(Variables.week_time.keys()))] = mult
                mult = -mult
            else:    
                days_list_sorted[loc % len(list(Variables.week_time.keys()))] = mult
                mult += 1  
            loc +=1
            
        curr_time = datetime.datetime.strptime(time, '%H:%M')      
        curr_time_centered = curr_time + datetime.timedelta(hours = 24 * days_list_sorted[day_mult])    
        hours, minutes = map(int, (curr_time_centered.strftime('%H:%M')).split(':'))
        
        if days_list_sorted[day_mult] >= 0:
            tim_fixed = (hours + (minutes/60)) + 24 * days_list_sorted[day_mult]
        else:
            tim_fixed = -(hours + (minutes/60)) + 24 * (days_list_sorted[day_mult] + 1)
        
        if Variables.debug:
            print(days_list_sorted)
            print("Mult", days_list_sorted[day_mult])
            print("Time", curr_time)
            print("Time centered: ", curr_time_centered)
            print("Time fixed", tim_fixed)
       
        return tim_fixed
    
    # Applies special format to the output file
    def excelFormatter(dataset, name):
    
        #header = "ID;Location;Raised (UTC);Fixed;Client;Family;Subfamily;Subfamily Action Duration;Team;User Chosen;Action Chosen;Action Chosen Duration;Ticket Duration;Status"
        
        if not Utils.saveTXTFile(dataset, name): 
            if Variables.format_selected_idx == 0:
                name = "./Output/Generation/" + name + ".csv"
                dataset.to_csv(name, encoding='utf-8', index=False, sep=';')
            else:
                name = "./Output/Generation/" + name + ".xlsx"
                writer = pd.ExcelWriter(name, engine='xlsxwriter')
                dataset.to_excel(writer, sheet_name='Tickets Info', index = False)  
                workbook  = writer.book
                worksheet = writer.sheets['Tickets Info']   

                # Add special format for better reading and debug
                format1 = workbook.add_format()
                format1.set_align('center')
    
                #worksheet.set_column(dataset.columns.get_loc("ID"), dataset.columns.get_loc("Time Difference"), 7, format1)
                #worksheet.set_column(dataset.columns.get_loc("Location"), dataset.columns.get_loc("Time Difference"), 18, format1, {'level': 1, 'hidden': True})
                #worksheet.set_column(dataset.columns.get_loc("Ticket Raised (UTC)"), dataset.columns.get_loc("Users Off Days"), 20, format1)
                #worksheet.set_column(dataset.columns.get_loc("Team Users"), dataset.columns.get_loc("Users Next Shift"), 20, format1, {'level': 1, 'hidden': True})
                #worksheet.set_column(dataset.columns.get_loc("Users Available"), dataset.columns.get_loc("Destination PORT"), 20, format1)
    
                writer.save()        
            #Utils.saveActionsFile(dataset)
                    
    # Save dataset in .txt file
    def saveTXTFile(dataset, name):
        # Excel limit row is 1,048,576 
        if dataset.shape[0] > 1000000:
            print("Saved on txt file due to excel limit rows!")
            name = "./Output/Generation/" + name + ".txt"
            dataset.to_csv(name, encoding='utf-8', index=False, sep=';')
            #numpy_array = dataset.to_numpy()
# =============================================================================
#             np.savetxt(name, numpy_array, 
#                    header = header,
#                    delimiter=';', fmt='%s' , comments='')
# ============================================================================
            return True
        else:
            return False

    # Saves a new excel file with information regarding the actions taken by each subfamily and client
    def saveActionsFile(dataset, actions_taken):
        
        #print("len", len(dataset))
        dataset = dataset[['ID', 'Subfamily', 'Action Chosen']]

        actions_cleaned = []
            
        for i in dataset['Action Chosen']:
            #print("Prev action:", i)
            action = i.replace("''", ",")
            action = action.replace("'", "")
            action_divided = action.split(",")
            action_str = [str(x) for x in action_divided]
            #action_str.insert(0, "init")
            #print("New Action:", action_str)
            actions_cleaned.append(action_str)
        
        all_techniques = []
        
        for l in actions_cleaned:
            for action in l:
                if action not in all_techniques:
                    all_techniques.append(action)
                    
        #print("All techniques:", all_techniques)
        #print("Techniques length:", len(all_techniques))
        
        label_encoder = LabelEncoder()
        integer_encoded = label_encoder.fit_transform(all_techniques)
        #print(integer_encoded)
        mapping = dict(zip(label_encoder.classes_, range(len(label_encoder.classes_))))
        #print(mapping)
        
        actions_list_encoded = []
        actions_encoded = []
        for p in actions_cleaned:
            #print("Transition", l)
            for k in p:
                #print("State")
                actions_encoded.append(mapping[k])
                
            actions_list_encoded.append(list(actions_encoded))
            actions_encoded = []
        #print(actions_list_encoded)
        #print(Utils.findMaxLength(actions))
        
        columns = []
        for k in range(1, Utils.findMaxLength(actions_cleaned) + 1):
            columns.append("Step " + str(k))
        #print("Columns:", columns)
        
        actions_steps = pd.DataFrame(actions_cleaned,columns=columns)
        actions_steps = actions_steps.fillna("-")
        actions_steps['ID'] = dataset['ID']

        columns_normalized = []
        for j in range(1, Utils.findMaxLength(actions_cleaned) + 1):
            columns_normalized.append("Step normalized " + str(j))
        #print("Columns:", columns)
        
        actions_steps_normalized = pd.DataFrame(actions_list_encoded,columns=columns_normalized)
        actions_steps_normalized = actions_steps_normalized.fillna("-")
        actions_steps_normalized['ID'] = dataset['ID']
        
        actions_dataframe = pd.merge(dataset, actions_steps, on="ID")
        actions_dataframe = pd.merge(actions_dataframe, actions_steps_normalized, on="ID")
        actions_dataframe['combined'] = actions_list_encoded
        
        v = dataset[['Subfamily', 'Action Chosen']]
        actions_dataframe = actions_dataframe[v.replace(v.apply(pd.Series.value_counts)).gt(30).all(1)]

        name = "./Output/Generation/actions" + ".xlsx"
        writer = pd.ExcelWriter(name, engine='xlsxwriter', engine_kwargs={'options': {'strings_to_numbers': False}})
        actions_dataframe.to_excel(writer, sheet_name='Actions Info', index = False)  
        
        workbook  = writer.book
        worksheet = writer.sheets['Actions Info']   
        format1 = workbook.add_format()
        format1.set_align('center')
        writer.save()     
        
        # Add special format for better reading and debug
        #for k in range(1, Utils.findMaxLength(actions) + 1):
        final_column = 'Step normalized ' + str(Utils.findMaxLength(actions_cleaned))
        #final_column = 'Step ' + str(Utils.findMaxLength(actions))
        worksheet.set_column(actions_dataframe.columns.get_loc('ID'), actions_dataframe.columns.get_loc(final_column), 12, format1)

    #Get the special actions (start, end and transfer)
    def getLockedTechniques():
        
        #print("Special Operations:", Variables.actions_checkpoints)
        init_operations = Variables.actions_checkpoints["init_op"].values()
        #print("init", init_operations)
        end_operations = Variables.actions_checkpoints["end_op"].values()
        #print("end", end_operations)
        transfer_actions = list(Variables.actions_checkpoints["transfer_sub_op"].keys())
        #print("transfer", transfer_actions)
        
        initial_actions = []
        for opt in init_operations:
            initial_actions+= list(opt.keys())
        #print("Initial", initial_actions)
        
        final_actions = []
        for opt in end_operations:
            final_actions+= list(opt.keys())
        #print("Final", final_actions)
        
        return initial_actions, final_actions, transfer_actions

    # Resets the output folder
    def resetOutputFolder(path):
        
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            #print("filename", file_path)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
                
        print("All files from " + path + "  were removed")

    # Finds the max length of a list from a list of lists
    def findMaxLength(lst):
        #maxList = max((x) for x in lst)
        maxLength = max(len(x) for x in lst)
        return maxLength
        
    # Check if analysts are assigned to teams
    def checkAnalystsInfo():
        
        for i in Variables.analysts_skills.keys():
            #print("Team", i)
            for l in Variables.analysts_skills[i].keys():
                #print("Analyst", l)
                if len(list(Variables.analysts_skills[i][l].items())) == 1:
                    return True
                else:
                    return False
                
    # Split dictionary in two dictionaries
    def splitDict(d):
        n = len(d) // 2          # length of smaller half
        i = iter(d.items())      # alternatively, i = d.iteritems() works in Python 2
    
        d1 = dict(itertools.islice(i, n))   # grab first n items
        d2 = dict(i)                        # grab the rest

        return d1, d2
    
    # Returns the differences between two dates (in minutes)
    def calculateDateDiff(date1, date2):
         #print("Date unsolved:", date1)
         #print("Date fixed", date2)
         d1 = Utils.convertStrToDatetime(date1)
         d2 = Utils.convertStrToDatetime(date2)
         time_diff = d2 - d1
         #print("time diff", time_diff)
         diff_minutes = (time_diff.days * 24 * 60) + (time_diff.seconds/60)
         #print("diff days", time_diff.days)
         
         return diff_minutes
     
    # Merges dictionaries
    def mergeDictionaries(dict1):
        result = {}
        for d in dict1:
            result.update(d)
            
        print("Merged dict:", result)
        return result
    
    # prints a list
    def printList(list_):
        for i in list_:
            print("Action:", i)