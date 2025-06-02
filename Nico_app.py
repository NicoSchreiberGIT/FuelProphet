
############################
######  KIVY test app ######
############################

# import packages
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen as KivyScreen
from kivy.uix.label import Label
from kivy.graphics import Rectangle
from kivy.uix.scrollview import ScrollView
from get_current_fuel_prices import get_current_fuel_prices

class BaseScreen(KivyScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.image_width = 200
        self.image_height = 150

        with self.canvas:
            self.bg_image = Rectangle(
                source='images/FuelProphet_1.png',
                size=(self.image_width, self.image_height),
                pos=(0, 0)
            )

        self.bind(size=self.update_image_position, pos=self.update_image_position)

    def update_image_position(self, *args):
        x = self.width - self.image_width
        y = self.height - self.image_height
        self.bg_image.pos = (x, y)

class start(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Button(text='Go to data information', on_press=self.go_to_info,size_hint=(0.3,0.2)))
        layout.add_widget(Button(text='Go to visualizations', on_press=self.go_to_vis,size_hint=(0.3,0.2)))
        layout.add_widget(Button(text='Close App', on_press=self.close_app,size_hint=(0.3,0.2)))
        self.add_widget(layout)

    def go_to_info(self, instance):
        self.manager.current = 'Data information'

    def close_app(self, instance):
        App.get_running_app().stop()

    def go_to_vis(self, instance):
        self.manager.current = 'Visualization'

class info(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        data = get_current_fuel_prices(49.76394930569202,9.51664370931457,5)

        text = '\n'.join([f"Gas station: {row.get('name', 'N/A')}, E5 price: {row.get('e5', 'N/A')}" for _, row in data.iterrows()])

        layout = BoxLayout()
        label = Label(text="Current fuel prices in Wertheim", font_size=20)
        layout.add_widget(label)
        layout.add_widget(Button(text='Exit', on_press=self.go_to_start,size_hint=(0.1,0.1),pos_hint={'x': 0.9, 'y': 0}))
        self.add_widget(layout)

        scrollview = ScrollView()
        layout = BoxLayout(orientation='vertical', size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        label = Label(
            text=text,
            size_hint_y=None,
            height=len(data) * 40,
            font_size='18sp'
        )

        layout.add_widget(label)
        scrollview.add_widget(layout)
        self.add_widget(scrollview)

        
        
    def go_to_start(self, instance):
        self.manager.current = 'Start Screen'

class vis(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        label = Label(text="Visualizations", font_size=20)
        layout.add_widget(label)
        layout.add_widget(Button(text='Exit', on_press=self.go_to_start,size_hint=(0.1,0.1),pos_hint={'x': 0.9, 'y': 0}))
        self.add_widget(layout)

    def go_to_start(self, instance):
        self.manager.current = 'Start Screen'

class Test_App(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(start(name='Start Screen'))
        sm.add_widget(info(name='Data information'))
        sm.add_widget(vis(name='Visualization'))
        return sm

if __name__ == '__main__':
    Test_App().run()