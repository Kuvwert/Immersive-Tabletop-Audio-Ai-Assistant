import pyaudio
import speech_recognition as sr
import pygame
import requests
import json
import time
import keyboard


class AudioHandler:
    def capture_audio(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            try:
                audio_data = recognizer.listen(source, timeout=10)
                print("Audio captured.")
                return audio_data
            except sr.WaitTimeoutError:
                print("Timeout: No speech detected.")
                return None

    def transcribe_audio(self, audio_data):
        recognizer = sr.Recognizer()
        try:
            text = recognizer.recognize_google(audio_data)
            print(f"Transcribed text: {text}")
            return text
        except sr.UnknownValueError:
            print("Speech Recognition could not understand audio.")
            return None
        except sr.RequestError:
            print("API unavailable.")
            return None


class NLPService:
    OPENAI_API_ENDPOINT = "https://api.openai.com/v1/engines/davinci-codex/completions"
    OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"  # Replace with your OpenAI API key

    def process_text(self, text, commands_mapping):
        themes_list = ', '.join(commands_mapping.keys())
        prompt_text = f"Match this sentence to a sound from this list: {text}, {themes_list}. Respond only with the word from the list. No additional words or context."

        headers = {
            "Authorization": f"Bearer {self.OPENAI_API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "OpenAI Python Client"
        }
        data = {
            "prompt": prompt_text,
            "max_tokens": 50
        }

        try:
            response = requests.post(self.OPENAI_API_ENDPOINT, headers=headers, json=data)
            response.raise_for_status()

            matched_theme = response.json()["choices"][0]["text"].strip()
            print(f"Received matched theme from GPT-3.5 Turbo: {matched_theme}")
            return matched_theme

        except requests.RequestException as e:
            print(f"OpenAI API call failed: {e}")
            return None


class AudioPlayback:
    def play_audio_clip(self, audio_path):
        print(f"Playing audio clip: {audio_path}")
        pygame.mixer.init()
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(1)
        print("Audio clip playback finished.")


class MainApp:
    def __init__(self):
        with open("commands.json", "r") as file:
            self.commands_mapping = json.load(file)
        self.audio_handler = AudioHandler()
        self.nlp_service = NLPService()
        self.audio_playback = AudioPlayback()

    def run(self):
        while True:
            if keyboard.is_pressed("space"):
                print("Spacebar pressed. Starting audio capture...")

                audio_data = self.audio_handler.capture_audio()
                if audio_data:
                    transcribed_text = self.audio_handler.transcribe_audio(audio_data)
                    if transcribed_text:
                        nlp_response = self.nlp_service.process_text(transcribed_text, self.commands_mapping)
                        if nlp_response:
                            audio_clip_path = self.commands_mapping.get(nlp_response)
                            if audio_clip_path:
                                self.audio_playback.play_audio_clip(audio_clip_path)

                time.sleep(1)  # Avoid rapid repetitions


# Instantiate and run the app
app = MainApp()
app.run()
