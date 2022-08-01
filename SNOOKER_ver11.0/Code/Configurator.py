# -*- coding: utf-8 -*-
"""
Created on Fri Apr  2 12:10:27 2021

@author: Leonardo Ferreira
@goal: Reads the configuration file and manages several parameters for the generation
"""

import json
import os
import random
import ruamel.yaml

import string
from datetime import datetime
from fractions import Fraction

# import ipaddress
import pandas as pd
from PyQt5.QtWidgets import QFileDialog

from Code.Variables import Variables


class Configurator:
    
    config_data = {}
    
    def checkConfigFile(domain):
        
        path = "Configurations/" + domain + "/Init_cfg.yaml"
        
        if os.path.exists(path):
            return True
        
    def readConfigFile(domain, path):
        
        try:
            with open(path, "r") as fh:
                #yaml= ruamel.yaml.YAML(typ='safe',)
                #print("Path:", path)
                config_data = ruamel.yaml.load(fh, Loader=ruamel.yaml.RoundTripLoader)
                return config_data
        except FileNotFoundError:
            print("Couldn't find path!" )
            
    def checkConfigParameter(config, param):

        if param in config.keys():
            return True
        else:
            print("The config doesn't have the param " + str(param))
    
    def loadInitConfig(domain):

        path = "Configurations/" + domain + "/Init_cfg.yaml"
        Configurator.config_data = Configurator.readConfigFile(domain, path)
        
        try:
            Variables.standard_params['parameters'] = {}
            Variables.standard_params['parameters']['train_ticket'] = Configurator.config_data["standard_generation_parameters"]['train_ticket']
            Variables.standard_params['parameters']['families_number'] = Configurator.config_data["standard_generation_parameters"]['families_number']
            Variables.standard_params['parameters']['minsubfamilies_number'] = Configurator.config_data["standard_generation_parameters"]['minsubfamilies_number']
            Variables.standard_params['parameters']['maxsubfamilies_number'] = Configurator.config_data["standard_generation_parameters"]['maxsubfamilies_number']
            Variables.standard_params['parameters']['techniques_number'] = Configurator.config_data["standard_generation_parameters"]['techniques_number']
            Variables.standard_params['parameters']['minsubtechniques_number'] = Configurator.config_data["standard_generation_parameters"]['minsubtechniques_number']
            Variables.standard_params['parameters']['maxsubtechniques_number'] = Configurator.config_data["standard_generation_parameters"]['maxsubtechniques_number']
            
            Variables.incident_area = Configurator.config_data["incident_area"]
            Variables.teams_info_pool = Configurator.config_data["teams_info_pool"]
            Variables.analysts_skills = Configurator.config_data["analysts_skills"]
            Variables.teams_frequency = Configurator.config_data["teams_freq"]

            Variables.suspicious_countries = Configurator.config_data["suspicious_countries"]
            #print(Variables.suspicious_countries)
            Variables.suspicious_countries = dict(sorted(Variables.suspicious_countries.items()))
            #print(Variables.selected_countries)
            Variables.suspicious_selector = True	
        except KeyError as e:
            if str(e).find("generation"):
                Variables.suspicious_selector = False	
            print(domain + " configuration file doesn't the field " + str(e))
            print("Couldn't load " + domain + " configuration file!") 
            return False
            
        #print(Variables.teams_info_pool)
        Variables.family_time_4h = Configurator.config_data["family_time_4h"]
        Variables.family_weights = Configurator.config_data["families_weights"]
        Variables.default_alert_pool = Configurator.config_data["families"]
        Variables.week_time = Configurator.config_data["week_time"]
        Variables.day_stages = Configurator.config_data["day_stages"]
        Variables.shifts = Configurator.config_data["shifts"]
        Variables.ips_pool = Configurator.config_data["ips_pool"]
        Variables.priority_levels = Configurator.config_data["priority_levels"]
        Variables.start_date = Configurator.config_data["start_date"]
        Variables.end_date = Configurator.config_data["end_date"]
            
        for i in Variables.incident_area[domain].keys():
            if isinstance(Variables.incident_area[domain][i]['prob'], str): 
                Variables.incident_area[domain][i]['prob'] = float(sum(Fraction(s) for s in  Variables.incident_area[domain][i]['prob'].split()))
                   
        return True 
        
    def updateConfigFile(param, content, domain, output_path):
        
        Configurator.config_data[param].update(content)
        
        with open(output_path, 'w') as f:
            #yaml=ruamel.yaml.YAML(typ='safe')
            ruamel.yaml.dump(Configurator.config_data, f, Dumper=ruamel.yaml.RoundTripDumper)
            
        print(domain + " custom configuration saved!")    
        #print(Configurator.config_data[param])
        
    def readCustomConfigSection(domain, section):
        
        if Configurator.config_data:
            path = "Configurations/" + domain + "/Init_cfg.yaml"
            Configurator.config_data = Configurator.readConfigFile(domain, path)
        return Configurator.config_data[section] 
                 
    def loadConfigWindow(window):
        
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(window, "QFileDialog.getOpenFileName()", "Custom_cfg.yaml","Text files (*.yaml)", options=options)
        return filename
    
    def saveConfigWindow(window):
        
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(window, 'Save as... File', 'Custom_cfg', filter="YAML (*.yaml)",options=options)
        return filename
    
    def getCountriesFile():
        
        path = 'Resources/Countries/Countries_updated.json'
        with open(path) as country_file:
            data = json.load(country_file)
            countries_data = data['countries']
            for p in countries_data:
                Variables.countries[p] = countries_data[p]
                
    def getTicketSazonality():
        
        col_dtype={"ID": int,  
           "Location": 'category',
           "Raised (UTC)": str, 
           "Fixed": str,  
           "Family": 'category',
           "Subfamily": 'category',
           "Client": 'category',
           "Status": 'category',
           "Suspicious": "category",
           "Source IP": "category"}
        
        dataset = pd.read_csv("realDatasetCleaned.csv", sep=";", dtype=col_dtype)  
        #dataset = pd.read_csv("../../RealDatasetCleaner/NoResilient/real_dataset_updated_cleaned.csv", sep=";", dtype=col_dtype)   
        dataset["Raised (UTC)"] = pd.to_datetime(dataset['Raised (UTC)'], dayfirst=True)
        dataset.sort_values(by='Raised (UTC)', inplace=True)
        #dataset["discovered_date"] = pd.to_datetime(dataset['discovered_date'], dayfirst=True)
        #dataset.sort_values(by='discovered_date', inplace=True)
        #print(dataset.head(10))
        dataset['Year/month'] = dataset['Raised (UTC)'].apply(lambda x: datetime.strftime(x, '%m'))
        
        ticket_distribution = dataset['Year/month'].value_counts().reset_index(name="Count")
        family_distribution = dataset.groupby(['Year/month', 'Family']).size().reset_index(name="Count")
        #print(ticket_distribution)
        #family_distribution.set_option('display.max_rows', None)
        #pd.set_option('display.max_rows', None)
        #print(family_distribution.head(3000))
        #print(family_distribution)
        
        Variables.ticket_seasonality["high_season"] = {}
        Variables.ticket_seasonality["high_season"]["train_ticket"] = 0
        Variables.ticket_seasonality["off_season"] = {}
        Variables.ticket_seasonality["off_season"]["train_ticket"] = 0
        
        ticket_series = dataset['Year/month'].value_counts()
        #ticket_series = Variables.standard_params['parameters']['ticket_number']
        
        for index, row in family_distribution.iterrows():    
            #print("index", index)
            #print("Familia: ", row["Family"])
            month = int(row["Year/month"])
            family = row["Family"]
            #print("mes", month)
            month_name = datetime(1900, month, 1).strftime('%B')
            #print("month: ", month_name)
            #print(distribution[p])
            if month_name not in Variables.family_seasonality.keys():
                #print("Month created")
                Variables.family_seasonality[month_name] = {}
                Variables.family_seasonality[month_name][family] = 0
             
            ticket_number = ticket_series.get(key = row["Year/month"])
            #print("Ticket number", ticket_number)
            Variables.family_seasonality[month_name][family] = row["Count"]/ticket_number
            
            if month == 1 or month == 2 or 10 <= month <= 12:
                Variables.ticket_seasonality["off_season"]["train_ticket"] += row["Count"]
            else:
                Variables.ticket_seasonality["high_season"]["train_ticket"] += row["Count"]
        
        Variables.ticket_seasonality["off_season"]["prob"] = Variables.ticket_seasonality["off_season"]["train_ticket"]/len(dataset)  
        Variables.ticket_seasonality["high_season"]["prob"] = Variables.ticket_seasonality["high_season"]["train_ticket"]/len(dataset)
        
        Variables.ticket_seasonality["off_season"]["months"] = [1, 2, 10, 11, 12] 
        Variables.ticket_seasonality["high_season"]["months"] = [3, 4, 5, 6, 7, 8, 9] 
        #print(Variables.ticket_sazonality)
            
