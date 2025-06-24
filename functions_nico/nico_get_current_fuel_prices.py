# Function to get current prices from Tankerkoenig

import requests
import pandas as pd

def get_current_fuel_prices(lat=None,long=None,radius=None,uuid=None,api_key=None):
    """Creation of a dataset including current fuel prices at gas stations in a circular neighborhood or known gas stations

    Args:
        lat (float): Latidude of the center for searching gas stations
        long (float): Longitude of the center for searching gas stations
        radius (float): Radius for searching
        uuid (str, optional): UUID of gas station, prices are needed for. Defaults to None.
        api_key (str, optional): Individual api key. Defaults to None.

    Returns:
        dataframe: dataframe containing current fuel prices
    """

    
    # Set api key if not specified
    if api_key == None:
        api_key = '83710a8f-095c-bcdc-5766-243122e4903c'

    # Set url from tankerkoenig
    

    # Set url and parameters
    if uuid == None:

        url = "https://creativecommons.tankerkoenig.de/json/list.php"

        params = {
            'lat': lat,
            'lng': long,
            'rad': radius,
            'sort': 'dist',
            'type': 'all',
            'apikey': api_key
        }

    else:

        url = "https://creativecommons.tankerkoenig.de/json/prices.php"

        params = {
            'ids': uuid,
            'apikey': api_key
        }

    # Get data from website
    response = requests.get(url, params=params)

    if response.status_code == 200:
        df_prices = response.json()
    else:
        print("Error in response:", response.status_code, response.text)

    # Extract data
    if df_prices.get("ok") == False:
        print("Error in data collection:", df_prices.get("message"))
    else:
        if uuid == None:
            output = pd.DataFrame(df_prices["stations"])
            return output
        else:
            output = pd.DataFrame(df_prices["prices"])
            return output