from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QPlainTextEdit, QLineEdit, QPushButton, QWidget, QApplication, QHBoxLayout, QLabel, QDockWidget
from PySide6.QtWebSockets import QWebSocket
from PySide6.QtNetwork import QAbstractSocket
from PySide6.QtCore import QUrl, Qt
from main_client_service import WebSocketClient

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.client = WebSocketClient("wss://chat.aaf-services.uk")
        self.client.connected.connect(self.on_connected)
        self.client.disconnected.connect(self.on_disconnect)

        cca = self.central_chat_area()
        self.setCentralWidget(cca)

        self.setWindowTitle("AAF Chat")
        self.setFixedSize(500, 350)
    
    def central_chat_area(self):
        central_widget = QWidget()
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.conn_label = QLabel("🔴 Disconnected")
        self.chat_display = QPlainTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_input = QLineEdit()
        send_button = QPushButton("Send")

        conn_buttons = QHBoxLayout()
        connect_button = QPushButton("Connect")
        disconnect_button = QPushButton("Disconnect")
        conn_buttons.addWidget(connect_button)
        conn_buttons.addWidget(disconnect_button)
        conn_but_layout = QWidget(self)
        conn_but_layout.setLayout(conn_buttons)

        # send_button.clicked.connect(self.send_message)
        connect_button.clicked.connect(self.connect_to_server)
        disconnect_button.clicked.connect(self.disconnect)
        

        layout.addWidget(self.conn_label)
        layout.addWidget(self.chat_display)
        layout.addWidget(self.chat_input)
        layout.addWidget(send_button)
        layout.addWidget(conn_but_layout)

        return central_widget

    def connect_to_server(self):
        self.client.connect_to_server()
    
    def disconnect(self):
        self.client.disconnect_from_server()
    
    def on_connected(self):
        self.chat_display.appendPlainText("Connected to server")
        self.conn_label.setText("🟢 Connected")
    
    def on_disconnect(self):
        self.chat_display.appendPlainText("Disconnected from server")
        self.conn_label.setText("🔴 Disconnected")
