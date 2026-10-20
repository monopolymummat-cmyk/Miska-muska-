import os
import sys
import asyncio
import numpy as np
from scipy.io import wavfile
import edge_tts

async def generate_voiceover(text, output_audio_path, voice="en-US-ChristopherNeural"):
    """Generates high quality TTS audio using edge-tts."""
    print(f"[AudioEngine] Synthesizing voiceover: '{text}'...")
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_audio_path)
    print(f"[AudioEngine] Saved voiceover to {output_audio_path}")

def generate_sound_effects(duration_sec, output_sfx_path, sample_rate=44100):
    """Generates dynamic high-energy sound effects (whoosh, drill hum, impact)."""
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), False)

    # 1. Drill High Pitch Sine Hum (modulated)
    drill_freq = 2800 + 400 * np.sin(2 * np.pi * 12 * t)
    drill_signal = 0.15 * np.sin(2 * np.pi * drill_freq * t)
    # Only active between t=1.2s and t=3.8s
    drill_mask = (t >= 1.2) & (t <= 3.8)
    drill_signal = drill_signal * drill_mask

    # 2. Whoosh Swish Effect (t=0.2s to 0.8s)
    whoosh_mask = (t >= 0.2) & (t <= 0.8)
    whoosh_env = np.exp(-((t - 0.5) ** 2) / 0.02) * whoosh_mask
    noise = np.random.normal(0, 0.2, len(t))
    whoosh_signal = noise * whoosh_env

    # 3. Low Bass Impact (t=0.5s)
    impact_env = np.exp(-15 * np.maximum(0, t - 0.5)) * (t >= 0.5)
    impact_signal = 0.3 * np.sin(2 * np.pi * 65 * t) * impact_env

    # Mix
    combined = drill_signal + whoosh_signal + impact_signal
    # Normalize
    combined = np.clip(combined, -0.95, 0.95)
    int_data = (combined * 32767).astype(np.int16)

    wavfile.write(output_sfx_path, sample_rate, int_data)
    print(f"[AudioEngine] Generated sound effects to {output_sfx_path}")

if __name__ == "__main__":
    os.makedirs("output/audio", exist_ok=True)
    asyncio.run(generate_voiceover("When a cavity reaches your tooth enamel, a dentist must drill the decay before it hits the nerve!", "output/audio/voiceover.mp3"))
    generate_sound_effects(5.0, "output/audio/sfx.wav")
