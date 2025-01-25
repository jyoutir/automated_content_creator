from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
import os
import re 

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

# Read quotes from file
with open('crews/quote_agent/quotes2.md', 'r') as file:
    lines = file.readlines()
    
# Process each line to extract quote information
quotes = []
for line in lines:
    # Skip empty lines
    if not line.strip():
        continue
    
    # Extract quote number, text, and author using regex
    match = re.match(r'(\d+)\.\s*"([^"]+)"\s*[-–]\s*(.+)', line.strip())
    if match:
        num, quote, author = match.groups()
        quotes.append((int(num), quote.strip(), author.strip()))

VOICE_ID = "yoZ06aMxZJJ28mfd3POQ"

# Generate audio for each quote
for num, quote, author in quotes:
    # Check if file already exists
    filename = f"quote_{str(num).zfill(3)}.mp3"
    filepath = os.path.join(output_dir, filename)
    
    if os.path.exists(filepath):
        print(f"Skipping quote {num} - file already exists")
        continue
    
    print(f"Generating audio for quote {num}...")
    
    try:
        # Generate the audio
        audio_stream = client.text_to_speech.convert(
            text=f"{quote} - by {author}",
            voice_id=VOICE_ID,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        
        # Write the audio stream to file
        with open(filepath, "wb") as f:
            for chunk in audio_stream:
                f.write(chunk)
        
        print(f"Saved {filename}")
        
    except Exception as e:
        print(f"Error generating audio for quote {num}: {str(e)}")

print("Done! Check the assets/quote_audio folder for your files.")