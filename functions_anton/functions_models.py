import pandas as pd
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from datetime import datetime, date, time, timedelta
import warnings
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_percentage_error, mean_absolute_error
warnings.filterwarnings("ignore")








##############################################################################################################################







##############################################################################################################################
def merge_regressor(df_main, df_sec, column, df_main_date = 'date', df_sec_date = 'datetime'):
    """_summary_

    Args:
        df_main (_type_): _description_
        df_sec (_type_): _description_
        column (_type_): which column to merge on
        df_main_date (str, optional): _description_. Defaults to 'date'.
        df_sec_date (str, optional): _description_. Defaults to 'datetime'.

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """

    df_sec[column] = df_sec[column].ffill()
    df_sec[df_sec_date] = pd.to_datetime(df_sec[df_sec_date])
    df_sec['merge_date'] = df_sec[df_sec_date].dt.date
    df_main['merge_date'] = df_main[df_main_date].dt.date
    df_sec_merge = df_sec[['merge_date', column]].copy()
    df_comb = pd.merge(
        df_main,
        df_sec_merge, 
        how='left',
        on='merge_date'
    )
    df_comb = df_comb.drop(columns=['merge_date'])
    return df_comb






##############################################################################################################################





def step_modification_to_forecast(df_forecast, threshold = 0.01):
    """
    Modifies the 'yhat' column in a DataFrame to behave like a step function.
    Each value in the new 'yhat_step_modified' column is compared to the
    *previous* modified value. If the absolute difference is greater than
    the threshold, the current 'yhat' value is taken. Otherwise, the
    previous modified value is retained.

    This version is optimized for performance by operating on NumPy arrays
    for the core iterative logic.

    Args:
        df_forecast (pd.DataFrame): DataFrame expected to have 'ds' (datetime)
                                   and 'yhat' (numeric) columns.
        threshold (float): The maximum absolute difference for a value to be
                           replaced by the previous modified value.

    Returns:
        pd.DataFrame: A new DataFrame with an additional 'yhat_step_modified' column.
                      The 'ds' column is used to ensure proper ordering.
    """
    if 'ds' not in df_forecast.columns or 'yhat' not in df_forecast.columns:
        raise ValueError("Input DataFrame must contain 'ds' and 'yhat' columns.")
    
    # Ensure the DataFrame is sorted by 'ds' to correctly apply the sequential logic
    df_modified = df_forecast.sort_values(by='ds').copy()
    
    if df_modified.empty:
        df_modified['yhat_step_modified'] = [] # Add the column for empty DataFrame
        return df_modified

    # Extract yhat to a NumPy array for faster iteration
    yhat_array = df_modified['yhat'].to_numpy()
    
    # Initialize the array for modified yhat values
    yhat_step_modified_array = np.empty_like(yhat_array)
    
    # The first value is always the original first yhat
    yhat_step_modified_array[0] = yhat_array[0]

    # Iterate through the array starting from the second element
    # This loop operates directly on NumPy arrays, which is much faster than df.loc
    for i in range(1, len(yhat_array)):
        current_yhat = yhat_array[i]
        previous_modified_yhat = yhat_step_modified_array[i-1]

        if abs(current_yhat - previous_modified_yhat) > threshold:
            yhat_step_modified_array[i] = current_yhat
        else:
            yhat_step_modified_array[i] = previous_modified_yhat
            
    # Assign the modified array back to a new column in the DataFrame
    df_modified['yhat'] = yhat_step_modified_array
            
    return df_modified





##############################################################################################################################








