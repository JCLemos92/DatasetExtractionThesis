# -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 11:43:03 2020
@author: Leonardo Ferreira
@goal: Stores some variables used across the project
"""

class Variables:

    standard_params = {}
    default_alert_pool = {}
    incident_area = {}
    teams_info_pool = {}
    teams_frequency = {}
    analysts_skills = {}
    analists_actions = {}
    family_time_4h = {}
    week_time = {}
    day_stages = {}
    shifts = {}
    countries = {}
    suspicious_countries = {}
    suspicious_ips = {}
    family_seasonality = {}
    ticket_seasonality  = {}
    actions_checkpoints = {}
    
    dataset_field_pool = ["Cybersecurity", "Finance", "Health", "Education"]
    actions_operations = ['=', '+', '-', '%']
    ips_pool = []
    priority_levels = []
    family_weights = []
    
    start_date = ""
    end_date = ""
    
    ticket_seasonality_selector = True
    family_seasonality_selector = True
    ip_selector = True
    outlier_selector = True
    suspicious_selector = False
    multiple_attack_selector = False
    debug = False 
    generation_mode = "standard"
    family_default_mode = True
    distribution_mode = "normal"
    time_probabilities_mode = True
    week_equal_probabilities = True
    abort = False
    allshifts_occupied = True
    lower_teams = True
    reset_user_shift_daysoff = True
    print_plots = False
    
    ip_selected_idx = 0
    format_selected_idx = 0 
    analyst_subfamily_action_probability = 0.9
    analyst_same_action_probability = 0.90
    outlier_rate = 10
    outlier_cost = 0.1
    escalate_rate_percentage = 1
    min_coordinated_attack = 4
    max_coordinated_attack = 5
    min_coordinated_attack_minutes = 90
    max_coordinated_attack_minutes = 120
    min_subtechnique_rate = 50
    max_subtechnique_rate = 200
    min_subtechnique_cost = 2
    max_subtechnique_cost = 7
    suspicious_subfamily = 0.4
    clients_number = 2
    actions_similarity = 3