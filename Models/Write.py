
from urllib import request, parse
class Write:
     def __init__(self, payload):
         self.payload=payload

     def send(self):
         data = parse.urlencode(self.payload).encode()
         req = request.Request(  data = data)  # this will make the method "POST"
         resp = request.urlopen(req)