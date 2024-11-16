""" EEG measurement example

Example how to get measurements using brainaccess library

Change Bluetooth device name to your device name (line 57)
"""
import os
import sys
path = sys.argv[1]
os.add_dll_directory(path)

import numpy as np
import time
import warnings
import threading
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from scipy.signal import butter, sosfiltfilt
from brainaccess import core
from brainaccess.core.eeg_manager import EEGManager
import brainaccess.core.eeg_channel as eeg_channel
from brainaccess.core.gain_mode import (
    GainMode,
)

def butter_bandpass(lowcut, highcut, fs, order=1):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    sos = butter(order, [low, high], analog=False, btype="bandpass", output="sos")
    return sos


def butter_bandpass_filter(data, lowcut, highcut, fs, order=1):
    sos = butter_bandpass(lowcut, highcut, fs, order=order)
    y = sosfiltfilt(sos, data)
    return y


def _acq_closure(ch_number: int = 1, buffer_length: int = 1000):
    data = np.zeros((ch_number, buffer_length))
    mutex = threading.Lock()

    def _acq_callback(chunk, chunk_size):
        nonlocal data
        nonlocal mutex
        with mutex:
            data = np.roll(data, -chunk_size)
            data[:, -chunk_size:] = chunk

    def get_data():
        nonlocal data
        with mutex:
            return data.copy()

    return _acq_callback, get_data


if __name__ == "__main__":
    device_name = "BA MINI 017"  # change to your device name
    core.init()

    # scan for devices find the defined one
    core.scan(0)  # adapter number (on windows always 0)
    count = core.get_device_count()
    port = 0

    print("Found devices:", count)
    for i in range(count):
        name = core.get_device_name(i)
        if device_name in name:
            port = i

    # connect to the device
    with EEGManager() as mgr:
        print("Connecting to device:", core.get_device_name(port))
        _status = mgr.connect(port)
        if _status == 1:
            raise Exception("Connection failed")
        elif _status == 2:
            warnings.warn("Stream is incompatible. Update the firmware.")

        # battery info
        print("battery level:", mgr.get_battery_info().level)

        # set the channels
        print("Setting the channels")
        ch_nr = 0
        eeg_channels_number = 8
        for i in range(eeg_channels_number):
            mgr.set_channel_enabled(eeg_channel.ELECTRODE_MEASUREMENT + i, True)
            ch_nr += 1
            mgr.set_channel_gain(eeg_channel.ELECTRODE_MEASUREMENT, GainMode.X8)
        mgr.set_channel_bias(eeg_channel.ELECTRODE_MEASUREMENT + i, True)

        # check if the device has accelerometer
        has_accel = mgr.get_device_features().has_accel()
        if has_accel:
            print("Setting the accelerometer")
            mgr.set_channel_enabled(eeg_channel.ACCELEROMETER, True)
            ch_nr += 1
            mgr.set_channel_enabled(eeg_channel.ACCELEROMETER + 1, True)
            ch_nr += 1
            mgr.set_channel_enabled(eeg_channel.ACCELEROMETER + 2, True)
            ch_nr += 1

        mgr.set_channel_enabled(eeg_channel.SAMPLE_NUMBER, True)
        ch_nr += 1

        mgr.set_channel_enabled(eeg_channel.STREAMING, True)
        ch_nr += 1

        # set the sample rate
        sr = mgr.get_sample_frequency()

        # define the callback for the acquisition
        duration = 20
        buffer_time = int(sr * duration)  # seconds
        _acq_callback, get_data = _acq_closure(
            ch_number=ch_nr, buffer_length=buffer_time
        )
        mgr.set_callback_chunk(_acq_callback)

        # load defined configuration
        mgr.load_config()

        # start the stream
        mgr.start_stream()
        print("Stream started")

        # collect data
        time.sleep(4)
        for i in range(duration):
            time.sleep(1)
            print(f"Collecting data {i+1}/{duration}")

        # get the data
        dat = get_data()

        # stop the stream
        mgr.stop_stream()

    # close the core
    core.close()

    # plot the data
    df = pd.DataFrame(dat.T)
    if has_accel:
        ch = []
        ch.append("sample")
        ch.extend([f"ch_{i}" for i in range(eeg_channels_number)])
        ch.extend(["accel_x", "accel_y", "accel_z"])
    else:
        ch = []
        ch.append("sample")
        ch.extend([f"ch_{i}" for i in range(eeg_channels_number)])
    ch.extend(["streaming"])
    df.columns = ch
    df.iloc[:, 1:eeg_channels_number+1] = butter_bandpass_filter(df.iloc[:, 1:eeg_channels_number+1].T, 1, 40, sr).T
    fig, axs = plt.subplots(4, 1, figsize=(10, 10))
    eeg_data = df.iloc[:, 1:eeg_channels_number+1].values
    eeg_data = (eeg_data - eeg_data.mean(axis=0)) / eeg_data.std(axis=0)
    eeg_data = eeg_data + np.arange(eeg_channels_number)
    sns.lineplot(data=eeg_data, ax=axs[0])
    sns.lineplot(data=df.iloc[:, len(ch)-4:-1], ax=axs[1])
    sns.lineplot(data=df.iloc[:, 0], ax=axs[2])
    sns.lineplot(data=df.iloc[:, -1], ax=axs[3])
    plt.show()