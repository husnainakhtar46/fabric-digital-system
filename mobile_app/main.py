"""
Fabric Scanner Mobile App - Android Compatible Version
Uses Kivy + HTTP-based Google Sheets access
"""
import os
from threading import Thread

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock
from kivy.lang import Builder

# Import sheets client
try:
    from sheets_client import GoogleSheetsClient
except ImportError:
    GoogleSheetsClient = None

# Your Google Sheet ID (from the sheet URL)
SHEET_ID = "1QBHM2ybTvgZFRjduFdxZnOu4dR4p_xBKdR6LE5fNJT4"

# Kivy UI Definition
KV = '''
#:import hex kivy.utils.get_color_from_hex

<ScannerScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 15
        canvas.before:
            Color:
                rgba: hex('#121212')
            Rectangle:
                pos: self.pos
                size: self.size
        
        Label:
            text: "Fabric Scanner"
            size_hint_y: 0.15
            font_size: '28sp'
            bold: True
            color: hex('#ffffff')
        
        Label:
            text: "Enter Fabric Code:"
            size_hint_y: 0.1
            font_size: '18sp'
            color: hex('#888888')
        
        TextInput:
            id: code_input
            size_hint_y: 0.15
            font_size: '24sp'
            hint_text: "e.g. TOM, ABC123"
            multiline: False
            background_color: hex('#2d2d2d')
            foreground_color: hex('#ffffff')
            cursor_color: hex('#4CAF50')
        
        Button:
            size_hint_y: 0.15
            text: "🔍 SEARCH"
            font_size: '20sp'
            background_normal: ''
            background_color: hex('#4CAF50')
            on_release: root.search_fabric()
        
        Label:
            id: status_label
            text: "Enter a fabric code and tap Search"
            size_hint_y: 0.1
            color: hex('#888888')
            text_size: self.size
            halign: 'center'
        
        # Spacer
        Widget:
            size_hint_y: 0.35

<DetailScreen>:
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: hex('#1e1e1e')
            Rectangle:
                pos: self.pos
                size: self.size

        # App Bar
        BoxLayout:
            size_hint_y: None
            height: '60dp'
            padding: 10
            canvas.before:
                Color:
                    rgba: hex('#2d2d2d')
                Rectangle:
                    pos: self.pos
                    size: self.size
            
            Button:
                text: "< Back"
                size_hint_x: 0.25
                background_normal: ''
                background_color: hex('#0e639c')
                on_release: root.go_back()
            
            Label:
                text: "Fabric Details"
                bold: True
                font_size: '18sp'

        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: 15
                spacing: 15

                # Header
                Label:
                    size_hint_y: None
                    height: '60dp'
                    text: "📋 Fabric Specifications"
                    font_size: '22sp'
                    bold: True
                    
                # Fabric Code
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: '80dp'
                    Label:
                        id: fabric_code
                        text: "LOADING..."
                        font_size: '28sp'
                        bold: True
                        halign: 'left'
                        text_size: self.size
                    Label:
                        id: supplier
                        text: ""
                        font_size: '16sp'
                        color: hex('#bbbbbb')
                        halign: 'left'
                        text_size: self.size
                
                # Specs Grid
                GridLayout:
                    cols: 2
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: 10
                    id: specs_grid

<SpecCard>:
    size_hint_y: None
    height: '80dp'
    canvas.before:
        Color:
            rgba: hex('#2d2d2d')
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [10,]
    
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        Label:
            text: root.title
            color: hex('#888888')
            font_size: '12sp'
            text_size: self.size
            halign: 'left'
        Label:
            text: root.value
            font_size: '16sp'
            bold: True
            text_size: self.size
            halign: 'left'
            valign: 'middle'
'''

class SpecCard(BoxLayout):
    from kivy.properties import StringProperty
    title = StringProperty('')
    value = StringProperty('')

class ScannerScreen(Screen):
    def search_fabric(self):
        code = self.ids.code_input.text.strip()
        if not code:
            self.ids.status_label.text = "Please enter a fabric code"
            return
        
        self.ids.status_label.text = f"Searching for {code}..."
        detail_screen = self.manager.get_screen('details')
        detail_screen.fetch_data(code)
        self.manager.current = 'details'

class DetailScreen(Screen):
    def go_back(self):
        self.manager.current = 'scanner'

    def fetch_data(self, code):
        self.ids.fabric_code.text = f"Loading {code}..."
        self.ids.specs_grid.clear_widgets()
        Thread(target=self._background_fetch, args=(code,)).start()

    def _background_fetch(self, code):
        try:
            if GoogleSheetsClient is None:
                Clock.schedule_once(lambda dt: self._show_error("Sheets client not available"))
                return
            
            client = GoogleSheetsClient(SHEET_ID)
            data = client.find_by_code(code)
            
            if data:
                Clock.schedule_once(lambda dt: self._update_ui(data, code))
            else:
                Clock.schedule_once(lambda dt: self._show_error(f"Code '{code}' not found"))
        except Exception as e:
            print(f"Error: {e}")
            Clock.schedule_once(lambda dt: self._show_error(str(e)))

    def _update_ui(self, data, code):
        self.ids.fabric_code.text = str(data.get('Fabric_Code', code))
        self.ids.supplier.text = f"Supplier: {data.get('Supplier', 'Unknown')}"

        specs = [
            ('Composition', 'Composition'),
            ('Weight', 'BW_Weight'),
            ('Weave', 'Weave'),
            ('Width', 'Width'),
            ('Finish', 'Finish'),
            ('Warp Shrink', 'Warp_Shrink'),
            ('Weft Shrink', 'Weft_Shrink'),
            ('Stretch', 'Stretch'),
        ]
        
        for title, key in specs:
            val = str(data.get(key, '-'))
            if val:
                card = SpecCard()
                card.title = title
                card.value = val
                self.ids.specs_grid.add_widget(card)

    def _show_error(self, error):
        self.ids.fabric_code.text = "Not Found"
        self.ids.supplier.text = str(error)

class FabricScannerApp(App):
    def build(self):
        Builder.load_string(KV)
        sm = ScreenManager()
        sm.add_widget(ScannerScreen(name='scanner'))
        sm.add_widget(DetailScreen(name='details'))
        return sm

if __name__ == "__main__":
    FabricScannerApp().run()
