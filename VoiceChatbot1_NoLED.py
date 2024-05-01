# A Voice Chatbot built with Google Gemini Pro and Python 
# Tested and working on Raspberry Pi 4
# By TechMakerAI on YouTube
# 
import google.generativeai as genai
import speech_recognition as sr
from datetime import date
from gtts import gTTS
from io import BytesIO
from pygame import mixer
import threading
import queue
import time

mixer.init()
#os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

# set the Google Gemini API key as an environment variable or here
# genai.configure(api_key= "GOOGLE_API_KEY")
 
today = str(date.today())
 
# model of Google Gemini API
model = genai.GenerativeModel('gemini-pro',
    generation_config=genai.GenerationConfig(
        candidate_count=1,
        top_p = 0.7,
        top_k = 4,
        max_output_tokens=128, # 100 tokens correspond to roughly 60-80 words.
        temperature=0.7,
    ))

chat = model.start_chat(history=[])
 
def chatfun(request,text_queue, llm_finished): 
    response = chat.send_message(request, stream=True)
 
    # response.resolve() # waits for the completion of streaming response.
  
    for chunk in response:
        if chunk.candidates[0].content.parts:
            print(chunk.candidates[0].content.parts[0].text, end='') #, flush=True) 
            text_queue.put(chunk.text.replace("*", ""))
            time.sleep(0.5)
 
    append2log(f"AI: {response.candidates[0].content.parts[0].text } \n")
    
    llm_finished.set()  # Signal completion after the loop
    
def speak_text(text):
 
    mp3file = BytesIO()
    tts = gTTS(text, lang="en", tld = 'us') 
    tts.write_to_fp(mp3file)

    mp3file.seek(0)
  
    try:
        mixer.music.load(mp3file, "mp3")
        mixer.music.play()

        while mixer.music.get_busy():
            pass

    except KeyboardInterrupt:
        mixer.music.stop()
        mp3file.close()

 
    mp3file.close()	

    
def text2speech(text_queue, audio_queue, stop_event, data_available,busynow):
    
    time.sleep(1.0)

    while not stop_event.is_set():  # Keep running until stop_event is set
        try:
            text = text_queue.get(timeout=1)  # Wait for 1 second  
            if len(text) < 2:
                text_queue.task_done()
                print("skip short string text.. ")
                continue 
            
            mp3file = BytesIO()
            tts = gTTS(text, lang="en", tld = 'us') 
            tts.write_to_fp(mp3file)
        
            audio_queue.put(mp3file)
 
            waiting = True 
            
            while waiting:
                if busynow.is_set():
                    time.sleep(0.5)
                    #print("waiting")
                else:
                    data_available.set()
                    waiting = False 
 
            text_queue.task_done()
 
            
        except queue.Empty:
            pass  # Do nothing if the queue is empty
 
    
def play_audio(audio_queue, stop_event, data_available, busynow):

 
    while not stop_event.is_set():  # Keep running until stop_event is set
 
        data_available.wait()   # Wait for data to be ready
        data_available.clear()  # Reset the event for the next iteration 
        
        try:
            busynow.set()

            
            mp3file = audio_queue.get()   

            mp3file.seek(0)
  

            mixer.music.load(mp3file, "mp3")
            mixer.music.play()

            while mixer.music.get_busy():
                pass
 
            # mp3file.close()	

            busynow.clear()

            audio_queue.task_done()

            if audio_queue.empty(): 
                #print("no more audio data, breaking from audio thread")
                break  # Exit loop if queue is empty          
        except queue.Empty:
            continue  # Do nothing if the queue is empty
            
    
# save conversation to a log file 
def append2log(text):
    global today
    fname = 'chatlog-' + today + '.txt'
    with open(fname, "a", encoding='utf-8') as f:
        f.write(text + "\n")
        f.close 
 
                    
# define default language to work with the AI model 
slang = "en-EN"

# Main function  
def main():
    global today, chat, model, slang 
    
    rec = sr.Recognizer()
    mic = sr.Microphone()
    rec.dynamic_energy_threshold=False
    rec.energy_threshold = 400    
    
    sleeping = True 
    # while loop for conversation 
    while True:     
        
        with mic as source:            
            rec.adjust_for_ambient_noise(source, duration= 0.5)
 
            print("Listening ...")
 
            try: 
                audio = rec.listen(source, timeout = 20, phrase_time_limit = 30)
                text = rec.recognize_google(audio, language=slang )
 
    
                
                # AI is in sleeping mode
                if sleeping == True:
                    # User must start the conversation with the wake word "Jack"
                    # This word can be chagned by the user. 
                    if "jack" in text.lower():
                        request = text.lower().split("jack")[1]
                        
                        sleeping = False
                        # AI is awake now, 
                        # start a new conversation 
                        append2log(f"_"*40)                    
                        today = str(date.today())                         
                        chat = model.start_chat(history=[])
                        
                        # if the user's question is none or too short, skip 
                        if len(request) < 2:
 
                            speak_text("Hi, there, how can I help?")
                            append2log(f"AI: Hi, there, how can I help? \n")
                            continue                      

                    # if user did not say the wake word, nothing will happen 
                    else:
                        continue
                      
                # AI is awake         
                else: 
                    
                    request = text.lower()

                    if "that's all" in request:
                                               
                        append2log(f"You: {request}\n")
                        
                        speak_text("Bye now")
                        
                        append2log(f"AI: Bye now. \n")                        

                        print('Bye now')
                        
                        sleeping = True
                        # AI goes back to speeling mode
                        continue
                    
                    if "jack" in request:
                        request = request.split("jack")[1]                        

                # process user's request (question)
                append2log(f"You: {request}\n ")

                print(f"You: {request}\n AI: " , end='')

                text_queue = queue.Queue()
                audio_queue = queue.Queue()
                
                stop_event = threading.Event()                
                data_available = threading.Event()
                llm_finished = threading.Event()
                busynow = threading.Event()
                
                             
                # Thread 1 for getting LLM replies
                llm_thread = threading.Thread(target=chatfun, args=(request,text_queue,llm_finished,))

                # Thread 2 for text-to-speech
                tts_thread = threading.Thread(target=text2speech, args=(text_queue, audio_queue, stop_event, data_available,busynow,))
                
                # Thread 3 for playing audio
                play_thread = threading.Thread(target=play_audio, args=(audio_queue, stop_event, data_available,busynow,))
 
                llm_thread.start()
                tts_thread.start()
                play_thread.start()

                # Wait for threads to do the work 
                time.sleep(1.0)
                text_queue.join() 
                
                llm_finished.wait()
               
                llm_thread.join()
  
                time.sleep(0.5)
                audio_queue.join() 
 
                stop_event.set() 
 
                tts_thread.join()
 
                play_thread.join()  
 
                print('\n')
 
            except Exception as e:
                continue 
 
if __name__ == "__main__":
    main()




