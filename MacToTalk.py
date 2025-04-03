import asyncio
import json
import os
import signal
import sys
import time
import websockets
from datetime import datetime
from logging import getLogger, StreamHandler, DEBUG, INFO, ERROR, WARNING
from  AppKit import NSSpeechSynthesizer

logger = getLogger(__name__)
logger.addHandler(StreamHandler(stream=sys.stdout))
#logger.setLevel(DEBUG)
#logger.setLevel(INFO)
#logger.setLevel(WARNING)
logger.setLevel(ERROR)

#import custom speaker lists
try:
    import custom_speakers
except:
    logger.warning("No custom_speakers.py found.")

#define own rate of speach
rate = "+200.0"

# define voices
en_neutral = 'com.apple.voice.premium.en-US.Ava'
en_female = 'com.apple.voice.enhanced.en-GB.Stephanie'
en_male = 'com.apple.voice.premium.en-GB.Malcolm'
de_neutral = 'com.apple.voice.premium.de-DE.Petra'
de_female = 'com.apple.voice.premium.de-DE.Anna'
de_male = 'com.apple.voice.enhanced.de-DE.Markus'

# instance text to speech object from macOS
nssp = NSSpeechSynthesizer
ve = nssp.alloc().init()

#print all voices available
logger.debug("DEBUG: all available voices:")
for voice in nssp.availableVoices():
   logger.debug (voice)
logger.debug("")


async def connect_to_websocket(uri):
    while True:
        try:
            async with websockets.connect(uri, ping_interval=10, ping_timeout=5) as websocket:
                print("Connected to WebSocket server")
                while True:
                    try:
                        message = await websocket.recv()
                        logger.debug(f"Received message: {message}")
                        await process_message(message)
                    except websockets.ConnectionClosedError as e:
                        logger.warning(f"WebSocket connection closed while receiving message: {e}")
                        break  # Break inner loop to reconnect
                    except Exception as e:
                        logger.error(f"Error receiving message: {e}")
                        break  # Break inner loop to reconnect
        except (websockets.ConnectionClosedError, Exception) as e:
            logger.error(f"WebSocket connection failed: {e}")

        time.sleep(1)
        print(f"Reconnecting...")

async def process_message(message):
    try:
        message_data = json.loads(message)
        type = message_data.get("Type")

        if not type:
            logger.warning("Received message without 'Type'")
            logger.warning(f"Received message: {message}")
            return
        
        if type == 'Say':
            
            #load message data
            payload = message_data.get("Payload")
            lang = message_data.get("Language")
            voice = message_data.get("Voice")
            gender = voice.get("Name")
            speaker = message_data.get("Speaker")

            if not payload:
                # say message without payload makes no sense -> exit
                logger.warning("Received message without 'Payload'")
                logger.warning(f"Received message: {message}")
                return

            if not voice:
                logger.warning("Received message without 'Voice'")
                logger.warning(f"Received message: {message}")
                gender = 'None'

            if not gender:
                logger.warning("Received message without 'Voice'->'Name' (Gender)")
                logger.warning(f"Received message: {message}")
                gender = 'None'

            if not lang:
                logger.warning("Received message without 'Language'")
                logger.warning(f"Received message: {message}")
                lang = 'English'

            # print values used
            print(datetime.now(), "Say message received.")
            print("Gender =", gender)
            print("Language =", lang)
            print("Speaker =", speaker)
            print("Payload =", payload)
            print("")

            #set default voice
            ve.setVoice_(en_neutral)

            # set voice according to language and gender
            if gender == 'None' and lang == 'English':
                ve.setVoice_(en_neutral)
            if gender == 'Male' and lang == 'English':
                ve.setVoice_(en_male)
            if gender == 'Female' and lang == 'English':
                ve.setVoice_(en_female)
            if gender == 'None' and lang == 'German':
                ve.setVoice_(de_neutral)
            if gender == 'Male' and lang == 'German':
                ve.setVoice_(de_male)
            if gender == 'Female' and lang == 'German':
                ve.setVoice_(de_female)
              
            # overrite voices from lists
            try:
                for sp in custom_speakers.en_male_speaker:
                    if speaker == sp:
                        ve.setVoice_(en_male)
            except NameError:
                logger.warning("no custom_speakers.en_male_speaker defined")
            try:
                for sp in custom_speakers.en_female_speaker:
                    if speaker == sp:
                        ve.setVoice_(en_female)
            except NameError:
                logger.warning("no custom_speakers.en_female_speaker defined")
            try:
                for sp in custom_speakers.de_male_speaker:
                    if speaker == sp:
                        ve.setVoice_(de_male)
            except NameError:
                logger.warning("no custom_speakers.de_male_speaker defined")
            try:
                for sp in custom_speakers.de_female_speaker:
                    if speaker == sp:
                        ve.setVoice_(de_female)
            except NameError:
                logger.warning("no custom_speakers.de_female_speaker defined")

            # set rate after voice or it is ignored
            try:
                ve.setRate_(float(rate))
            except NameError:
                logger.warning("no rate defined")

            # start speaking (will continue in background till finished or stoped)
            ve.startSpeakingString_(payload)

        if type == 'Cancel':
            print(datetime.now(), "Cancel message received.")
            print("")
            # stop speaking
            ve.stopSpeaking()

    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON message: {e}")
    except Exception as e:
        logger.error(f"Error processing message: {e}")

def ask_exit():
    for task in asyncio.all_tasks():
        task.cancel()

async def main(uri):
    tasks = [
        connect_to_websocket(uri),
    ]

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    uri = "ws://127.0.0.1:3000/Messages"
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # add signal handler to end loop cleanly after ctrl+c by user
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, ask_exit)

    try:
        loop.run_until_complete(main(uri))
        loop.run_forever()
    except KeyboardInterrupt:
        logger.error("Program interrupted by user")
    except asyncio.exceptions.CancelledError:
        logger.error("Program interrupted by user")
    finally:
        loop.close()
