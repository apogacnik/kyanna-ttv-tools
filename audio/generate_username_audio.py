from gtts import gTTS
import os

def generate_username_audio(username: str):
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'generatedAudio')
    output_file = os.path.join(output_dir, f'{username}.mp3')
    # Make sure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    tts = gTTS(username)
    tts.save(output_file)

# Testing
if __name__ == '__main__':
    generate_username_audio("matan")