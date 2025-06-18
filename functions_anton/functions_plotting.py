import pandas as pd
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
import plotly.express as px
import datetime as dt
import warnings
warnings.filterwarnings("ignore")

###############################################################################################################################

def plot_weekday_comp(df, year, week, uuid, analyzer='e5'):
    """Compares the prices for one gas station for one year, one, week but different days.

    Input example: 
        plot_weekday_comp(df_fw, 2025, 21 , 'ca59821d-9be3-4716-81e8-9aba1bca33d5', analyzer = 'e5')
    Args:
        df (DataFrame): input DataFrame containing fuel prices.
        year (integer): i.e. 2025, single value
        week (integer): i.e. 18, single value
        uuid (string): individual value 'ca59821d-9be3-4716-81e8-9aba1bca33d5'
        analyzer (str, optional): _description_. Defaults to 'e5'.
    """
    df_proc = df[(df['year'] ==year) & (df['week'] == week)  & (df['station_uuid'] == uuid)]

    df_proc['hue'] = df_proc['day'].astype(str) + '  ' + df_proc['year'].astype(str) + '  ' + df_proc['week'].astype(str)

    plt.figure(figsize=(16, 7))
    
    sns.lineplot(
        data=df_proc,
        x='time',
        y= analyzer,
        hue='hue',
        palette='Dark2',
        errorbar=None,
        drawstyle='steps-post',
        #legend = None,
        #marker = 'o',
        #linestyle='-',
        linewidth = 3,
        #style='day'

    )
    brand = df_proc['brand'].unique()
    city = df_proc['city'].unique()
    plt.legend(title = f'Day/Year/Week', fontsize=12, title_fontsize=14, loc='upper right', frameon=True, fancybox=True, shadow=True)
    
    plt.xlim(5,24)
    plt.ylim(1.6,2.0)
    plt.xticks(np.arange(5, 24, 2),fontsize=12)
    plt.yticks(fontsize=12)
    plt.title(f'{city[0]}: {analyzer} price in {year} week {week}', fontsize=16)
    plt.xlabel('time', fontsize=14)
    plt.ylabel(f'{analyzer} Price (€)', fontsize=14)


    plt.tight_layout(pad=2)
    plt.gca().set_facecolor('#f7f7fa')
    plt.gcf().patch.set_facecolor('#eaeaf2')
    plt.grid(True, which='both', axis='y', linestyle=':', linewidth=0.7)
    plt.grid(True, which='both', axis='x', linestyle=':', linewidth=0.7)  # vertical grid lines



###############################################################################################################################






def plot_weekdays(df, year, week, day, uuid, analyzer='e5'):
    """Compares the prices for one gas station for the same week days but different weeks. Year and week are a list.

    Input example: 
        plot_weekdays(df_fw, [2025],[5,7,8,9,10,15,19], 'Sunday', 'ca59821d-9be3-4716-81e8-9aba1bca33d5', analyzer = 'e5')
    Args:
        df (DataFrame): input DataFrame containing fuel prices.
        year (list): List expected i.e. [2023, 2025], single values [2025]
        week (list): List expected i.e. [5, 12], single values [12]
        day (string): i.e. 'Sunday', single value
        uuid (string): individual value 'ca59821d-9be3-4716-81e8-9aba1bca33d5'
        analyzer (str, optional): _description_. Defaults to 'e5'.
    """
    df_proc = df[(df['year'].isin(year)) & (df['week'].isin(week)) & (df['day'] == day) & (df['station_uuid'] == uuid)]

    df_proc['hue'] = df_proc['year'].astype(str) + '  ' + df_proc['week'].astype(str)

    plt.figure(figsize=(16, 7))
    
    sns.lineplot(
        data=df_proc,
        x='time',
        y= analyzer,
        hue='hue',
        palette='Dark2',
        errorbar=None,
        drawstyle='steps-post',
        #legend = None,
        #marker = 'o',
        #linestyle='-',
        linewidth = 3,
        #style='day'

    )
    brand = df_proc['brand'].unique()
    city = df_proc['city'].unique()
    plt.legend(title = f'{day} Year/Week', fontsize=12, title_fontsize=14, loc='upper right', frameon=True, fancybox=True, shadow=True)
    
    plt.xlim(5,24)
    plt.ylim(1.6,2.0)
    plt.xticks(np.arange(5, 24, 2),fontsize=12)
    plt.yticks(fontsize=12)
    plt.title(f'{city[0]}: {analyzer} price {day} in {year} week {week}', fontsize=16)
    plt.xlabel('time', fontsize=14)
    plt.ylabel(f'{analyzer} Price (€)', fontsize=14)


    plt.tight_layout(pad=2)
    plt.gca().set_facecolor('#f7f7fa')
    plt.gcf().patch.set_facecolor('#eaeaf2')
    plt.grid(True, which='both', axis='y', linestyle=':', linewidth=0.7)
    plt.grid(True, which='both', axis='x', linestyle=':', linewidth=0.7)  # vertical grid lines

    return



###############################################################################################################################




