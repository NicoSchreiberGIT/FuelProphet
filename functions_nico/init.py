
# Import packages
import pandas as pd
from datetime import datetime, date, time, timedelta

def load_data(filename,filetype="parquet",date="date",outliers=("e5",1.0,2.5),resample="5min",id=["station_uuid","name"]):
    """Loads and preprocesses a parquet or csv file

    Args:
        filename (str): Complete name of the file with extension
        filetype (str, optional): Must be 'parquet' or 'csv'. Defaults to "parquet".
        date (str, optional): Date variable if available and in str format. Defaults to "date".
        outliers (tuple, optional): Tuple with following entries: 1:Name of variable 2: Lower limit 3: Upper limit. Defaults to ("e5",1.0,2.5).

    Returns:
        DataFrame: Loaded dataframe
    """
    
    # Load data
    if filetype == "parquet":
        df = pd.read_parquet(filename)
    elif filetype == "csv":
        df = pd.read_csv(filename)
    else:
        print("Wrong filetype")
        return
    
    # Drop missing values
    df.dropna(inplace=True)

    # Drop outliers
    if outliers != None:
        df = df[(df[outliers[0]]>outliers[1]) & (df[outliers[0]]< outliers[2])]


    if date != None:
        df["datetime"] = df[date].apply(lambda x: datetime.strptime(x.split("+")[0], "%Y-%m-%d %H:%M:%S"))
        df["datedate"] = df["datetime"].dt.date
        df["hour"] = df["datetime"].dt.hour

    if resample != None:
        df_resample = df.set_index('datetime')
        df_resample = df_resample.groupby(id)[outliers[0]].resample(resample).ffill().reset_index()

    return df_resample

