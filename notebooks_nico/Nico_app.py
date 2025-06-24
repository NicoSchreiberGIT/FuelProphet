
############################
########  KIVY APP #########
############################

# PACKAGES
import pandas as pd
from datetime import datetime, date, time, timedelta
import time
from matplotlib import pyplot as plt
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen as KivyScreen
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.uix.scrollview import ScrollView
from kivy.utils import get_color_from_hex
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.spinner import Spinner
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.anchorlayout import AnchorLayout

import sys
import os
# Get the parent directory and add it to sys.path
parent_dir = os.path.abspath("../FuelProphet")
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from functions_nico.nico_get_current_fuel_prices import get_current_fuel_prices
from functions_nico.nico_app_helper_functions import preprocess_data,print_model
from functions_nico.nico_fuelprophet import FuelProphet

####################################################################################
# HELPER CLASSES
####################################################################################

# Set window size
Window.size = (1920, 1080)
Window.left = 0   # Set x-position on screen
Window.top = 0     # Set y-position on screen
Window.borderless = False  # Set to True for no window border
Window.fullscreen = False  # Or "auto", or True

class ClickableImage(ButtonBehavior, Image):
    pass

class OrangeBox(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(1, 0.5, 0, 1)  # Orange RGBA
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

####################################################################################
# OVERALL SCREEN LAYOUT
####################################################################################

class BaseScreen(KivyScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Set background color
        with self.canvas.before:
            self.bg_color = Color(*get_color_from_hex("#393939ff"))
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self.update_bg_rect, pos=self.update_bg_rect)

        # Display FuelProphet logo in the top right corner
        self.image_width = 200
        self.image_height = 200
        layout = FloatLayout()
        img = Image(
            source='../images/FuelProphet.png',
            size_hint=(None, None),          # Use fixed size
            size=(150, 150),                 # Your image size
            pos_hint={'right': 1, 'top': 1}, # Top right corner
            allow_stretch=True,
            keep_ratio=True
        )
        layout.add_widget(img)
        self.add_widget(layout)

    # Additional functions
    def update_bg_rect(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def update_image_position(self, *args):
        x = self.width - self.image_width
        y = self.height - self.image_height
        self.bg_image.pos = (x, y)

####################################################################################
# OPENING
####################################################################################

class opening(KivyScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Set background color
        with self.canvas.before:
            self.bg_color = Color(*get_color_from_hex("#393939ff"))
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self.update_bg_rect, pos=self.update_bg_rect)

        # Display FuelProphet logo in the middle of the screen and use it as a button
        self.image_width = 500
        self.image_height = 500
        layout = BoxLayout(orientation='vertical')
        img = ClickableImage(source='../images/FuelProphet_text.png', allow_stretch=True)
        img.bind(on_press=self.go_to_presettings)
        layout.add_widget(img)
        self.add_widget(layout)

    # Additional functions
    def update_bg_rect(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos
    def update_image_position(self, *args):
        x = (self.width - self.image_width) / 2
        y = (self.height - self.image_height) / 2
        self.bg_image.pos = (x, y)

    def go_to_presettings(self, instance):
        self.alldata = preprocess_data(days=7*4)#,file="alldata_2025-06-19.parquet")
        self.manager.current = 'presettings'

####################################################################################
# PRESETTINGS
####################################################################################

class presettings(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Add header
        header = FloatLayout()
        orange_box = OrangeBox(size_hint=(None, None), size=(150, 80), pos_hint={'x': 0, 'top': 1})
        label = Label(text='Settings',
                      color="#393939ff",
                      font_size=24,
                      size_hint=(None, None),
                      size=(150, 80),
                      pos_hint={'x': 0, 'top': 1})

        header.add_widget(orange_box)
        header.add_widget(label)
        self.add_widget(header)

        # Include text
        intro = FloatLayout()
        introtext = Label(
            text="[b]Welcome to FuelProphet.\n\nPlease insert your zipcode and the fuel you need[/b]",
            size_hint=(None, None),
            size=(200, 100),
            pos_hint={'center_x': 0.5, 'center_y': 0.8},
            halign='left',
            color="#f1881aff",
            font_size=27,
            markup = True
        )

        intro.add_widget(introtext)
        self.add_widget(intro)

        # Include options
        layout = FloatLayout()
        grid = GridLayout(cols=2, rows=3,
                                size_hint=(None, None),
                                size=(350, 200),
                                pos_hint={'center_x': 0.45, 'center_y': 0.5})
        #1
        grid.add_widget(Label(text="Location", font_size=27, halign="left",color="#e8dcca"))
        #2
        anchor = AnchorLayout(anchor_x='center', anchor_y='center')
        self.zip_field = TextInput(
            size_hint=(None,None),
            height=40,
            width=160,
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            background_color="#e8dcca",
            hint_text="ZIP code",
            font_size=24,
            multiline=False
        )
        anchor.add_widget(self.zip_field)
        grid.add_widget(anchor)
        #3
        grid.add_widget(Label(text="Fuel Type", font_size=27, halign="left",color="#e8dcca"))
        #4
        anchor = AnchorLayout(anchor_x='center', anchor_y='center')
        self.fuel_field = TextInput(
            size_hint=(None,None),
            height=40,
            width=160,
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            background_color="#e8dcca",
            hint_text="e5/e10/Diesel",
            font_size=24,
            multiline=False
        )
        anchor.add_widget(self.fuel_field)
        grid.add_widget(anchor)
        #5 (empty)
        grid.add_widget(Widget())
        #6
        grid.add_widget(Button(text='Accept', on_press=self.go_to_stations))

        # Add grid to layout
        layout.add_widget(grid)

        # Include Back and close App buttons
        layout.add_widget(Button(text='Back', on_press=self.go_to_opening,size_hint=(None,None),size=(150,60),pos_hint={'right': 0.5, 'y': 0}))
        layout.add_widget(Button(text='Close App', on_press=self.close_app,size_hint=(None,None),size=(150,60),pos_hint={'right': 1, 'y': 0}))
        self.add_widget(layout)

    # Additional functions
    def go_to_stations(self, instance):
        # Load alldata from Opening Screen
        screen_manager = App.get_running_app().root
        self.alldata = screen_manager.get_screen('opening').alldata
        # Save user input
        self.analysisdata = self.alldata[self.alldata["post_code"] == self.zip_field.text]
        # Drop missing values
        self.analysisdata.dropna(inplace=True)

        # Drop outliers
        self.analysisdata = self.analysisdata[(self.analysisdata["e5"]>1.0) & (self.analysisdata["e5"]< 2.5)]

        self.analysisdata["datedate"] = self.analysisdata["datetime"].dt.date
        self.analysisdata["hour"]     = self.analysisdata["datetime"].dt.hour

        self.df_resample = self.analysisdata.set_index('datetime')
        self.df_resample = self.df_resample.groupby(["station_uuid","name","street","house_number","brand"])["e5"].resample("5min").ffill().reset_index()

        stations_screen = self.manager.get_screen('stations')
        stations_screen.load_analysisdata(self.df_resample)
        prediction_screen = self.manager.get_screen('prediction')
        prediction_screen.load_analysisdata(self.df_resample)
        self.manager.current = 'stations'

    def go_to_opening(self, instance):
        self.manager.current = 'opening'

    def close_app(self, instance):
        App.get_running_app().stop()

####################################################################################
# STATIONS
####################################################################################

class stations(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Add header
        header = FloatLayout()
        orange_box = OrangeBox(size_hint=(None, None), size=(150, 80), pos_hint={'x': 0, 'top': 1})
        label = Label(text='Gas Stations',
                      color="#393939ff",
                      font_size=24,
                      size_hint=(None, None),
                      size=(150, 80),
                      pos_hint={'x': 0, 'top': 1})

        header.add_widget(orange_box)
        header.add_widget(label)
        self.add_widget(header)

    # Additional functions:
    def load_analysisdata(self, analysisdata):
        self.analysisdata = analysisdata
        self.gasstations = self.analysisdata.drop_duplicates(subset=['name', "street", "house_number"])

        # Refresh or rebuild layout with new data here
        self.build_layout()

    def build_layout(self):
        
        fontsize=20
        textsize=300

        for c in list(self.children):
            if "ScrollView" in str(c): self.remove_widget(c)

        headers = FloatLayout()
        grid = GridLayout(cols=4, rows=1,
                        size_hint=(None, None),
                        size=(1600, 100),
                        pos_hint={"top":0.94,"center_x":0.5})
        
        grid.add_widget(Label(text="Name", font_size=fontsize, halign="left", color="#f1881aff",text_size=(textsize, None)))
        grid.add_widget(Label(text="Brand", font_size=fontsize, halign="left", color="#f1881aff",text_size=(textsize, None)))
        grid.add_widget(Label(text="Adress", font_size=fontsize, halign="left", color="#f1881aff",text_size=(textsize, None)))
        grid.add_widget(Widget())
        headers.add_widget(grid)
        self.add_widget(headers)

        self.layout = ScrollView(size_hint=(None, None),size=(1600,600),pos_hint={"top":0.85,"center_x":0.5})
        grid = GridLayout(cols=4, rows=len(self.gasstations),
                        size_hint=(None, None),
                        size=(1600, (len(self.gasstations)+1)*80),
                        pos_hint={'center_x': 0.4, 'center_y': 0.6})
        
        img = []
        count=0

        for index, row in self.gasstations.iterrows():
            grid.add_widget(Label(text=str(row["name"]), font_size=fontsize, halign="left", color="#e8dcca",text_size=(textsize, None)))
            grid.add_widget(Label(text=str(row["brand"]), font_size=fontsize, halign="left", color="#e8dcca",text_size=(textsize, None)))
            if row["house_number"] is None:
                grid.add_widget(Label(text=str(row["street"]), font_size=fontsize, halign="left", color="#e8dcca",text_size=(textsize, None)))
            else:
                grid.add_widget(Label(text=str(row["street"]) + " " + str(row["house_number"]), font_size=fontsize, halign="left", color="#e8dcca",text_size=(textsize, None)))
            
            # Add prediction button
            img.append(ClickableImage(source='../images/FuelProphet.png', allow_stretch=True))
            img[count].bind(on_press=lambda inst, row=row: self.choose_station(row, inst))
            grid.add_widget(img[count])
            count +=1

        self.layout.add_widget(grid)
        self.add_widget(self.layout)

        layout2 = FloatLayout()
        layout2.add_widget(Button(text='Back', on_press=self.go_to_presettings,size_hint=(None,None),size=(150,60),pos_hint={'right': 0.5, 'y': 0}))
        layout2.add_widget(Button(text='Close App', on_press=self.close_app,size_hint=(None,None),size=(150,60),pos_hint={'right': 1, 'y': 0}))
        self.add_widget(layout2)

    def choose_station(self,station, instance):
        self.gas_station = station["station_uuid"]
        prediction_screen = self.manager.get_screen('prediction')
        prediction_screen.load_gas_station(self.gas_station)
        self.manager.current = 'prediction'

    def go_to_presettings(self, instance):
        self.manager.current = 'presettings'

    def close_app(self, instance):
        App.get_running_app().stop()

####################################################################################
# PREDICTION
####################################################################################

class prediction(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Add header
        header = FloatLayout()
        orange_box = OrangeBox(size_hint=(None, None), size=(150, 80), pos_hint={'x': 0, 'top': 1})
        label = Label(text='Predictions',
                      color="#393939ff",
                      font_size=24,
                      size_hint=(None, None),
                      size=(150, 80),
                      pos_hint={'x': 0, 'top': 1})

        header.add_widget(orange_box)
        header.add_widget(label)
        self.add_widget(header)

    # Additional functions

    def load_analysisdata(self, analysisdata):
        self.analysisdata = analysisdata

    def load_gas_station(self, gas_station):
        self.gas_station = gas_station

        # Refresh or rebuild layout with new data here
        self.build_layout()

    def build_layout(self):
        self.text = FloatLayout()
        grid = GridLayout(cols=2, rows=4,
                                size_hint=(None, None),
                                size=(600, 380),
                                pos_hint={'center_x': 0.46, 'center_y': 0.8})
        
        # Get station information
        self.station_data = self.analysisdata[self.analysisdata["station_uuid"]==self.gas_station].iloc[0]
        self.active_plot = False
        # Add buttons to the grid
        #1
        grid.add_widget(Label(text="Gas station", font_size=20, halign="left", color="#e8dcca",text_size=(250, None)))
        #2
        grid.add_widget(Label(text=self.station_data["name"], font_size=20, halign="left", color="#f1881aff",text_size=(250, None)))
        #3
        grid.add_widget(Label(text="Current Price", font_size=20, halign="left", color="#e8dcca",text_size=(250, None)))
        #4
        grid.add_widget(Label(text=str(get_current_fuel_prices(uuid=self.gas_station).loc["e5"].iloc[0]), font_size=20, halign="left", color="#f1881aff",text_size=(250, None)))
        #5
        grid.add_widget(Label(text="Adress", font_size=20, halign="left", color="#e8dcca",text_size=(250, None)))
        #6
        if self.station_data["house_number"] is not None:
            grid.add_widget(Label(text=str(self.station_data["street"]) + " " + str(self.station_data["house_number"]), font_size=20, halign="left", color="#f1881aff",text_size=(250, None)))
        else:
            grid.add_widget(Label(text=str(self.station_data["street"]), font_size=20, halign="left", color="#f1881aff",text_size=(250, None)))
        #7
        grid.add_widget(Label(text="Status", font_size=20, halign="left", color="#e8dcca",text_size=(250, None)))
        #8
        grid.add_widget(Label(text=str(get_current_fuel_prices(uuid=self.gas_station).loc["status"].iloc[0]), font_size=20, halign="left", color="#f1881aff",text_size=(250, None)))

        self.text.add_widget(grid)
        self.add_widget(self.text)

        # Add additional buttons
        self.buttons = FloatLayout()
        self.buttons.add_widget(Button(text='Close App', on_press=self.close_app,size_hint=(None,None),size=(150,60),pos_hint={'right': 1, 'y': 0}))
        self.buttons.add_widget(Button(text='Settings', on_press=self.go_to_presettings,size_hint=(None,None),size=(150,60),pos_hint={'right': 0.5, 'y': 0}))
        self.add_widget(self.buttons)

        # Add graph creation button
        self.btn = FloatLayout()
        self.btn.add_widget(Button(text='Load predictions', on_press=self.load,size_hint=(0.3,0.15),pos_hint={'center_x': 0.4, 'center_y': 0.3}))
        self.add_widget(self.btn)

    def load(self,instance):
        self.thinking(instance)
        self.predict(instance)
        self.remove_widget(self.think)

    def thinking(self,instance):
        self.remove_widget(self.btn)
        self.think = FloatLayout()
        img = Image(
            source='../images/FuelProphet_think.png',
            size_hint=(None, None),          # Use fixed size
            size=(200, 200),                 # Your image size
            pos_hint={'center_x': 0.4, 'center_y': 0.3},
            allow_stretch=True,
            keep_ratio=True
        )
        self.think.add_widget(img)
        self.add_widget(self.think)
        
    def predict(self, instance):

        # Create train data
        self.train = self.analysisdata[self.analysisdata["station_uuid"]==self.gas_station]
        model = FuelProphet()
        model.fit_pacf(self.train,threshold=0.2,lags=288*3)
        model.normalize()
        self.pred = model.predict(X=self.train,num_predictions=288*7)
        #Prepare data for plotting
        self.train = self.train[self.train["datetime"] >= self.train["datetime"].iloc[(-2*288)]]

        self.plot(self.train,self.pred,days=1)

        # Create buttons for changing graph
        self.layout_btns = FloatLayout()
        self.layout_btns.add_widget(Button(text='1 day', on_press=lambda inst: self.plot(self.train,self.pred,1, inst),size_hint=(None,None),size=(120,70),pos_hint={'center_x': 0.7, 'center_y': 0.64}))
        self.layout_btns.add_widget(Button(text='3 days', on_press=lambda inst: self.plot(self.train,self.pred,3, inst),size_hint=(None,None),size=(120,70),pos_hint={'center_x': 0.77, 'center_y': 0.64}))
        self.layout_btns.add_widget(Button(text='7 days', on_press=lambda inst: self.plot(self.train,self.pred,7, inst),size_hint=(None,None),size=(120,70),pos_hint={'center_x': 0.84, 'center_y': 0.64}))
        self.add_widget(self.layout_btns)

    def plot(self, train, pred, days, instance=None):

        if self.active_plot:
            self.remove_widget(self.plot_layout)

        pred_short = pred.iloc[:(288*days)]
        
        #Create plot
        self.plot_layout = BoxLayout(orientation="horizontal")
        fig = print_model(train, pred_short)
        plot_widget = FigureCanvasKivyAgg(fig, size_hint_x=0.9,size_hint_y=0.5, pos_hint={'center_x': 0.5, 'center_y': 0.35})
        self.plot_layout.add_widget(plot_widget)
        self.add_widget(self.plot_layout)
        self.active_plot = True

    def close_app(self, instance):
        App.get_running_app().stop()

    def go_to_presettings(self, instance):
        self.remove_widget(self.text)
        self.remove_widget(self.plot_layout)
        self.remove_widget(self.layout_btns)
        self.manager.current = 'presettings'

####################################################################################

class Test_App(App):
    def build(self):
        self.title = 'FuelProphet'
        sm = ScreenManager()
        sm.add_widget(opening(name='opening'))
        sm.add_widget(presettings(name='presettings'))
        sm.add_widget(stations(name='stations'))
        sm.add_widget(prediction(name='prediction'))
        return sm

####################################################################################

if __name__ == '__main__':
    Test_App().run()

####################################################################################