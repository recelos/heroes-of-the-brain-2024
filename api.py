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

from fastapi import FastAPI
import threading
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
np_data = None  # Global variable to store the latest data

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
    
    freqs = spectrum.freqs
    psd_data = spectrum.get_data(return_freqs=True)[0]

    psd_mean = psd_data.mean(axis=0)

    band_powers = {}

    for band, (fmin, fmax) in bands.items():
        band_idx = np.logical_and(freqs >= fmin, freqs <= fmax)
        band_powers[band] = psd_mean[band_idx].mean()
    
    focus_ratio = band_powers["beta"] / (band_powers["alpha"] + band_powers["theta"] + band_powers["gamma"] + 1e-6)
    relax_ratio = (band_powers["alpha"] + band_powers["theta"]) / (band_powers["beta"] + band_powers["gamma"] + 1e-6)

    # Definiujemy oczekiwane minimalne i maksymalne wartości współczynników
    min_focus_ratio = 0.088
    max_focus_ratio = 0.1  # Dostosuj tę wartość na podstawie obserwowanych danych
    min_relax_ratio = 8.5
    max_relax_ratio = 9.2  # Dostosuj tę wartość na podstawie obserwowanych danych

    # Normalizujemy współczynniki do zakresu 0-100%
    focus_level = ((focus_ratio - min_focus_ratio) / (max_focus_ratio - min_focus_ratio)) * 100
    relaxaction_level = ((relax_ratio - min_relax_ratio) / (max_relax_ratio - min_relax_ratio)) * 100

    # Zapewniamy, że wartości mieszczą się w zakresie 0-100%
    focus_level = np.clip(focus_level, 0, 100)
    relaxaction_level = np.clip(relaxaction_level, 0, 100)

    return relaxaction_level, focus_level

def acquire_data():
    global np_data
    global relax
    global focus

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

        annotation = 1
        while True:
            time.sleep(1)
            print(f"Sending annotation {annotation} to the device")
            eeg.annotate(str(annotation))
            annotation += 1
            data = eeg.get_mne(tim=1)
            relax, focus = calculate_relax(data)
            print("Relax: ", relax)
            print("Focus: ", focus)
            np_data = data.get_data()
            #print(np_data[:, -1:])

        eeg.get_mne()
        eeg.stop_acquisition()
        mgr.disconnect()

    eeg.data.save(f'data/data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.fif')
    eeg.close()
    eeg.data.mne_raw.filter(1, 40).plot(scalings="auto", verbose=False)
    plt.show()

data_thread = threading.Thread(target=acquire_data)
data_thread.start()

@app.get("/data")
async def get_data():
    global np_data
    global relax
    global focus
    if np_data is not None:
        # Oblicz średnie wartości dla każdej tablicy w np_data
        avg_values = np.mean(np_data, axis=1)
        return {"average_data": avg_values.tolist(), "relax": relax, "focus": focus}
    else:
        return {"average_data": None}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)