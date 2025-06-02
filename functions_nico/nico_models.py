
# Import packages
import numpy as np
import pandas as pd
from datetime import datetime, date, time, timedelta
import seaborn as sns
import matplotlib.pyplot as plt
from prophet import Prophet
from sklearn.metrics import mean_squared_error,mean_absolute_error

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
        last_date_predict = first_date_predict+(timedelta(minutes=stepsize[0]*predictions))
    elif stepsize[1] == "hours":
        first_date_predict  = data[date].iloc[-1]+timedelta(minutes=stepsize[0])
        last_date_predict = first_date_predict+(timedelta(hours=stepsize[0]*predictions))
    elif stepsize[1] == "days":
        first_date_predict  = data[date].iloc[-1]+timedelta(minutes=stepsize[0])
        last_date_predict = first_date_predict+(timedelta(days=stepsize[0]*predictions))

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

def prophet_model(data,station_uuid,test_days=1,date="datetime",value="e5",stepsize=5):


    if station_uuid != None:
        df = data[data["station_uuid"] == station_uuid]
    else:
        df = data
    
    # Split data
    train,test = split_data(df,interval=("days",test_days))

    model = Prophet(daily_seasonality=True, weekly_seasonality=True)
    train  = train.copy().rename(columns={date: "ds", value: "y"})
    model.fit(train)

    future = model.make_future_dataframe(periods=int(test_days*24*(60/stepsize)), freq=str(stepsize)+"min")
    predictions = model.predict(future)
    predictions = predictions[predictions['ds'].isin(train['ds']) == False]
    predictions  = predictions.copy().rename(columns={"ds": date, "yhat": value})

    return df,predictions

##############################################################################################################################

def split_data(data,date="datetime",interval=("days",1)):
    """Splits data into train and test data, while test includes the last time interval from the whole dataset

    Args:
        data (DataFrame): Input dataset
        date (str, optional): Name of the datetime variable. Defaults to "datetime".
        interval (tuple, optional): Interval unit and number of units which should be used as test data. Defaults to ("days",1).

    Returns:
        train,test: A train and a test dataset
    """

    params = {interval[0]: interval[1]}
    
    split_date = data[date].iloc[-1]-timedelta(**params)
    train = data[data[date] <= split_date]
    test = data[data[date] > split_date]

    return train,test

##############################################################################################################################

def print_model(real_data,predictions,x="datetime",y="e5",xlim=None,ylim=None,name="name"):
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

    sns.set_theme(rc={'figure.figsize':(15,6)})

    sns.lineplot(data=real_data, x="datetime", y="e5", color="blue",drawstyle='steps-post')
    plt.vlines(predictions[x].iloc[0],ymin=real_data[y].iloc[-1],ymax=predictions[y].iloc[0],color="orange")
    sns.lineplot(data=predictions, x="datetime", y="e5", color="orange",drawstyle='steps-post')
    if xlim != None:
        plt.xlim((pd.to_datetime(xlim[0]),pd.to_datetime(xlim[1])))
    if ylim != None:
        plt.ylim((ylim[0],ylim[1]))

    plt.title("Fuel price prediction of " + real_data[name].iloc[1],fontweight="bold",fontsize=14)
    plt.xlabel(" ",fontweight="bold")
    plt.ylabel(y + " price (€)",fontweight="bold")

    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M\n%d-%m-%y'))
    plt.gcf().autofmt_xdate()

    plt.show()

    print("RMSE:", round(np.sqrt(mean_squared_error(real_data[real_data[x].isin(predictions[x])][y],predictions[y])),3))
    print("MAE:", round(mean_absolute_error(real_data[real_data[x].isin(predictions[x])][y],predictions[y]),3))

