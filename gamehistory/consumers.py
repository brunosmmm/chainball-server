import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class ChainbotRemoteConsumer(WebsocketConsumer):
    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            "chainbot_slv", self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            "chainbot_slv", self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        self.send(text_data=json.dumps({"message": message}))

    def slv_event(self, event):
        """Event."""
        self.send(text_data=json.dumps(event))

    def slv_start(self, event):
        """Event."""
        self.send(text_data=json.dumps(event))

    def slv_stop(self, event):
        """Event."""
        self.send(text_data=json.dumps(event))
