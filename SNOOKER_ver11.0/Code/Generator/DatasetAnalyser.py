# https://machinelearningmastery.com/machine-learning-in-python-step-by-step/

# Load libraries
import pandas as pd
import numpy as np
from datetime import datetime
from pandas.plotting import scatter_matrix
import matplotlib.pyplot as plt
import time
import seaborn as sns
import os
from sklearn.preprocessing import LabelEncoder

from Code.Variables import Variables
from Code.Utils import Utils

print("\014")

subfamilies = {}
transfered_tickets = {}

def change_width(ax, new_value) :
    for patch in ax.patches :
        current_width = patch.get_width()
        diff = current_width - new_value

        # we change the bar width
        patch.set_width(new_value)

        # we recenter the bar
        patch.set_x(patch.get_x() + diff * .5)
        

def cleanDataset(data):
    
    data['Raised (UTC)'] = pd.to_datetime(data['Raised (UTC)'])
    #data['Day'] = pd.DatetimeIndex(data['Raised (UTC)']).day
    #data['Weekday'] = pd.DatetimeIndex(data['Raised (UTC)']).day_name()
    #data['Month'] = pd.DatetimeIndex(data['Raised (UTC)']).month
    #data['Year'] = pd.DatetimeIndex(data['Raised (UTC)']).year
    data['Time UTC'] = pd.DatetimeIndex(data['Raised (UTC)']).time
    
    data['User'] = data['User Chosen']
    data['Action'] = data['Action Chosen']
    data['Subfamily Duration'] = data['Subfamily Action Duration']
    data['Action Duration'] = data['Ticket Duration']
    
    #data = data[data['Status'] == "Closed"]
    
    #print(data['Action Duration'])
    return data

def insert_color(row):    

    highlight1 = 'background-color: #009900;'
    highlight2 = 'background-color: #33FF33;'
    highlight3 = 'background-color: #CCFFCC;'
    highlight4 = 'background-color: #FFFF00;'
    highlight5 = 'background-color: #FF0000;'
    default = ''
    # must return one string per cell in this row
    if row['Ratings'] == 5:
        return [highlight1]
    elif row['Ratings'] == 4:
        return [highlight2]
    elif row['Ratings'] == 3:
        return [highlight3]
    elif row['Ratings'] == 2:
        return [highlight4]
    elif row['Ratings'] == 1:
        return [highlight5]
    else:
        return [default]

def extractShiftsAndRatings(data):
    
    analysts_shifts = []
    ratings = []
    
    #print(data)
    
    for index, row in data.iterrows():
        time = row['Time UTC']
        status = row['Status']
        team = row['Team']
        subfamily = row['Subfamily']
        subfamily_dur = row['Subfamily Duration']
        action_dur = row['Action Duration']
        user = row['User']
        #print("Time", time)
        
        for curr in Variables.shifts.keys():
            if Utils.isTimeBetween(Variables.shifts[curr]["start"], Variables.shifts[curr]["end"], time.strftime('%H:%M')):
                analysts_shifts.append(curr)
                break
        
        if subfamily not in subfamilies.keys():
            #print("New entry")
            subfamilies[subfamily] = {}
            #print(data[data["Subfamily"] == subfamily]['Action Duration'])
            subfamilies[subfamily]["first"] = np.percentile(data[data["Subfamily"] == subfamily]['Action Duration'].values, 25)
            subfamilies[subfamily]["median"] = np.percentile(data[data["Subfamily"] == subfamily]['Action Duration'].values, 50)
            subfamilies[subfamily]["third"] = np.percentile(data[data["Subfamily"] == subfamily]['Action Duration'].values, 75)
        
        if action_dur < subfamilies[subfamily]["first"]:
            ratings.append(5)
        elif subfamilies[subfamily]["first"] <= action_dur < subfamily_dur:
            ratings.append(4)
        elif subfamily_dur <= action_dur <= subfamilies[subfamily]["median"]:
            ratings.append(3)
        elif subfamilies[subfamily]["median"] < action_dur < subfamilies[subfamily]["third"]:
            ratings.append(2)
        elif subfamilies[subfamily]["third"] <= action_dur:
            ratings.append(1)
        else:
            ratings.append("Not Rated")
            
        if team not in transfered_tickets.keys():
            transfered_tickets[team] = {}
            transfered_tickets[team]["transfered tickets"] = 0
            transfered_tickets[team]["total tickets"] = 0
            
        if status == "Transfer":
            if user not in transfered_tickets[team].keys():
                transfered_tickets[team][user] = 1
            else:
                transfered_tickets[team][user] += 1
            transfered_tickets[team]["transfered tickets"] += 1
        
        transfered_tickets[team]["total tickets"] += 1
        
    data['Shift'] = analysts_shifts
    data['Ratings'] = ratings
    
    return data

