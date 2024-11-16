import mne
import numpy as np
import matplotlib.pyplot as plt

file_path = "skupiony_gra.fif"
raw = mne.io.read_raw_fif(file_path, preload=True)

raw.drop_channels(['Accel_x', 'Accel_y', 'Accel_z', 'Sample'])

raw.crop(tmin=0, tmax=10)

raw.filter(l_freq=8, h_freq=30, fir_design='firwin')

data, times = raw.get_data(return_times=True)
fs = raw.info['sfreq']

frequencies = np.fft.rfftfreq(data.shape[1], d=1/fs)
fft_data = np.fft.rfft(data, axis=1)

channel_names = raw.info['ch_names']
n_channels = len(channel_names)

rows, cols = 6, 2
fig, axes = plt.subplots(rows, cols, figsize=(14, 10))
axes = axes.flatten()

y_min, y_max = 0, 700000
x_min, x_max = 0, 60

for i, ax in enumerate(axes):
    if i < n_channels:
        ax.bar(frequencies, np.abs(fft_data[i]), width=frequencies[1]-frequencies[0])
        ax.set_title(f"Channel: {channel_names[i]}")
        ax.set_ylabel("Amplitude")
        ax.set_ylim(y_min, y_max)
        ax.set_xlim(x_min, x_max)
        ax.grid(True)
    else:
        ax.axis('off')

for ax in axes[-cols:]:
    ax.set_xlabel("Frequency (Hz)")

plt.tight_layout()
plt.show()