# =============================================================================
#         for l in Variables.family_seasonality.keys():
#             print("Month", l)
#             print(Variables.family_seasonality[l])
#             print("\n")     
# =============================================================================
            
    def getSuspiciousIPs():
        path = 'Resources/Ips/bad_ips.txt'
        
        with open(path, 'r') as file:
            fileread = file.readlines()
            
        for line in fileread:
            line_split = line.split("\t")
            #print("Line", line_split)
            Variables.suspicious_ips[line_split[0]] = line_split[1].rstrip()
        
        #print("Suspicious IPS", Variables.suspicious_ips)
        #print("Size Suspicious IPS", len(Variables.suspicious_ips))
        
    def getActionsCheckpoints():
        
        techniques_pool = string.ascii_letters + string.digits    
        #print("\nTechniques pool:", techniques_pool)
        
        init_techniques_pool = random.sample(techniques_pool, k = 2)
        #print("Initial techniques:", init_techniques_pool)
        end_techniques_pool = random.sample([tec for tec in techniques_pool if tec not in init_techniques_pool], k = 2)
        #print("End techniques:", end_techniques_pool)
        Variables.actions_checkpoints["init_op"] = {}
        Variables.actions_checkpoints["end_op"] = {}
        Variables.actions_checkpoints["transfer_sub_op"] = {}
        transfer_op = random.choice([tec for tec in techniques_pool if (tec not in init_techniques_pool and tec not in end_techniques_pool)])
        Variables.actions_checkpoints["transfer_sub_op"][transfer_op] = random.randint(1, 5)
        #print("Special techniques techniques:", Variables.actions_checkpoints)
        
        subtechniques_used = []
        for i in init_techniques_pool:
            Variables.actions_checkpoints["init_op"][i] = {}
            for l in range(2):
                ## Add hexadecimal options like the the subactions created later in the subfamily action generation
                init_sup_opt = random.sample([tec for tec in techniques_pool if (tec not in init_techniques_pool and tec not in end_techniques_pool and tec != transfer_op and tec not in subtechniques_used)], k = 1)
                #print("Init subopt", init_sup_opt[0])
                subtechniques_used.append(init_sup_opt[0])
                Variables.actions_checkpoints["init_op"][i][init_sup_opt[0]] = random.randint(1, 5)
            
        #print("Sub Techniques used:", subtechniques_used)
        #print("Special Operations:", Variables.actions_checkpoints)
        for e in end_techniques_pool:
            Variables.actions_checkpoints["end_op"][e] = {}
            for k in range(2):
                end_sup_opt = random.sample([tec for tec in techniques_pool if (tec not in init_techniques_pool and tec not in end_techniques_pool and tec != transfer_op and tec not in subtechniques_used)], k = 1)
                #print("End subopt", end_sup_opt[0])
                subtechniques_used.append(end_sup_opt[0])
                Variables.actions_checkpoints["end_op"][e][end_sup_opt[0]] = random.randint(1, 5)
            
        #print("Special Operations:", Variables.actions_checkpoints)
        
    def mergeCountriesData():
        
        path = 'Resources/Countries/Countries.json'
        
        countries_available = []
        countries_ips = {}
        
        with open(path) as country_file:
            countries_data = json.load(country_file)
            for p in countries_data['countries']:
                if p not in countries_available:
                    countries_available.append(p)      

        #print(countries_available) 
        #print(len(countries_available))
        
        path = 'Resources/Ips/ipv4.json'
        with open(path) as country_file:
            data_ips = json.load(country_file)
        
