import numpy as np
import soundfile as sf
def generate_stereo_dynamic_frequency_and_volume(frequency_func_left, frequency_func_right, modulation_frequency, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    frequencies_left = frequency_func_left(t)
    frequencies_right = frequency_func_right(t)

    modulation_wave = 0.35 * (1 + np.sin(2 * np.pi * modulation_frequency * t)) + 0.65
    modulation_wave = modulation_wave[:, np.newaxis]  # Shape becomes (N, 1)


    left_wave = 0.5 * np.sin(2 * np.pi * np.cumsum(frequencies_left / sample_rate))
    right_wave = 0.5 * np.sin(2 * np.pi * np.cumsum(frequencies_right / sample_rate))


    left_wave *= modulation_wave[:, 0]
    right_wave *= modulation_wave[:, 0]
    stereo_wave = np.column_stack((left_wave, right_wave))

    return  stereo_wave, sample_rate


audio_data, sample_rate = generate_stereo_dynamic_frequency_and_volume(
    frequency_func_left=lambda t: 240 + (200 - 200) * (t / t[-1]),
    frequency_func_right=lambda t: 250 + (280 - 200) * (t / t[-1]),
    modulation_frequency=0.25,
    duration=10
)
sf.write('change_audio.wav', audio_data, sample_rate)
