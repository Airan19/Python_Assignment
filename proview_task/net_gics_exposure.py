import pandas as pd
import json

# Load the Excel file and data sheets
xls = pd.ExcelFile('Mistral.xlsm')
shares = pd.read_excel(xls, 'Shares', header=1)
bonds = pd.read_excel(xls, 'Bonds', header=1)
bonds['CASH VEHICLE?'] = 'N'
bonds['% OF NAV'] = 0.98
print(bonds.shape)
options = pd.read_excel(xls, 'Options', header=1)
futures = pd.read_excel(xls, 'Futures', header=1)

# Define categories list
categories = [
    "OTHER", "FINANCIAL", "COMMUNICATION SERVICES", "CONSUMER DISCRETIONARY", 
    "ENERGY", "FUNDS", "BASIC MATERIALS", "INDUSTRIALS", "TECHNOLOGY", 
    "CONSUMER STAPLES", "UTILITIES", "DIVERSIFIED", "GOVERNMENT", "INDEX"
]

# Initialize categories DataFrame
categories_df = pd.DataFrame({'Category': categories, 'Col_G': '', 'Col_J': '', 'Col_I': ''})



def cal_col_i26(bonds_df):
    i26 = bonds_df.loc[bonds_df['CASH VEHICLE?'] == 'Y', '% OF NAV'].sum()
    return i26


def cal_col_j26(bonds_df):
    bonds_pos_sum = bonds_df.loc[(bonds_df['CASH VEHICLE?'] == 'Y') & (bonds_df['% OF NAV'] > 0), '% OF NAV'].sum()
    bonds_neg_sum = bonds_df.loc[(bonds_df['CASH VEHICLE?'] == 'Y') & (bonds_df['% OF NAV'] < 0), '% OF NAV'].sum()
    j26 = bonds_pos_sum + abs(bonds_neg_sum)
    return j26


VAL_H26 = 'GOVERNMENT'
VAL_I26 = cal_col_i26(bonds)
VAL_J26 = cal_col_j26(bonds)
VAL_D2 = 106.23
VAL_D3 = 51.04


def cal_col_g(shares_df, bonds_df, options_df, futures_df, categories_df):
    for index, row in categories_df.iterrows():
        h_value = row['Category'].capitalize()
        col_g = (
            shares_df.loc[shares_df['GICS_SECTOR_NAME'] == h_value, 'GICS_SECTOR_NAME'].count() +
            bonds_df.loc[(bonds_df['GICS_SECTOR_NAME'] == h_value) & (bonds_df['CASH VEHICLE?'] == 'N'), 'GICS_SECTOR_NAME'].count() +
            options_df.loc[options_df['GICS_SECTOR_NAME'] == h_value, 'GICS_SECTOR_NAME'].count() +
            futures_df.loc[futures_df['GICS_SECTOR_NAME'] == h_value, 'GICS_SECTOR_NAME'].count()
        )
        categories_df.loc[index, 'Col_G'] = col_g
    return categories_df


