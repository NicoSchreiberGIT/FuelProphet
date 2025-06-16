import pandas as pd
from datetime import datetime
from statsmodels.tsa.seasonal import seasonal_decompose

def resample(merged_df, fuel='e5', time='5min'):

    '''
   Creates a dataframe with average fuel prices per timestamp

    Args:
        merged_df (pd.DataFrame): Dataframe with station info and prices from multiple stations
        fuel (str, optional): Fuel Type: 'e5', 'e10' or 'diesel'. Defaults to 'e5'.
        time (str, optional): Step size of time intervals. Defaults to '5min'.

    Returns:
        pd.DataFrame: resampled df
    '''
    # make datetime
    #merged_df['datetime'] = merged_df['date'].apply(lambda x: datetime.strptime(x.split("+")[0], "%Y-%m-%d %H:%M:%S"))
    # 1. First get only needed columns and sort
    reduced_df = merged_df[['datetime', 'station_uuid', fuel]]
    reduced_df = reduced_df.sort_values(by=['datetime', 'station_uuid'])
    
    # Remove duplicates keeping the last record for each station-datetime combination
    reduced_df_2 = reduced_df.drop_duplicates(subset=['station_uuid', 'datetime'], keep='last')
    reduced_df_2 = reduced_df_2.set_index('datetime')
    
    # Define the columns to resample and ffill
    columns_to_resample_and_ffill = [col for col in reduced_df_2.columns if col != 'station_uuid'] # ffill all columns except 'station_uuid' 
    resampled_df = reduced_df_2.groupby('station_uuid')[columns_to_resample_and_ffill].resample(time).ffill()
    resampled_df = resampled_df.reset_index() # Reset the index to turn 'date' and 'station_uuid' back into columns
    resampled_df_2 = resampled_df.iloc[1:] # drop the first row, which is NaN after resampling
    grouped = (
    resampled_df_2.groupby('datetime')[fuel]
      .mean()
      .reset_index()
    )
    df = grouped[grouped[fuel].notna()]
    return df 

####################################################################################################################################################################

def add_seasonal(resampled, fuel='e5', period=288):
    '''
    Creates a dataframe containing the original dataframe with the seasonal pattern extracted by seasonal decomposition

    Args:
        resampled (pd.DataFrame): Resampled dataframe (contains: 'datetime' and a fuel column (default: 'e5'))
        fuel (str, optional): Fuel Type: 'e5', 'e10' or 'diesel'. Defaults to 'e5'.
        period (int, optional): Periodicity of the seasonal decomposition. Defaults to 288 (equals 1 day).

    Returns:
        pd.DataFrame: df with seasonal pattern
    '''
    decompose = seasonal_decompose(resampled[fuel], model='additive', period = period)
    seasonal_df = decompose.seasonal.reset_index()

    df = pd.DataFrame({
        'datetime': resampled['datetime'],
        'seasonal_component': seasonal_df['seasonal'],
        'e5' : resampled[fuel]
    })
    df = df[df[fuel].notna()]
    return df

####################################################################################################################################################################
def resample_with_seasonality(merged_df, fuel='e5', time='5min', period=288):
    '''
    _summary_

    Args:
        merged_df (pd.DataFrame): Dataframe with station info and prices from multiple stations
        fuel (str, optional): Fuel Type: 'e5', 'e10' or 'diesel'. Defaults to 'e5'.
        time (str, optional): Step size of time intervals. Defaults to '5min'.
        period (int, optional): Periodicity of the seasonal decomposition. Defaults to 288 (equals 1 day, when time='5min').
    Returns:
        pd.DataFrame: resampled df with seasonal pattern
    '''
    
    # make datetime
    merged_df['datetime'] = merged_df['date'].apply(lambda x: datetime.strptime(x.split("+")[0], "%Y-%m-%d %H:%M:%S"))  
    # 1. First get only needed columns and sort
    reduced_df = merged_df[['datetime', 'station_uuid', fuel]]
    reduced_df = reduced_df.sort_values(by=['datetime', 'station_uuid'])
    
    # Remove duplicates keeping the last record for each station-datetime combination
    reduced_df_2 = reduced_df.drop_duplicates(subset=['station_uuid', 'datetime'], keep='last')
    reduced_df_2 = reduced_df_2.set_index('datetime')
    
    # Define the columns to resample and ffill
    columns_to_resample_and_ffill = [col for col in reduced_df_2.columns if col != 'station_uuid'] # ffill all columns except 'station_uuid' 
    resampled_df = reduced_df_2.groupby('station_uuid')[columns_to_resample_and_ffill].resample(time).ffill()
    resampled_df = resampled_df.reset_index() # Reset the index to turn 'date' and 'station_uuid' back into columns
    resampled_df_2 = resampled_df.iloc[1:] # drop the first row, which is NaN after resampling
    grouped = (
    resampled_df_2.groupby('datetime')['e5']
      .mean()
      .reset_index()
    )
    resampled = grouped[grouped[fuel].notna()]

    decompose = seasonal_decompose(resampled[fuel], model='additive', period = period)
    seasonal_df = decompose.seasonal.reset_index()

    df = pd.DataFrame({
        'datetime': resampled['datetime'],
        'seasonal_component': seasonal_df['seasonal'],
        'e5' : resampled[fuel]
    })
    df = df[df[fuel].notna()]
    return df


