from flask import Flask, Response
import numpy as np
import io
import wave

app = Flask(__name__)

sample_rate = 44100

def generate_kick(duration=0.2):
    # Kick: quick low-frequency sine wave with decay
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    freq_start = 150
    freq_end = 60
    freqs = np.linspace(freq_start, freq_end, t.size)
    envelope = np.exp(-10 * t)
    kick = envelope * np.sin(2 * np.pi * freqs * t)
    return kick

def generate_snare(duration=0.2):
    # Snare: white noise with quick decay
    noise = np.random.normal(0, 1, int(sample_rate * duration))
    envelope = np.exp(-20 * np.linspace(0, duration, int(sample_rate * duration)))
    snare = noise * envelope
    return snare

def mix_sounds(sounds):
    # Mix multiple sounds by summing and normalizing
    mix = np.sum(sounds, axis=0)
    max_val = np.max(np.abs(mix))
    if max_val > 0:
        mix = mix / max_val  # Normalize to -1..1
    return mix

@app.route('/beat')
def generate_beat():
    bpm = 120
    beat_length = 60 / bpm  # seconds per beat
    bars = 2
    beats_per_bar = 4
    total_duration = bars * beats_per_bar * beat_length

    # Create silent audio buffer
    total_samples = int(sample_rate * total_duration)
    audio = np.zeros(total_samples)

    kick = generate_kick()
    snare = generate_snare()

    kick_samples = len(kick)
    snare_samples = len(snare)

    # Beat pattern: kick on beats 1 and 3, snare on 2 and 4
    for bar in range(bars):
        for beat in range(beats_per_bar):
            pos = int(sample_rate * (bar * beats_per_bar + beat) * beat_length)
            if beat in [0, 2]:  # Kick
                audio[pos:pos + kick_samples] += kick
            elif beat in [1, 3]:  # Snare
                audio[pos:pos + snare_samples] += snare

    # Normalize final mix
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val

    # Convert to 16-bit PCM
    audio_int16 = (audio * 32767).astype(np.int16)

    # Write to WAV buffer
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_int16.tobytes())
    buffer.seek(0)

    return Response(buffer, mimetype='audio/wav')

if __name__ == '__main__':
    app.run(debug=True)
