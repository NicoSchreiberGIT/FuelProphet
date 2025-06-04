
import numpy as np
import pandas as pd
import plotly_express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import sys
import os
sys.path.append(os.path.abspath(".."))

from datetime import datetime
from get_current_fuel_prices import get_current_fuel_prices
from statsmodels.tsa.seasonal import seasonal_decompose


brand_colors = {
'aral': '#0069B3',
'shell': '#FFD100',
'total': '#EA1C24',
'esso': '#003399',
'avia': '#333333',
'bft' : '#EF4023',
'jet' : '#FFDD00',
'sb' : '#999999',
'raiffeisen' : '#00A651',
'star' : '#E50010',
'agip' : '#FFCC00',
'oil!' : '#212121',
'freie tankstelle' : '',
'other': "#BBAEAE"
}

def one_station(df=None, uuid=None, fuel='e5'):
    '''
    Creates a plot of the price of one station given the uuid.
    Example: 
    fig = one_station(myfd, '115b95c1-9c5b-405c-9f51-1e7309c49268')
    fig.show()

    Args:
        df (dataframe): _description_. Defaults to None.
        uuid (str): _description_. Defaults to None.
        fuel (str, optional): Fuel Type: 'e5', 'e10' or 'diesel'. Defaults to 'e5'.
    Returns:
        plot: price of fuel over time for one gas station
    '''
    one_station_df = df[df["station_uuid"] == uuid]

    fig = px.line(one_station_df, x="datetime", y=fuel, title="Fuel Price Over Time")
    fig.update_layout(
        title_font_size=20,
        xaxis_title="Date",
        yaxis_title="Price (€/L)",
        width=900,
        height=1000,
        margin=dict(l=40, r=40, t=60, b=40),
        template="plotly_white"
    )
    return fig

###################################################################################################
def average_prices(df, fuel='e5', brand=False, area='Germany', brand_column_name='brand_clean'):
    '''
    _summary_

    Args:
        df (dataframe): must contain columns: 'station_uuid', 'datetime' and one of: 'e5', 'e10' or 'diesel', optional: 'brand_clean'.
        fuel (str, optional): Fuel Type: 'e5', 'e10' or 'diesel'. Defaults to 'e5'.
        brand (bool, optional): Plots a line per brand (must contain cleaned brand column (from data_cleaning -> extract brand)). Defaults to False.
        area (str, optional): City, area or postcode, only needed for title. Defaults to Germany.
        brand_column_name (str, optional): name of the column with cleaned brand name. Defaults to 'brand_clean'
    Returns:
        plots: average price per df per uuid total (brand=False) or by brand (brand=True)

    '''

    
    df = (
    df.sort_values('datetime')  # ensure sorting so last() works as expected
    .groupby(['station_uuid', 'datetime'], as_index=False)
    .last()  # or .mean() if multiple entries should be averaged
    )
    df = df.set_index('datetime') #datetime as index
    
    if brand == False:

        df = (
        df.groupby('station_uuid')[fuel]
        .resample('5min')  
        .ffill() # there are values for every 5 minutes for all stations
        .reset_index()
        )

        df = (
        df
        .groupby('datetime')[fuel] 
        .mean() #average price per 5 minutes
        .reset_index()
        )

        df = df[df[fuel].isna() == False] #drop the first missing value

        fig = px.line(df, x="datetime", y=fuel, title=f"Average {fuel} price in {area} over Time")
        fig.update_layout(
        title_font_size=20,
        xaxis_title="Time",
        yaxis_title="Average price (€/L)",
        width=1500,
        height=800,
        margin=dict(l=40, r=40, t=60, b=40),
        template="plotly_white"
        )

    if brand == True:

        df = (
        df.groupby('station_uuid')[fuel, brand_column_name]
        .resample('5min')  
        .ffill() # there are values for every 5 minutes for all stations
        .reset_index()
        )

        df = (
        df
        .groupby('datetime')
        .agg({
            fuel: 'mean',
            brand_column_name: lambda x: x.mode()[0] 
        })
        .reset_index()
        )

        df = df[df[fuel].isna() == False] #drop the first missing value

        fig = px.line(df, x="datetime", y=fuel, title=f"Average {fuel} price in {area} over Time", color=brand_column_name)
        fig.update_layout(
        title_font_size=20,
        xaxis_title="Time",
        yaxis_title="Average price (€/L)",
        width=1500,
        height=800,
        margin=dict(l=40, r=40, t=60, b=40),
        template="plotly_white",
        color_discrete_map=brand_colors
        )
    
    return fig
