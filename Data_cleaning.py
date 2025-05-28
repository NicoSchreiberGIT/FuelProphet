import pandas as pd
import os


def concatenate_station_info_city(stations_path, prices_folder_path, city):
    ''' 
    This function creates a dataframe for the gas stations of a city by concatenating the stations info and the price info
    Keywords: 

        stations_path (str): path of the stations csv file used, e.g. 'data/2024-12-31-stations.csv'

        prices_folder_path(str): path of the folder containing csv files with price info, e.g. 'data/2024-prices/'

        city(str): city of gas station, e.g. 'Hamburg'

    How to call:

        from Data_cleaning import concatenate_station_info

        result_df = concatenate_station_info('data/2024-12-31-stations.csv', 'data/2024-prices', 'Hamburg')
    
    Returns: dataframe with station info and fuel prices

    '''
    df_s = pd.read_csv(stations_path)
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


def concatenate_station_info_zipcode(stations_path, prices_folder_path, zipcode):
    ''' 
    This function creates a dataframe for the gas stations of a zip code by concatenating the stations info and the price info
    Keywords: 

        stations_path (str): path of the stations csv file used, e.g. 'data/2024-12-31-stations.csv'

        prices_folder_path (str): path of the folder containing csv files with price info, e.g. 'data/2024-prices/'

        zipcode (str): zipcode of gas station, e.g. '22337'

    How to call:

        from Data_cleaning import concatenate_station_info

        result_df = concatenate_station_info('data/2024-12-31-stations.csv', 'data/2024-prices', '22337')
    
    Returns: dataframe with station info and fuel prices
    '''
    df_s = pd.read_csv(stations_path)
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



def extract_brand(text):
    """
    Extracts the brand name from the brand column or the main column. 
    
    Recognized brands:
    (aral, shell, esso, total, avia, jet, star, agip eni, raiffeisen, bft, oil!, sb) // else: other

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

# Create 'brand_clean' column
def get_clean_brand(row):
    return (
        extract_brand(row["brand"])
        if extract_brand(row["brand"]) != "other"
        else extract_brand(row["name"])
    )