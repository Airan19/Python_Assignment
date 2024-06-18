import pandas as pd
import json

xls = pd.ExcelFile('Mistral.xlsm')
shares_df = pd.read_excel(xls, 'Shares', header=1)
bonds_df = pd.read_excel(xls, 'Bonds', header=1)
bonds_df['CASH VEHICLE?'] = 'N'
bonds_df['% OF NAV'] = 0.98

# # List of given values for CNTRY_OF_RISK
# cntry_of_risk_values = [
#     'FR', 'IT', 'IT', 'IT', 'IT', 'IT', 'IT', 'IT', 'IT', 'JE',
#     'IT', 'IT', 'GB', 'IT', 'IT', 'FR', 'IT', 'DE', 'DE', 'IT'
# ]

# # Calculate the length of the 'bonds' DataFrame
# num_rows = len(bonds_df)

# # Calculate how many times the given values need to be repeated to cover all rows
# repeats_needed = num_rows // len(cntry_of_risk_values)
# remaining_values = num_rows % len(cntry_of_risk_values)

# # Create the list of values for CNTRY_OF_RISK by repeating the given values
# cntry_of_risk_column = cntry_of_risk_values * repeats_needed + cntry_of_risk_values[:remaining_values]

# # Add the 'CNTRY_OF_RISK' column to the 'bonds' DataFrame
# bonds_df['CNTRY OF RISK'] = cntry_of_risk_column



options_df = pd.read_excel(xls, 'Options', header=1)
futures_df = pd.read_excel(xls, 'Futures', header=1)

VAL_D2 = 106.23
VAL_D3 = 51.04


