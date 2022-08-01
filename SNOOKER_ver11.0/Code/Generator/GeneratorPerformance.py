# -*- coding: utf-8 -*-
"""
Created on Tue Dec 15 11:54:50 2020

@author: Leonardo Ferreira
@goal: Analyses the output generated (deprecated)
"""

import matplotlib.pyplot as plt
from datetime import datetime
from collections import Counter

class GeneratorPerformance:
    
    def __init__(self):
        self.analysts_performance = {}

    # Analyse the performance of analysts
    def analystInfo(self, tickets_info):
    
        for i in tickets_info.keys():
            curr_ticket = tickets_info[i]
            analyst = curr_ticket['analyst']
    
            if analyst not in self.analysts_performance.keys():         
                 self.analysts_performance[analyst] = {}
                 self.analysts_performance[analyst]['Number Tickets'] = 1
                 self.analysts_performance[analyst]['Time spent on Tickets'] = curr_ticket['duration']
            else:
                 self.analysts_performance[analyst]['Number Tickets'] =  self.analysts_performance[analyst]['Number Tickets'] + 1
                 self.analysts_performance[analyst]['Time spent on Tickets'] = self.analysts_performance[analyst]['Time spent on Tickets'] + curr_ticket['duration']
   

    def performanceAnalysis(self, start, alert_family, ticket_priority, ticket_teams, subfamily_problematic, analysts_inshift, analysts_chosen, analysts_actions_duration, tickets_info):
    
        print("\nAnalysis start...\n")
        end = datetime.now()
        time_delta = end - start
        wait_time = time_delta.total_seconds()

        print("Time elapsed in seconds: ", wait_time)
        #print("Time elapsed in minutes: ", wait_time/60)
    
# =============================================================================
#         #Returns the most common ticket family
#         alert_family_counter = Counter(alert_family)
#         print("\nAlert Family Counter: ", alert_family_counter)
#         print("Most Frequent Family: " + str(alert_family_counter.most_common(1)[0][0]) + " with the frequency of " + str(alert_family_counter.most_common(1)[0][1]))
#         print("Least Frequent Family: " + str(alert_family_counter.most_common()[-1][0]) + " with the frequency of " + str(alert_family_counter.most_common()[-1][1]))
#     
#         x1_keys = list(alert_family_counter.keys())
#         x1_freq = list(alert_family_counter.values())
#     
#         fig = plt.figure()
#         ax = fig.add_axes([0,0,1,1])
#         ax.bar(x1_keys, x1_freq)
#         plt.show()
#     
#         #Returns the most common and less common ticket priority
#         priority_counter = Counter(ticket_priority)
#         print("\nPriority Counter: ", priority_counter)
#         print("Most Frequent Priority: " + str(priority_counter.most_common(1)[0][0]) + " with the frequency of " + str(priority_counter.most_common(1)[0][1]))
#         print("Least Frequent Priority: " + str(priority_counter.most_common()[-1][0]) + " with the frequency of " + str(priority_counter.most_common()[-1][1]))
#         
#         x2_keys = list(priority_counter.keys())
#         x2_freq = list(priority_counter.values())
#         
#         fig = plt.figure()
#         ax = fig.add_axes([0,0,1,1])
#         ax.bar(x2_keys, x2_freq,  color='red')
#         plt.show()
#     
#         #Returns the most common team and less common team
#         team_counter = Counter(ticket_teams)
#         print("\nMost Frequent Team: " + str(team_counter.most_common(1)[0][0]) + " with the frequency of " + str(team_counter.most_common(1)[0][1]))
#         print("Least Frequent Team: " + str(team_counter.most_common()[-1][0]) + " with the frequency of " + str(team_counter.most_common()[-1][1]))
# 
#         #Returns the number of problematic tickets
#         sub_problematic_counter = Counter(subfamily_problematic)
#         print("\nThere are " + str(sub_problematic_counter.most_common(1)[0][1]) + str(' ') + str(sub_problematic_counter.most_common(1)[0][0]) + " tickets")
#         print("There are " + str(sub_problematic_counter.most_common()[-1][1]) + str(' ') + str(sub_problematic_counter.most_common()[-1][0]) + " tickets")
#     
#         #Returns number of times that required changing the shift
#         no_users_counter = analysts_inshift.count("No users available. Check next shift!")
#         ending_shift_counter = analysts_inshift.count("Time to fix will surpass the analyst's maximum shift!")
#         print("\nThe tickets were delayed " + str(no_users_counter + ending_shift_counter) + str(" times"))
#         print("The tickets were delayed " + str(no_users_counter) + str(" time(s) because there were no analysts available in the shift"))
#         print("The tickets were delayed " + str(ending_shift_counter) + str(" times(s) because the time to fix the ticket would surpass the analyst shift"))
#     
#         #Returns the user who solved the most tickets and the one that solved less tickets
#         analysts_counter = Counter(analysts_chosen)
#         print("\nThe user with the most tickets solved was " + str(analysts_counter.most_common(1)[0][0]) + " with " + str(analysts_counter.most_common(1)[0][1]) + str(" tickets"))
#         print("The user with less tickets fixed was " + str(analysts_counter.most_common()[-1][0]) + " with " + str(analysts_counter.most_common()[-1][1]) + str(" tickets"))
#     
#         #Returns average time taken to fix a ticket
#         actions_duration_average = sum(analysts_actions_duration) / len(analysts_actions_duration)
#         print("\nThe average to solve a ticket was " + str(actions_duration_average) + str(" minutes"))
#     
#         self.analystInfo(tickets_info)
#     
#         for l in self.analysts_performance.keys():
#             curr_analyst = self.analysts_performance[l]
#             analyst_avg_time = round(curr_analyst['Time spent on Tickets']/curr_analyst['Number Tickets'], 2)
#             print("The average time spent by the user " + str(l) + " was " + str(analyst_avg_time) + " minutes")
#     
#         x3_keys = list(self.analysts_performance.keys())
#         x3_freq = []
#     
#         for i in self.analysts_performance.values():
#             x3_freq.append(i['Number Tickets'])
#     
#         fig = plt.figure()
#         ax = fig.add_axes([0,0,1,1])
#         ax.bar(x3_keys, x3_freq,  color='black')
#         plt.show()
# 
# =============================================================================
