import pandas as pd
import os
from datetime import datetime

def data_cleaning_datetime(df):
    '''
    removes NaNs, converts datetime and drops unnecessary columns
    Args:
        dataframe

    Returns:
        dataframe: cleaned data with datetime
    '''
    # columns to drop
    drop = ['dieselchange', 'e5change', 'e10change', 'date', 'openingtimes_json']
    # removes entries with missing values

    df = df[~df['date'].isna() == True]
    # makes a datetime column
    df['datetime'] = df['date'].apply(lambda x: datetime.strptime(x.split("+")[0], "%Y-%m-%d %H:%M:%S"))
    
    return df

def clean_stations_file(path):
    '''
    Used in concatenate station info functions

    Args:
        path (string): enter path of stations file in csv format (e.g.: 'data/data/2025-05-25-stations.csv)

    Returns:
        dataframe: stations dataframe cleaned
    '''
    stations_df = pd.read_csv(path)
    stations_df.loc[stations_df['brand'] == 'Günstige Tankstelle Schaal', 'name'] = stations_df['brand'] #replace missing name
    stations_df = stations_df[~stations_df["uuid"].astype(str).str.startswith("000000")] # drop test entries
    stations_df = stations_df[~stations_df['name'].str.lower().str.contains('gelöscht|please delete', na=False)]
    return stations_df
                              

###################################################################################################
def concatenate_station_info_city(stations_path, prices_folder_path, city):
    ''' 
    This function creates a dataframe for the gas stations of a city by concatenating the stations info and the price info
    Args: 

        stations_path (str): path of the stations csv file used, e.g. 'data/2024-12-31-stations.csv'

        prices_folder_path(str): path of the folder containing csv files with price info, e.g. 'data/2024-prices/'

        city(str): city of gas station, e.g. 'Hamburg'

    How to call:

        from Data_cleaning import concatenate_station_info

        result_df = concatenate_station_info('data/2024-12-31-stations.csv', 'data/2024-prices', 'Hamburg')
    
    Returns: 
        dataframe: df with station info and fuel prices

    '''
    df_s = clean_stations_file(stations_path)
    df_s = df_s[df_s['city'] == city]
    df_s.rename(columns={'uuid': 'station_uuid'}, inplace=True)
    
    uuids = set(df_s['station_uuid'])
    df_list = []
    for file in sorted(os.listdir(prices_folder_path)):
        if file.endswith('.csv'):
            df = pd.read_csv(os.path.join(prices_folder_path, file))
            filtered = df[df['station_uuid'].isin(uuids)]
            df_list.append(filtered)
    
    prices = pd.concat(df_list, ignore_index=True)
    final_df = pd.merge(df_s, prices, on='station_uuid', how='left')
    
    return final_df

###################################################################################################
def concatenate_station_info_zipcode(stations_path, prices_folder_path, zipcode):
    ''' 
    This function creates a dataframe for the gas stations of a zip code by concatenating the stations info and the price info
    Args: 

        stations_path (str): path of the stations csv file used, e.g. 'data/2024-12-31-stations.csv'

        prices_folder_path (str): path of the folder containing csv files with price info, e.g. 'data/2024-prices/'

        zipcode (str): zipcode of gas station, e.g. '22337'

    How to call:

        from Data_cleaning import concatenate_station_info

        result_df = concatenate_station_info('data/2024-12-31-stations.csv', 'data/2024-prices', '22337')
    
    Returns: 
        dataframe: df with station info and fuel prices
    '''
    df_s = clean_stations_file(stations_path)
    df_s = df_s[df_s['post_code'] == zipcode]
    df_s.rename(columns={'uuid': 'station_uuid'}, inplace=True)
    
    uuids = set(df_s['station_uuid'])
    df_list = []
    for file in sorted(os.listdir(prices_folder_path)):
        if file.endswith('.csv'):
            df = pd.read_csv(os.path.join(prices_folder_path, file))
            filtered = df[df['station_uuid'].isin(uuids)]
            df_list.append(filtered)
    
    prices = pd.concat(df_list, ignore_index=True)
    final_df = pd.merge(df_s, prices, on='station_uuid', how='left')
    
    return final_df

###################################################################################################
def extract_brand(text):
    """
    Extracts the brand name from the brand column or the main column. 
    
    Recognized brands:
    (aral, shell, esso, total, avia, jet, star, agip, raiffeisen, bft, oil!, sb) // else: other

    How to call: 
    from Data_cleaning import extract_brand // df["brand_clean"] =df.apply(extract_brand, axis=1)
    
    Returns: Text (str) with brand name or 'other'
   """
    known_brands=['aral', 'shell', 'esso', 'total', 'avia', 'jet', 'star', 'agip', 'raiffeisen', 'bft', 'oil!', 'sb']
    

    text = str(text).lower()
    for brand in known_brands:
        if brand in text:
            return brand
    return 'other'


def get_clean_brand(row):
    return (
        extract_brand(row["brand"])
        if extract_brand(row["brand"]) != "other"
        else extract_brand(row["name"])
    )

###################################################################################################
def datetime_format(df):
    '''
    Creates a new column 'datetime' with the formatted datetime without timezone
    Args:
        df (data frame): your dataframe

    Returns: 
        dataframe : with datetime column

    '''
    df['datetime'] = df['date'].apply(lambda x: datetime.strptime(x.split("+")[0], "%Y-%m-%d %H:%M:%S"))
    return df

###################################################################################################

