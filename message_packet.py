import json

class MessagePacket():
    def __init__(self, text, connected_clients):
        self.message = text
        self.userlist = list(connected_clients)
    
    def createPacket(self):
        return json.dumps([self.message, self.userlist])
    
    def decodePacket(self, packet):
        return json.loads(packet)