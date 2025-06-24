import os
import requests
import pandas as pd
from datetime import datetime, date, time, timedelta
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

import sys
import os
# Get the parent directory and add it to sys.path
parent_dir = os.path.abspath("../FuelProphet")
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

##################################################################################################################

def preprocess_data(days = 3,file=None):

    #############################################

    # Create data/rawdata/prices
    folder_prices = "data/appdata/prices"
    if not os.path.exists(folder_prices):
        os.makedirs(folder_prices)

    # Create data/rawdata/stations
    folder_stations = "data/appdata/stations"
    if not os.path.exists(folder_stations):
        os.makedirs(folder_stations)

    # Create data/rawdata/stations
    folder_daily = "data/appdata/dailydata"
    if not os.path.exists(folder_daily):
        os.makedirs(folder_daily)

    #############################################

    #Load specific file if required
    if file is not None:
        return pd.read_parquet(folder_daily + "/" + file)

    #############################################

    # Check if daily data is already available
    if os.path.exists(folder_daily + "/alldata_" + str(datetime.today().date()) + ".parquet"):
        return pd.read_parquet(folder_daily + "/alldata_" + str(datetime.today().date()) + ".parquet")

    #############################################

    # Download all needed files from prices and concatenate together
    price_data_all = pd.DataFrame()

    for i in range(days):
        date = datetime.today() - timedelta(days = i+1)
        filename = str(date.year) + "-" + str(date.month).zfill(2) + "-" + str(date.day).zfill(2) + "-prices.csv"

        # Check if file has already been downloaded
        if not os.path.exists(folder_prices + "/" + filename):

            url = "https://dev.azure.com/tankerkoenig/tankerkoenig-data/_apis/git/repositories/tankerkoenig-data/items"
            params = {
                "path": "/prices/" + str(date.year) + "/" + str(date.month).zfill(2) + "/" + filename, # Path in repo
                "versionDescriptor.version": "master",           # Branch name
                "api-version": "6.0",                            # API version
                "$format": "octetStream",                        # Should download a binary file
            }

            response = requests.get(url, params=params, stream=True)
            response.raise_for_status()  # ensure we got a good response

            with open(folder_prices + "/" + filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

        # Read data
        price_data = pd.read_csv(folder_prices + "/" + filename)

        # Concatenate data
        price_data_all = pd.concat([price_data_all,price_data])

    #############################################

    # Download newest stations file and concatenate to price data
    date = datetime.today() - timedelta(days = 1)
    filename = str(date.year) + "-" + str(date.month).zfill(2) + "-" + str(date.day).zfill(2) + "-stations.csv"
    
    # Download file if not already done
    if not os.path.exists(folder_stations + "/" + filename):
        url = "https://dev.azure.com/tankerkoenig/tankerkoenig-data/_apis/git/repositories/tankerkoenig-data/items"
        params = {
            "path": "/stations/" + str(date.year) + "/" + str(date.month).zfill(2) + "/" + filename, # Path in repo
            "versionDescriptor.version": "master",           # Branch name
            "api-version": "6.0",                            # API version
            "$format": "octetStream",                        # Should download a binary file
        }

        response = requests.get(url, params=params, stream=True)
        response.raise_for_status()  # ensure we got a good response

        with open(folder_stations + "/" + filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

    # Read data
    stations_data = pd.read_csv(folder_stations + "/" + filename)
    stations_data.rename(columns={"uuid":"station_uuid"},inplace=True)

    # Concatenate data
    all_data = pd.merge(stations_data,price_data_all,how="left",on="station_uuid")

    # Save data premanently
    all_data.dropna(inplace=True)
    all_data["datetime"] = all_data["date"].apply(lambda x: datetime.strptime(x.split("+")[0], "%Y-%m-%d %H:%M:%S"))
    all_data = all_data.sort_values("datetime",ascending=True).reset_index()
    all_data.to_parquet(folder_daily + "/alldata_" + str(datetime.today().date()) + ".parquet")

    return all_data

##################################################################################################################

def plotly_plot(real_data,predictions):

    # Definition of time range for the buttons
    pred_start_time = predictions["datetime"].iloc[0]

    buttons = [
        dict(
            label="1 Day",
            method="relayout",
            args=[{
                "xaxis.range": [pred_start_time - pd.Timedelta(days=3), pred_start_time + pd.Timedelta(days=1)]
            }]
        ),
        dict(
            label="3 Days",
            method="relayout",
            args=[{
                "xaxis.range": [pred_start_time - pd.Timedelta(days=3), pred_start_time + pd.Timedelta(days=3)]
            }]
        ),
        dict(
            label="7 Days",
            method="relayout",
            args=[{
                "xaxis.range": [pred_start_time - pd.Timedelta(days=3), pred_start_time + pd.Timedelta(days=7)]
            }]
        )
    ]

    plot_df = pd.concat([real_data, predictions])

    # Create the base plot
    fig = px.line(
        plot_df,
        x="datetime",
        y="e5",
        #color="type",
        labels={"e5": "price", "datetime": "date/time"},
        color_discrete_map={
            "real": "#4281eaff",      
            "predicted": "#f1881aff"  
        }
    )

    # Comprehensive layout settings
    fig.update_layout(
        # Title settings
        title=dict(
            text="Prediction",
            x=0.5,
            font=dict(size=30, weight='bold')
        ),
        
        # Size and margins
        width=1500,
        height=500,
        margin=dict(l=40, r=40, t=60, b=40),
        
        # Background settings
        template="plotly_white",
        plot_bgcolor="#f9fcfc",
        paper_bgcolor="#f9fcfc",
        
        # X-axis settings
        xaxis=dict(
            title="Time",
            tickfont=dict(size=14),
            tickformatstops=[
                dict(dtickrange=[None, 1000*60*60*6], value="%H:%M"),
                dict(dtickrange=[1000*60*60*6, 1000*60*60*24*2], value="%b %d\n%H:%M"),
                dict(dtickrange=[1000*60*60*24*2, None], value="%b %d"),
            ]
        ),
        
        # Y-axis settings
        yaxis=dict(
            title="e5 price (€/L)",
            title_font=dict(size=25, weight='bold'),
            tickfont=dict(size=20),
            gridcolor="#dcdbd9"
        ),
        
        # Button menu settings
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                buttons=buttons,
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.1,
                xanchor="left",
                y=1.15,
                yanchor="top"
            )
        ]
    )

    # Line style settings
    fig.update_traces(line=dict(width=5))

    # Display the plot
    return fig

