from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QPlainTextEdit, QLineEdit, QPushButton, QWidget, QApplication, QHBoxLayout, QLabel, QDockWidget, QListView
from PySide6.QtWebSockets import QWebSocket
from PySide6.QtNetwork import QAbstractSocket
from PySide6.QtCore import QUrl, Qt
from main_client_service import WebSocketClient
from PySide6.QtGui import QStandardItemModel, QStandardItem, QColor


class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.client = WebSocketClient("wss://chat.aaf-services.uk")
        self.client.connected.connect(self.on_connected)
        self.client.disconnected.connect(self.on_disconnect)
        self.client.message_received.connect(self.incoming_text_message)
        self.client.client_list_updated.connect(self.on_user_list_updated)

        cca = self.central_chat_area()
        self.setCentralWidget(cca)

        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.user_list_dock())

        self.setWindowTitle("AAF Chat")
        self.setFixedSize(500, 350)
    
    def user_list_dock(self):
        uld = QDockWidget("Connected Users")
        uld.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        uld.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        uld.setFixedWidth(100)
        uld.setWidget(self.user_list_handler())
        return uld
    
    def user_list_handler(self):
        self.user_list_view = QListView()
        self.user_list_model = QStandardItemModel() # Create the model
        self.user_list_view.setModel(self.user_list_model) # Set the model for the view

    def update_user_list(self, clients):
        """
        Updates the QListView with the new list of connected clients using a QStandardItemModel.

        Args:
            clients (list): A list of client dictionaries, e.g., [{'color': '#RRGGBB'}, ...].
        """
        self.user_list_model.clear() # Clear the model

        for client_data in clients:
            color = client_data.get('color')
            if color:
                item = QStandardItem(f"User: {color}") # Create a model item
                item.setForeground(QColor(color)) # Style the item
                self.user_list_model.appendRow(item) # Add item to the model
    
    def on_user_list_updated(self, clients):
        self.update_user_list(clients)

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

        send_button.clicked.connect(self.send_message)
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
    
    def incoming_text_message(self, text, sendercolor):
        self.chat_display.appendPlainText(f"{sendercolor}: {text}")
    
    def send_message(self):
        self.chat_display.appendPlainText(f"{self.client.get_client_color()} (You): {self.chat_input.text()}")
        self.client.send_chat_message(self.chat_input.text())
