## -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 21:42:16 2020

@author: Leonardo Ferreira
@goal: Manages the main processes of the generator
"""


#from Code.Generator.GeneratorPerformance import GeneratorPerformance
from Code.Generator.TicketGenerator import TicketGenerator
from Code.Utils import Utils
from Code.Variables import Variables
from Code.Generator.ShiftGenerator import ShiftGenerator
from Code.Configurator import Configurator

from datetime import datetime
import os

def main(thread, domain, train_tickets, families, family_types, min_subfamilies, max_subfamilies, techniques, min_subtechniques, max_subtechniques):

    print("Start Generation...")        
    print("Domain:", domain)
    print("Number of tickets:", train_tickets)
    print("Number of Families:", families)
    print("Types of Families:", family_types)
    print("Minimum number of Families:", min_subfamilies)
    print("Maximum number of Families:", max_subfamilies)
    print("Number of Techniques:", techniques)
    print("Minimum number of sub techniques:", min_subtechniques)
    print("Maximum number of sub techniques:", max_subtechniques)
    print("Outlier Rate:", Variables.outlier_rate)
    print("Debug Mode:", Variables.debug)
    print("Shifts Mode:", Variables.allshifts_occupied)
    print("Plots:", Variables.print_plots)
    print("Distribution:", Variables.distribution_mode)

    ticket_generator = TicketGenerator()
    ticket_generator.family_pool = Variables.default_alert_pool
    curr_time = datetime.now()
    #generation_init = curr_time
    
    Utils.familyProbability(thread, 10, families, family_types, min_subfamilies, max_subfamilies, ticket_generator)
    end = datetime.now()
    time_delta = end - curr_time
    wait_time = time_delta.total_seconds()
    curr_time = end
    print("\nFamily generation Time spent: " + str(wait_time) + " seconds")
    
    if 1 == True: #if not thread.canceled:
        if Variables.reset_user_shift_daysoff:
            ShiftGenerator.resetShiftsDaysOff(domain, Variables.allshifts_occupied, ticket_generator.analysts_info)
        else:
            ticket_generator.analysts_info = Variables.analysts_skills
            ShiftGenerator.setRemainingUserInfo(ticket_generator.analysts_info)
            
        #Utils.getAllAnalysts(ticket_generator.all_analysts)
        ShiftGenerator.setAnalystsAvailability(ticket_generator.analysts_info, ticket_generator.analysts_availability)
    
    if 1 == True: #if not thread.canceled:
        ticket_generator.trainTicketInfoGenerator(thread, 20, train_tickets)
    
        end = datetime.now()
        time_delta = end - curr_time
        wait_time = time_delta.total_seconds()
        curr_time = end
        print("Train Ticket basic data Time spent: " + str(wait_time) + " seconds")
    
    if 1 == True: # if not thread.canceled:
        ticket_generator.actionsGenerator(thread, 5, techniques, min_subtechniques, max_subtechniques)
    
        end = datetime.now()
        time_delta = end - curr_time
        wait_time = time_delta.total_seconds()
        curr_time = end
        print("Family and subfamily Actions Generation Time spent: " + str(wait_time) + " seconds")
    
    if 1 == True: #if not thread.canceled:
        ticket_generator.teamsAssignment(thread, 5)
    
        end = datetime.now()
        time_delta = end - curr_time
        wait_time = time_delta.total_seconds()
        curr_time = end    
        print("Analysts and Teams available Time spent: " + str(wait_time)  + " seconds")
    
    if 1 == True: #if not thread.canceled:
        tickets_to_replicate = ticket_generator.findSimilarAndCoordinatedTickets(thread, 15)
        end = datetime.now()
        time_delta = end - curr_time
        wait_time = time_delta.total_seconds()
        curr_time = end
        print("Similar and Coordinated tickets search Time spent: " + str(wait_time)  + " seconds")

    if 1 == True: #if not thread.canceled:
        ticket_generator.analystsAssignment(thread, tickets_to_replicate, 15)
        
        end = datetime.now()
        time_delta = end - curr_time
        wait_time = time_delta.total_seconds()
        curr_time = end
        print("Analyst Ticket Search Time spent: " + str(wait_time) + " seconds")

    if 1 == True: #if not thread.canceled:
        ticket_generator.trainTicketAdvancedInfo(thread, 5)
    
        end = datetime.now()
        time_delta = end - curr_time
        wait_time = time_delta.total_seconds()
        curr_time = end    
        print("Ticket Advanced Data Time spent:", wait_time)

    if 1 == True: #if not thread.canceled:
        ticket_generator.trainDatasetOutput(thread, 20)
    
        end = datetime.now()
        time_delta = end - curr_time
        wait_time = time_delta.total_seconds()
        curr_time = end
        print("Train Tickets export Time spent: " + str(wait_time) + " seconds")
        
        if Variables.format_selected_idx == 0:
            os.system('start excel.exe ./Output/Generation/trainDataset.csv')
        else:
            os.system('start excel.exe ./Output/Generation/trainDataset.xlsx')
    else:
        print("Generation canceled!")

# =============================================================================
# #### Used to do profiling on the project
# if __name__ == '__main__':
# 
#     os.chdir("../../")
#     Utils.closeExcel()
#     Configurator.getCountriesFile()
#     Configurator.getSuspiciousIPs()
#     Configurator.getActionsCheckpoints()
#     if Configurator.loadInitConfig("Cybersecurity"):
#         print("Cybersecurity configuration file successfully loaded!") 
#             
#     Configurator.getTicketSazonality()
#     main(None, "Cybersecurity", 10000, 10, 7, "Random", 1, 11, 7, 2, 3)   
# 
# =============================================================================
