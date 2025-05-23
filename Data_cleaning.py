import pandas as pd
import os

''' 
This function creates a dataframe for the gas stations of a city by concatenating the stations info and the price info
Keywords: 
stations_path: path of the stations csv file used, e.g. 'data/2024-12-31-stations.csv'
prices_folder_path: path of the folder containing csv files with price info, e.g. 'data/2024-prices/'
city: city of gas station, e.g. 'Hamburg'

How to call this function in your notebook (example):

from Data_cleaning import concatenate_station_info
result_df = concatenate_station_info('data/2024-12-31-stations.csv', 'data/2024-prices', 'Hamburg')


'''
def concatenate_station_info(stations_path, prices_folder_path, city):
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
    final_df = pd.merge(prices, df_s, on='station_uuid', how='left')
    
    return final_df