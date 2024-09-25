from pydub import AudioSegment

thank_you_audio_path = 'assets/audio/alert_cosmic_thank-you.mp3'
mwah_audio_path = 'assets/audio/alert_cosmic_mwah.mp3'
generatedAudio_path = 'generatedAudio/'

def combine_audio(username: str):
    # Load audio files
    thank_you_audio = AudioSegment.from_mp3(thank_you_audio_path)
    mwah_audio = AudioSegment.from_mp3(mwah_audio_path)
    username_audio = AudioSegment.from_mp3(generatedAudio_path + username + ".mp3")

    # Combine audio clips
    combined_audio = thank_you_audio + username_audio + mwah_audio

    # Export the combined audio
    combined_audio.export(generatedAudio_path + username + " thank you.mp3", format="mp3")

# Testing
if __name__ == '__main__':
    combine_audio("matan")