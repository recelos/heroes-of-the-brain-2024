import os
import sys
import mne
import numpy as np
from datetime import datetime
from scipy.signal import welch

path = sys.argv[1]
os.add_dll_directory(path)

import matplotlib.pyplot as plt
import matplotlib
import time

from brainaccess.utils import acquisition
from brainaccess.core.eeg_manager import EEGManager


def calculate_relax(raw):
    raw.filter(0.5, 100)

    bands = {
        "theta": (4, 8),
        "alpha": (8, 13),
        "beta": (13, 30),
        "gamma": (30, 100),
    }

    sampling_rate = raw.info["sfreq"]
    n_per_seg = int(sampling_rate * 2)
    
    spectrum = raw.compute_psd(method="welch", fmin=0.5, fmax=100, n_fft=n_per_seg, n_per_seg=n_per_seg)
    
    freqs = spectrum.freqs  # Frequency bins
    psd_data = spectrum.get_data(return_freqs=True)[0]  # Extract the PSD data

    psd_mean = psd_data.mean(axis=0)  # Average across channels (axis 0)

    band_powers = {}

    for band, (fmin, fmax) in bands.items():
        band_idx = np.logical_and(freqs >= fmin, freqs <= fmax)
        band_powers[band] = psd_mean[band_idx].mean()

    focus_ratio = band_powers["beta"] / (band_powers["alpha"] + band_powers["theta"] + band_powers["gamma"] + 1e-6)
    relax_ratio = (band_powers["alpha"] + band_powers["theta"]) / (band_powers["beta"] + band_powers["gamma"] + 1e-6)

    # Normalize to 0-100% without clipping
    max_relax = 160  # You can change this value as needed
    max_focus = 0.032  # You can change this value as needed

    focus_level = min((focus_ratio / max_focus) * 100, 100)
    relaxaction_level = min((relax_ratio / max_relax) * 100, 100)

    return relaxaction_level, focus_level



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
    eeg.start_acquisition()
    time.sleep(3)

    start_time = time.time()
    annotation = 1
    while time.time() - start_time < 30:
        time.sleep(2)
        print(f"Sending annotation {annotation} to the device")
        eeg.annotate(str(annotation))
        annotation += 1
        data = eeg.get_mne(tim=2)
        relax, focus = calculate_relax(data)
        print("Relax: ", relax)
        print("Focus: ", focus)
        np_data = data.get_data()
        # print(np_data[:, -1:])
        # for idx, channel_name in enumerate(data.ch_names):
        #    print(f"{channel_name}: {np_data[idx, -1]}")

    eeg.get_mne()
    eeg.stop_acquisition()
    mgr.disconnect()

eeg.data.save(f'data/data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.fif')
eeg.close()
eeg.data.mne_raw.filter(1, 40).plot(scalings="auto", verbose=False)
plt.show()