def find_dominant_stable_hours(df_data, price_col='e5', tolerance=0.01, stability_threshold=0.95, min_block_length=3):
    """
    Optimized function to find the most consistently stable block of hours (plateau)
    for each day of the week, based on price stability across all historical data.

    Args:
        df_data (pd.DataFrame): DataFrame with 'date' (datetime) and price_col (numeric).
                                MUST have 'hour' and 'dayofweek' columns already.
        price_col (str): The name of the price column.
        tolerance (float): Max absolute change in price to consider a period stable.
        stability_threshold (float): Proportion of an hour that must be stable for it to count.
        min_block_length (int): Minimum number of consecutive stable hours to be considered a dominant plateau.

    Returns:
        dict: {dayofweek_idx: (start_hour, end_hour) or (None, None)} of the most consistently stable period.
              Returns (None, None) if no clear pattern is found for a day, meaning no plateau.
    """
    df_temp = df_data.copy()
    df_temp['price_diff'] = df_temp[price_col].diff().fillna(0)
    df_temp['is_stable_point'] = (abs(df_temp['price_diff']) <= tolerance).astype(int)

    hourly_stability_by_weekday = df_temp.groupby(['dayofweek', 'hour'])['is_stable_point'].mean().unstack(fill_value=0)

    plateau_hours_by_weekday = {}
    weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    for day_idx in range(7):
        day_name = weekday_names[day_idx]
        
        # Default to (None, None) for days with no data or no clear plateau
        plateau_hours_by_weekday[day_idx] = (None, None) 

        if day_idx not in hourly_stability_by_weekday.index:
            print(f"No data found for {day_name}. No plateau detected, all hours will be 'open'.")
            continue

        hourly_proportions = hourly_stability_by_weekday.loc[day_idx]
        extended_proportions = pd.concat([hourly_proportions, hourly_proportions], ignore_index=True)

        max_stable_block_length = 0
        best_start_hour = None
        current_block_length = 0
        current_block_start_index = None

        for i in range(len(extended_proportions)):
            if extended_proportions.iloc[i] >= stability_threshold:
                if current_block_length == 0:
                    current_block_start_index = i
                current_block_length += 1
            else:
                if current_block_length > max_stable_block_length:
                    max_stable_block_length = current_block_length
                    best_start_hour = current_block_start_index % 24
                current_block_length = 0
                current_block_start_index = None
        
        if current_block_length > max_stable_block_length:
            max_stable_block_length = current_block_length
            best_start_hour = current_block_start_index % 24

        # If a significant plateau is found, store its hours
        if best_start_hour is not None and max_stable_block_length >= min_block_length:
            opening_hour = (best_start_hour + max_stable_block_length) % 24
            plateau_hours_by_weekday[day_idx] = (best_start_hour, opening_hour)
            #print(f"Detected longest plateau for {day_name}: From {best_start_hour}:00 to {opening_hour}:00 (next day if starts >= ends)")
        else:
            # If no clear plateau is found, keep (None, None) for this day, so all hours will be 'open'
            print(f"No clear plateau found for {day_name} (max consecutive stable hours: {max_stable_block_length}). All hours will be 'open'.")
            
    return plateau_hours_by_weekday





##############################################################################################################################





def plot_forecast(df_train, df_test, station_uuid = None, df_train_prediction=None, df_test_prediction=None, train_dates=None, test_dates=None):
    plt.figure(figsize=(15, 6))
    
    train_mask = (df_train['date'] >= train_dates[0]) & (df_train['date'] <= train_dates[1]) if train_dates else slice(None)
    test_mask = (df_test['date'] >= test_dates[0]) & (df_test['date'] <= test_dates[1]) if test_dates else slice(None)

    plt.plot(df_train.loc[train_mask, 'date'], df_train.loc[train_mask, 'e5'], label='Train Actual', color='blue', linewidth=2, drawstyle='steps-post', alpha=0.7)
    plt.plot(df_test.loc[test_mask, 'date'], df_test.loc[test_mask, 'e5'], label='Test Actual', color='orange', linewidth=2, drawstyle='steps-post', alpha=0.7)

    if station_uuid is not None:
        df_train = df_train[df_train['station_uuid'] == station_uuid]
        df_test = df_test[df_test['station_uuid'] == station_uuid]

    if df_train_prediction is not None:
        df_train_prediction = df_train_prediction[(df_train_prediction['date'] >= train_dates[0]) & (df_train_prediction['date'] <= train_dates[1])]
        plt.plot(df_train_prediction['date'], df_train_prediction['e5'], label='Train Prediction', color='green', linestyle='--', linewidth=2, drawstyle='steps-post')

    if df_test_prediction is not None:
        df_test_prediction = df_test_prediction[(df_test_prediction['date'] >= test_dates[0]) & (df_test_prediction['date'] <= test_dates[1])]
        plt.plot(df_test_prediction['date'], df_test_prediction['e5'], label='Test Prediction', color='red', linestyle='--', linewidth=2, drawstyle='steps-post')

        # --- Error Calculation and Display ---
        df_merged = df_test.merge(df_test_prediction, on='date', suffixes=('_actual', '_pred'))
        df_merged = df_merged.sort_values('date').reset_index(drop=True)

        for i, days in enumerate([1, 3, 7]):
            time_cutoff = df_merged['date'].min() + timedelta(days=days)
            df_subset = df_merged[df_merged['date'] < time_cutoff]

            if not df_subset.empty:
                mae = mean_absolute_error(df_subset['e5_actual'], df_subset['e5_pred'])
                # Print to console
                print(f"{days}-Day MAE in cent: {mae *100:.4f}")
                # Show on plot
                plt.text(0.01, 0.95 - 0.05 * i, f'{days}-day MAE in cent: {mae*100:.4f}', transform=plt.gca().transAxes,
                         fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="gray", alpha=0.7))

    plt.legend(fontsize=12, title_fontsize=14, loc='upper right', frameon=True, fancybox=True, shadow=True)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.title('E5 Price: Actual vs Prediction', fontsize=16)
    plt.xlabel('date', fontsize=14)
    plt.ylabel('E5 price', fontsize=14)
    plt.tight_layout(pad=2)
    plt.gca().set_facecolor('#f7f7fa')
    plt.gcf().patch.set_facecolor('#eaeaf2')
    plt.grid(True, which='both', axis='y', linestyle=':', linewidth=0.7)
    plt.grid(True, which='both', axis='x', linestyle=':', linewidth=0.7)




##############################################################################################################################


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