####################################################################################################################################################################
## adjusted from anton functions_models package
def train_test_split(df, start_date_train = '2023-01-01', end_date_train = '2025-04-30', start_date_test = '2025-05-01', end_date_test = '2025-05-24'):
    """Splits the DataFrame into training and testing sets based on date ranges.

    Args:
        df (DataFrame): Input DataFrame containing fuel prices.
        start_date_train (str): Start date for the training set.
        end_date_train (str): End date for the training set.
        start_date_test (str): Start date for the testing set.
        end_date_test (str): End date for the testing set.

    Returns:
        tuple: Training and testing DataFrames.
    """
    train = df[(df['datetime'] >= start_date_train) & (df['datetime'] <= end_date_train)]
    test = df[(df['datetime'] >= start_date_test) & (df['datetime'] <= end_date_test)]
    
    return train, test

####################################################################################################################################################################
def one_station_resample_with_seasonality(merged_df, uuid=None, fuel='e5', time='5min', period=288):
    '''
    _summary_

    Args:
        merged_df (pd.DataFrame): Dataframe with station info and prices from multiple stations
        uuid (str): uuid of the station 
        fuel (str, optional): Fuel Type: 'e5', 'e10' or 'diesel'. Defaults to 'e5'.
        time (str, optional): Step size of time intervals. Defaults to '5min'.
        period (int, optional): Periodicity of the seasonal decomposition. Defaults to 288 (equals 1 day, when time='5min').
    Returns:
        pd.DataFrame: resampled df with seasonal pattern
    '''
    
    #Drop NaNs
    merged_df = merged_df[merged_df['e5'].notna()]
    # make datetime
    #merged_df['datetime'] = merged_df['date'].apply(lambda x: datetime.strptime(x.split("+")[0], "%Y-%m-%d %H:%M:%S"))  
    # 1. First get only needed columns and sort
    reduced_df = merged_df[['datetime', 'station_uuid', fuel]]
    reduced_df = reduced_df.sort_values(by=['datetime', 'station_uuid'])


    
    # Remove duplicates keeping the last record for each station-datetime combination
    reduced_df_2 = reduced_df.drop_duplicates(subset=['station_uuid', 'datetime'], keep='last')
    reduced_df_2 = reduced_df_2.set_index('datetime')

    #Only data for one station
    one_station_df = reduced_df_2[reduced_df_2['station_uuid'] == uuid]
    
    # Define the columns to resample and ffill
    columns_to_resample_and_ffill = [col for col in one_station_df.columns if col != 'station_uuid'] # ffill all columns except 'station_uuid' 
    resampled_df = one_station_df.groupby('station_uuid')[columns_to_resample_and_ffill].resample(time).ffill()
    resampled_df = resampled_df.reset_index() # Reset the index to turn 'date' and 'station_uuid' back into columns
    resampled_df_2 = resampled_df.iloc[1:] # drop the first row, which is NaN after resampling
    grouped = (
    resampled_df_2.groupby('datetime')['e5']
      .mean()
      .reset_index()
    )
    resampled = grouped[grouped[fuel].notna()]

    decompose = seasonal_decompose(resampled[fuel], model='additive', period = period)
    seasonal_df = decompose.seasonal.reset_index()

    df = pd.DataFrame({
        'datetime': resampled['datetime'],
        'seasonal_component': seasonal_df['seasonal'],
        'e5' : resampled[fuel]
    })
    df = df[df[fuel].notna()]
    return df

####################################################################################################################################################################
####################################################################################################################################################################
####################################################################################################################################################################
####################################################################################################################################################################
####################################################################################################################################################################