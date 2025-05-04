import numpy as np
import sounddevice as sd
import time
import threading

SAMPLE_RATE = 44100
NOTE_DURATION = 10
note_names = ['C', 'C#', 'D', 'D#', 'E', 'F',
              'F#', 'G', 'G#', 'A', 'A#', 'B']

def note_to_freq(note):
    A4 = 440.0
    if len(note) == 3:
        key = note[:2]
        octave = int(note[2])
    else:
        key = note[0]
        octave = int(note[1])
    n = note_names.index(key)
    midi_num = (octave + 1) * 12 + n
    return A4 * 2 ** ((midi_num - 69) / 12)

class SoundManager:
    def __init__(self):
        self.waveforms = {}
        self.streams = {}
        self.volumes = {}
        self.positions = {}
        self.play_start_time = {}
        self.delayed_stops = {}

        # 啟動背景監控執行緒
        self._monitor_thread = threading.Thread(target=self._background_monitor, daemon=True)
        self._monitor_thread.start()

    def generate_waveform(self, freq):
        t = np.linspace(0, NOTE_DURATION, int(SAMPLE_RATE * NOTE_DURATION), False)
        waveform = np.sin(2 * np.pi * freq * t).astype(np.float32)
        return waveform

    def preload_notes(self, notes):
        for note in notes:
            freq = note_to_freq(note)
            if freq not in self.waveforms:
                self.waveforms[freq] = self.generate_waveform(freq)
            if note not in self.streams:
                wf = self.waveforms[freq]
                self.volumes[note] = 0.0
                self.positions[note] = 0

                def make_callback(note_id):
                    def callback(outdata, frames, time_info, status):
                        wf = self.waveforms[note_to_freq(note_id)]
                        pos = self.positions[note_id]
                        total_len = len(wf)

                        if pos + frames <= total_len:
                            chunk = wf[pos:pos+frames]
                        else:
                            part1 = wf[pos:]
                            part2 = wf[:(frames - (total_len - pos))]
                            chunk = np.concatenate((part1, part2))

                        self.positions[note_id] = (pos + frames) % total_len
                        outdata[:] = (self.volumes[note_id] * chunk.reshape(-1, 1))
                    return callback

                stream = sd.OutputStream(callback=make_callback(note), samplerate=SAMPLE_RATE, channels=1)
                stream.start()
                self.streams[note] = stream
        print(f"✅ 預先啟動 {len(notes)} 個音符的 stream")

    def play_note(self, note_name, volume=1.0):
        if note_name in self.volumes:
            self.volumes[note_name] = volume
            if note_name not in self.play_start_time:
                self.play_start_time[note_name] = time.time()

    def stop_note(self, note_name):
        if note_name in self.volumes:
            now = time.time()
            started = self.play_start_time.get(note_name, 0)
            min_duration = 0.2
            if now - started >= min_duration:
                self.volumes[note_name] = 0.0
                self.play_start_time.pop(note_name, None)
                self.delayed_stops.pop(note_name, None)
            else:
                self.delayed_stops[note_name] = started + min_duration

    def _check_and_stop_expired_notes(self):
        now = time.time()
        to_remove = []
        for note, stop_time in self.delayed_stops.items():
            if now >= stop_time:
                self.volumes[note] = 0.0
                self.play_start_time.pop(note, None)
                to_remove.append(note)
        for note in to_remove:
            self.delayed_stops.pop(note)

    def _background_monitor(self):
        while True:
            self._check_and_stop_expired_notes()
            time.sleep(0.01)  # 每 10ms 檢查一次
