import pandas as pd
import json

xls = pd.ExcelFile('Mistral.xlsm')
shares = pd.read_excel(xls, 'Shares', header=1)
bonds = pd.read_excel(xls, 'Shares', header=1)
bonds['CASH VEHICLE?'] = 'N'
bonds['% OF NAV'] = 0.98
options = pd.read_excel(xls, 'Options', header=1)
futures = pd.read_excel(xls, 'Futures', header=1)

currencies = ['EUR', 'USD']
currencies_excel = ['EUR', 'NOK', 'GBP', 'DKK', 'USD', 'CAD', 'HKD', 'KRW', 'TRY', 'SEK', 'CNY', 'TWD', 'JPY', 'CHF']
selected_values_dict = {'CURRENCY': [], 'NET': []}
col_W_values = []
col_V_values = []
val_D2 = 1.0623
val_D3 = 0.5104


def get_selected_values(bonds_df, col_U_currency):
    filtered_bonds = bonds_df[(bonds_df['CASH VEHICLE?'] == 'Y') & (bonds_df['CRNCY'] == col_U_currency)]    
    # Sum the values in column '% OF NAV' of the filtered DataFrame
    summed_value = filtered_bonds['% OF NAV'].sum()    
    return summed_value


for currency in currencies:
    net_value = get_selected_values(bonds, currency)
    selected_values_dict['CURRENCY'].append(currency)
    selected_values_dict['NET'].append(net_value)

selected_values_df = pd.DataFrame(selected_values_dict)


def calculate_col_T(shares_df, bonds_df, options_df, futures_df, col_U_currency):    
    shares_count = shares_df[shares_df['CRNCY'] == col_U_currency].shape[0]
    bonds_count = bonds_df[(bonds_df['CRNCY'] == col_U_currency) & (bonds_df['CASH VEHICLE?'] == 'N')].shape[0]
    options_count = options_df[options_df['CRNCY'] == col_U_currency].shape[0]
    futures_count = futures_df[futures_df['CRNCY'] == col_U_currency].shape[0]
    
    # Calculate col_T value
    col_T_value = shares_count + bonds_count +  options_count + futures_count
    return col_T_value


def calculate_col_W(shares_df, bonds_df, options_df, futures_df, col_U_currency):
    val_T = calculate_col_T(shares_df, bonds_df, options_df, futures_df, col_U_currency)
    if val_T == 0:
        return ''
    
    else:    
       # Define the conditions for each SUMIFS
        shares_condition = (shares_df['REAL'] > 0) & (shares_df['CRNCY'] == col_U_currency)
        bonds_condition = (bonds_df['% OF NAV'] > 0) & (bonds_df['CRNCY'] == col_U_currency)
        options_condition = (options_df['% OF NAV DELTA ADJ'] > 0) & (options_df['CRNCY'] == col_U_currency)
        futures_condition = (futures_df['% NAV (VALUE)'] > 0) & (futures_df['CRNCY'] == col_U_currency)

        shares_sum = shares_df.loc[shares_condition & shares_df.index.isin(range(1, 903)), 'REAL'].sum()
        bonds_sum = bonds_df.loc[bonds_condition & bonds_df.index.isin(range(1, 1009)), '% OF NAV'].sum()
        options_sum = options_df.loc[options_condition & options_df.index.isin(range(1, 164)), '% OF NAV DELTA ADJ'].sum()
        futures_sum = futures_df.loc[futures_condition & futures_df.index.isin(range(1, 945)), '% NAV (VALUE)'].sum()
        shares_neg_sum = shares_df.loc[~shares_condition & shares_df.index.isin(range(1, 903)), 'REAL'].sum()
        bonds_neg_sum = bonds_df.loc[~bonds_condition & bonds_df.index.isin(range(1, 1009)), '% OF NAV'].sum()
        options_neg_sum = options_df.loc[~options_condition & options_df.index.isin(range(1, 164)), '% OF NAV DELTA ADJ'].sum()
        futures_neg_sum = futures_df.loc[~futures_condition & futures_df.index.isin(range(1, 945)), '% NAV (VALUE)'].sum()

        # Calculate col_W value
        col_W_value = shares_sum + bonds_sum + options_sum + futures_sum - shares_neg_sum - bonds_neg_sum - options_neg_sum - futures_neg_sum
        return col_W_value


def calculate_col_V(shares_df, bonds_df, options_df, futures_df, col_U_currency):
    val_W = calculate_col_W(shares_df, bonds_df, options_df, futures_df, col_U_currency)
    if val_W == '':
        col_W_values.append(0)
        return ''  
    
    else:
        col_W_values.append(val_W)
        conditioned_values = selected_values_df.loc[selected_values_df['CURRENCY'] == col_U_currency, 'NET']
        sum_of_selected_values = conditioned_values.sum()
        sum_of_shares_df = shares_df.loc[shares_df['CRNCY'] == col_U_currency, 'REAL'].sum()
        sum_of_bonds_df = bonds_df.loc[bonds_df['CRNCY'] == col_U_currency, '% OF NAV'].sum()
        sum_of_options_df = options_df.loc[options_df['CRNCY'] == col_U_currency, '% OF NAV DELTA ADJ'].sum()
        sum_of_futures_df = futures_df.loc[futures_df['CRNCY'] == col_U_currency, '% NAV (VALUE)'].sum()
        return (
            sum_of_shares_df +
            sum_of_bonds_df +
            sum_of_options_df +
            sum_of_futures_df -
            sum_of_selected_values
        )

    
def calculate_other_w(val_D2, sum_W):
    if abs(val_D2 - sum_W) < 0.0001:
        return ""
    else:
        return val_D2 - sum_W
    

def calculate_other(val_D3, sum_V):
    W31 = calculate_other_w(val_D2, sum(col_W_values))
    if W31 == "":
        return ""
    else:
        return val_D3 - sum_V


def calculate_col_U(shares_df, bonds_df, options_df, futures_df):
    smh_summary_dict = {'CURRENCY':[], 'NET': []}
    val_other = calculate_other(val_D3, sum(col_V_values))
    smh_summary_dict['CURRENCY'].append('OTHER')
    smh_summary_dict['NET'].append(val_other)

    for col_U_currency in currencies_excel:
        val_V = calculate_col_V(shares_df, bonds_df, options_df, futures_df, col_U_currency)
        if val_V == '':
            col_V_values.append(0)
        else:
            col_V_values.append(val_V)
        smh_summary_dict['CURRENCY'].append(col_U_currency)
        smh_summary_dict['NET'].append(val_V)
    return smh_summary_dict


def cal_top_five():
    smh_summary_dict_values = calculate_col_U(shares, bonds, options, futures)
    summary_df = pd.DataFrame(smh_summary_dict_values)
    summary_df['NET'] = summary_df['NET'].replace('', pd.NA)
    top_five = summary_df.sort_values(by='NET', ascending=False).head(5)
    top_five_with_others = pd.concat([top_five, summary_df[summary_df['CURRENCY'] == 'OTHER']])
    return top_five_with_others

top_five_with_others = cal_top_five()
# Print the top five rows with 'OTHERS' included
print('\nTOP FIVE using pandas sort method \n', top_five_with_others)


def cal_net_exposure():
    # result_json = cal_net_currency_exposure(col_A_values)
    result_dict = {'NET CURRENCY EXPOSURE': top_five_with_others.set_index('CURRENCY')['NET'].to_dict()}

    # Convert dictionary to JSON
    result_json = json.dumps(result_dict, indent=4)
    return result_json

net_exposure_result = cal_net_exposure()
print('\nNET CURRENCY RESULT JSON \n', net_exposure_result)

