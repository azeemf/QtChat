from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWebSockets import QWebSocket
import json

class WebSocketClient(QObject):
    """
    A PySide6 class to handle WebSocket client interactions for a chat application.

    This class manages the WebSocket connection, message handling (receiving and sending),
    and provides signals to notify about various events like connection status,
    received messages, client list updates, and typing indicators.

    No GUI elements are included in this class, focusing solely on the logic
    to interact with the WebSocket server.
    """

    # Signals to communicate events to external UI components
    connected = Signal()
    disconnected = Signal()
    message_received = Signal(str, str)  # message, sender_color (for room messages)
    direct_message_received = Signal(str, str, str)  # message, sender_color, recipient_color
    client_list_updated = Signal(list)  # list of client dictionaries [{'color': color}]
    typing_started = Signal(str)  # sender_color
    typing_stopped = Signal(str)  # sender_color
    error_received = Signal(str)  # error message
    color_assigned = Signal(str) # assigned color for this client

    def __init__(self, server_url, parent=None):
        """
        Initializes the WebSocketClient.

        Args:
            server_url (str): The WebSocket server URL (e.g., "ws://localhost:8765").
            parent (QObject, optional): Parent object for Qt object hierarchy. Defaults to None.
        """
        super().__init__(parent)
        self.server_url = server_url
        self.websocket = QWebSocket()
        self.websocket.connected.connect(self._on_connected)
        self.websocket.disconnected.connect(self._on_disconnected)
        self.websocket.textMessageReceived.connect(self._on_text_message_received)
        self.client_color = None  # Assigned color from the server
        self.connected_clients = []  # List of connected clients (updated by server)

    def connect_to_server(self):
        """
        Initiates the WebSocket connection to the server.
        """
        self.websocket.open(self.server_url)

    def disconnect_from_server(self):
        """
        Closes the WebSocket connection to the server.
        """
        self.websocket.close()

    @Slot()
    def _on_connected(self):
        """
        Slot called when the WebSocket connection is successfully established.
        Emits the 'connected' signal.
        """
        self.connected.emit()
        print("WebSocket connected")

    @Slot()
    def _on_disconnected(self):
        """
        Slot called when the WebSocket connection is closed.
        Emits the 'disconnected' signal and resets client color.
        """
        self.disconnected.emit()
        self.client_color = None # Reset color on disconnect
        print("WebSocket disconnected")

    @Slot(str)
    def _on_text_message_received(self, message):
        """
        Slot called when a text message is received from the WebSocket server.
        Parses the JSON message and emits appropriate signals based on the 'type' field.

        Args:
            message (str): The received JSON message as a string.
        """
        try:
            data = json.loads(message)
            message_type = data.get("type")

            if message_type == "color_assignment":
                self.client_color = data.get("color")
                self.color_assigned.emit(self.client_color)
                print(f"Color assigned: {self.client_color}")

            elif message_type == "client_list":
                clients = data.get("clients", [])
                self.connected_clients = clients # Update internal client list
                self.client_list_updated.emit(clients)

            elif message_type == "message":
                sender_color = data.get("sender_color")
                message_text = data.get("message")
                self.message_received.emit(message_text, sender_color)

            elif message_type == "direct_message":
                sender_color = data.get("sender_color")
                recipient_color = data.get("recipient_color")
                message_text = data.get("message")
                self.direct_message_received.emit(message_text, sender_color, recipient_color)

            elif message_type == "typing_start":
                sender_color = data.get("sender_color")
                self.typing_started.emit(sender_color)

            elif message_type == "typing_stop":
                sender_color = data.get("sender_color")
                self.typing_stopped.emit(sender_color)

            elif message_type == "error":
                error_message = data.get("message", "Unknown error")
                self.error_received.emit(error_message)
                print(f"Server Error: {error_message}")

            else:
                print(f"Received unknown message type: {message_type}")

        except json.JSONDecodeError:
            print(f"Failed to decode JSON message: {message}")
        except Exception as e:
            print(f"Error processing received message: {e}")

    def send_chat_message(self, message_text):
        """
        Sends a chat message to the room (broadcast to all connected clients).

        Args:
            message_text (str): The message text to send.
        """
        message_payload = {"type": "message", "message": message_text}
        self._send_message_json(message_payload)

    def send_direct_message(self, recipient_color, message_text):
        """
        Sends a direct message to a specific client.

        Args:
            recipient_color (str): The color of the recipient client.
            message_text (str): The message text to send.
        """
        message_payload = {"type": "direct_message", "recipient_color": recipient_color, "message": message_text}
        self._send_message_json(message_payload)

    def send_typing_start(self):
        """
        Sends a 'typing_start' indicator to the server.
        """
        message_payload = {"type": "typing_start"}
        self._send_message_json(message_payload)

    def send_typing_stop(self):
        """
        Sends a 'typing_stop' indicator to the server.
        """
        message_payload = {"type": "typing_stop"}
        self._send_message_json(message_payload)

    def _send_message_json(self, payload):
        """
        Internal helper function to send a JSON payload over the WebSocket connection.

        Args:
            payload (dict): The message payload to send as a dictionary (will be converted to JSON).
        """
        if self.websocket.isValid(): # Check if socket is in a valid state to send
            try:
                json_message = json.dumps(payload)
                self.websocket.sendTextMessage(json_message)
            except Exception as e:
                print(f"Error sending message: {e}")
        else:
            print("WebSocket is not connected or in an invalid state. Cannot send message.")

    # --- Optional Accessors (if needed, though signals are the primary way to get updates) ---
    def get_client_color(self):
        """
        Returns the assigned client color. Returns None if not yet assigned or disconnected.
        """
        return self.client_color

    def get_connected_clients(self):
        """
        Returns the current list of connected clients (as received from the server).
        Returns an empty list if not connected or list not yet received.
        """
        return self.connected_clients[:] # Return a copy to avoid direct modification

