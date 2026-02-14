import speech_recognition as sr
import pyttsx3
import subprocess
import urllib.parse
import os

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Initialize text-to-speech engine
engine = pyttsx3.init()

def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)

        try:
            command = recognizer.recognize_google(audio)
            print("You said:", command)
            return command.lower()
        except sr.UnknownValueError:
            speak("Sorry, I did not understand.")
            return ""
        except sr.RequestError:
            speak("Speech service is unavailable.")
            return ""

def execute_command(command):

    # OPEN CHROME
    if "open chrome" in command:
        speak("Opening Chrome")
        subprocess.Popen("start chrome", shell=True)

    # CLOSE CHROME
    elif "close chrome" in command:
        speak("Closing Chrome")
        os.system("taskkill /f /im chrome.exe")

    # DIRECT SEARCH (e.g., "search python tutorial")
    elif command.startswith("search "):
        query = command.replace("search ", "")
        speak(f"Searching for {query}")
        search_url = "https://www.google.com/search?q=" + urllib.parse.quote(query)
        subprocess.Popen(f'start chrome "{search_url}"', shell=True)

    # INTERACTIVE SEARCH
    elif "search" in command:
        speak("What should I search?")
        query = listen()

        if query:
            speak(f"Searching for {query}")
            search_url = "https://www.google.com/search?q=" + urllib.parse.quote(query)
            subprocess.Popen(f'start chrome "{search_url}"', shell=True)
        else:
            speak("I did not get the search query.")

    # SHUTDOWN SYSTEM
    elif "shutdown" in command:
        speak("Shutting down system in 5 seconds")
        subprocess.Popen("shutdown /s /t 5", shell=True)

    # EXIT PROGRAM
    elif "exit" in command or "stop" in command:
        speak("Goodbye")
        exit()

    else:
        speak("Command not recognized.")

# Start Assistant
speak("Saksham AI started")

# Main Loop
while True:
    command = listen()
    if command:
        execute_command(command)
