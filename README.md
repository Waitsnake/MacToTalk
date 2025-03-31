# MacToTalk
Python script to foreward TextToTalk(https://github.com/karashiiro/TextToTalk) WebSocket IpcMessage to TTS of macOS

# Install and Run
- download or clone this repo to your harddisk
- install needed requirements for the python script via pip package manager:
  ```
  pip install -r requirements.txt
  ```
- the script MacToTalk.py defines some voices it uses:
  ```
  en_neutral = 'com.apple.voice.premium.en-US.Ava'
  en_female = 'com.apple.voice.enhanced.en-GB.Stephanie'
  en_male = 'com.apple.voice.premium.en-GB.Malcolm'
  de_neutral = 'com.apple.voice.premium.de-DE.Petra'
  de_female = 'com.apple.voice.premium.de-DE.Anna'
  de_male = 'com.apple.voice.enhanced.de-DE.Markus'
  ```
  You need to download those in macOS system preferences under voices for text to speech.
  If the script trys to use a voice that was not downloaded before it will use a standard fallback voice that not sounds good, but works as a fallback.
- In the script you can also define the speech rate in words per minute:
  ```
  rate = "+225.0"
  ```
  It is set per daufault to a very fast value to keep up with the default autoadvance speed of FFXIV during some cutscenes.
- In the script custom_speakers.py you can add some overrides for voices ofr certain character names of your choice. E.g. I usually have my game set to English, but certain players always talk german to me, so I assign them here to a German voice. If no override is set it uses the language(your game language) and gender that TextToTalk send via the Websocket API.
  ```
  de_male_speaker = ["Papalymo Lalafell","Alphinaud Elezen"]
  de_female_speaker = ["Krile Lalafell", "Alisaie Elezen"]
  en_male_speaker = ["G'raha Miqo'te","Estinien Elezen"]
  en_female_speaker = ["Y'shtola Miqo'te", "Yda Hyur"]
  ```
- to run the script:
  ```
  python MacToTalk.py
  ```
  The script will try once per second to connect to the Websocket API of TextToTalk on IP 127.0.0.1 (localhost) and port 3000. So you need to start your came with Dalamud and change the settings in TextToTalk that "Websocket" is used and change the IP and port to that value.
  You can stop the script at any time with ctrl+C in terminal where you run it.
