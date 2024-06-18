import pandas as pd
import json

xls = pd.ExcelFile('Mistral.xlsm')
shares = pd.read_excel(xls, 'Shares', header=1)
bonds = pd.read_excel(xls, 'Bonds', header=1)
bonds['CASH VEHICLE?'] = 'N'
bonds['% OF NAV'] = 0.98
options = pd.read_excel(xls, 'Options', header=1)
futures = pd.read_excel(xls, 'Futures', header=1)

categories = [
    "OTHER", "FINANCIAL", "COMMUNICATIONS", "CONSUMER, CYCLICAL", "ENERGY",
    "FUNDS", "BASIC MATERIALS", "INDUSTRIAL","TECHNOLOGY", "CONSUMER, NON-CYCLICAL",
    "UTILITIES", "DIVERSIFIED", "GOVERNMENT", "INDEX"
]

categories_df = pd.DataFrame({'Category': categories, 'Col_A':'', 'Col_C':'', 'Col_D':''})


def cal_column_c26(bonds_df):
    c26 = bonds_df.loc[bonds_df['CASH VEHICLE?'] == 'Y', '% OF NAV'].sum()
    return c26


def cal_column_d26(bonds_df):
    bonds_pos_sum = bonds_df.loc[(bonds_df['CASH VEHICLE?'] == 'Y') & (bonds_df['% OF NAV'] > 0), '% OF NAV'].sum()
    bonds_neg_sum = bonds_df.loc[(bonds_df['CASH VEHICLE?'] == 'Y') & (bonds_df['% OF NAV'] < 0), '% OF NAV'].sum()
    d26 = bonds_pos_sum + abs(bonds_neg_sum)
    return d26


VAL_B26 = 'GOVERNMENT'
VAL_C26 = cal_column_c26(bonds)
VAL_D2 = 106.23
VAL_D3 = 51.04
VAL_D26 = cal_column_d26(bonds)


def cal_column_a(shares_df, bonds_df, options_df, futures_df, categories_df):
    for index, row in categories_df.iterrows():
        col_b_val = row['Category'].capitalize()
        shares_count = shares_df.loc[shares_df['INDUSTRY_SECTOR'] == col_b_val, 'INDUSTRY_SECTOR'].count()
        bonds_count = bonds_df.loc[(bonds_df['INDUSTRY_SECTOR'] == col_b_val) & (bonds_df['CASH VEHICLE?'] == 'N'), 'INDUSTRY_SECTOR'].count()
        options_count = options_df.loc[options_df['INDUSTRY_SECTOR'] == col_b_val, 'INDUSTRY_SECTOR'].count()
        futures_count = futures_df.loc[futures_df['INDUSTRY_SECTOR'] == col_b_val, 'INDUSTRY_SECTOR'].count()
        col_a_val = shares_count + bonds_count + options_count + futures_count
        categories_df.loc[index, 'Col_A'] = col_a_val
    
    return categories_df


def cal_column_d(shares_df, bonds_df, options_df, futures_df, categories_df):
    # col_a_val = cal_column_a(shares_df, bonds_df, options_df, futures_df, col_b_val)
    for index, row in categories_df.iterrows():
        col_b_val = row['Category'].capitalize()
        col_a_val = row['Col_A']
        
        if col_a_val == 0:
            net_sum = pd.NA

        else:
            shares_pos_sum = shares_df.loc[(shares_df['REAL'] > 0) & (shares_df['INDUSTRY_SECTOR'] == col_b_val), 'REAL'].sum()
            shares_neg_sum = shares_df.loc[(shares_df['REAL'] < 0) & (shares_df['INDUSTRY_SECTOR'] == col_b_val), 'REAL'].sum()
            
            bonds_pos_sum = bonds_df.loc[(bonds_df['% OF NAV'] > 0) & (bonds_df['INDUSTRY_SECTOR'] == col_b_val), '% OF NAV'].sum()
            bonds_neg_sum = bonds_df.loc[(bonds_df['% OF NAV'] < 0) & (bonds_df['INDUSTRY_SECTOR'] == col_b_val), '% OF NAV'].sum()
            
            options_pos_sum = options_df.loc[(options_df['% OF NAV DELTA ADJ'] > 0) & (options_df['INDUSTRY_SECTOR'] == col_b_val), '% OF NAV DELTA ADJ'].sum()
            options_neg_sum = options_df.loc[(options_df['% OF NAV DELTA ADJ'] < 0) & (options_df['INDUSTRY_SECTOR'] == col_b_val), '% OF NAV DELTA ADJ'].sum()
            
            futures_pos_sum = futures_df.loc[(futures_df['% NAV (VALUE)'] > 0) & (futures_df['INDUSTRY_SECTOR'] == col_b_val), '% NAV (VALUE)'].sum()
            futures_neg_sum = futures_df.loc[(futures_df['% NAV (VALUE)'] < 0) & (futures_df['INDUSTRY_SECTOR'] == col_b_val), '% NAV (VALUE)'].sum()

            
            net_sum = (shares_pos_sum - shares_neg_sum + bonds_pos_sum - bonds_neg_sum +
                    options_pos_sum - options_neg_sum + futures_pos_sum - futures_neg_sum)

            # Subtract d26 if col_b_val is equal to "GOVERNMENT"
            if col_b_val ==  VAL_B26:
                net_sum -= VAL_D26

        categories_df.loc[index, 'Col_D'] = net_sum

    return categories_df