# Compressed dictionary of country codes and country names
country_dict = {
    "AF": "AFGHANISTAN", "AX": "ÅLAND ISLANDS", "AL": "ALBANIA", "DZ": "ALGERIA", "AS": "AMERICAN SAMOA",
    "AD": "ANDORRA", "AO": "ANGOLA", "AI": "ANGUILLA", "AQ": "ANTARCTICA", "AG": "ANTIGUA AND BARBUDA",
    "AR": "ARGENTINA", "AM": "ARMENIA", "AW": "ARUBA", "AU": "AUSTRALIA", "AT": "AUSTRIA",
    "AZ": "AZERBAIJAN", "BS": "BAHAMAS", "BH": "BAHRAIN", "BD": "BANGLADESH", "BB": "BARBADOS",
    "BY": "BELARUS", "BE": "BELGIUM", "BZ": "BELIZE", "BJ": "BENIN", "BM": "BERMUDA",
    "BT": "BHUTAN", "BO": "BOLIVIA, PLURINATIONAL STATE OF", "BQ": "BONAIRE, SINT EUSTATIUS AND SABA", "BA": "BOSNIA AND HERZEGOVINA", "BW": "BOTSWANA",
    "BV": "BOUVET ISLAND", "BR": "BRAZIL", "IO": "BRITISH INDIAN OCEAN TERRITORY", "BN": "BRUNEI DARUSSALAM", "BG": "BULGARIA",
    "BF": "BURKINA FASO", "BI": "BURUNDI", "KH": "CAMBODIA", "CM": "CAMEROON", "CA": "CANADA",
    "CV": "CAPE VERDE", "KY": "CAYMAN ISLANDS", "CF": "CENTRAL AFRICAN REPUBLIC", "TD": "CHAD", "CL": "CHILE",
    "CN": "CHINA", "CX": "CHRISTMAS ISLAND", "CC": "COCOS (KEELING) ISLANDS", "CO": "COLOMBIA", "KM": "COMOROS",
    "CG": "CONGO", "CD": "CONGO, THE DEMOCRATIC REPUBLIC OF THE", "CK": "COOK ISLANDS", "CR": "COSTA RICA", "CI": "CÔTE D'IVOIRE",
    "HR": "CROATIA", "CU": "CUBA", "CW": "CURAÇAO", "CY": "CYPRUS", "CZ": "CZECH REPUBLIC",
    "DK": "DENMARK", "DJ": "DJIBOUTI", "DM": "DOMINICA", "DO": "DOMINICAN REPUBLIC", "EC": "ECUADOR",
    "EG": "EGYPT", "SV": "EL SALVADOR", "GQ": "EQUATORIAL GUINEA", "ER": "ERITREA", "EE": "ESTONIA",
    "ET": "ETHIOPIA", "FK": "FALKLAND ISLANDS (MALVINAS)", "FO": "FAROE ISLANDS", "FJ": "FIJI", "FI": "FINLAND",
    "FR": "FRANCE", "GF": "FRENCH GUIANA", "PF": "FRENCH POLYNESIA", "TF": "FRENCH SOUTHERN TERRITORIES", "GA": "GABON",
    "GM": "GAMBIA", "GE": "GEORGIA", "DE": "GERMANY", "GH": "GHANA", "GI": "GIBRALTAR",
    "GR": "GREECE", "GL": "GREENLAND", "GD": "GRENADA", "GP": "GUADELOUPE", "GU": "GUAM",
    "GT": "GUATEMALA", "GG": "GUERNSEY", "GN": "GUINEA", "GW": "GUINEA-BISSAU", "GY": "GUYANA",
    "HT": "HAITI", "HM": "HEARD ISLAND AND MCDONALD ISLANDS", "VA": "HOLY SEE (VATICAN CITY STATE)", "HN": "HONDURAS", "HK": "HONG KONG",
    "HU": "HUNGARY", "IS": "ICELAND", "IN": "INDIA", "ID": "INDONESIA", "IR": "IRAN, ISLAMIC REPUBLIC OF",
    "IQ": "IRAQ", "IE": "IRELAND", "IM": "ISLE OF MAN", "IL": "ISRAEL", "IT": "ITALY",
    "JM": "JAMAICA", "JP": "JAPAN", "JE": "JERSEY", "JO": "JORDAN", "KZ": "KAZAKHSTAN",
    "KE": "KENYA", "KI": "KIRIBATI", "KP": "KOREA, DEMOCRATIC PEOPLE'S REPUBLIC OF", "KR": "KOREA, REPUBLIC OF", "KW": "KUWAIT",
    "KG": "KYRGYZSTAN", "LA": "LAO PEOPLE'S DEMOCRATIC REPUBLIC", "LV": "LATVIA", "LB": "LEBANON", "LS": "LESOTHO",
    "LR": "LIBERIA", "LY": "LIBYA", "LI": "LIECHTENSTEIN", "LT": "LITHUANIA", "LU": "LUXEMBOURG",
    "MO": "MACAO", "MK": "MACEDONIA, THE FORMER YUGOSLAV REPUBLIC OF", "MG": "MADAGASCAR", "MW": "MALAWI", "MY": "MALAYSIA",
    "MV": "MALDIVES", "ML": "MALI", "MT": "MALTA", "MH": "MARSHALL ISLANDS", "MQ": "MARTINIQUE",
    "MR": "MAURITANIA", "MU": "MAURITIUS", "YT": "MAYOTTE", "MX": "MEXICO", "FM": "MICRONESIA, FEDERATED STATES OF",
    "MD": "MOLDOVA, REPUBLIC OF", "MC": "MONACO", "MN": "MONGOLIA", "ME": "MONTENEGRO", "MS": "MONTSERRAT",
    "MA": "MOROCCO", "MZ": "MOZAMBIQUE", "MM": "MYANMAR", "NA": "NAMIBIA", "NR": "NAURU",
    "NP": "NEPAL", "NL": "NETHERLANDS", "NC": "NEW CALEDONIA", "NZ": "NEW ZEALAND", "NI": "NICARAGUA",
    "NE": "NIGER", "NG": "NIGERIA", "NU": "NIUE", "NF": "NORFOLK ISLAND", "MP": "NORTHERN MARIANA ISLANDS",
    "NO": "NORWAY", "OM": "OMAN", "PK": "PAKISTAN", "PW": "PALAU", "PS": "PALESTINE, STATE OF",
    "PA": "PANAMA", "PG": "PAPUA NEW GUINEA", "PY": "PARAGUAY", "PE": "PERU", "PH": "PHILIPPINES",
    "PN": "PITCAIRN", "PL": "POLAND", "PT": "PORTUGAL", "PR": "PUERTO RICO", "QA": "QATAR",
    "RE": "RÉUNION", "RO": "ROMANIA", "RU": "RUSSIAN FEDERATION", "RW": "RWANDA", "BL": "SAINT BARTHÉLEMY",
    "SH": "SAINT HELENA, ASCENSION AND TRISTAN DA CUNHA", "KN": "SAINT KITTS AND NEVIS", "LC": "SAINT LUCIA", "MF": "SAINT MARTIN (FRENCH PART)",
    "PM": "SAINT PIERRE AND MIQUELON", "VC": "SAINT VINCENT AND THE GRENADINES", "WS": "SAMOA", "SM": "SAN MARINO", "ST": "SAO TOME AND PRINCIPE",
    "SA": "SAUDI ARABIA", "SN": "SENEGAL", "RS": "SERBIA", "SC": "SEYCHELLES", "SL": "SIERRA LEONE",
    "SG": "SINGAPORE", "SX": "SINT MAARTEN (DUTCH PART)", "SK": "SLOVAKIA", "SI": "SLOVENIA", "SB": "SOLOMON ISLANDS",
    "SO": "SOMALIA", "ZA": "SOUTH AFRICA", "GS": "SOUTH GEORGIA AND THE SOUTH SANDWICH ISLANDS", "SS": "SOUTH SUDAN", "ES": "SPAIN",
    "LK": "SRI LANKA", "SD": "SUDAN", "SR": "SURINAME", "SJ": "SVALBARD AND JAN MAYEN", "SZ": "SWAZILAND",
    "SE": "SWEDEN", "CH": "SWITZERLAND", "SY": "SYRIAN ARAB REPUBLIC", "TW": "TAIWAN, PROVINCE OF CHINA", "TJ": "TAJIKISTAN",
    "TZ": "TANZANIA, UNITED REPUBLIC OF", "TH": "THAILAND", "TL": "TIMOR-LESTE", "TG": "TOGO", "TK": "TOKELAU",
    "TO": "TONGA", "TT": "TRINIDAD AND TOBAGO", "TN": "TUNISIA", "TR": "TURKEY", "TM": "TURKMENISTAN",
    "TC": "TURKS AND CAICOS ISLANDS", "TV": "TUVALU", "UG": "UGANDA", "UA": "UKRAINE", "AE": "UNITED ARAB EMIRATES",
    "GB": "UNITED KINGDOM", "US": "UNITED STATES", "UM": "UNITED STATES MINOR OUTLYING ISLANDS", "UY": "URUGUAY", "UZ": "UZBEKISTAN",
    "VU": "VANUATU", "VE": "VENEZUELA, BOLIVARIAN REPUBLIC OF", "VN": "VIET NAM", "VG": "VIRGIN ISLANDS, BRITISH",
    "VI": "VIRGIN ISLANDS, U.S.", "WF": "WALLIS AND FUTUNA", "EH": "WESTERN SAHARA", "YE": "YEMEN", "ZM": "ZAMBIA",
    "ZW": "ZIMBABWE"
}

