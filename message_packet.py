import json

class MessagePacket():
    def __init__(self, typecode, text="", connected_clients=[]):
        self.typecode = typecode # string that controls they type of message t: text u: userlist
        if 't' in self.typecode:
            self.text = text
        elif 'u' in self.typecode:
            self.userlist = list(connected_clients)
    
    def createPacket(self):
        message = [self.typecode]
        for char in self.typecode:
            if char == 't':
                message.append(self.text)
            elif char == 'u':
                message.append(self.userlist)

        return json.dumps(message)
    
    def decodePacket(self, packet):
        uin = json.loads(packet)
        index = 1
        for char in uin:
            if char == 't':
                self.text = uin[index]
                index += 1
            elif char == 'u':
                self.userlist = uin[index]
                index += 1
    