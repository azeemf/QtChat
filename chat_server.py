import asyncio
import websockets
from message_packet import MessagePacket

connected_clients = set()
connected_clients_info = []

async def BroadcastAll(message, websocket):
    message = MessagePacket("tu" , message, connected_clients_info).createPacket()
    for client in connected_clients:
                if client != websocket:
                    await client.send(message)

async def handler(websocket, path):
    # Add client to the set
    connected_clients.add(websocket)
    connected_clients_info.append(str(websocket.remote_address[1]))
    try:
        print("New Client: " + str(websocket.remote_address[1]))
        await BroadcastAll("tu", str(websocket.remote_address[1]) + " Connected", websocket)
        async for message in websocket:
            print(f"Received: {message}")  # Print received message to console
            # Broadcast message to all connected clients
            await BroadcastAll("tu", message, websocket)

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # Remove client when disconnected
        connected_clients.remove(websocket)
        connected_clients_info.remove(str(websocket.remote_address[1]))

async def main():
    server = await websockets.serve(handler, "0.0.0.0", 8765)
    print("WebSocket server started on ws://0.0.0.0:8765")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
