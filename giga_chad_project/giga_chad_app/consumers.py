import asyncio
import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer
import os
import sys
import mne
import numpy as np
from datetime import datetime
from scipy.signal import welch
huj = "C://Users//craksys//Desktop//git//heroes-of-the-brain-2024//BrainAccessSDK"
os.add_dll_directory(huj)

import matplotlib.pyplot as plt
import matplotlib
import time

from brainaccess.utils import acquisition
from brainaccess.core.eeg_manager import EEGManager

class BCIConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        matplotlib.use("TKAgg", force=True)
        eeg = acquisition.EEG()
        cap: dict = {
            0: "F3",
            1: "F4",
            2: "C3",
            3: "C4",
            4: "P3",
            5: "P4",
            6: "O1",
            7: "O2"
        }
        device_name = "BA MINI 017"
        with EEGManager() as mgr:
            eeg.setup(mgr, device_name=device_name, cap=cap)
            print(mgr.get_device_info())
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


class BrainLevelConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "brain_level"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        self.send_data_task = asyncio.create_task(self.send_brain_level_periodically())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        self.send_data_task.cancel()

    async def send_brain_level_data(self):
        brain_level = round(random.random(), 2)
        relax = round(random.uniform(0, 1), 2)
        focus = round(random.uniform(0, 1), 2)

        await self.send(text_data=json.dumps({
            'brain_level': brain_level,
            'relax': relax,
            'focus': focus,
        }))

    async def send_brain_level_periodically(self):
        while True:
            await self.send_brain_level_data()
            await asyncio.sleep(1)
