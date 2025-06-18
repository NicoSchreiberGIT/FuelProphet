import pandas as pd
import warnings
warnings.filterwarnings("ignore")

def outliers_cut(df, highest_price = 2.5, lowest_price = 1.0, analyzer = 'e5'):
    """Function for cutting off the outliers

    Args:
        df (DataFrame): input DataFrame containing fuel prices.
        highest_price (float, optional): _description_. Defaults to 2.5.
        lowest_price (float, optional): _description_. Defaults to 1.0.
        analyzer(string, optional): e5, Diesel or e10 Defaults to 'e5

    Returns:
        _type_: _description_
    """
    df = df[(df[analyzer]>lowest_price) & (df[analyzer]< highest_price)]
    return df

###############################################################################################################################

def date_format(df):
    """Converts the column date to a datetime format

    Args:
        df (DataFrame): input DataFrame containing fuel prices.
    """
    df['dateNew'] = df['date'].str.replace('+01', '').str.replace('+02', '')
    df['date'] = pd.to_datetime(df['dateNew'], format = "%Y-%m-%d %H:%M:%S")
    df.drop('dateNew', inplace = True, axis = 1)

###############################################################################################################################

def encode_date(df):
    """Encode the column date into multiple columns

    Args:
        df (DataFrame): input DataFrame containing fuel prices.
    """
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['week'] = df['date'].dt.isocalendar().week
    df['dayNr'] = df['date'].dt.day
    df['day'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    df['time'] = df['date'].dt.hour + df['date'].dt.minute/60 #represents time in hours and minutes, minutes are converter into comma vlaues, relevant for the plots
    df['date_only'] = df['date'].dt.date

###############################################################################################################################


# def residual_price(df, covid = 1):
#     """This function creates a new column, which contains the  residual/unknown portion of the actual price

    
#     In case data between 1.6.2020 and 31.12.2020 is used, the VAT is set to 16% instead of 19%. Covid == 1 is used to indicate this.
#     The CO2 factors are set to 0 for the years before 2021, and the values for 2021-2025 are used for the respective years.

#     Args:
#         df (DataFrame): input DataFrame containing fuel prices.

#     """
#     co2_e5 = [[2021,2022,2023,2024,2025],[0.07,0.084,0.084, 0.127, 0.157]]
#     co2_diesel = [[2021,2022,2023,2024,2025],[0.08,0.095,0.095, 0.142, 0.173]]
#     tax_energy_e5 = 0.6545
#     tax_energy_diesel = 0.4704
#     vat = 0.19
#     vat_covid = 0.16

#     def tax_decision(row):
#         year = row['year']
#         month = row['month']

#         if year == 2020 and month >= 6 and month <= 12:
#             return vat_covid
#         else:
#             return vat
#     def co2_decision(row):
#         year = row['year']
#         if year < 2021:
#             e5_factor = 0
#             diesel_factor = 0
#         elif year == 2021:
#              e5_factor = co2_e5[1][0]
#              diesel_factor = co2_diesel[1][0]
#         elif year == 2022:
#              e5_factor = co2_e5[1][1]
#              diesel_factor = co2_diesel[1][1]
#         elif year == 2023:
#             e5_factor = co2_e5[1][2]
#             diesel_factor = co2_diesel[1][2]
#         elif year == 2024:
#             e5_factor = co2_e5[1][3]
#             diesel_factor = co2_diesel[1][3]
#         elif year == 2025:
#             e5_factor = co2_e5[1][4]
#             diesel_factor = co2_diesel[1][4]
#         elif year > 2025:
#             # Issue the warning BEFORE returning a value
#             warnings.warn(f"Year {year} exceeds 2025, new CO2 input required. Using default factor for 2025.", UserWarning)
#             # Return a sensible default. Here, I'm using the factor for 2025 as a placeholder.
#             # You might choose 0, NaN, or 1 depending on your desired behavior.
#             e5_factor = co2_e5[1][4]
#             diesel_factor = co2_diesel[1][4]
#         return pd.Series({'e5_co2_factor': e5_factor, 'diesel_co2_factor': diesel_factor})
    
#     if covid == 1:
#         df['tax_rate'] = df.apply(tax_decision, axis=1)
#         df['e5_after_vat'] = df['e5'] * (1 - df['tax_rate'])
#         df['diesel_after_vat'] = df['diesel'] * (1 - df['tax_rate'])
#         df['e5_after_vat_energy'] = df['e5_after_vat'] - tax_energy_e5
#         df['diesel_after_vat_energy'] = df['diesel_after_vat'] - tax_energy_diesel
#         df[['e5_co2_factor', 'diesel_co2_factor']] = df.apply(co2_decision, axis=1)
#         df['e5_residual_price'] = (df['e5_after_vat_energy'] - df['e5_co2_factor']).round(3)
#         df['diesel_residual_price'] = (df['diesel_after_vat_energy'] - df['diesel_co2_factor']).round(3)
#         return df.drop(columns=['tax_rate', 'e5_after_vat', 'diesel_after_vat', 'e5_after_vat_energy', 'diesel_after_vat_energy', 'e5_co2_factor', 'diesel_co2_factor'])
    
#     elif covid == 0:
#         df['e5_after_vat_energy'] = df['e5'] * (1 - 0.19) - tax_energy_e5
#         df['diesel_after_vat_energy'] = df['diesel'] * (1 - 0.19) - tax_energy_diesel
#         df[['e5_co2_factor', 'diesel_co2_factor']] = df.apply(co2_decision, axis=1)
#         df['e5_residual_price'] = (df['e5_after_vat_energy'] - df['e5_co2_factor']).round(3)
#         df['diesel_residual_price'] = (df['diesel_after_vat_energy'] - df['diesel_co2_factor']).round(3)
#         return df.drop(columns=['e5_after_vat_energy', 'diesel_after_vat_energy', 'e5_co2_factor', 'diesel_co2_factor'])
 
###############################################################################################################################


def residual_price(df, covid=1):
    """This function creates a new column, which contains the residual/unknown portion of the actual price.

    In case data between 1.6.2020 and 31.12.2020 is used, the VAT is set to 16% instead of 19%. Covid == 1 is used to indicate this.
    The CO2 factors are set to 0 for the years before 2021, and the values for 2021-2025 are used for the respective years.

    Args:
        df (DataFrame): input DataFrame containing fuel prices.
        covid (int): Flag to indicate if COVID-19 related VAT changes should be applied (1 for yes, 0 for no).
    """
    
    # Define constants
    tax_energy_e5 = 0.6545
    tax_energy_diesel = 0.4704
    vat = 0.19
    vat_covid = 0.16

    # CO2 factors mapping for direct lookup
    co2_e5_map = {
        2021: 0.07, 2022: 0.084, 2023: 0.084, 2024: 0.127, 2025: 0.157
    }
    co2_diesel_map = {
        2021: 0.08, 2022: 0.095, 2023: 0.095, 2024: 0.142, 2025: 0.173
    }
    
    # --- VAT Calculation ---
    if covid == 1:
        # Vectorized VAT calculation using boolean indexing
        mask_covid_vat = (df['year'] == 2020) & (df['month'] >= 6) & (df['month'] <= 12)
        df['tax_rate'] = vat
        df.loc[mask_covid_vat, 'tax_rate'] = vat_covid
    else: # covid == 0
        df['tax_rate'] = vat # Always 19% VAT if covid is 0
    
    # Vectorized calculation for prices after VAT and energy tax
    df['e5_after_vat'] = df['e5'] * (1 - df['tax_rate'])
    df['diesel_after_vat'] = df['diesel'] * (1 - df['tax_rate'])
    df['e5_after_vat_energy'] = df['e5_after_vat'] - tax_energy_e5
    df['diesel_after_vat_energy'] = df['diesel_after_vat'] - tax_energy_diesel

    # --- CO2 Factor Calculation ---
    # Initialize CO2 factors to 0
    df['e5_co2_factor'] = 0.0
    df['diesel_co2_factor'] = 0.0

    # Get unique years to apply CO2 factors efficiently
    years_with_co2 = df['year'].unique()

    for year in years_with_co2:
        if year >= 2021 and year <= 2025:
            mask_year = (df['year'] == year)
            df.loc[mask_year, 'e5_co2_factor'] = co2_e5_map.get(year, 0.0)
            df.loc[mask_year, 'diesel_co2_factor'] = co2_diesel_map.get(year, 0.0)
        elif year > 2025:
            warnings.warn(f"Year {year} exceeds 2025, new CO2 input required. Using default factor for 2025.", UserWarning)
            mask_year = (df['year'] == year)
            df.loc[mask_year, 'e5_co2_factor'] = co2_e5_map.get(2025, 0.0) # Use 2025 factor as placeholder
            df.loc[mask_year, 'diesel_co2_factor'] = co2_diesel_map.get(2025, 0.0) # Use 2025 factor as placeholder
    
    # --- Residual Price Calculation ---
    df['e5_residual_price'] = (df['e5_after_vat_energy'] - df['e5_co2_factor']).round(3)
    df['diesel_residual_price'] = (df['diesel_after_vat_energy'] - df['diesel_co2_factor']).round(3)

    # --- Cleanup ---
    columns_to_drop = [
        'tax_rate', 'e5_after_vat', 'diesel_after_vat',
        'e5_after_vat_energy', 'diesel_after_vat_energy',
        'e5_co2_factor', 'diesel_co2_factor'
    ]
    
    df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])

    return df