
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

##############################################################################################################################

def merge_oil(data,date="datetime",oildata="../data/nico_features/oil_EIA.parquet"):
    """Merges oil data to the input dataset by date

    Args:
        data (DataFrame): Input dataframe including fuel prices
        date (str, optional): Name of the date variable. Defaults to "datetime".
        oildata (str, optional): Oil dataset to be used. Should not be changed. Defaults to "data/oildata/oil_EIA.parquet".

    Returns:
        DataFrame: Input dataset with two additional columns for daily and monthly oil prices
    """

    # Load data
    df_oil = pd.read_parquet(oildata)
    df_data = data.copy()

    # Prepare data
    df_oil["_mo_date"] = df_oil["datetime"].dt.date
    df_oil.drop([date],axis=1,inplace=True)
    df_data["_mo_date"] = df_data[date].dt.date

    # Merge data together
    df_final = pd.merge(df_data,df_oil,on=["_mo_date"],how="left")
    df_final.drop("_mo_date",axis=1,inplace=True)

    return df_final

##############################################################################################################################

def merge_ex_rate(data,date="datetime",exdata="../data/nico_features/exchange_rate.parquet"):
    """Merges daily exchange rates to the input dataset

    Args:
        data (DataFrame): Input dataframe including fuel prices
        date (str, optional): Name of the date variable. Defaults to "datetime".
        exdata (str, optional): Exchange rate dataset to be used. Should not be changed. Defaults to "data/exchange_rate/exchange_rate.parquet".

    Returns:
        DataFrame: Input dataset with one additional column including daily exchange rates
    """

    # Load data
    df_ex = pd.read_parquet(exdata)
    df_data = data.copy()

    # Prepare data
    df_ex["_me_date"] = df_ex["datetime"].dt.date
    df_ex.drop(["datetime"],axis=1,inplace=True)
    df_data["_me_date"] = df_data[date].dt.date

    # Merge data together
    df_final = pd.merge(df_data,df_ex,on=["_me_date"],how="left")
    df_final.drop("_me_date",axis=1,inplace=True)

    return df_final

##############################################################################################################################

def get_oil_euro(data,oil_var="oilprice",exrate_var="exchange_rate"):
    """Calculates oil price in euros and adds it to the input dataset

    Args:
        data (DataFrame): Input dataframe including fuel prices
        oil_var (str, optional): Name of the oil price variable. Defaults to "oilprice".
        exrate_var (str, optional): Name of the exchange rate variable. Defaults to "exchange_rate".
    """

    data[oil_var+"_euro"] = round(data[oil_var]/data[exrate_var],2)