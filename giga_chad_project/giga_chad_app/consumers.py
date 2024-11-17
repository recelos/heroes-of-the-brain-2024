from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
import json
import time
import random

class BCIConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "bci_data"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        
        self.data_service = BluetoothDataService()
        self.data_service.start_streaming()
        self.send_data_task = asyncio.create_task(self.stream_bci_data())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        self.send_data_task.cancel()
        self.data_service.stop_streaming()

    async def stream_bci_data(self):
        while True:
            data = self.data_service.get_data()
            await self.send(text_data=json.dumps(data))
            await asyncio.sleep(0.1)  # Adjust to match your streaming needs


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


import threading
from brainaccess.utils import acquisition
from brainaccess.core.eeg_manager import EEGManager
import numpy as np
from datetime import datetime

class BluetoothDataService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance.initialize(*args, **kwargs)
        return cls._instance

    def initialize(self, device_name="BA MINI 017"):
        self.device_name = device_name
        self.eeg = acquisition.EEG()
        self.mgr = EEGManager()
        self.data = {"voltages": [], "relax": 0, "focus": 0}
        self.running = False

    def start_streaming(self):
        with self.mgr:
            cap = {0: "F3", 1: "F4", 2: "C3", 3: "C4", 4: "P3", 5: "P4", 6: "O1", 7: "O2"}
            self.eeg.setup(self.mgr, device_name=self.device_name, cap=cap)
            print("starting acquisition")
            self.eeg.start_acquisition()
            self.running = True
            threading.Thread(target=self._stream_data, daemon=True).start()

    def _stream_data(self):
        while self.running:
            try:
                data = self.eeg.get_mne(tim=2)
                if data.get_data().size > 0:
                    self.data["voltages"] = data.get_data()[:, -1].tolist()
                    relax, focus = self._calculate_relax(data)
                    self.data.update({"relax": relax, "focus": focus})
                else:
                    print("Data buffer is empty. Retrying...")
            except IndexError:
                print("Data not yet available. Ensure acquisition is running.")
            except Exception as e:
                print(f"Error: {e}")
            finally:
                time.sleep(1)

    def stop_streaming(self):
        self.running = False
        self.eeg.stop_acquisition()
        self.mgr.disconnect()

    def get_data(self):
        return self.data

    def _calculate_relax(self, raw):
        raw.filter(0.5, 100)
        bands = {"theta": (4, 8), "alpha": (8, 13), "beta": (13, 30), "gamma": (30, 100)}
        sampling_rate = raw.info["sfreq"]
        n_per_seg = int(sampling_rate * 2)
        spectrum = raw.compute_psd(method="welch", fmin=0.5, fmax=100, n_fft=n_per_seg, n_per_seg=n_per_seg)
        freqs = spectrum.freqs
        psd_mean = spectrum.get_data().mean(axis=0)
        band_powers = {band: psd_mean[(freqs >= fmin) & (freqs <= fmax)].mean() for band, (fmin, fmax) in bands.items()}
        focus_ratio = band_powers["beta"] / (band_powers["alpha"] + band_powers["theta"] + band_powers["gamma"] + 1e-6)
        relax_ratio = (band_powers["alpha"] + band_powers["theta"]) / (band_powers["beta"] + band_powers["gamma"] + 1e-6)
        focus_level = min((focus_ratio / 0.032) * 100, 100)
        relaxaction_level = min((relax_ratio / 160) * 100, 100)
        return relaxaction_level, focus_level