def transferedTicketsStatistics():
    
    for i in transfered_tickets.keys():
        if i != "L4":
            #print(transfered_tickets[i]["transfered tickets"])
            #print(transfered_tickets[i]["total tickets"])
            team_rate =  transfered_tickets[i]["transfered tickets"] / transfered_tickets[i]["total tickets"]
            print(str(i) + " has " +  str(transfered_tickets[i]["transfered tickets"]) + " transfered tickets")
            print(str(i) +  " has a transfering rate of " + str(team_rate))
            for l in transfered_tickets[i].keys():
                #print("Aqui 2", l)
                if l != "transfered tickets" and l != "total tickets":
                    print(str(l) +  " transfered " + str(transfered_tickets[i][l]) + " tickets")
                    user_rate = transfered_tickets[i][l] / transfered_tickets[i]["transfered tickets"]
                    print(str(l) +  " has a transfering rate of " + str(user_rate))
            print("\n")
        else:
            print(str(i) + " has " +  str(transfered_tickets[i]["total tickets"]) + " tickets")

def plotData(name, path):

    generated = False
    if "generated" in path:
        generated = True
        print("Generated Dataset!")
    else:
        print("Real Dataset!")
        
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
        
    dataset = pd.read_csv(path, sep=";", dtype=col_dtype)   
    dataset["Raised (UTC)"] = pd.to_datetime(dataset['Raised (UTC)'], dayfirst=True)
    #dataset.sort_values(by='Raised (UTC)', inplace=True)
    dataset["Fixed"] = pd.to_datetime(dataset['Fixed'], dayfirst=True)
    #print(dataset.head(10))
    dataset['Year/month'] = dataset['Raised (UTC)'].apply(lambda x: datetime.strftime(x, '%m'))
    dataset.sort_values(by='Year/month', inplace=True)
    #dataset["Year/month"] = pd.to_datetime(dataset['Year/month'])
    dataset['start_timestamp'] = dataset['Raised (UTC)'].apply(lambda x: datetime.timestamp(x))
    dataset['end_timestamp'] = dataset['Fixed'].apply(lambda x: datetime.timestamp(x))
    dataset['duration'] = dataset['end_timestamp'] - dataset['start_timestamp']
    

    #dataset["Year/month"] = dataset["Year/month"].astype("datetime64")
    dataTypeSeries = dataset.dtypes    
    print(dataTypeSeries)
    print(dataset['Year/month'].value_counts())
    
    raised_status = dataset.groupby(['Year/month', 'Status']).size().reset_index(name="count")
    #print(raised_status)
    closed = raised_status[raised_status["Status"] == "Closed"]
    #print("Closed", closed)
    transfer = raised_status[raised_status["Status"] == "Transfer"]
    #print("Tranfer", transfer)
    #dataset_generated_plot = dataset_generated.groupby(['Year/month', 'Ticket Status'])['Ticket Status'].count().plot(kind= "bar",figsize=(10,5),legend=None)

    #print(mean_duration)
    fig, axs = plt.subplots()
    #fig.subplots_adjust(hspace=1.2)
    
    axs.bar(closed['Year/month'], closed['count'], label = 'Closed')
    axs.bar(transfer['Year/month'], transfer['count'], label = 'Transfer')
  
    for tick in axs.get_xticklabels():
        tick.set_rotation(45)
    
    #axs.set_title("Status distribution")
    axs.set_xlabel("Timerange", fontsize=12)
    axs.set_ylabel("Ticket Frequency", fontsize=12)
    plt.legend()
    
    plt.savefig("Plots/" + name + "_status_distribution.png", bbox_inches='tight')
    
    fig, axs = plt.subplots()
    ## Frequency Distribution of incident_status with barplot
    incident_status = dataset['Status'].value_counts()

    sns.set(style="darkgrid")
    sns.barplot(x= incident_status.index, y= incident_status.values, alpha=0.9)
    #axs.set_title('Frequency Distribution of incident_status')
    axs.set_xlabel('Status', fontsize=12)
    axs.set_ylabel('Number of Occurrences', fontsize=12)
    
    plt.savefig( "Plots\\" + name + "_status_frequency.png", bbox_inches='tight')
    
    # Frequency Distribution of incident_status with pie chart
    labels = dataset['Status'].astype('category').cat.categories.tolist()
    counts = dataset['Status'].value_counts()
    sizes = [counts[var_cat] for var_cat in labels]
    
    fig1, ax1 = plt.subplots()
    #ax1.set_title("Status distribution")
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=False) #autopct is show the % on plot
    ax1.axis('equal')
    plt.legend()
    
    plt.savefig('Plots\\' + name + '_status_pie.png', bbox_inches='tight')
    
    fig, axs = plt.subplots()
    mean_duration = dataset.groupby(["Year/month"])["duration"].mean().reset_index(name="dur")
    axs.bar(mean_duration['Year/month'], mean_duration['dur'])
  
    for tick in axs.get_xticklabels():
        tick.set_rotation(45)
    
    #axs.set_title("Mean Fix Duration")
    axs.set_xlabel("Timerange", fontsize=12)
    axs.set_ylabel("Time (seconds)", fontsize=12)
    
    plt.savefig('Plots\\' + name + '_mean_fix_duration.png', bbox_inches='tight')
            
    fig, axs = plt.subplots()
    category = dataset['Family'].value_counts()

    sns.set(style="darkgrid")
    sns.barplot(x= category.index, y= category.values, alpha=0.9)
    #axs.set_title('Frequency Distribution of Types of Attacks')
    axs.set_xlabel('Attack Types', fontsize=12)
    axs.set_ylabel('Number of Occurrences', fontsize=12)
    
    for tick in axs.get_xticklabels():
        tick.set_rotation(45)
    
    plt.savefig('Plots\\' + name + '_families_frequency.png', bbox_inches='tight')
    
