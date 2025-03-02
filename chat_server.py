import asyncio
import websockets
import json
import secrets  # For generating random colors and potentially client IDs in the future

connected_clients = set()
client_colors = {}
typing_clients = set()

async def get_client_list_message():
    """Generates a client list message payload."""
    client_list = [{"color": client_colors[client]} for client in connected_clients if client in client_colors] # Ensure client is still in client_colors
    return {"type": "client_list", "clients": client_list}

async def broadcast_client_list():
    """Broadcasts the updated client list to all connected clients."""
    message = await get_client_list_message()
    if connected_clients: # Avoid error if no clients are connected during server start/shutdown
        await asyncio.wait([client.send(json.dumps(message)) for client in connected_clients if client.open])

def generate_unique_color():
    """Generates a random hex color code."""
    return f"#{secrets.token_hex(3)}" # Generates a 6-digit hex color

async def send_direct_message(sender, recipient_color, message_text):
    """Sends a direct message to a specific client."""
    recipient_client = None
    for client, color in client_colors.items():
        if color == recipient_color:
            recipient_client = client
            break
    if recipient_client and recipient_client in connected_clients and recipient_client.open: # Check if recipient is connected and open
        message = {
            "type": "direct_message",
            "sender_color": client_colors[sender],
            "message": message_text,
            "recipient_color": recipient_color
        }
        await recipient_client.send(json.dumps(message))
    else:
        # Optionally, inform the sender if the recipient is not found/offline
        error_message = {"type": "error", "message": f"Recipient with color {recipient_color} not found or offline."}
        await sender.send(json.dumps(error_message))

async def handle_client(websocket, path):
    """Handles each client connection."""
    client_color = generate_unique_color()
    connected_clients.add(websocket)
    client_colors[websocket] = client_color

    try:
        # Send initial messages to the new client
        await websocket.send(json.dumps({"type": "color_assignment", "color": client_color}))
        await websocket.send(json.dumps(await get_client_list_message())) # Send initial client list

        await broadcast_client_list() # Inform other clients about the new connection

        async for message in websocket:
            data = json.loads(message)
            message_type = data.get("type")

            if message_type == "message":
                broadcast_message = {
                    "type": "message",
                    "sender_color": client_color,
                    "message": data["message"]
                }
                await asyncio.wait([
                    client.send(json.dumps(broadcast_message))
                    for client in connected_clients
                    if client != websocket and client.open # Don't send back to sender, and ensure connection is open
                ])
            elif message_type == "direct_message":
                await send_direct_message(websocket, data["recipient_color"], data["message"])
            elif message_type == "typing_start":
                typing_clients.add(websocket)
                typing_indicator = {
                    "type": "typing_start",
                    "sender_color": client_color
                }
                await asyncio.wait([
                    client.send(json.dumps(typing_indicator))
                    for client in connected_clients
                    if client != websocket and client.open
                ])
            elif message_type == "typing_stop":
                if websocket in typing_clients: # Ensure client is actually in typing_clients before removing
                    typing_clients.remove(websocket)
                    typing_indicator = {
                        "type": "typing_stop",
                        "sender_color": client_color
                    }
                    await asyncio.wait([
                        client.send(json.dumps(typing_indicator))
                        for client in connected_clients
                        if client != websocket and client.open
                    ])
            else:
                print(f"Unknown message type: {message_type}")

    except websockets.exceptions.ConnectionClosedOK:
        print(f"Client disconnected cleanly.") # Expected disconnection
    except websockets.exceptions.ConnectionClosedError:
        print(f"Client disconnected unexpectedly.") # Unexpected disconnection
    except Exception as e:
        print(f"Error handling client connection: {e}")
    finally:
        if websocket in connected_clients: # Ensure client is still in connected_clients (might have been removed due to error)
            connected_clients.remove(websocket)
        if websocket in client_colors: # Ensure client is still in client_colors
            del client_colors[websocket]
        if websocket in typing_clients: # Ensure client is still in typing_clients
            typing_clients.remove(websocket)
        await broadcast_client_list() # Update client list for everyone on disconnect

async def main():
    """Starts the WebSocket server."""
    server = await websockets.serve(handle_client, "0.0.0.0", 8765) # Listen on all interfaces, port 8765
    print("WebSocket server started at ws://0.0.0.0:8765")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())