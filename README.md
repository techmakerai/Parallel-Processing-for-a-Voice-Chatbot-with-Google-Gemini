# Parallel Processing for Speeding up a Voice Chatbot with Google Gemini

In my previous project, I built a Google Gemini-powered voice chatbot with Python. However, in that code, I used sequential (programming) processing such that there is a pause in the middle of the reply from AI. In this project, I will build a Google Gemini-powered voice chatbot with parallel processing in Python. Specifically, we will use parallel computing in Python to split tasks such as Text generation, Text-to-Speech conversation, and audio playing onto three threads (CPU cores) and speed up the program. I have one version of the code that only works on Raspberry Pi because it requires LEDs and resistors. If you do not have LEDs or resistors, I have another version that works on Raspberry Pi and Windows PCs.   

Following the YouTube video below to learn more about this code:     
[https://youtu.be/BQuYTOirVy4](https://youtu.be/b7lRQkJ2xJA)

Here is a schematic of the Raspberry Pi and LEDs    
<img src="https://github.com/techmakerai/Google-Gemini-Voice-Chatbot-on-Raspberry-Pi/blob/main/PaspberryPiSchematic.jpg" width="720"/>

## Materials 

1. Raspberry Pi (https://amzn.to/4bmstJa)
2. microSD card (https://amzn.to/4ay0HbY)
2. Audio amplifier (https://amzn.to/3JjPWy9)
3. USB Microphone (https://amzn.to/3HGGSCA) 
4. Mini speaker (https://amzn.to/3TB9Pp3)    
5. (optional) LEDs and resistors (https://amzn.to/3Jg4Yoz)     

## Set System Environment Variables 

GOOGLE_API_KEY=(API key from Google)   
PYGAME_HIDE_SUPPORT_PROMPT=hide

## Install Python and Packages 
You will need to install the following packages to run this code: 

```console
pip install -q -U google-generativeai
pip install speechrecognition gtts pygame pyaudio gpiozero
```
   
If you have Python 3.12 or newer, also install the "setuptools" package,       

```console
pip install setuptools
```    