#this function plots the comparison of prices for 3 different datasets different gas station on a certain day.
def plot_diffstat_city(df1,df2,df3, year, week, day, uuid1, uuid2, uuid3, analyzer='e5'):
    """Plots the comparison of prices for 3 different datasets and 3 different gas stations on a certain day.
    
    Input example: 
        plot_diffstat_city(df_fw, df_hh, df_wh, 2025,8, 'Tuesday', [ 'ca59821d-9be3-4716-81e8-9aba1bca33d5'], ['02c3a06b-41c8-4c6a-87ca-32223c52df3a','08386c5e-29e9-4e40-ab34-ea2107e8eddf'] , ['fb0f8030-c1eb-4df1-9410-054eea7422ad'] ,analyzer = 'e5')

    Args:
        df1 (DataFrame): input DataFrame containing fuel prices.
        df2 (DataFrame): input DataFrame containing fuel prices.
        df3 (DataFrame): input DataFrame containing fuel prices.
        year (integer): i.e. 2025, single value
        week (integer): i.e. 18, single value
        day (integer): i.e. 'Sunday', single value
        uuid1 (list, string): List expected i.e. ['ca59821d-9be3-4716-81e8-9aba1bca33d5', '08386c5e-29e9-4e40-ab34-ea2107e8eddf'], single values ['ca59821d-9be3-4716-81e8-9aba1bca33d5'] 
        uuid2 (list, string): List expected i.e. ['ca59821d-9be3-4716-81e8-9aba1bca33d5', '08386c5e-29e9-4e40-ab34-ea2107e8eddf'], single values ['ca59821d-9be3-4716-81e8-9aba1bca33d5']
        uuid3 (list, string): List expected i.e. ['ca59821d-9be3-4716-81e8-9aba1bca33d5', '08386c5e-29e9-4e40-ab34-ea2107e8eddf'], single values ['ca59821d-9be3-4716-81e8-9aba1bca33d5']
        analyzer (str, optional): _description_. Defaults to 'e5'.
    """
    df_proc1 = df1[(df1['year'] == year) & (df1['week'] == week) & (df1['day'] == day) & (df1['station_uuid'].isin(uuid1))]
    df_proc2 = df2[(df2['year'] == year) & (df2['week'] == week) & (df2['day'] == day)  & (df2['station_uuid'].isin(uuid2))]
    df_proc3 = df3[(df3['year'] == year) & (df3['week'] == week) & (df3['day'] == day) & (df3['station_uuid'].isin(uuid3))]

    df_proc1['hue'] = df_proc1['brand'].astype(str)+ '  ' + df_proc1['city'].astype(str) + '  ' + df_proc1['street'].astype(str)
    df_proc2['hue'] = df_proc2['brand'].astype(str)+ '  ' + df_proc2['city'].astype(str) + '  ' + df_proc2['street'].astype(str)
    df_proc3['hue'] = df_proc3['brand'].astype(str)+ '  ' + df_proc3['city'].astype(str) + '  ' + df_proc3['street'].astype(str)

    plt.figure(figsize=(16, 7))
    
    sns.lineplot(
        data=df_proc1,
        x='time',
        y= analyzer,
        hue='hue',
        palette='Paired', # Paired or Set1 are also great
        errorbar=None,
        drawstyle='steps-post',
        #marker = 'o',
        linestyle='--',
        linewidth = 3,
        #style='day'

    )
    sns.lineplot(
        data=df_proc2,
        x='time',
        y= analyzer,
        hue='hue',
        palette='Dark2', # Paired or Set1 are also great
        errorbar=None,
        drawstyle='steps-post',
        #marker = 'o',
        linestyle='-',
        linewidth = 3,
        #style='day'

    )
    sns.lineplot(
        data=df_proc3,
        x='time',
        y= analyzer,
        hue='hue',
        palette='Set1',
        errorbar=None,
        drawstyle='steps-post',
        #marker = 'o',
        linestyle=':',
        linewidth = 3,
        #style='day'

    )
   
    plt.legend(title = 'Gas Station ID', fontsize=12, title_fontsize=14, loc='upper right', frameon=True, fancybox=True, shadow=True)
    
    plt.xlim(5,24)
    plt.ylim(1.6,2.0)
    plt.xticks(np.arange(5, 24, 2),fontsize=12)
    plt.yticks(fontsize=12)
    plt.title(f'{analyzer} price for {day} in {year} week {week}', fontsize=16)
    plt.xlabel('time', fontsize=14)
    plt.ylabel(f'{analyzer} Price (€)', fontsize=14)


    plt.tight_layout(pad=2)
    plt.gca().set_facecolor('#f7f7fa')
    plt.gcf().patch.set_facecolor('#eaeaf2')
    plt.grid(True, which='both', axis='y', linestyle=':', linewidth=0.7)
    plt.grid(True, which='both', axis='x', linestyle=':', linewidth=0.7)  # vertical grid lines


    return


###############################################################################################################################






