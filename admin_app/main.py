import sys
import os
import qrcode
from PIL import Image

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QGroupBox, QFileDialog, QFormLayout, QMessageBox, QScrollArea)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap

from backend.data_models import FabricSpec
from backend.google_services import GoogleServices
from admin_app.ui_style import DARK_STYLESHEET

class WorkerThread(QThread):
    finished = pyqtSignal(bool, str) # success, message

    def __init__(self, services, sheet_name, fabric_spec):
        super().__init__()
        self.services = services
        self.sheet_name = sheet_name
        self.fabric_spec = fabric_spec

    def run(self):
        try:
            # Append to Sheet (no image upload)
            self.services.initialize_sheet_headers(self.sheet_name)
            
            row_data = self.fabric_spec.to_sheet_row()
            success = self.services.append_fabric_row(self.sheet_name, row_data)
            
            if success:
                self.finished.emit(True, "Saved successfully!")
            else:
                self.finished.emit(False, "Failed to save to Sheet.")
                
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")

class AdminWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fabric Digital Admin")
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet(DARK_STYLESHEET)
        
        # Backend Config (Ideally loaded from a config file or inputs)
        # For now, we assume user might want to hardcode or set these once
		# We'll default to placeholders or environment variables
        self.sheet_name = "fabric_library" # Default
        self.drive_folder_id = None # Default root
        
        self.services = GoogleServices()
        self.selected_image_path = None

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(main_widget)
        self.setCentralWidget(scroll)

        # Header
        header = QLabel("Fabric Entry System")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #4CAF50; margin-bottom: 20px;")
        main_layout.addWidget(header)

        # === DATA ENTRY FORM ===
        self.inputs = {}
        
        # Group 1: Identity & Origin
        grp_identity = QGroupBox("Identity & Origin")
        layout_identity = QFormLayout()
        self.add_input(layout_identity, "Fabric_Code", "Fabric Code (e.g., SODER)", required=True)
        self.add_input(layout_identity, "Supplier", "Supplier (e.g., Indigo)")
        grp_identity.setLayout(layout_identity)
        main_layout.addWidget(grp_identity)

        # Group 2: General Info
        grp_general = QGroupBox("General Info")
        layout_general = QFormLayout()
        # EXCLUDED: Payment Terms as per user request
        self.add_input(layout_general, "MoQ", "MoQ")
        self.add_input(layout_general, "Category", "Category (e.g., Denim)")
        self.add_input(layout_general, "Status", "Status (e.g., Running)")
        grp_general.setLayout(layout_general)
        main_layout.addWidget(grp_general)

        # Group 3: Specs
        grp_specs = QGroupBox("Fabric Specifications")
        layout_specs = QFormLayout()
        self.add_input(layout_specs, "Composition", "Composition (e.g., 100% CTN)")
        self.add_input(layout_specs, "Shade", "Shade (e.g., Marine)")
        self.add_input(layout_specs, "BW_Weight", "Weight (e.g., 10.00)")
        self.add_input(layout_specs, "Finish", "Finish (e.g., NC)")
        self.add_input(layout_specs, "Width", "Width in inches (e.g., 62)")
        grp_specs.setLayout(layout_specs)
        main_layout.addWidget(grp_specs)
        
        # Group 4: Technical
        grp_tech = QGroupBox("Technical Performance")
        layout_tech = QFormLayout()
        self.add_input(layout_tech, "Warp_Shrink", "Warp Shrinkage")
        self.add_input(layout_tech, "Weft_Shrink", "Weft Shrinkage")
        self.add_input(layout_tech, "Weave", "Weave (e.g., 3/1 RHT)")
        self.add_input(layout_tech, "Stretch", "Stretch %")
        self.add_input(layout_tech, "Growth", "Growth %")
        grp_tech.setLayout(layout_tech)
        main_layout.addWidget(grp_tech)

        # === ACTION BUTTONS ===
        btn_layout = QHBoxLayout()
        
        self.btn_save = QPushButton("SAVE & GENERATE QR")
        self.btn_save.setMinimumHeight(50)
        self.btn_save.setStyleSheet("background-color: #4CAF50; font-size: 16px;")
        self.btn_save.clicked.connect(self.save_data)
        
        btn_layout.addWidget(self.btn_save)
        main_layout.addLayout(btn_layout)

        # Config Inputs
        grp_config = QGroupBox("Configuration")
        layout_config = QFormLayout()
        self.inp_sheet_name = QLineEdit("fabric_library")
        layout_config.addRow("Sheet Name:", self.inp_sheet_name)
        grp_config.setLayout(layout_config)
        main_layout.addWidget(grp_config)

    def add_input(self, layout, key, label_text, required=False):
        inp = QLineEdit()
        if required:
            inp.setPlaceholderText("Required")
            inp.setStyleSheet("border: 1px solid #dba72c;") # Gold border for required
        self.inputs[key] = inp
        layout.addRow(label_text, inp)

    def generate_qr(self, fabric_code):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(fabric_code)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save locally
        save_path = f"{fabric_code}_QR.png"
        img.save(save_path)
        return save_path

    def save_data(self):
        # Validate
        code = self.inputs["Fabric_Code"].text().strip()
        if not code:
            QMessageBox.warning(self, "Validation Error", "Fabric Code is required!")
            return

        # Prepare Data
        spec = FabricSpec(
            fabric_code=code,
            supplier=self.inputs["Supplier"].text(),
            moq=self.inputs["MoQ"].text(),
            category=self.inputs["Category"].text(),
            status=self.inputs["Status"].text(),
            composition=self.inputs["Composition"].text(),
            shade=self.inputs["Shade"].text(),
            weight=self.inputs["BW_Weight"].text(),
            finish=self.inputs["Finish"].text(),
            width=self.inputs["Width"].text(),
            warp_shrink=self.inputs["Warp_Shrink"].text(),
            weft_shrink=self.inputs["Weft_Shrink"].text(),
            weave=self.inputs["Weave"].text(),
            stretch=self.inputs["Stretch"].text(),
            growth=self.inputs["Growth"].text(),
        )

        # Generate QR immediately (Local action)
        try:
            qr_path = self.generate_qr(code)
            print(f"QR Generated at {qr_path}")
        except Exception as e:
            QMessageBox.warning(self, "QR Error", f"Could not generate QR: {e}")
            return

        # Start Background Process
        self.btn_save.setEnabled(False)
        self.btn_save.setText("Saving...")
        
        sheet = self.inp_sheet_name.text().strip() or "fabric_library"

        self.worker = WorkerThread(self.services, sheet, spec)
        self.worker.finished.connect(self.on_save_complete)
        self.worker.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminWindow()
    window.show()
    sys.exit(app.exec())
