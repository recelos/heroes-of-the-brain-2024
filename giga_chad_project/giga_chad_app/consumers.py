import asyncio
import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer

class BCIConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "bci_data"
        
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        
        await self.accept()
        
        self.send_data_task = asyncio.create_task(self.send_data_periodically())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        
        self.send_data_task.cancel()

    async def send_bci_data(self):
        voltages = [random.randint(50, 150) for _ in range(8)]
        diodes = [voltage > 100 for voltage in voltages]

        await self.send(text_data=json.dumps({
            'voltages': voltages,
            'diodes': diodes,
        }))

    async def send_data_periodically(self):
        while True:
            await self.send_bci_data()
            await asyncio.sleep(1)