#this function compares the prices for different gas station on a certain day. Target identify if brands change the prices simultaionsly
def plot_diffstat(df, year, week, day, uuid, analyzer='e5'):
    """Compares the prices for different gas stations on a certain day
    
    Input example: 
        plot_diffstat(df_hh,2025,8,'Tuesday', list(df_hh[df_hh['brand']== 'ARAL']['station_uuid'].unique()), analyzer = 'e5')
        plot_diffstat(df_fw,2025,8, 'Tuesday', ['f97bcef8-619c-4ac4-bf9d-35995dea884e', 'ca59821d-9be3-4716-81e8-9aba1bca33d5'], analyzer = 'e5')

    Args:
        df (DataFrame): input DataFrame containing fuel prices.
        year (integer): i.e. 2025, single value
        week (integer): i.e. 18, single value
        day (integer): i.e. 'Sunday', single value
        uuid (list,string): List expected i.e. ['ca59821d-9be3-4716-81e8-9aba1bca33d5', '08386c5e-29e9-4e40-ab34-ea2107e8eddf'], single values ['ca59821d-9be3-4716-81e8-9aba1bca33d5']
        analyzer (str, optional): _description_. Defaults to 'e5'.
    """
    df_proc = df[(df['year'] == year) & (df['week'] == week) & (df['day'] == day) & (df['station_uuid'].isin(uuid))]

    df_proc['hue'] = df_proc['brand'].astype(str) + '  ' + df_proc['street'].astype(str)

    plt.figure(figsize=(16, 7))
    
    sns.lineplot(
        data=df_proc,
        x='time',
        y= analyzer,
        hue='hue',
        palette='Dark2',
        errorbar=None,
        drawstyle='steps-post',
        #legend = None,
        #marker = 'o',
        #linestyle='-',
        linewidth = 3,
        #style='day'

    )
    brand = df_proc['brand'].unique()
    city = df_proc['city'].unique()
    plt.legend(title = 'Gas Station ID', fontsize=12, title_fontsize=14, loc='upper right', frameon=True, fancybox=True, shadow=True)
    
    plt.xlim(5,24)
    plt.ylim(1.6,2.0)
    plt.xticks(np.arange(5, 24, 2),fontsize=12)
    plt.yticks(fontsize=12)
    plt.title(f'{city[0]}: {analyzer} price {day} in {year} week {week}', fontsize=16)
    plt.xlabel('time', fontsize=14)
    plt.ylabel(f'{analyzer} Price (€)', fontsize=14)


    plt.tight_layout(pad=2)
    plt.gca().set_facecolor('#f7f7fa')
    plt.gcf().patch.set_facecolor('#eaeaf2')
    plt.grid(True, which='both', axis='y', linestyle=':', linewidth=0.7)
    plt.grid(True, which='both', axis='x', linestyle=':', linewidth=0.7)  # vertical grid lines

    return



###############################################################################################################################


#this function compares the data for a certain analyzer (e5, diesel..), for a certain station_uuid and for a certain day of week and number of displayed weeks
def plot_comp_days(df, day, year_start, year_end, week_start, week_end, uuid, analyzer='e5'):
    """Compares the price for one week day for multiple years and weeks
    
    Input example: 
        plot_comp_days(df_fw,'Monday',2024, 2025, 8,9,'f97bcef8-619c-4ac4-bf9d-35995dea884e','e5')

    Args:
        df (DataFrame): input DataFrame containing fuel prices.
        day (integer): i.e. 'Sunday', single value
        year_start (integer): year to begin plotting i.e. 2025, single value
        year_end (integer): year to end plotting i.e. 2025, single value
        week_start (integer): week to begin plotting i.e. 12, single value
        week_end (integer): week to end plotting i.e. 14, single value
        uuid (string): individual value 'ca59821d-9be3-4716-81e8-9aba1bca33d5'
        analyzer (str, optional): _description_. Defaults to 'e5'.
    """
    df_proc = df[(df['day'] == day) & (df['year'] >= year_start) & (df['year'] <= year_end) & (df['week'] >= week_start) & (df['week'] <= week_end) & (df['station_uuid'] == uuid)]
        
    plt.figure(figsize=(16, 7))
    
    df_proc['hue'] = df_proc['year'].astype(str) + ' week ' + df_proc['week'].astype(str)

    sns.lineplot(
        data=df_proc,
        x='time',
        y= analyzer,
        hue= 'hue',
        palette='Dark2',
        errorbar=None,
        drawstyle='steps-post',
        #linestyle='-',
        linewidth = 3,
    )

    plt.legend(title = day, fontsize=12, title_fontsize=14, loc='upper left', frameon=True, fancybox=True, shadow=True)
  
    #plt.xticks(range(0, 24), fontsize=12)
    plt.yticks(fontsize=12)
    plt.title(f'{analyzer} price for {day} between {year_start} week {week_start} and {year_end} week {week_end}', fontsize=16) 
    plt.xlabel('time', fontsize=14)
    plt.ylabel(f'{analyzer} Price (€)', fontsize=14)


    plt.tight_layout(pad=2)
    plt.gca().set_facecolor('#f7f7fa')
    plt.gcf().patch.set_facecolor('#eaeaf2')
    plt.grid(True, which='both', axis='y', linestyle=':', linewidth=0.7)
    plt.grid(True, which='both', axis='x', linestyle=':', linewidth=0.7)  # vertical grid lines