# =============================================================================
#         temp = []
#         path = 'Resources/ipv4.json'
#         with open(path) as country_file:
#             data_ips = json.load(country_file)
#             for p in data_ips:
#                 if p["country_name"] != "null" and p["country_name"] not in temp:
#                     temp.append(p["country_name"])
#             
#         print(temp) 
#         print(len(temp))
# =============================================================================
        
        for p in data_ips:
            if p["country_name"] != "null" and p["country_name"] in countries_available:
                if p["country_name"] not in countries_ips.keys():
                    countries_ips[p["country_name"]] = []
                    countries_ips[p["country_name"]].append(p["network"])
                else:
                    countries_ips[p["country_name"]].append(p["network"])
                    
        #print("Dict", countries_ips)
        #print(len(countries_ips.keys()))

        for p in countries_data['countries']:
            countries_data["countries"][p]["ips"] = countries_ips[p]

        #print("Update", countries_data)
        json_object = json.dumps(countries_data, indent = 4)

        with open("sample.json", "w") as outfile:
            outfile.write(json_object)

# =============================================================================
# os.chdir("../")
# Configurator.mergeCountriesData()
# =============================================================================


#print(ipaddress.IPv6Address('2002::' + "43.241.136.0").compressed)
# =============================================================================
# os.chdir("../")
# Configurator.getSuspiciousIPs()
# 
# =============================================================================
