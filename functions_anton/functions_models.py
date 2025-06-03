import pandas as pd
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from datetime import datetime, date, time, timedelta
import warnings
warnings.filterwarnings("ignore")

###############################################################################################################################


def train_test_split(df, start_date_train = '01-01-2023', end_date_train = '30-04-2025', start_date_test = '01-05-2025', end_date_test = '24-05-2025'):
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
    pd.to_datetime([start_date_train, end_date_train, start_date_test, end_date_test], format='%d-%m-%Y')
    train = df[(df['date'] >= start_date_train) & (df['date'] <= end_date_train)]
    test = df[(df['date'] >= start_date_test) & (df['date'] <= end_date_test)]
    return train, test

###############################################################################################################################

def resample_data(df, freq='5min'):
    """General function to resample data by a given frequency and forward fill missing values.

    Args:
        df (DataFrame): input DataFrame containing fuel prices.
        freq (str, optional): How often the data should be sampled. Default to '5min'.

    Returns:
        _type_: _description_
    """

    df = df.drop_duplicates(subset=['station_uuid', 'date'], keep='last') # since in the fw_df there are duplicates, apparently
    df = df.set_index('date')

    # Define the columns to resample and ffill
    columns_to_resample_and_ffill = [col for col in df.columns if col != 'station_uuid'] # ffill all columns except 'station_uuid' 
    resampled_df = df.groupby('station_uuid')[columns_to_resample_and_ffill].resample(freq).ffill()
    resampled_df = resampled_df.reset_index() # Reset the index to turn 'date' and 'station_uuid' back into columns
    

    return resampled_df.iloc[1:] # drop the first row, which is NaN after resampling



