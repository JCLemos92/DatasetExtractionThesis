import pandas as pd

# ROWS
# ID: number
# Location: string
# Raised (UTC): date
# Allocated: date
# Stages: date[]
# Fixed: date
# Client: string - contar cada cliente
# Family: string - contar cada família
# Family Action: string - contar cada family action
# Subfamily: string - contar cada subfamília
# Subfamily Action: string - contar cada subfamily action
# Subfamily Action Duration: number
# Team: string - contar cada equipa
# Users in the Shift: users[]
# Users Next Shift: users[]
# Users Competent: users[]
# User actions: action[]
# User Chosen: string - user
# Action Chosen: string
# Action Chosen Status: string
# Action Chosen Duration: number
# Action Chosen (With Outlier): number
# Ticket Duration: number
# Escalate: boolean
# Status: string - contar
# Outlier: boolean

#df['Location'].value_counts() - counts per country

path = '../../Output/Generation/generatedDataset.csv'
f = open("../../Output/Analysis/Cars/SimpleMetaFeatures.txt", "w")

df = pd.read_csv(path, sep=";", index_col=False)

instance_count = df.shape[0]  # Gives number of rows
class_count = df.shape[1]  # Gives number of columns
attribute_count = instance_count * class_count
boolean_true = df['Escalate'].values.sum() + df['Outlier'].values.sum()
boolean_false = (~df['Escalate']).values.sum() + (~df['Outlier']).sum()
boolean_count = boolean_true + boolean_false
numeric_count = df.count(numeric_only=True).sum()

categorical_count = df['Location'].value_counts().sum() + df['Client'].value_counts().sum() + \
                    df['Family'].value_counts().sum() + df['Family Action'].value_counts().sum() + \
                    df['Subfamily'].value_counts().sum() + df['Subfamily Action'].value_counts().sum() + \
                    df['Team'].value_counts().sum() + df['Users in the Shift'].value_counts().sum() + \
                    df['Users Next Shift'].value_counts().sum() + df['Users Competent'].value_counts().sum() + \
                    df['User actions'].value_counts().sum() + df['User Chosen'].value_counts().sum() + \
                    df['Action Chosen'].value_counts().sum() + df['Action Chosen Status'].value_counts().sum()

date_count = df['Raised (UTC)'].value_counts().sum() + df['Allocated'].value_counts().sum() + \
             df['Stages'].value_counts().sum() + df['Fixed'].value_counts().sum()

missing_data_count = df.isnull().sum().sum()

catToNum = categorical_count/numeric_count
numToCat = numeric_count/categorical_count
attrToInst = attribute_count/instance_count
classToAttr = class_count/attribute_count
dateNumPercentage = date_count/numeric_count * 100

f.write(f'Number of Classes: {class_count}.\n')
f.write(f'Number of Instances: {instance_count}.\n')
f.write(f'Attribute count: {attribute_count}.\n')
f.write(f'Boolean registers count: {boolean_count}.\n')
f.write(f'Numeric registers count: {numeric_count}.\n')
f.write(f'Date registers count: {date_count}.\n')
f.write(f'Categorical registers count: {categorical_count}.\n')
f.write(f'Missing data: {missing_data_count}.\n')
f.write(f'attrToInst ratio: {attrToInst}.\n')
f.write(f'classToAttr ratio: {classToAttr}.\n')
f.write(f'catToNum ratio: {catToNum}.\n')
f.write(f'numToCat ratio: {numToCat}.\n')
f.write(f'Percentage of numbers that are dates: {dateNumPercentage}.\n')
f.close()
print('Simple meta-feature analysis complete')