import pandas as pd
import json

xls = pd.ExcelFile('Mistral.xlsm')
shares = pd.read_excel(xls, 'Shares', header=1)
shares['MARKET CAP (EUR'] = pd.to_numeric(shares['MARKET CAP (EUR'], errors='coerce')

GROSS_RANGE_COL_AA = [0,100000000, 300000000, 1000000000, 3000000000, 10000000000]
GROSS_RANGE_COL_AB = [100000000, 300000000, 1000000000, 3000000000, 10000000000, '']
COL_AA_AB_DF = pd.DataFrame({'AA': GROSS_RANGE_COL_AA, 'AB': GROSS_RANGE_COL_AB})
GROSS_DF = pd.DataFrame()
VAL_D2 = 106.23


def get_market_cap(COL_AA_AB_DF):
    MARKET_CAP = []
    for i in range(len(COL_AA_AB_DF)):
        aa_value = COL_AA_AB_DF.at[i, 'AA'] / 1000000
        ab_value = COL_AA_AB_DF.at[i, 'AB'] 
        if pd.isna(ab_value) or ab_value == '':
            result = f"{int(aa_value)} +"
        else:
            result = f"{int(aa_value)} - {int(ab_value / 1000000)}"
        GROSS_DF.at[i, 'GROSS-RANGE'] = result
        MARKET_CAP.append(result)
    GROSS_DF.loc[GROSS_DF.index[-1] + 1,'GROSS-RANGE'] = 'OTHER'
    MARKET_CAP.append('OTHER')
    return MARKET_CAP

MARKET_CAP_LIST = get_market_cap(COL_AA_AB_DF)


def cal_gross(shares_df, val_AA, val_AB):
    if val_AB == '':
        sum_positive = shares_df[(shares_df['MARKET CAP (EUR'] > val_AA) &
                             (shares_df['REAL'] > 0)]['REAL'].sum()
    
        sum_negative = shares_df[(shares_df['MARKET CAP (EUR'] > val_AA) &
                             (shares_df['REAL'] < 0)]['REAL'].sum()

    else:
        sum_positive = shares_df[(shares_df['MARKET CAP (EUR'] > val_AA) &
                                (shares_df['MARKET CAP (EUR'] <= val_AB) &
                                (shares_df['REAL'] > 0)]['REAL'].sum()
        
        sum_negative = shares_df[(shares_df['MARKET CAP (EUR'] > val_AA) &
                                (shares_df['MARKET CAP (EUR'] <= val_AB) &
                                (shares_df['REAL'] < 0)]['REAL'].sum()
    
    return sum_positive - sum_negative


def cal_other(VAL_D2):
    sum_column = GROSS_DF['GROSS-VALUE'].sum()
    abs_diff = abs(VAL_D2 - sum_column)
    if abs_diff < 0.0001:
        result = ''
    else:
        result = VAL_D2 - sum_column
    return round(result,2)


def cal_gross_market_cap_exposure():
    for i in range(len(COL_AA_AB_DF)):
        aa_value = COL_AA_AB_DF.at[i, 'AA']
        ab_value = COL_AA_AB_DF.at[i, 'AB']
        GROSS_DF.at[i, 'GROSS-VALUE'] = round(cal_gross(shares, aa_value, ab_value)*100, 2)

    val_other = cal_other(VAL_D2)
    GROSS_DF.loc[GROSS_DF['GROSS-RANGE'] == 'OTHER', 'GROSS-VALUE'] = val_other

    result_dict = {'GROSS MARKET CAP EXPOSURE': GROSS_DF.set_index('GROSS-RANGE')['GROSS-VALUE'].to_dict()}
    result_json = json.dumps(result_dict, indent=4)
    return result_json


print(cal_gross_market_cap_exposure())