from moviepy import (
    ImageClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips,
    AudioFileClip,
)
import os
import random
import time

video_width = 720
video_height = 1280

class VideoGenerator:
    def __init__(self, iteration=None):
        self.iteration = iteration
        self.image_dir = "crews/image_agent/generated_images"
        self.quotes_file = "crews/quote_agent/quotes2.md"
        self.output_dir = "video_output"
        
        # Create output directory if doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize image tracking
        self.available_images = [f for f in os.listdir(self.image_dir) 
                               if f.endswith(('.png', '.jpg', '.jpeg'))]
        self.unused_images = self.available_images.copy()  # Make a copy to track unused images
        
    def get_random_images(self, num_images=1):
        """Get random images, using all images before repeating any"""
        # If we've used all images, reset the unused images list
        if not self.unused_images:
            print("Resetting image pool - all images have been used")
            self.unused_images = self.available_images.copy()
        
        # Get random image from unused pool
        selected_image = random.choice(self.unused_images)
        self.unused_images.remove(selected_image)  # Remove it from unused pool
        
        return [selected_image]  
    
    def get_random_quote(self):
        """Get random quote from quotes file and format it"""
        with open(self.quotes_file, 'r') as file:
            quotes = [line.strip() for line in file if line.strip() and '. "' in line]
            raw_quote = random.choice(quotes)
        
        try:
            # Remove the number prefix (e.g., "1. ")
            quote_without_number = raw_quote.split('. "', 1)[1]
            
            # Split the quote into components using standard delimiter
            parts = quote_without_number.split('" – ')  # Note the specific separator " – "
            
            if len(parts) >= 2:  # At minimum: quote and author
                quote = parts[0]
                author = parts[1]  # Always take last part as author
                return f'"{quote}"\n\n- {author}'
            else:
                return self.get_random_quote()  # Skip malformed quotes
                
        except Exception as e:
            print(f"Error processing quote: {raw_quote}")
            return self.get_random_quote()  # Try another quote if error occurs
        
    def get_random_music(self):
        """Get random music file from music directory"""
        music_dir = "assets/music"
        available_music = [f for f in os.listdir(music_dir) if f.endswith('.mp3')]
        random_music = random.choice(available_music)
        return os.path.join(music_dir, random_music)


    def create_video(self):
        """Main method to create video"""
        try:
            print("Starting video creation...")
            
            # Get random images and quote
            image_files = self.get_random_images()
            quote = self.get_random_quote()
            
            print("Processing images...")
            # Create clips for each image
            clips = []
            for img_file in image_files:
                img_path = os.path.join(self.image_dir, img_file)
                clip = ImageClip(img_path).with_duration(9)  # Each image shows for 3 seconds
                clips.append(clip)
            
            text_clip = TextClip(
                text=quote,
                size=(800, None),  # Width of the text box; height is auto-determined
                font_size=60,      # Font size in points
                color='white',     # Text color
                font='assets/JosefinSans-Bold.ttf',  # Path to your font file
                method='caption',  # Ensures text wrapping within the specified width
                text_align='center',  # Center-aligns the text within the text box
                stroke_color='black',  # Adds a black outline for better readability
                stroke_width=2,     # Thickness of the outline
                interline=10,
                margin=(20, 20)    # Adds a 20-pixel margin horizontally and vertically
            ).with_duration(9)      # Duration of the text clip in seconds
            
            # Center the text
            text_clip = text_clip.with_position(('center', 'center'))

            # Logo creation
            logo = (ImageClip("assets/wordbook.png")
                    .with_duration(9)
                    .resized(height=160)  # Resize first
                    .with_position((80, 80)))  # x=60 from left, y=-80 from bottom
        
            wordbook_text = (TextClip(
                text="WordBook",
                font_size=50,
                color="white",
                stroke_color='black',
                stroke_width=2,
                font="assets/JosefinSans-Regular.ttf")
                .with_duration(9)
                .with_position((lambda t: (logo.w + 120, 150))))

            ##########################################
            #####       START OF "HOOK"       ######## <- to be replaced with static IMAGES 
            ##########################################    AI agent will determine which hook works best.
            
            # # Create logo and wordbook text combination
            # logo_clip = (ImageClip("assets/wordbook.png")
            #             .resized(height=80)
            #             .with_duration(3))
            
            # wordbook_text = (TextClip(
            #     text="WordBook",
            #     font_size=60,
            #     color="white",
            #     font="assets/JosefinSans-Regular.ttf")
            #     .with_duration(3)
            #     .with_position((lambda t: (logo_clip.w + 20, 10))))
            
            # logo_with_text = (CompositeVideoClip([logo_clip, wordbook_text], size=(video_width, video_height))
            #                 .with_position(('center', 400))
            #                 .with_duration(3))
            
            # # Create promotional text
            # promo_text = (TextClip(
            #     text="If you liked this,\n\nYou will LOVE my\n\napp WordBook\n\nGet it now!",
            #     font_size=60,
            #     color="white",
            #     font="assets/JosefinSans-Regular.ttf",
            #     method='caption',
            #     interline=25,
            #     size=(800, None),
            #     text_align='center')
            #     .with_duration(3)
            #     .with_position(('center', 600)))

            ##########################################
            #####       END OF "HOOK"         ######## 
            ##########################################

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

            # Add background music
            audio = AudioFileClip(self.get_random_music())
            if audio.duration < final_video.duration:
                audio = audio.loop(duration=final_video.duration)
            else:
                audio = audio.subclipped(0, final_video.duration) 
            
            # Add audio to video + output
            final_video = final_video.with_audio(audio)
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
    for i in range(70):
        try:
            print(f"\nGenerating video {i+1} of 70...")
            generator = VideoGenerator(iteration=i+1)
            generator.create_video()
            time.sleep(2)
        except Exception as e:
            print(f"Error generating video {i+1}: {e}")
            continue