# Convert the dictionary to a pandas DataFrame
country_df = pd.DataFrame(list(country_dict.items()), columns=["Country_Code", "Country_Name"])
country_df['Col_P'] = ''
country_df['Col_Q'] = ''


def cal_column_m(country_df, shares_df, bonds_df, options_df, futures_df):
    for index, row in country_df.iterrows():
        country_code = row['Country_Code']

        # Calculate the count of occurences for each sheet
        count_shares = shares_df[shares_df['CNTRY OF RISK'] == country_code].shape[0]
        count_bonds = bonds_df[(bonds_df['CNTRY_OF_RISK'] == country_code) & (bonds_df['CASH VEHICLE?'] == 'N')].shape[0]
        count_options = options_df[options_df['CNTRY OF RISK'] == country_code].shape[0]
        count_futures = futures_df[futures_df['CNTRY OF RISK'] == country_code].shape[0]

        # Calculate column M
        country_df.loc[index, 'Col_M'] = count_shares + count_bonds + count_options + count_futures

    return country_df


def cal_column_q(country_df, shares_df, bonds_df, options_df, futures_df):
    for index, row in country_df.iterrows():
        
        if row['Col_M'] == 0:
            country_df.loc[index, 'Col_Q'] == ''
        
        else:
            country_code = row['Country_Code']

            sum_shares_pos = shares_df[(shares_df['REAL'] > 0) & (shares_df['CNTRY OF RISK'] == country_code)]['REAL'].sum()
            sum_bonds_pos = bonds_df[(bonds_df['% OF NAV'] > 0) & (bonds_df['CNTRY OF RISK'] == country_code)]['% OF NAV'].sum()
            sum_options_pos = options_df[(options_df['% OF NAV DELTA ADJ'] > 0) & (options_df['CNTRY OF RISK'] == country_code)]['% OF NAV DELTA ADJ'].sum()
            sum_futures_pos = futures_df[(futures_df['% NAV (VALUE)'] > 0) & (futures_df['CNTRY OF RISK'] == country_code)]['% NAV (VALUE)'].sum()
            
            sum_shares_neg = shares_df[(shares_df['REAL'] < 0) & (shares_df['CNTRY OF RISK'] == country_code)]['REAL'].sum()
            sum_bonds_neg = bonds_df[(bonds_df['% OF NAV'] < 0) & (bonds_df['CNTRY OF RISK'] == country_code)]['% OF NAV'].sum()
            sum_options_neg = options_df[(options_df['% OF NAV DELTA ADJ'] < 0) & (options_df['CNTRY OF RISK'] == country_code)]['% OF NAV DELTA ADJ'].sum()
            sum_futures_neg = futures_df[(futures_df['% NAV (VALUE)'] < 0) & (futures_df['CNTRY OF RISK'] == country_code)]['% NAV (VALUE)'].sum()

            # Calculate column Q
            country_df.loc[index, 'Col_Q'] = sum_shares_pos + sum_bonds_pos + sum_options_pos + sum_futures_pos \
                                         - (sum_shares_neg + sum_bonds_neg + sum_options_neg + sum_futures_neg)

    return country_df


