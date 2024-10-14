from gtts import gTTS
import os
import re

# Some cleanup for better tts results
def preprocess_username(username):
    # Remove numbers at the end
    username = re.sub(r'\d+$', '', username)
    # Ignore underscores
    username = username.replace('_', ' ')
    # Replace numbers with corresponding letters
    username = username.replace('3', 'e').replace('1', 'i')
    # Remove "lol" (case insensitive) at the end
    username = re.sub(r'(?i)lol$', '', username)
    # Replace characters repeating 3 or more times with 2 occurrences
    username = re.sub(r'(.)\1{2,}', r'\1\1', username)
    # Convert to lowercase only if the entire username is uppercase
    if username.isupper():
        username = username.lower()
    # Remove spaces at the end
    username = username.rstrip()
    return username

def generate_username_audio(username: str):
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'generatedAudio')
    output_file = os.path.join(output_dir, f'{username}.mp3')
    # Make sure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    username = preprocess_username(username)
    tts = gTTS(username)
    tts.save(output_file)

# Testing
if __name__ == '__main__':
    generate_username_audio("matan")