DARK_STYLESHEET = """
QMainWindow {
    background-color: #1e1e1e;
}

QWidget {
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
    color: #e0e0e0;
}

QGroupBox {
    border: 1px solid #3e3e3e;
    border-radius: 8px;
    margin-top: 10px;
    background-color: #252526;
    font-weight: bold;
    color: #4CAF50; /* Accent color for headers */
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}

QLabel {
    color: #b0b0b0;
}

QLineEdit {
    background-color: #333333;
    border: 1px solid #3e3e3e;
    border-radius: 4px;
    padding: 6px;
    color: #ffffff;
    selection-background-color: #264f78;
}

QLineEdit:focus {
    border: 1px solid #4CAF50;
}

QPushButton {
    background-color: #0e639c;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #1177bb;
}

QPushButton:pressed {
    background-color: #094770;
}

QPushButton#uploadBtn {
    background-color: #383838;
    border: 1px dashed #555;
}

QPushButton#uploadBtn:hover {
    background-color: #444;
    border: 1px dashed #777;
}

QStatusBar {
    background-color: #007acc;
    color: white;
}
"""