##################################################################################################################

def print_model(real_data,predictions,x="datetime",y="e5",name="name",title=None,params=None):
    """Plots the real data and the predictions in one line plot

    Args:
        real_data (DataFrame): Includes the real time series data
        predictions (DataFrame): Includes model predictions
        x (str, optional): Name of the datetime variable. Defaults to "datetime".
        y (str, optional): Name of the prediction variable. Defaults to "e5".
        xlim (tuple, optional): Minimum and maximum limit of x-axis. Defaults to None.
        ylim (tuple, optional): Minimum and maximum limit of y-axis. Defaults to None.
        name (str, optional): Gas station name variable. Defaults to "name".
    """

    if params == None:
        params = {"background":"#f9fcfc",
                  "gridcolor": "#dcdbd9",
                  "legendedge": "#dcdbd9",
                  "legendface": "white",
                  "legendcol": "black",
                  "textcolor": "black"
                  }

    now = datetime.today()
    

    # Set grid color
    sns.set_style("darkgrid", {"grid.color": params.get("gridcolor")})

    fig, ax = plt.subplots()

    # Change border color of the figure (spines)
    #ax = plt.gca()
    for spine in ax.spines.values():
        spine.set_edgecolor(params.get("gridcolor"))

    
    
    # Dashed plot
    sns.lineplot(data      = real_data[real_data[x] >= predictions[x].iloc[0]],
                 x         = "datetime",
                 y         = "e5",
                 color     = "#4281eaff",
                 drawstyle = 'steps-post',
                 #linestyle = "dashed",
                 linewidth = 3
                 )
    
    # Create line between train and test set
    # plt.vlines(x         = predictions[x].iloc[0],
    #            ymin      = real_data.iloc[0][y],
    #            ymax      = predictions[y].iloc[0],
    #            color     = "#a6a5a4",
    #            linewidth = 2,
    #            linestyle = "dashed"
    #            )
    
    # Set transparency (alpha)
    for line in fig.lines:
        line.set_alpha(0.4)
    
    # Create lines
    sns.lineplot(data      = real_data[real_data[x] <= predictions[x].iloc[0]],
                 x         = "datetime",
                 y         = "e5",
                 color     = "#4281eaff",
                 drawstyle = 'steps-post',
                 label     = "Real price",
                 linewidth = 3
    )

    plt.vlines(x         = predictions[x].iloc[0],
               ymin      = real_data[real_data[x] == predictions[x].iloc[0]][y],
               ymax      = predictions[y].iloc[0],
               color     = "#f1881aff",
               linewidth = 3
               )
    
    sns.lineplot(data      = predictions,
                 x         = "datetime",
                 y         = "e5",
                 color     = "#f1881aff",
                 drawstyle = 'steps-post',
                 label     = "Predicted price",
                 linewidth = 3
                 )
    
    # plt.vlines(x         = now,
    #            ymin      = ax.get_ylim()[0],
    #            ymax      = ax.get_ylim()[1],
    #            color     = "#a6a5a4",
    #            linewidth = 2,
    #            linestyle = "dashed"
    #             )
    
    now_rounded = now - timedelta(minutes=now.minute % 5,
                            seconds=now.second,
                            microseconds=now.microsecond)

    # plt.hlines(y         = predictions[predictions[x] == now_rounded][y],
    #            xmin      = real_data.iloc[0][x],
    #            xmax      = predictions.iloc[-1][x],
    #            color     = "#a6a5a4",
    #            linewidth = 2,
    #            linestyle = "dashed"
    #             )
    
    # plt.text(ax.get_xlim()[0],predictions[predictions[x] == now_rounded][y],str(round(predictions[predictions[x] == now_rounded][y].iloc[0],3)),fontweight="bold",fontsize=12,color="#a6a5a4")

    if ~(predictions[x] == now_rounded).any() == False:
        plt.plot(now_rounded,predictions[predictions[x] == now_rounded][y], color='red', marker='x',markersize=14,markeredgewidth=6)
        plt.text(now_rounded,predictions[predictions[x] == now_rounded][y]+0.02,
                "Current predicted price:\n"+str(round(predictions[predictions[x] == now_rounded][y].iloc[0],3)),
                fontweight="bold",fontsize=12,color="#393939ff")

    # Adapt title
    if title == None:
        plt.title("Fuel price prediction of " + real_data[name].iloc[1],fontweight="bold",fontsize=14,color=params.get("textcolor"))
    else:
        plt.title(title,fontweight="bold",fontsize=14,color=params.get("textcolor"))

    # Adapt labels
    plt.xlabel(" ",fontweight="bold",fontsize=14,color=params.get("textcolor"))
    plt.ylabel(y + " price (€/l)",fontweight="bold",fontsize=14,color=params.get("textcolor"))

    # Adapt xticks
    xticks = ax.get_xticks()
    xticklabels = []
    for i, tick in enumerate(xticks):
        if i % 2 == 0:
            label = plt.matplotlib.dates.num2date(tick).strftime('%H:%M\n%d/%m/%Y')
        else:
            label = plt.matplotlib.dates.num2date(tick).strftime('%H:%M')
        xticklabels.append(label)
    ax.set_xticklabels(xticklabels)
    for label in plt.gca().get_xticklabels():
        label.set_fontsize(14)
        label.set_color(params.get("textcolor"))
        label.set_fontsize(14)

    # Adapt yticks
    for label in plt.gca().get_yticklabels():
        label.set_fontweight('normal')
        label.set_color(params.get("textcolor"))
        label.set_fontsize(14)

    # Adapt background color
    plt.gca().set_facecolor(params.get("background"))
    plt.gcf().set_facecolor(params.get("background"))

    # Create legend
    plt.legend(fontsize=14,loc='upper right', edgecolor=params.get("legendedge"), facecolor=params.get("legendface"), labelcolor = params.get("legendcol"),framealpha=1)

    plt.close(fig)

    return fig