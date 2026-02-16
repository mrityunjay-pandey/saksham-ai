import speech_recognition as sr
import pyttsx3
import subprocess
import urllib.parse
import os
import pyautogui
import pytesseract
from PIL import Image
import cv2
import numpy as np
import time
from ultralytics import YOLO

# Set Tesseract Path (Adjust if needed)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Initialize recognizer and TTS engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()
engine.setProperty('rate', 175)

def speak(text):
    print("Assistant:", text)
    engine.stop()
    engine.say(text)
    engine.runAndWait()
    time.sleep(0.7)

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
            return ""
        except sr.RequestError:
            speak("Speech service unavailable.")
            return ""

# ---------------- OCR FEATURE ----------------

def read_text_under_cursor():
    try:
        x, y = pyautogui.position()

        screenshot = pyautogui.screenshot(region=(x-150, y-50, 300, 100))
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

        text = pytesseract.image_to_string(gray)
        cleaned_text = text.strip().replace("\n", " ")

        if cleaned_text and len(cleaned_text) > 2:
            speak(cleaned_text)
        else:
            speak("No readable text found.")

    except Exception as e:
        speak("Error reading screen.")
        print("OCR Error:", e)

# ---------------- CAMERA OBJECT DETECTION ----------------

def start_camera_detection():
    speak("Starting camera object detection")

    model = YOLO("yolov8n.pt")  # Lightweight model
    cap = cv2.VideoCapture(0)

    spoken_objects = set()
    last_spoken_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, verbose=False)

        for result in results:
            boxes = result.boxes
            for box in boxes:
                confidence = float(box.conf[0])
                cls_id = int(box.cls[0])
                label = model.names[cls_id]

                # Speak only confident detections and avoid repetition
                if confidence > 0.6 and label not in spoken_objects:
                    if time.time() - last_spoken_time > 2:
                        speak(label)
                        spoken_objects.add(label)
                        last_spoken_time = time.time()

        cv2.imshow("Saksham AI - Camera Detection (Press Q to stop)", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    speak("Camera stopped")

# ---------------- COMMAND EXECUTION ----------------

def execute_command(command):

    if "open chrome" in command:
        speak("Opening Chrome")
        subprocess.Popen("start chrome", shell=True)

    elif "close chrome" in command:
        speak("Closing Chrome")
        os.system("taskkill /f /im chrome.exe")

    elif command.startswith("search "):
        query = command.replace("search ", "")
        speak(f"Searching for {query}")
        search_url = "https://www.google.com/search?q=" + urllib.parse.quote(query)
        subprocess.Popen(f'start chrome "{search_url}"', shell=True)

    elif "search" in command:
        speak("What should I search?")
        query = listen()
        if query:
            speak(f"Searching for {query}")
            search_url = "https://www.google.com/search?q=" + urllib.parse.quote(query)
            subprocess.Popen(f'start chrome "{search_url}"', shell=True)
        else:
            speak("I did not get the search query.")

    elif "read here" in command:
        speak("Reading text under cursor")
        read_text_under_cursor()

    elif "start camera" in command:
        start_camera_detection()

    elif "shutdown" in command:
        speak("Shutting down system in 5 seconds")
        subprocess.Popen("shutdown /s /t 5", shell=True)

    elif "exit" in command or "stop" in command:
        speak("Goodbye")
        exit()

    else:
        speak("Command not recognized.")

# ---------------- START ASSISTANT ----------------

speak("Saksham AI started")

while True:
    command = listen()
    if command:
        execute_command(command)
        time.sleep(1)