# =============================================================================
#     fig, ax = plt.subplots(figsize=(10,6))
#     dataset.plot(x='start_timestamp', y='end_timestamp', kind='scatter', ax=ax)
#     ax.set_xticklabels([datetime.fromtimestamp(ts).strftime('%Y-%m') for ts in ax.get_xticks()])
#     ax.set_yticklabels([datetime.fromtimestamp(ts).strftime('%Y-%m') for ts in ax.get_yticks()])
# =============================================================================
    
    lb_make = LabelEncoder()
    dataset['_start'] = lb_make.fit_transform(dataset['start_timestamp'])
    le_name_mapping_start = dict(zip(lb_make.classes_, lb_make.transform(lb_make.classes_)))
    #print(le_name_mapping_start)
    
    dataset['_end'] = lb_make.fit_transform(dataset['end_timestamp'])
    le_name_mapping_end = dict(zip(lb_make.classes_, lb_make.transform(lb_make.classes_)))
    #print(le_name_mapping_end)
    
    dataset['_area'] = lb_make.fit_transform(dataset['Family'])
    le_name_mapping_category = dict(zip(lb_make.classes_, lb_make.transform(lb_make.classes_)))
    #print(le_name_mapping_category)
    
    dataset['_alert'] = lb_make.fit_transform(dataset['Subfamily'])
    le_name_mapping_alert_code = dict(zip(lb_make.classes_, lb_make.transform(lb_make.classes_)))
    #print(le_name_mapping_alert_code)
    
    dataset['_client'] = lb_make.fit_transform(dataset['Client'])
    le_name_mapping_org_name = dict(zip(lb_make.classes_, lb_make.transform(lb_make.classes_)))
    #print(le_name_mapping_org_name)
    
    dataset['_status'] = lb_make.fit_transform(dataset['Status'])
    le_name_mapping_incident_status = dict(zip(lb_make.classes_, lb_make.transform(lb_make.classes_)))
    #print(le_name_mapping_incident_status)
    
    #print(list(le_name_mapping.keys())[list(le_name_mapping.values()).index(1)])
    #fig, axs = plt.subplots()
    new_dataset = dataset[['_start', '_end', '_area', '_alert', '_client', '_status']].copy()
# =============================================================================
#     axes = scatter_matrix(new_dataset)
# 
#     for ax in axes.flatten():
#         ax.xaxis.label.set_rotation(90)
#         ax.yaxis.label.set_rotation(0)
#         ax.yaxis.label.set_ha('right')
#         
#     
#     sns.catplot('Family', 'Subfamily', data = dataset)
#     for tick in axs.get_xticklabels():
#         tick.set_rotation(45)
# =============================================================================

    # near +1 -> strong positive relation between X and Y
    # near -1 -> strong negative relation between X and Y
    # near 0 -> absence of any relationship between X and Y

    correlation = new_dataset.corr()
    #print(correlation)
    fig, axs = plt.subplots()   
    sns.heatmap(correlation, annot=True)
    plt.savefig('Plots\\' + name + '_heatmap.png', bbox_inches='tight')
    
    a4_dims = (15, 11)
    fig, ax = plt.subplots(figsize=a4_dims)
    #pd.set_option('display.max_rows', None)
    #print(dataset["Raised (UTC)"].head(1500))
    sns.countplot(x = "Year/month", hue = "Family", data = dataset, ax=ax)
    #dataset['Year/month'].value_counts().plot(kind="bar")
    change_width(ax, .18)
    plt.xticks(rotation=45)
    plt.legend(fontsize = 20, bbox_to_anchor=(1, 0.6))
    
    #ax.set_title("Family distribution over time", fontsize=20)
    ax.set_xlabel("Timerange", fontsize=20)
    ax.set_ylabel("Ticket Frequency", fontsize=20)
    
    plt.savefig('Plots\\' + name + '_families_month.png', bbox_inches='tight')
    