# if __name__ == '__main__':
#     import sys
#     from PySide6.QtWidgets import QApplication

#     app = QApplication(sys.argv)

#     server_url = "ws://localhost:8765"  # Replace with your server URL if different
#     client = WebSocketClient(server_url)

#     def on_connected():
#         print("Client: Connected to server!")

#     def on_disconnected():
#         print("Client: Disconnected from server!")

#     def on_message_received(message, sender_color):
#         print(f"Client: Room Message from {sender_color}: {message}")

#     def on_direct_message_received(message, sender_color, recipient_color):
#         print(f"Client: Direct Message from {sender_color} to {recipient_color}: {message}")

#     def on_client_list_updated(clients):
#         print("Client: Updated client list:", clients)

#     def on_typing_started(sender_color):
#         print(f"Client: {sender_color} started typing...")

#     def on_typing_stopped(sender_color):
#         print(f"Client: {sender_color} stopped typing.")

#     def on_error_received(error_message):
#         print(f"Client: Error from server: {error_message}")

#     def on_color_assigned(color):
#         print(f"Client: My assigned color is {color}")

#     client.connected.connect(on_connected)
#     client.disconnected.connect(on_disconnected)
#     client.message_received.connect(on_message_received)
#     client.direct_message_received.connect(on_direct_message_received)
#     client.client_list_updated.connect(on_client_list_updated)
#     client.typing_started.connect(on_typing_started)
#     client.typing_stopped.connect(on_typing_stopped)
#     client.error_received.connect(on_error_received)
#     client.color_assigned.connect(on_color_assigned)


#     client.connect_to_server()

#     # Example sending messages after a delay (for testing purposes - in a real app, user actions would trigger this)
#     def send_test_messages():
#         client.send_chat_message("Hello room, this is a test message from the client class!")
#         client.send_direct_message("#abcdef", "Hello direct message to color #abcdef!") # Replace with an actual color from client list if available
#         client.send_typing_start()
#         # Simulate typing stop after 3 seconds
#         QObject.singleShot(3000, client.send_typing_stop)

#     QObject.singleShot(5000, send_test_messages) # Send test messages after 5 seconds

#     sys.exit(app.exec())