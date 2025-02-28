from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QPlainTextEdit, QLineEdit, QPushButton, QWidget, QApplication, QHBoxLayout, QLabel, QDockWidget
from PySide6.QtWebSockets import QWebSocket
from PySide6.QtNetwork import QAbstractSocket
from PySide6.QtCore import QUrl, Qt
from message_packet import MessagePacket
import json

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.websocket = None
        self.connected_list = []
        cwidget = self.central_chat_area()
        self.setCentralWidget(cwidget)
        

        lhs_dock = self.lhs_dock()

        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, lhs_dock)

        self.setWindowTitle("Chat Window")
        self.resize(500, 350)
    
    def lhs_dock(self):
        dock_widget = QDockWidget("Chats")
        dock_widget.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        dock_widget.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        dock_widget.setFixedWidth(200)
        self.user_label = QLabel(" ")
        dock_widget.setWidget(self.user_label)
        return dock_widget

    def central_chat_area(self):
        central_widget = QWidget()
        master_layout = QVBoxLayout()
        central_widget.setLayout(master_layout)

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

        master_layout.addWidget(self.conn_label)
        master_layout.addWidget(self.chat_display)
        master_layout.addWidget(self.chat_input)
        master_layout.addWidget(send_button)
        master_layout.addWidget(conn_but_layout)

        return central_widget

    def connect_to_server(self):
        uri = "wss://chat.aaf-services.uk"
        self.websocket = QWebSocket()
        self.websocket.connected.connect(self.on_connected)
        self.websocket.disconnected.connect(self.on_disconnected)
        self.websocket.textMessageReceived.connect(self.on_message_received)
        self.websocket.errorOccurred.connect(self.on_error)
        self.websocket.open(QUrl(uri))

    def disconnect(self):
        uri = "wss://chat.aaf-services.uk"
        self.websocket.close()

    def on_connected(self):
        self.chat_display.appendPlainText("Connected to server")
        self.conn_label.setText("🟢 Connected")

    def on_disconnected(self):
        self.chat_display.appendPlainText("Disconnected from server")
        self.conn_label.setText("🔴 Disconnected")
        self.websocket = None

    def on_message_received(self, message):
        tempMessage = MessagePacket("tu")
        tempMessage.decodePacket(message)
        self.connected_list = tempMessage.userlist
        user_string = ""
        for user in list(message)[1]:
            user_string += "\n " + user

        self.user_label.setText(user_string)
        self.chat_display.appendPlainText(f"Server: {tempMessage.text}")

    def on_error(self, error):
        self.chat_display.appendPlainText(f"Error: {error}")

    def send_message(self):
        if self.websocket and self.websocket.state() == QAbstractSocket.SocketState.ConnectedState:
            message = MessagePacket("t", self.chat_input.text())
            self.websocket.sendTextMessage(message.createPacket())
            self.chat_display.appendPlainText(f"You: {self.chat_input.text()}")
            self.chat_input.clear()
        else:
            self.chat_display.appendPlainText("Not connected to server")

if __name__ == "__main__":
    app = QApplication([])
    window = ChatWindow()
    window.show()
    app.exec()