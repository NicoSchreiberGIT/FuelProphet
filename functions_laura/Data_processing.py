import pandas as pd
from datetime import datetime

def resample(df, fuel='e5', time='5min'):

    '''
   Creates a dataframe with average fuel prices per timestamp

    Args:
        df (pd.DataFrame): Concatenated dataframe
        fuel (str, optional): Fuel Type: 'e5', 'e10' or 'diesel'. Defaults to 'e5'.
        time (str, optional): Step size of time intervals. Defaults to '5min'.
    '''
    
    # 1. First get only needed columns and sort
    df = df[['datetime', 'station_uuid', fuel]]
    df = df.sort_values(by=['datetime', 'station_uuid'])
    
    # Remove duplicates keeping the last record for each station-datetime combination
    df = df.drop_duplicates(subset=['station_uuid', 'datetime'], keep='last')
    
    # 2. Create a complete time range for each station
    min_time = df['datetime'].min()
    max_time = df['datetime'].max()
    time_range = pd.date_range(start=min_time, end=max_time, freq=time)
    stations = df['station_uuid'].unique()
    
    # 3. Create MultiIndex with all combinations
    multi_idx = pd.MultiIndex.from_product(
        [stations, time_range],
        names=['station_uuid', 'datetime']
    )
    
    # 4. Set MultiIndex on original data and reindex
    df = df.set_index(['station_uuid', 'datetime'])
    df = df.reindex(multi_idx)
    
    # 5. Forward fill within each station group
    df = df.groupby('station_uuid').ffill()
    
    # 6. Reset index to get back to columns
    df = df.reset_index()
    df = df[df[fuel].notna()]
    
    df = (
    df.groupby('datetime')['e5']
      .mean()
      .reset_index()
    )
    
    return df