def cal_column_p(country_df, shares_df, bonds_df, options_df, futures_df):
    for index, row in country_df.iterrows():

        if row['Col_Q'] == '':
            country_df.loc[index, 'Col_P'] = ''

        else:
            country_code = row['Country_Code']

            # Calculate sum across the sheets based on the country code
            sum_shares = shares_df[shares_df['CNTRY OF RISK'] == country_code]['REAL'].sum()
            sum_bonds = bonds_df[bonds_df['CNTRY OF RISK'] == country_code]['% OF NAV'].sum()
            sum_options = options_df[options_df['CNTRY OF RISK'] == country_code]['% OF NAV DELTA ADJ'].sum()
            sum_futures = futures_df[futures_df['CNTRY OF RISK'] == country_code]['% NAV (VALUE)'].sum() 

            # Calculate column P
            country_df.loc[index, 'Col_P'] = sum_shares + sum_bonds + sum_options + sum_futures

    return country_df

# i want to add a new row in our country_df , country code OTHER, country name OTHER,

# Calculate column M, Q, and P using the functions
country_df = cal_column_m(country_df, shares_df, bonds_df, options_df, futures_df)
country_df = cal_column_q(country_df, shares_df, bonds_df, options_df, futures_df)
country_df = cal_column_p(country_df, shares_df, bonds_df, options_df, futures_df)

country_df['Col_Q'] = pd.to_numeric(country_df['Col_Q'], errors='coerce')
country_df['Col_P'] = pd.to_numeric(country_df['Col_P'], errors='coerce')

filtered_df = country_df.dropna(subset=['Col_P'])
result_df = filtered_df[['Country_Name', 'Col_P']]


def cal_other_q(val_d2):    
    # Calculate the range sum for Q$38:Q$425
    range_sum_q = country_df['Col_Q'].sum()

    abs_diff = abs(val_d2 - range_sum_q)

    if abs_diff < 0.0001:
        other_val_q = ''
    else:
        other_val_q = val_d2 - range_sum_q
    return other_val_q


def cal_other_net(result_df, val_d3):
    other_val_q = cal_other_q(VAL_D2)
    if other_val_q == '':
        other_row = pd.DataFrame({'Country_Name':['OTHER'], 'Col_P': ['']})
    else:
        range_sum_p = result_df['Col_P'].sum()
        other_val_p = val_d3 - range_sum_p
        other_row = pd.DataFrame({'Country_Name':['OTHER'], 'Col_P': [other_val_p]})
    result_df = pd.concat([result_df, other_row], ignore_index=True)
    return result_df


def cal_net_country_exposure(result_df):
    result_df = cal_other_net(result_df, VAL_D3)
    result_df = result_df.sort_values(by='Col_P', ascending=False)
    result_dict = {'NET COUNTRY EXPOSURE (TOTAL)': result_df['Col_P'].sum(), 'NET COUNTRY EXPOSURE': result_df.set_index('Country_Name')['Col_P'].to_dict()}
    result_json = json.dumps(result_dict, indent=4)
    return result_json


print(cal_net_country_exposure(result_df))