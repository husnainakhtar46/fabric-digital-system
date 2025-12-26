import sys
import os
import cv2
from threading import Thread
from datetime import datetime

# Add project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.camera import Camera
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.lang import Builder
from kivy.loader import Loader

# Setup Backend services
from backend.google_services import GoogleServices
from backend.data_models import FabricSpec

# Kivy String Builder for Styling
KV = '''
#:import hex kivy.utils.get_color_from_hex

<ScannerScreen>:
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: hex('#121212')
            Rectangle:
                pos: self.pos
                size: self.size
        
        Label:
            text: "Scan Fabric QR"
            size_hint_y: 0.1
            font_size: '24sp'
            bold: True
            color: hex('#ffffff')

        # Instruction
        Label:
            size_hint_y: 0.1
            text: "Select a QR code PNG file from your folder"
            color: hex('#888888')
        
        # File Chooser
        FileChooserIconView:
            id: file_chooser
            path: '.'
            filters: ['*.png', '*.jpg', '*.jpeg']
            size_hint_y: 0.7
        
        # Upload button
        Button:
            size_hint_y: 0.1
            text: "📁 Decode Selected QR Code"
            font_size: '18sp'
            background_normal: ''
            background_color: hex('#4CAF50')
            on_release: root.decode_selected_qr()
        
        Label:
            id: status_label
            text: "Select a QR code image file above"
            size_hint_y: 0.1
            color: hex('#888888')
            text_size: self.size
            halign: 'center'

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
                text: " < Scan "
                size_hint_x: 0.2
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

                # Info Message (No Images)
                Label:
                    size_hint_y: None
                    height: '80dp'
                    text: "📋 Fabric Specifications"
                    font_size: '22sp'
                    bold: True
                    canvas.before:
                        Color:
                            rgba: hex('#2d2d2d')
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [10,]
                    
                # Title Info
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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_android = False
        self.camera = None
        
    def on_enter(self):
        # Detect platform
        try:
            from android import __version__
            self.is_android = True
            Clock.schedule_once(self.init_camera, 0.5)
        except ImportError:
            self.is_android = False
            # Desktop - file chooser already in UI
    
    def init_camera(self, dt):
        """Initialize camera for Android"""
        if not self.is_android:
            return
            
        try:
            # Use pyzbar for QR decoding on Android
            from pyzbar.pyzbar import decode
            self.decode = decode
            
            # Hide file chooser, show camera feed
            self.ids.file_chooser.opacity = 0
            self.ids.file_chooser.disabled = True
            
            # Start camera scanning loop
            Clock.schedule_interval(self.scan_camera, 1.0/3.0)  # 3 FPS
            
        except Exception as e:
            self.ids.status_label.text = f"Camera error: {e}"
    
    def scan_camera(self, dt):
        """Scan camera feed for QR codes (Android only)"""
        # This would use Android camera API
        # For actual implementation, use zbarcam or similar
        pass

    def decode_selected_qr(self):
        """Decode QR from the selected file in the file chooser (Desktop only)"""
        try:
            selected = self.ids.file_chooser.selection
            if not selected:
                self.ids.status_label.text = "Please select a file first"
                return
            
            file_path = selected[0]
            self.ids.status_label.text = f"Processing: {os.path.basename(file_path)}"
            
            # Decode QR from image
            img = cv2.imread(file_path)
            detector = cv2.QRCodeDetector()
            data, bbox, _ = detector.detectAndDecode(img)
            
            if data:
                self.ids.status_label.text = f"Found: {data}"
                self.process_qr(data)
            else:
                self.ids.status_label.text = "No QR code found. Try another image."
        except Exception as e:
            self.ids.status_label.text = f"Error: {str(e)}"

    def process_qr(self, code):
        print(f"Detected: {code}")
        detail_screen = self.manager.get_screen('details')
        detail_screen.fetch_data(code)
        self.manager.current = 'details'

class DetailScreen(Screen):
    def go_back(self):
        self.manager.current = 'scanner'

    def fetch_data(self, code):
        # Clear previous
        self.ids.fabric_code.text = f"Loading {code}..."
        self.ids.specs_grid.clear_widgets()
        
        # Async Fetch
        Thread(target=self._background_fetch, args=(code,)).start()

    def _background_fetch(self, code):
        try:
            services = GoogleServices()
            data = services.get_fabric_details("fabric_library", code)
            
            Clock.schedule_once(lambda dt: self._update_ui(data, code))
        except Exception as e:
            print(f"Error fetching: {e}")
            Clock.schedule_once(lambda dt: self._show_error(str(e)))

    def _update_ui(self, data, code):
        if not data:
            self.ids.fabric_code.text = "Not Found"
            return
        
        # Update specific fields
        self.ids.fabric_code.text = str(data.get('Fabric_Code', code))
        self.ids.supplier.text = str(data.get('Supplier', 'Unknown Origin'))

        # Spec Cards
        specs_to_show = [
            ('Composition', 'Composition'),
            ('Weight', 'BW_Weight'),
            ('Weave', 'Weave'),
            ('Width', 'Width'),
            ('Finish', 'Finish'),
            ('Shrinkage', 'Warp_Shrink'), # Simplified
        ]
        
        for title, key in specs_to_show:
            val = str(data.get(key, '-'))
            card = SpecCard()
            card.title = title
            card.value = val
            self.ids.specs_grid.add_widget(card)

    def _show_error(self, error):
        self.ids.fabric_code.text = "Error"
        self.ids.supplier.text = error

class FabricMobileApp(App):
    def build(self):
        Builder.load_string(KV)
        sm = ScreenManager()
        sm.add_widget(ScannerScreen(name='scanner'))
        sm.add_widget(DetailScreen(name='details'))
        return sm

if __name__ == "__main__":
    FabricMobileApp().run()
