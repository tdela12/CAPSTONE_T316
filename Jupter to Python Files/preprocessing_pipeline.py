# %% [markdown]
# # Preprocessing Pipeline

# %% [markdown]
# ## Import Statements

# %%
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
import numpy as np

# %% [markdown]
# ## Functions

# %%
def remove_outliers(df, group_by="TaskName", value_col="price"):
    def filter_group(group):
        Q1 = group[value_col].quantile(0.25)
        Q3 = group[value_col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        return group[(group[value_col] >= lower) & (group[value_col] <= upper)]
    
    return df.groupby(group_by, group_keys=False).apply(filter_group)

# %% [markdown]
# ## Read in Data

# %%
# CPI for price adjustment
cpi_index = pd.read_csv('data/cpi.csv')
cpi_index.head()

# %%
# Booking/Ticket data
df = pd.read_csv('data/data.csv', encoding = 'windows-1252')
df.head()

# %% [markdown]
# ## Rename Columns

# %%
df = df.rename(columns={
    'cVMake': 'Make',
    'cVMakeModel': 'Model',
    'cVYear': 'Year',
    'idFuel': 'FuelType',
    'idLitres': 'EngineSize',
    'idTransmission': 'Transmission',
    'idDrive': 'DriveType',
    'idIsHybrid': 'IsHybrid',
    'BOdoNum' : 'Odometer',
    })

# %% [markdown]
# ## Drop Columns that will not be used

# %%
columns_to_drop = ['ï»¿FCID', 'BOdoText', 'VMid']
df.drop(columns = columns_to_drop, inplace=True)
df.head()

# %% [markdown]
# ## Remove Rows
# 

# %%
# Remove custom services and repairs
df = df[df['IsCustomService'] != '1']
df = df[df['IsCustomRepair'] != '1']
df = df[df['TaskName'] != 'Custom Repair']

# Remove products and tyres as they are unpredictable without quantity information 
df = df[df['TaskName'] != '((Products))']
df = df[df['TaskName'] != '((Tyres))']
df = df[df['TaskName'] != 'Tyre Replacement']

# Remove Rare ticket types
df = df[df['BTicketType'] != 'OtherTicket']
df = df[df['BTicketType'] != 'Custom']
df = df[df['BTicketType'] != 'Basic']

# Remove Tickets with zero or negative prices 
df = df[df['PriceIncGSTRaw'] > 0]

# %% [markdown]
# ## Create Months and Kilometer Columns from TicketType

# %%
# Create Columns
df['Distance'] = None
df['Months'] = None

mask = df['BTicketType'] == 'Log'
split_1 = df.loc[mask, 'TaskName'].str.split(' - ', n=1, expand=True)
df.loc[mask, 'TaskName'] = split_1[0]
df.loc[mask, 'Rest'] = split_1[1].fillna('')

split_2 = df.loc[mask, 'Rest'].str.split(' / ', n=1, expand=True)
df.loc[mask, 'Distance'] = split_2[0]
df.loc[mask, 'Months'] = split_2[1]

mask = df['BTicketType'] == 'Capped'
split_1 = df.loc[mask, 'TaskName'].str.split(' - ', n=1, expand=True)
df.loc[mask, 'TaskName'] = split_1[0]
df.loc[mask, 'Distance'] = split_1[1].fillna('')

mask = df['BTicketType'] == 'Prescribed'
split_1 = df.loc[mask, 'TaskName'].str.split(' - ', n=1, expand=True)
df.loc[mask, 'TaskName'] = split_1[0]
df.loc[mask, 'Distance'] = split_1[1].fillna('')

df = df.drop(columns=['Rest'])

# %%
# Format as Numeric
df['Months'] = df['Months'].astype(str).str.extract(r'(\d+)')
df['Months'] = pd.to_numeric(df['Months'], errors='coerce')

df['Distance'] = df['Distance'].astype(str).str.replace(',', '', regex=False)  
df['Distance'] = df['Distance'].astype(str).str.extract(r'(\d+)')
df['Distance'] = pd.to_numeric(df['Distance'], errors='coerce')

df.head()


# %% [markdown]
# ## Create Adjusted Price based on CPI

# %%
# 1. Create date column
df['BCreatedDateAEST'] = pd.to_datetime(df['BCreatedDateAEST'], format='mixed', dayfirst=True);
df['Date'] = df['BCreatedDateAEST'].dt.date

# %%
# 2. Price Adjustment
df = df[df['PriceIncGSTRaw'] != 0]
df['Date'] = pd.to_datetime(df['Date']) # ensure 'date' is in datetime format
df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)
df = df.merge(cpi_index, on='Quarter', how='left')
base_cpi = cpi_index['CPI'].iloc[-1]
df['AdjustedPrice'] = round(df['PriceIncGSTRaw'] * (base_cpi / df['CPI']), 2) # round to 2 decimal places for consistency
df['AdjustedPrice'] = round(df['AdjustedPrice'].fillna(df['PriceIncGSTRaw'])) # use original price where CPI is missing (for current quarter which does not need adjustment)

