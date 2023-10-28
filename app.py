import openai
import speech_recognition as sr
import pygame
import json

# OpenAI API key
openai.api_key = "YOUR_OPENAI_API_KEY"

# Load the commands mapping
with open("commands.json", "r") as file:
    commands_mapping = json.load(file)

def listen_and_play_audio():
    """
    Listen for audio input, recognize it, determine theme using OpenAI, and play corresponding audio clip.
    """
    # Create speech recognizer object
    r = sr.Recognizer()

    # Listen for input
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)

    # Try to recognize the audio
    try:
        spoken_text = r.recognize_google(audio, language="en-EN", show_all=False)
        print("You mentioned:", spoken_text)

        # Create a prompt for OpenAI
        themes_list = ', '.join(commands_mapping.keys())
        prompt_text = f"Match this sentence to a sound from this list: {spoken_text}, {themes_list}. Respond only with the word from the list. No additional words or context."

        # Use OpenAI to match the theme
        response = openai.Completion.create(
            engine="davinci-codex",
            prompt=prompt_text,
            temperature=0.7,
            max_tokens=50
        )

        # Extract the matched theme
        matched_theme = str(response['choices'][0]['text']).strip()
        print(f"Matched theme: {matched_theme}")

        # Play the corresponding audio clip
        audio_clip_path = commands_mapping.get(matched_theme)
        if audio_clip_path:
            pygame.mixer.init()
            pygame.mixer.music.load(audio_clip_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pass  # Wait for audio to finish playing

    # Handle exceptions for speech recognition
    except sr.UnknownValueError:
        print("Sorry, couldn't understand the audio.")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")

def main():
    while True:
        listen_and_play_audio()

if __name__ == "__main__":
    main()