###################################################################################################
def daily_pattern(df, fuel='e5', brand=False, area='Germany', brand_column_name='brand_clean'):
    '''
    _summary_

    Args:
        df (df): must contain columns: 'station_uuid', 'datetime' and one of: 'e5', 'e10' or 'diesel', optional: 'brand_clean'.
        fuel (str, optional): Fuel Type: 'e5', 'e10' or 'diesel'. Defaults to 'e5'.
        brand (bool, optional): Plots a line per brand (must contain cleaned brand column (from data_cleaning -> extract brand)). Defaults to False.
        area (str, optional): City, area or postcode, only needed for title. Defaults to 'Germany'.
        brand_column_name (str, optional): name of the column with cleaned brand name. Defaults to 'brand_clean'.
    Returns:
         plots: daily price per df per uuid total (brand=False) or by brand (brand=True)

    '''
    df = (
    df.sort_values('datetime')  # ensure sorting so last() works as expected
    .groupby(['station_uuid', 'datetime'], as_index=False)
    .last()  # or .mean() if multiple entries should be averaged
    )
    df = df.set_index('datetime') #datetime as index
    


    if brand == False:

        df = (
        df.groupby('station_uuid')[fuel]
        .resample('5min')  
        .ffill() # there are values for every 5 minutes for all stations
        .reset_index()
        )
            
        df['time_of_day'] = df['datetime'].dt.strftime('%H:%M')

        df = (
        df.groupby('time_of_day')[fuel]
        .mean()
        .reset_index()
        )

        fig = px.line(df, x="datetime", y=fuel, title=f"Average {fuel} price in {area} per day", color=brand_column_name)
        fig.update_layout(
        title_font_size=20,
        xaxis_title="Time",
        yaxis_title="Average price (€/L)",
        width=1500,
        height=800,
        margin=dict(l=40, r=40, t=60, b=40),
        template="plotly_white"
        )

    if brand == True:

        df = (
        df.groupby('station_uuid')[fuel, brand_column_name]
        .resample('5min')  
        .ffill() # there are values for every 5 minutes for all stations
        .reset_index()
        )

        df['time_of_day'] = df['datetime'].dt.strftime('%H:%M')

        df = (
        df
        .groupby([brand_column_name, 'time_of_day'])
        .agg({
            fuel: 'mean'
        })
        .reset_index()
        )

        fig = px.line(df, x="datetime", y=fuel, title=f"Average {fuel} price in {area} per day")
        fig.update_layout(
        title_font_size=20,
        xaxis_title="Time",
        yaxis_title="Average price (€/L)",
        width=1500,
        height=800,
        margin=dict(l=40, r=40, t=60, b=40),
        template="plotly_white",
        color_discrete_map=brand_colors
        )
    
    return fig
###################################################################################################
def print_scattermap(df=None, brand=False, centerlat= 51.1634, centerlon=10.4477, zoom=5.4, brand_column_name='brand_clean'):

    '''
    Creates a scattermap of the gas stations in a dataframe. Center default is center of Germany.

    Args:
        df (dataframe): must contain columns: 'latitude', 'longitude', 'name', optional: 'brand_clean'  Defaults to None.
        brand (bool, optional): If true, plots brand color and legend (must contain cleaned brand column (from data_cleaning -> extract brand)). Defaults to False.
        centerlat (float, optional): _description_. Defaults to 51.1634.
        centerlon (float, optional): _description_. Defaults to 10.4477.
        zoom (float, optional): _description_. Defaults to 5.4.

    Returns:
        Scattermap: of gas station locations
    '''
    if brand == True:
    
        fig =   px.scatter_map(
        df, 
        lat = 'latitude',
        lon = 'longitude',
        hover_name = 'name',
        hover_data = {'latitude' : False, 'longitude' : False},
        #center = {'lat': 51.1634, 'lon': 10.4477},
        zoom = 5.4,
        color=brand_column_name,
        color_discrete_map=brand_colors,
        labels={"brand_clean": "brand"}
        )
        fig.update_layout(autosize=False,
        width=1200,
        height=800,
         margin={
        'l':50,
        'r':50,
        'b':30,
        't':30},
        mapbox_center = {'lat': centerlat, 'lon': centerlon} 
)
        
    if brand == False:

        fig =   px.scatter_map(
            df, 
            lat = 'latitude',
            lon = 'longitude',
            hover_name = 'name',
            hover_data = {'latitude' : False, 'longitude' : False},
            center = {'lat': centerlat, 'lon': centerlon},
            zoom = zoom
            )
        fig.update_layout(autosize=False,
            width=1200,
            height=800,
            margin={
                'l':50,
                'r':50,
                'b':30,
                't':30}
            )
    return fig