def cal_column_c(shares_df, bonds_df, options_df, futures_df, categories_df):
    # col_d_val = cal_column_d(shares_df, bonds_df, options_df, futures_df, col_b_val)
    for index, row in categories_df.iterrows():
        col_b_val = row['Category'].capitalize()
        col_d_val = row['Col_D']
        if not pd.notna(col_d_val):
            col_c_val = pd.NA
        else:
            shares_sum = shares_df.loc[shares_df['INDUSTRY_SECTOR'] == col_b_val, 'REAL'].sum()
            bonds_sum = bonds_df.loc[bonds_df['INDUSTRY_SECTOR'] == col_b_val, '% OF NAV'].sum()
            options_sum = options_df.loc[options_df['INDUSTRY_SECTOR'] == col_b_val, '% OF NAV DELTA ADJ'].sum()
            futures_sum = futures_df.loc[futures_df['INDUSTRY_SECTOR'] == col_b_val, '% NAV (VALUE)'].sum()

            col_c_val = shares_sum + bonds_sum + options_sum + futures_sum

            if col_b_val == VAL_B26:
                col_c_val -= VAL_C26
        categories_df.loc[index, 'Col_C'] = col_c_val
    return categories_df


def calculate_other_col_d(categories_df, val_d2):
    col_d_sum = categories_df.loc[categories_df['Category'] != 'OTHER', 'Col_D'].sum()
    abs_difference = abs(val_d2 - col_d_sum)
    if abs_difference < 0.0001:
        return pd.NA
    else:
        return val_d2 - col_d_sum
    

def calculate_other(categories_df, val_d3):
    other_col_d_val = calculate_other_col_d(categories_df, VAL_D2)
    if pd.isna(other_col_d_val):
        other_col_c_val = pd.NA
    else:
        col_c_sum = categories_df.loc[categories_df['Category'] != 'OTHER', 'Col_C'].sum()
        other_col_c_val = val_d3 - col_c_sum
        
    categories_df.loc[categories_df['Category'] == 'OTHER', 'Col_C'] = other_col_c_val
    categories_df.loc[categories_df['Category'] == 'OTHER', 'Col_D'] = other_col_d_val


def cal_net_industry_exposure(categories_df):
    categories_df = cal_column_a(shares, bonds, options, futures, categories_df)
    categories_df = cal_column_d(shares, bonds, options, futures, categories_df)
    categories_df = cal_column_c(shares, bonds, options, futures, categories_df)
    calculate_other(categories_df, VAL_D3)
    filtered_df = categories_df.dropna(subset='Col_C')
    result_df = filtered_df[['Category', 'Col_C']]
    result_df = result_df.sort_values(by='Col_C', ascending=False)
    result_dict = {'NET INDUSTRY EXPOSURE (TOTAL)': result_df['Col_C'].sum(), 
                   'NET INDUSTRY EXPOSURE': result_df.set_index('Category')['Col_C'].to_dict()}
    result_json = json.dumps(result_dict, indent=4)
    return result_json


print(cal_net_industry_exposure(categories_df))
