import os
import sys
import warnings
from datetime import datetime

path = sys.argv[1]
os.add_dll_directory(path)

import matplotlib.pyplot as plt
import matplotlib
import time

from brainaccess.utils import acquisition
from brainaccess.core.eeg_manager import EEGManager

matplotlib.use("TKAgg", force=True)

eeg = acquisition.EEG()

# define electrode locations
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

# define device name
device_name = "BA MINI 017"

# start EEG acquisition setup
with EEGManager() as mgr:
    eeg.setup(mgr, device_name=device_name, cap=cap)
    print(mgr.get_device_info())
    # Start acquiring data
    eeg.start_acquisition()
    time.sleep(3)

    start_time = time.time()
    annotation = 1
    while time.time() - start_time < 60:
        time.sleep(1)
        # send annotation to the device
        print(f"Sending annotation {annotation} to the device")
        eeg.annotate(str(annotation))
        annotation += 1
        data = eeg.get_mne(tim=1)
        np_data = data.get_data()
        print(np_data[:, -1:])
        #for idx, channel_name in enumerate(data.ch_names):
        #    print(f"{channel_name}: {np_data[idx, -1]}")

    # get all eeg data and stop acquisition
    eeg.get_mne()
    eeg.stop_acquisition()
    mgr.disconnect()

# save EEG data to MNE fif format
eeg.data.save(f'data/data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.fif')
# Close brainaccess library
eeg.close()
# Show recorded data
eeg.data.mne_raw.filter(1, 40).plot(scalings="auto", verbose=False)
plt.show()
