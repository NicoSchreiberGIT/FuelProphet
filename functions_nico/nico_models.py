
# Import packages
import numpy as np
import pandas as pd
from datetime import datetime, date, time, timedelta
import seaborn as sns
import matplotlib.pyplot as plt
from prophet import Prophet
from sklearn.metrics import mean_squared_error,mean_absolute_error, r2_score

##############################################################################################################################

def baseline_model(data,date="datetime",value="e5",predictions=12*24,stepsize=(5,"minutes"),rule="daily mean"):
    """Predicts fuel prices with a simple model

    Args:
        data (DataFrame): Input dataset
        date (str, optional): Name of the datetime variable. Defaults to "datetime".
        value (str, optional): Name of the prediction variable. Defaults to "e5".
        predictions (int, optional): Number of predictions to make by the model. Defaults to 12*24.
        stepsize (tuple, optional): Time difference between predictions. Defaults to (5,"minutes").
        rule (str, optional): Rule for setting the prediction value. Can be "daily mean" (mean of previous day) or "last value" (last available value). Defaults to "daily mean".

    Returns:
        DataFrame: Prediction dataset
    """

    # Get first and last prediction dat
    if stepsize[1] == "minutes":
        first_date_predict  = data[date].iloc[-1]+timedelta(minutes=stepsize[0])
        last_date_predict = first_date_predict+(timedelta(minutes=(stepsize[0]*predictions)-1))
    elif stepsize[1] == "hours":
        first_date_predict  = data[date].iloc[-1]+timedelta(minutes=stepsize[0])
        last_date_predict = first_date_predict+(timedelta(hours=(stepsize[0]*predictions)-1))
    elif stepsize[1] == "days":
        first_date_predict  = data[date].iloc[-1]+timedelta(minutes=stepsize[0])
        last_date_predict = first_date_predict+(timedelta(days=(stepsize[0]*predictions)-1))

    # Get prediction value
    if rule == "last value":
        pred_value = data[value].iloc[-1]
    elif rule == "daily mean":
        pred_value = data[data[date]>= data[date].iloc[-1]-timedelta(days=1)][value].mean()
    

    # Create DataFrame with new predictions
    df_predict = pd.DataFrame(columns=[date,value])
    df_predict[date] = pd.date_range(start=first_date_predict, end=last_date_predict, freq=timedelta(minutes=stepsize[0]))
    df_predict[value] = pred_value

    return df_predict

##############################################################################################################################

def prophet_model(data,station_uuid,test_days=1,date="datetime",value="e5",stepsize=5,regressor=None):


    if station_uuid != None:
        df = data[data["station_uuid"] == station_uuid]
    else:
        df = data
    
    # Split data
    train,test = split_data(df,interval=("days",test_days))

    model = Prophet(daily_seasonality=True, weekly_seasonality=True)
    train  = train.copy().rename(columns={date: "ds", value: "y"})
    test  = test.copy().rename(columns={date: "ds", value: "y"})

    if regressor != None:
        model.add_regressor(regressor)

    model.fit(train)

    predictions = model.predict(test)
    predictions = predictions[predictions['ds'].isin(train['ds']) == False]
    predictions  = predictions.copy().rename(columns={"ds": date, "yhat": value})

    return df,predictions

##############################################################################################################################

def split_data(data,date="datetime",interval="2025-04-30 23:59:59"):
    """Splits data into train and test data, while test includes the last time interval from the whole dataset

    Args:
        data (DataFrame): Input dataset
        date (str, optional): Name of the datetime variable. Defaults to "datetime".
        interval (tuple, optional): Interval unit and number of units which should be used as test data or split date. Defaults to "2025-04-30".

    Returns:
        train,test: A train and a test dataset
    """

    if type(interval) == tuple:
        params = {interval[0]: interval[1]}
        split_date = data[date].iloc[-1]-timedelta(**params)
    else:
        split_date = pd.to_datetime(interval)

    train = data[data[date] <= split_date]
    test = data[data[date] > split_date]

    return train,test

##############################################################################################################################

def print_model(real_data,predictions,x="datetime",y="e5",xlim=None,ylim=None,name="name",title=None,params=None):
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

    # Set figure size
    sns.set_theme(rc={'figure.figsize':(12,6)})

    # Set grid color
    sns.set_style("darkgrid", {"grid.color": params.get("gridcolor")})

    # Change border color of the figure (spines)
    ax = plt.gca()
    for spine in ax.spines.values():
        spine.set_edgecolor(params.get("gridcolor"))

    
    
    # Dashed plot
    dash = sns.lineplot(data      = real_data[real_data[x] >= predictions[x].iloc[0]],
                 x         = "datetime",
                 y         = "e5",
                 color     = "#4281eaff",
                 drawstyle = 'steps-post',
                 #linestyle = "dashed",
                 linewidth = 3
                 )
    
    # Create line between train and test set
    plt.vlines(x         = predictions[x].iloc[0],
               ymin      = ylim[0],
               ymax      = ylim[1],
               color     = "#a6a5a4",
               linewidth = 2,
               linestyle = "dashed"
               )
    
    # Set transparency (alpha)
    for line in dash.lines:
        line.set_alpha(0.4)
    
    # Create lines
    real = sns.lineplot(data      = real_data[real_data[x] <= predictions[x].iloc[0]],
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
    
    plt.text(predictions[x].iloc[0]+timedelta(minutes=40),ylim[0]+0.02,"Test →",fontweight="bold",fontsize=14,color="#a6a5a4")
    plt.text(predictions[x].iloc[0]-timedelta(minutes=360),ylim[0]+0.02,"← Train",fontweight="bold",fontsize=14,color="#a6a5a4")
    
    

    # Set limits
    if xlim != None:
        plt.xlim((pd.to_datetime(xlim[0]),pd.to_datetime(xlim[1])))
    if ylim != None:
        plt.ylim((ylim[0],ylim[1]))

    # Adapt title
    if title == None:
        plt.title("Fuel price prediction of " + real_data[name].iloc[1],fontweight="bold",fontsize=14,color=params.get("textcolor"))
    else:
        plt.title(title,fontweight="bold",fontsize=18,color=params.get("textcolor"))

    # Adapt labels
    plt.xlabel(" ",fontweight="bold",fontsize=16,color=params.get("textcolor"))
    plt.ylabel(y + " price (€/l)",fontweight="bold",fontsize=16,color=params.get("textcolor"))

    # Adapt xticks
    ax = plt.gca()
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
        label.set_fontsize(16)
        label.set_color(params.get("textcolor"))
        label.set_fontsize(16)

    # Adapt yticks
    for label in plt.gca().get_yticklabels():
        label.set_fontweight('normal')
        label.set_color(params.get("textcolor"))
        label.set_fontsize(16)

    # Adapt background color
    plt.gca().set_facecolor(params.get("background"))
    plt.gcf().set_facecolor(params.get("background"))

    # Create legend
    plt.legend(fontsize=16,loc='upper right', edgecolor=params.get("legendedge"), facecolor=params.get("legendface"), labelcolor = params.get("legendcol"),framealpha=1)

    plt.show()

    print("RMSE:", round(np.sqrt(mean_squared_error(real_data[real_data[x].isin(predictions[x])][y],predictions[y])),3))
    print("MAE:", round(mean_absolute_error(real_data[real_data[x].isin(predictions[x])][y],predictions[y]),3))
    print("R2:", round(r2_score(real_data[real_data[x].isin(predictions[x])][y],predictions[y]),3))

