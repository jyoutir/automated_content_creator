from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
import os

# Load environment variables
load_dotenv()

# Get API key and verify it exists
api_key = os.getenv('ELEVEN_API_KEY')
if not api_key:
    raise ValueError("No API key found. Make sure ELEVEN_API_KEY is set in your .env file")

# Initialize client with API key
client = ElevenLabs(api_key=api_key)

# Create output directory
output_dir = "assets/quote_audio"
os.makedirs(output_dir, exist_ok=True)

# Test quotes
test_quotes = [
    (123, "Long ago, there lived great founders; Nukul Rajpoot, Kai Quan Lian and Jyoutir Raj. Together they created the first AGI", "Some Guy")
]

VOICE_ID = "W9jDLMGhiMBIh9dsQSLP" 

# Generate audio for each quote
for num, quote, author in test_quotes:
    print(f"Generating audio for quote {num}...")
    
    # Generate the audio
    audio_stream = client.text_to_speech.convert(
        text=f"{quote} - by {author}",
        voice_id=VOICE_ID,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128"
    )
    
    # Save the file
    filename = f"quote_{str(num).zfill(3)}.mp3"
    filepath = os.path.join(output_dir, filename)
    
    # Write the audio stream to file
    with open(filepath, "wb") as f:
        for chunk in audio_stream:
            f.write(chunk)
    
    print(f"Saved {filename}")

print("Done! Check the assets/quote_audio folder for your files.")