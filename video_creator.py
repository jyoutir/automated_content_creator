from moviepy import (
    CompositeAudioClip,
    ImageClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips,
    AudioFileClip,
)
import os
import random
import time
from moviepy.audio.fx.MultiplyVolume import MultiplyVolume

video_width = 720
video_height = 1280

class VideoGenerator:
    # Class-level variables for shared tracking
    _available_images = []
    _unused_images = []
    _all_quotes = []
    _unused_quotes = []

    def __init__(self, iteration=None):
        self.iteration = iteration
        self.image_dir = "crews/image_agent/generated_images"
        self.quotes_file = "crews/quote_agent/quotes2.md"
        self.output_dir = "video_output"
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize class-level tracking only once
        if not VideoGenerator._available_images:
            VideoGenerator._available_images = [f for f in os.listdir(self.image_dir) 
                                              if f.endswith(('.png', '.jpg', '.jpeg'))]
            VideoGenerator._unused_images = VideoGenerator._available_images.copy()
            
        if not VideoGenerator._all_quotes:
            with open(self.quotes_file, 'r') as file:
                VideoGenerator._all_quotes = [line.strip() for line in file if line.strip() and '. "' in line]
            VideoGenerator._unused_quotes = VideoGenerator._all_quotes.copy()

    def get_random_images(self, num_images=1):
        """Get random images, using all images before repeating any"""
        if not VideoGenerator._unused_images:
            print("Resetting image pool - all images have been used")
            VideoGenerator._unused_images = VideoGenerator._available_images.copy()
        
        selected_image = random.choice(VideoGenerator._unused_images)
        VideoGenerator._unused_images.remove(selected_image)
        print(f"Selected image: {selected_image}. {len(VideoGenerator._unused_images)} images remaining")
        return [selected_image]
    
    def get_center_position(container_width, container_height, item_width, item_height, y_offset=0):
        x = (container_width - item_width) // 2
        y = (container_height - item_height) // 2 + y_offset
        return (x, y)

    def get_random_quote_with_audio(self):
        """Get random quote with matching audio file"""
        # Only use quotes 1-15 since those are the ones we have audio for
        valid_quotes = [q for q in VideoGenerator._unused_quotes if int(q.split('.')[0]) <= 15]
        
        if not valid_quotes:
            print("Resetting quote pool - all quotes have been used")
            VideoGenerator._unused_quotes = VideoGenerator._all_quotes.copy()
            valid_quotes = [q for q in VideoGenerator._unused_quotes if int(q.split('.')[0]) <= 15]
        
        raw_quote = random.choice(valid_quotes)
        VideoGenerator._unused_quotes.remove(raw_quote)
        
        try:
            # Extract quote number and content
            quote_num = int(raw_quote.split('.')[0])
            quote_without_number = raw_quote.split('. "', 1)[1]
            parts = quote_without_number.split('" – ')
            
            # Format quote text
            formatted_quote = f'"{parts[0]}"\n\n- {parts[1]}' if len(parts) >= 2 else None
            
            # Get corresponding audio file
            audio_file = f"assets/quote_audio/quote_{quote_num:03d}.mp3"
            
            if formatted_quote and os.path.exists(audio_file):
                return formatted_quote, audio_file
            else:
                print(f"Missing audio file or invalid quote format for quote {quote_num}")
                return self.get_random_quote_with_audio()
                
        except Exception as e:
            print(f"Error processing quote: {raw_quote}")
            return self.get_random_quote_with_audio()
        
    
    def get_random_music(self):
        """Get random music file from music directory"""
        music_dir = "assets/music"
        # Modified this line to include both .mp3 and .mp4 files
        available_music = [f for f in os.listdir(music_dir) if f.endswith(('.mp3', '.mp4'))]
        random_music = random.choice(available_music)
        return os.path.join(music_dir, random_music)


    def create_video(self):
        """Main method to create video"""
        try:
            print("Starting video creation...")
            
            # Get random images and quote
            image_files = self.get_random_images()
            quote, quote_audio = self.get_random_quote_with_audio()
            
            print("Processing images...")
            # Create clips for each image
            clips = []
            for img_file in image_files:
                img_path = os.path.join(self.image_dir, img_file)
                clip = ImageClip(img_path).with_duration(11)  # Each image shows for 3 seconds
                clips.append(clip)
            
            text_clip = TextClip(
                text=quote,
                size=(800, None),  # Width of the text box; height is auto-determined
                font_size=70,      # Font size in points
                color='white',     # Text color
                font='assets/JosefinSans-Bold.ttf',  # Path to your font file
                method='caption',  # Ensures text wrapping within the specified width
                text_align='center',  # Center-aligns the text within the text box
                stroke_color='black',  # Adds a black outline for better readability
                stroke_width=3,     # Thickness of the outline
                interline=10,
                margin=(20, 20)    # Adds a 20-pixel margin horizontally and vertically
            ).with_duration(11)      # Duration of the text clip in seconds
            
            # Center the text
            text_clip = text_clip.with_position(('center', 'center'))

            # Logo creation
            logo = (ImageClip("assets/wordbook.png")
                    .with_duration(11)
                    .resized(height=160))  # Resize first

            # Calculate center position for logo with manual x-offset
            x_offset = 160  # Adjust this value to shift right (increase) or left (decrease)
            logo_x = (video_width - logo.w) // 2 + x_offset  # Added x_offset here
            logo_y = (video_height - logo.h) // 2 - 200  # Keep the good vertical position
            logo = logo.with_position((logo_x, logo_y))

            # WordBook text
            wordbook_text = (TextClip(
                text="WordBook",
                font_size=60,
                color="white",
                stroke_color='black',
                stroke_width=2,
                font="assets/JosefinSans-Regular.ttf")
                .with_duration(11))

            # Calculate center position for text with the same x-offset
            text_x = (video_width - wordbook_text.w) // 2 + x_offset  # Added same x_offset here
            text_y = logo_y + logo.h + 20
            wordbook_text = wordbook_text.with_position((text_x, text_y))


            print("Combining clips...")
            # Concatenate everything
            base_video = concatenate_videoclips(clips, method="compose")
            
            # Create final video with proper duration
            final_video = CompositeVideoClip([
                base_video,
                text_clip,
                logo,
                wordbook_text
                # logo_with_text.with_start(8),  
                # promo_text.with_start(8)      
            ]) 

            # Add quote audio and background music
            quote_audio_clip = AudioFileClip(quote_audio)
            background_music = AudioFileClip(self.get_random_music())
            
            quote_audio_clip = quote_audio_clip.with_effects([MultiplyVolume(1)])      # 100% volume
            background_music = background_music.with_effects([MultiplyVolume(0.2)])      # 20% volume
            if background_music.duration < final_video.duration:
                background_music = background_music.loop(duration=final_video.duration)
            else:
                background_music = background_music.subclipped(0, final_video.duration)
            
            # Combine audio tracks
            final_audio = CompositeAudioClip([background_music, quote_audio_clip])
            
            # Add combined audio to video
            final_video = final_video.with_audio(final_audio)
            output_path = os.path.join(self.output_dir, f"output_{int(time.time())}.mp4")
            
            print("Writing video file...")
            final_video.write_videofile(
                output_path, 
                fps=24, 
                codec='libx264',
                audio_codec='aac'
            )
            
            print(f"Video created successfully: {output_path}")
            
        except Exception as e:
            print(f"Error creating video: {e}")
            raise

if __name__ == "__main__":
    print("Starting 70 video generations...")
    for i in range(111):
        try:
            print(f"\nGenerating video {i+1} of 111...")
            generator = VideoGenerator(iteration=i+1)
            generator.create_video()
            time.sleep(2)
        except Exception as e:
            print(f"Error generating video {i+1}: {e}")
            continue