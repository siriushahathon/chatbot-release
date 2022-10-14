#!/usr/bin/env python3

from vosk import Model, KaldiRecognizer, SetLogLevel
import subprocess
import json

SetLogLevel(0)

sample_rate=16000
model = Model("./model")
rec = KaldiRecognizer(model, sample_rate)

def convert_to_text(voice_bytes):
    process = subprocess.Popen(['ffmpeg', '-loglevel', 'quiet', '-i', '/dev/stdin',
                                '-ar', str(sample_rate) , '-ac', '1', '-f', 's16le', '-'],
                                stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    process.stdin.write(voice_bytes)
    process.stdin.close()
    while True:
        data = process.stdout.read(4000)
        if len(data) == 0:
            break
        rec.AcceptWaveform(data)

    return json.loads(rec.FinalResult())['text']