# %%
df.head()

# %% [markdown]
# ## Remove Columns that will not be used

# %%
columns_to_drop = [ 'BCreatedDateAEST', 'CPI', 'Quarter', 'PriceIncGSTRaw' , 'BShopID', 'BShopRegionName', 'BShopPostcode', 'IsDeleted', 'BStatusFromDateTimeAEST', 'Date', 'BStatusFinal', ]
df.drop(columns = columns_to_drop, inplace=True)
df.head()

# %% [markdown]
# ## Remove Duplicate Rows

# %%
# Duplicates can skew analysis and lead to incorrect conclusions, thus it is important each row is unique. Duplicates in this dataset are considered as rows that contain the same values across all columns other than the ID columns 
print(f"size before: {df.shape}" )
df = df.drop_duplicates(subset=[col for col in df.columns if col not in ['BookingID', 'BTicketID', 'BCreatedDateAEST', 'BStatusFromDateTimeAEST']])
print(f"size after: {df.shape}" )

# %% [markdown]
# ## Remove False Negatives 

# %%
# False negatives are rows which have a status of '16. Requires Changes' when they should have a status of '33. Approved'. This occurs in the dataset as bookings contain multiple tickets. If a single ticket in a booking requires changes, the entire booking is marked as 'Requires Changes', thus marking tickets that do not require changes incorrectly. These false negatives can be detected and removed by checking if a duplicate entry exists where only the status changes.
print(f"size before: {df.shape}" )
df['StatusPriority'] = df['BStatusAfterSubmitted'].apply(lambda x: 0 if x == '33. Approved' else 1) # Assign priority: approved gets highest priority (lowest number)
dedup_cols = [col for col in df.columns if col not in ['BStatusAfterSubmitted', 'StatusPriority','BCreatedDateAEST', 'BStatusFromDateTimeAEST', 'Date' ]] # Define columns to check for duplicates
df = df.sort_values(by=dedup_cols + ['StatusPriority']) # Sort so approved status is first
df = df.drop_duplicates(subset=dedup_cols, keep='first') # Keep the first occurrence (which is the approved status)
df = df.drop(columns='StatusPriority') # drop the temporary column used for sorting

df['Label'] = df['BStatusAfterSubmitted'].map({'33. Approved': 1, '16. Requires Changes': 0, '29. Rejected': 0}) # create label column for model training
df = df.drop(columns=['BStatusAfterSubmitted'], axis=1) # drop the original status column as it is no longer needed
print(f"size after: {df.shape}" ) 

# %% [markdown]
# # Final Column Removal

# %%
columns_to_drop = ['BookingID', 'BTicketID', 'IsCustomService', 'IsCustomRepair', 'BShopRegionClass', 'BShopState']
df.drop(columns = columns_to_drop, inplace=True)
df.head()

# %% [markdown]
# ## Split data Frame by Ticket Type and Export

# %%
df_repair = df[df['BTicketType'] == 'Repair'].drop(columns=['BTicketType'])
df_log = df[df['BTicketType'] == 'Log'].drop(columns=['BTicketType'])
df_capped = df[df['BTicketType'] == 'Capped'].drop(columns=['BTicketType'])
df_prescribed = df[df['BTicketType'] == 'Prescribed'].drop(columns=['BTicketType'])

# %%
df_repair.to_csv('data/preprocessed_repair_data.csv', index=False)
df_log.to_csv('data/preprocessed_log_data.csv', index=False)
df_capped.to_csv('data/preprocessed_capped_data.csv', index=False)
df_prescribed.to_csv('data/preprocessed_prescribed_data.csv', index=False)


