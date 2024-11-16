import mne
import matplotlib.pyplot as plt

file_path = "./data/relax.fif"

def process_eeg(file_path, frequency_bands):
    raw = mne.io.read_raw_fif(file_path, preload=True)
    raw.set_eeg_reference(ref_channels="average")
    raw.filter(l_freq=0.5, h_freq=None)
    
    filtered_data = {}
    for band, (l_freq, h_freq) in frequency_bands.items():
        filtered_data[band] = raw.copy().filter(l_freq=l_freq, h_freq=h_freq, verbose=False)
    return filtered_data

frequency_bands = {
    "theta": (4, 8),
    "alpha": (8, 13),
    "beta": (13, 30),
    "gamma": (30, 100),
}

file_paths = ["data/focus_max.fif", "data/relax_max.fif"]

all_filtered_data = [process_eeg(file_path, frequency_bands) for file_path in file_paths]

fig, axes = plt.subplots(len(file_paths), len(frequency_bands), figsize=(15, 10), sharey=True)

for (row_idx, filtered_data), file_path in zip(enumerate(all_filtered_data), file_paths):
    for col_idx, (band, data) in enumerate(filtered_data.items()):
        psds, freqs = data.compute_psd(fmin=frequency_bands[band][0],
                                       fmax=frequency_bands[band][1]).get_data(return_freqs=True)
        ax = axes[row_idx, col_idx]
        ax.semilogy(freqs, psds.mean(axis=0))
        if row_idx == 0:
            ax.set_title(f"Moc w paśmie {band.capitalize()}")
        ax.set_xlabel("Częstotliwość (Hz)")
        if col_idx == 0:
            ax.set_ylabel(f"{file_path}\nMoc (µV²/Hz)")
        ax.grid(True)

plt.tight_layout()
plt.show()