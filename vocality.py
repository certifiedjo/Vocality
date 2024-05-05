import numpy as np
import openai
import random
from scipy.io.wavfile import write
import sounddevice as sd 
import pyttsx3
import os

from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

adjectives = ["beautiful", "magnificent", "gorgeous", "stunning", "breathtaking", "lovely", "charming", "exquisite", "elegant", "graceful"]
nouns = ["flower", "mountain", "lake", "river", "forest", "valley", "meadow", "field", "ocean", "desert"]

engine = pyttsx3.init()

engine.setProperty('rate', 160)

def change_voice(engine, language, gender='VoiceGenderMale'):
    try:
        for voice in engine.getProperty('voices'):
            if language in voice.languages and gender == voice.gender:
                engine.setProperty('voice', voice.id)
                return True
            
        raise RuntimeError("Language '{}' for gender '{}' not found".format(language, gender))
    except:
        print("Language not found")

change_voice(engine, "en_US", "VoiceGenderMale")

def generate_random_name():

    adjective = random.choice(adjectives)
    noun = random.choice(nouns)
    return f"{adjective} {noun}"

def new_record_audio():
    fs = 44100
    seconds = 5
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, blocking=True)
    sd.wait()

    audio_name = generate_random_name()
    write(f'./voices/{audio_name}.wav', fs, myrecording)
    print("recording stopped...")

    return f'./voices/{audio_name}.wav'

def speech_to_text(audio_path):
    print("entered transcribe", audio_path)
    with open(audio_path, "rb") as audio_file:
        response = openai.Audio.transcription.create(
            model="whisper-1",
            file=audio_file
        )
        transcript = response['text']
    print(transcript)
    return transcript

def text_to_speech(response):

    engine.say(response)
    engine.runAndWait()

def openai_chat_send(transcript):

    messages = [
        {"role": "system", "content": "Your name is Vocality and you are an AI assistant."},
        {"role": "user", "content": transcript}
    ]
    print("Transcript: ", transcript)

    completion = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = messages
    )
    return completion.choices[0].message["content"]

def main():
    try:
        while True:
            print("Press 's' to stop recording and transcribe the audio.")

            recorded_audio_path = new_record_audio()
            print("Recording stopped. Transcribing audio...")

            print("Recorded audio saved to:", recorded_audio_path)
            print("--- end ---")

            transcript = speech_to_text(recorded_audio_path)
            response = openai_chat_send(transcript)

            print("Vocality: ", response)
            text_to_speech(response)

    except KeyboardInterrupt:
        print("Exiting program...")
        engine.stop()  # Ensure to stop the pyttsx3 engine properly
        sys.exit()


if __name__ == "__main__":
    main()