def cal_col_j(shares_df, bonds_df, options_df, futures_df, categories_df):
    for index, row in categories_df.iterrows():
        h_value = row['Category'].capitalize()
        col_g = row['Col_G']
        
        if col_g == 0:
            col_j = pd.NA
        else:
            shares_pos_sum = shares_df.loc[(shares_df['GICS_SECTOR_NAME'] == h_value) & (shares_df['REAL'] > 0), 'REAL'].sum()
            bonds_pos_sum = bonds_df.loc[(bonds_df['GICS_SECTOR_NAME'] == h_value) & (bonds_df['% OF NAV'] > 0), '% OF NAV'].sum()
            options_pos_sum = options_df.loc[(options_df['GICS_SECTOR_NAME'] == h_value) & (options_df['% OF NAV DELTA ADJ'] > 0), '% OF NAV DELTA ADJ'].sum()
            futures_pos_sum = futures_df.loc[(futures_df['GICS_SECTOR_NAME'] == h_value) & (futures_df['% NAV (VALUE)'] > 0), '% NAV (VALUE)'].sum()
            
            shares_neg_sum = shares_df.loc[(shares_df['GICS_SECTOR_NAME'] == h_value) & (shares_df['REAL'] < 0), 'REAL'].sum()
            bonds_neg_sum = bonds_df.loc[(bonds_df['GICS_SECTOR_NAME'] == h_value) & (bonds_df['% OF NAV'] < 0), '% OF NAV'].sum()
            options_neg_sum = options_df.loc[(options_df['GICS_SECTOR_NAME'] == h_value) & (options_df['% OF NAV DELTA ADJ'] < 0), '% OF NAV DELTA ADJ'].sum()
            futures_neg_sum = futures_df.loc[(futures_df['GICS_SECTOR_NAME'] == h_value) & (futures_df['% NAV (VALUE)'] < 0), '% NAV (VALUE)'].sum()
            
            col_j = (
                shares_pos_sum - shares_neg_sum +
                bonds_pos_sum - bonds_neg_sum +
                options_pos_sum - options_neg_sum +
                futures_pos_sum - futures_neg_sum
            )
            
            if h_value == VAL_H26:
                col_j -= VAL_J26
            
        categories_df.loc[index, 'Col_J'] = col_j
    return categories_df


def cal_col_i(shares_df, bonds_df, options_df, futures_df, categories_df):
    for index, row in categories_df.iterrows():
        h_value = row['Category'].capitalize()
        col_j = row['Col_J']
        
        if pd.isna(col_j):
            col_i = pd.NA
        else:
            shares_sum = shares_df.loc[shares_df['GICS_SECTOR_NAME'] == h_value, 'REAL'].sum()
            bonds_sum = bonds_df.loc[bonds_df['GICS_SECTOR_NAME'] == h_value, '% OF NAV'].sum()
            options_sum = options_df.loc[options_df['GICS_SECTOR_NAME'] == h_value, '% OF NAV DELTA ADJ'].sum()
            futures_sum = futures_df.loc[futures_df['GICS_SECTOR_NAME'] == h_value, '% NAV (VALUE)'].sum()
            
            col_i = shares_sum + bonds_sum + options_sum + futures_sum
            
            if h_value == VAL_H26:
                col_i -= VAL_I26
        
        categories_df.loc[index, 'Col_I'] = col_i
    return categories_df


def calculate_other_col_j(categories_df, val_d2):
    col_j_sum = categories_df.loc[categories_df['Category'] != 'OTHER', 'Col_J'].sum()
    abs_difference = abs(val_d2 - col_j_sum)
    if abs_difference < 0.0001:
        return pd.NA
    else:
        return val_d2 - col_j_sum
    

def calculate_other(categories_df, val_d3):
    other_col_j_val = calculate_other_col_j(categories_df, VAL_D2)
    if pd.isna(other_col_j_val):
        other_col_i_val = pd.NA
    else:
        col_i_sum = categories_df.loc[categories_df['Category'] != 'OTHER', 'Col_I'].sum()
        other_col_i_val = val_d3 - col_i_sum
        
    categories_df.loc[categories_df['Category'] == 'OTHER', 'Col_I'] = other_col_i_val
    categories_df.loc[categories_df['Category'] == 'OTHER', 'Col_J'] = other_col_j_val


# Main function to calculate net industry exposure
def cal_net_industry_exposure(categories_df):
    categories_df = cal_col_g(shares, bonds, options, futures, categories_df)
    categories_df = cal_col_j(shares, bonds, options, futures, categories_df)
    categories_df = cal_col_i(shares, bonds, options, futures, categories_df)
    calculate_other(categories_df, VAL_D3)
    filtered_df = categories_df.dropna(subset='Col_I')
    result_df = filtered_df[['Category', 'Col_I']]
    result_df = result_df.sort_values(by='Col_I', ascending=False)
    result_dict = {'NET GICS EXPOSURE (TOTAL)': result_df['Col_I'].sum(), 
                   'NET GICS EXPOSURE': result_df.set_index('Category')['Col_I'].to_dict()}
    result_json = json.dumps(result_dict, indent=4)
    return result_json


print(cal_net_industry_exposure(categories_df))