###################################################################################################
def api_map(lat=53.6097731, lon=10.0330959, radius=5, ):
    
    df = get_current_fuel_prices(lat, lon, radius) # get the price data

    def make_circle(lat, lon, radius_km, num_points=100): # draw the circle taking geometry into account
        earth_radius = 6371  # in km
        lats, lons = [], []
        for i in range(num_points):
            angle = 2 * np.pi * i / num_points
            dx = radius_km * np.cos(angle)
            dy = radius_km * np.sin(angle)
            delta_lat = (dy / earth_radius) * (180 / np.pi)
            delta_lon = (dx / (earth_radius * np.cos(np.pi * lat / 180))) * (180 / np.pi)
            lats.append(lat + delta_lat)
            lons.append(lon + delta_lon)
        lats.append(lats[0])
        lons.append(lons[0])

        return lats, lons
    
    circle_lats, circle_lons = make_circle(lat, lon, radius)

    fig =  px.scatter_map(
        df, 
        lat = 'lat',
        lon = 'lng',
        hover_name = 'name',
        hover_data = {'lat' : False, 'lng' : False, 'e5' : True, 'e10' : True, 'diesel' : True, 'isOpen' : True},
        center = {'lat': lat, 'lon': lon},
        zoom = 11,
        )
    fig.update_layout(autosize=False,
        width=1200,
        height=800,
        margin={
            'l':50,
            'r':50,
            'b':30,
            't':30}
    )
    fig.add_trace(
        go.Scattermap(
            lat=circle_lats,
            lon=circle_lons,
            mode='lines',
            fill='toself',
            fillcolor='rgba(0, 100, 255, 0.1)',
            line=dict(color='blue'),
            name=f"{radius} km radius"
        )
    )

    return fig

###################################################################################################
def decompose_and_plot(merged_df, fuel='e5', time='5min', period=288):
    '''
    Resample, decompose and fancy plot the merged dataframe

    Args:
        merged_df (pd.DataFrame): Dataframe with station info and prices from multiple stations
        fuel (str, optional): Fuel Type: 'e5', 'e10' or 'diesel'. Defaults to 'e5'.
        time (str, optional): Step size of time intervals. Defaults to '5min'.
        period (int, optional): Periodicity of the seasonal decomposition. Defaults to 288 (equals 1 day, when time='5min').
    '''
    # Define colors for consistent styling
    colors = ['#193251','#FF5A36','#696969', '#7589A2']
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
    grouped = grouped.set_index('datetime')
    resampled = grouped[grouped[fuel].notna()]

    decompose = seasonal_decompose(resampled[fuel], model='additive', period = period)

    # Create subplot layout with 6 rows
    fig, ax = plt.subplots(6, 1, figsize=(12, 18), constrained_layout=True)

    # Plot Signal
    ax[0].set(title='Original Time Series', ylabel='Price (€/L)')
    decompose.observed.plot(color=colors[0], linewidth=1, ax=ax[0])

    # Plot Trend
    ax[1].set(title='Trend Component', ylabel='Price (€/L)')
    decompose.trend.plot(color=colors[1], linewidth=1, ax=ax[1])

    # Plot Full Seasonality
    ax[2].set(title='Seasonal Component (Full View)', ylabel='Price (€/L)')
    decompose.seasonal.plot(color=colors[2], linewidth=1, ax=ax[2])

    # Plot Week Zoom
    ax[3].set(title='Seasonal Component (One Week Zoom)', ylabel='Price (€/L)')
    week_zoom = decompose.seasonal.iloc[:288*7]  # One week of data
    week_zoom.plot(color=colors[2], linewidth=1, ax=ax[3])

    # Plot Day Zoom
    ax[4].set(title='Seasonal Component (24 Hour Zoom)', ylabel='Price (€/L)')
    day_zoom = decompose.seasonal.iloc[:288]  # One day of data (288 5-minute intervals)
    day_zoom.plot(color=colors[2], linewidth=1, ax=ax[4])

    # Plot Residual
    ax[5].set(title='Residual Component', ylabel='Price (€/L)')
    ax[5].scatter(decompose.resid.index, decompose.resid, color=colors[3], s=2)

    # for i in range(4):
    #     ax[i].set_xlim(pd.to_datetime("2023"),pd.to_datetime("2026"))
            
    # Add main title
    plt.suptitle('Seasonal Decomposition of E5 Fuel Prices', fontsize=16, y=1.02)
    plt.show()

