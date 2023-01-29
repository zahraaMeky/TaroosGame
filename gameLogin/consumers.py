import json
from channels.generic.websocket import WebsocketConsumer
from .models import *
from .views import *
from django.contrib.auth import authenticate, login, logout


class GameConsumer(WebsocketConsumer):

    def connect(self):
        self.accept()
        print('connection start -----------------')

    def disconnect(self, close_code):
        print('connection lose -----------------')
        print('user id from disconnect function', id, type(id))
        getUserId = extend_user.objects.get(user_id=id)
        print('getUserId -----------------', getUserId)
        print('getUserId.is_login ', getUserId.is_login)
        getUserId.is_login = 0
        getUserId.save()
        print('getUserId.is_login ', getUserId.is_login)
        

    def receive(self, text_data):
        global id
        text_data_json = json.loads(text_data)
        id = text_data_json['id']
        print(
            'user id from receive function send when open websocket in index.html page', id)
