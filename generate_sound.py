import numpy as np
import soundfile as sf

def generate_oscillating_volume_sound(frequency_left, frequency_right, duration, modulation_frequency, sample_rate=48000):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)  # Time array

    modulation_wave = 0.35 * (1 + np.sin(2 * np.pi * modulation_frequency * t)) + 0.65
    modulation_wave = modulation_wave[:, np.newaxis]

    left_wave = 0.5 * np.sin(2 * np.pi * frequency_left * t)
    right_wave = 0.5 * np.sin(2 * np.pi * frequency_right * t)
    stereo_wave = np.column_stack((left_wave, right_wave))
    stereo_signal = np.clip(stereo_wave, -1.0, 1.0)

    modulated_wave = stereo_signal * modulation_wave


    return modulated_wave, sample_rate

audio_data, sample_rate = generate_oscillating_volume_sound(frequency_left=240, frequency_right=250, duration=10, modulation_frequency=0.25)


sf.write('relax_audio.wav', audio_data, sample_rate)