# =============================================================================
#     # Frequency Distribution of suspicious with pie chart
#     if generated:   
#         labels = dataset['Suspicious'].astype('category').cat.categories.tolist()
#         counts = dataset['Suspicious'].value_counts()
#         sizes = [counts[var_cat] for var_cat in labels]
#         #print(sizes)
#         fig1, ax1 = plt.subplots()
#         #ax1.set_title("Suspicious Tickets distribution")
#         ax1.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=False) #autopct is show the % on plot
#         ax1.axis('equal')
#         plt.legend()
#     
#         plt.savefig('Plots\\' + name + '_suspicious_pie.png', bbox_inches='tight')
# =============================================================================


def plotStatistics(name, path):
    
    #print(subfamilies)
    
    print("\nThe FILE " + name + " is being analysed")
    df = pd.read_csv(path, sep=";", index_col=False)
    #df.columns = ["ID", "Location", "Raised (UTC)","Fixed","Client","Family","Subfamily","Subfamily Action Duration","Team","User Chosen","Action Chosen","Action Chosen Duration","Ticket Duration","Status"]

    #print("Total Tickets", df.shape[0])
    df = cleanDataset(df)  
    df = extractShiftsAndRatings(df)   
    #transferedTicketsStatistics()
    print("Total Tickets", df.shape[0])
    df = df[df['Status'] == "Closed"]
    print("Total Tickets filtered", df.shape[0])
    
    data = df[['User', 'Family', 'Subfamily', 'Action', 'Action Duration', 'Status']]
    #print("With transfered tickets exluded", data.shape[0])

    #print(data['User'].value_counts())
    #print(data['User'].value_counts()['Pedro'])
    #print(data)

    family_distribution = data.groupby(['User', 'Family', 'Action'],  as_index=False).mean()
    #print(family_distribution)
    #print("\n")
    family_indices = family_distribution.groupby('Family')['Action Duration'].idxmin()
    #print(family_indices)
    #print("\n")
    print(family_distribution.loc[family_indices])
    
    family_avg_time = data.groupby('Family')['Action Duration'].mean().reset_index(name="AVG")
    print(family_avg_time)

    subfamily_distribution = data.groupby(['User', 'Subfamily'], as_index=False).mean()
    #print("\n")
    #print("Subfamily Distribution",subfamily_distribution)
    #print("\n")
    subfamily_indices = subfamily_distribution.groupby('Subfamily')['Action Duration'].idxmin()
    #print("Indexes",subfamily_indices)
    #print("\n")
    print("Users who solved faster",subfamily_distribution.loc[subfamily_indices])

    #family_user_count = data.groupby(['User', 'Family']).size().reset_index(name="count")
    #print(family_user_count)
    
    #subfamily_user_count = data.groupby(['User', 'Subfamily']).size().reset_index(name="count")
    #print(subfamily_user_count)

    #total = (data.groupby(['User', 'Family'], as_index=False).mean().groupby('User')['Action Duration'].mean())
    #print(total)
    
# =============================================================================
#     #Users info
#     #print(type(df))
#     n_users_count = df.User.unique().shape[0]
#     #print(n_users_count)
#     n_users = df['User'].unique()
#     #print(n_users)
#     
#     #Actions Info
#     n_actions_count = df.Action.unique().shape[0]
#     #print(n_actions_count)
#     n_actions = df.Action.unique()
#     #print(n_actions)
# 
#     #print(df.columns)
#     #print(type(df.columns))
#     df = df[['ID','Location','Raised (UTC)','Time UTC','Fixed','Family','Subfamily','Subfamily Duration','Team','Shift','User','Action', 'Action Duration', 'Status', 'Ratings']]
# 
#     if df.shape[0] < 100000:
#          output = "Output/Generation/" + name + "_preprocessed.xlsx"
#          df = df.style.apply(insert_color, subset=['Ratings'], axis=1)
#          writer = pd.ExcelWriter(output, engine='xlsxwriter')
#          df.to_excel(writer, sheet_name='Preprocessing', index = False)  
#          writer.save()
#          #os.system('start excel.exe RS_preprocessed.xlsx')
# =============================================================================
    
