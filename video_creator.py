from moviepy import (
    ImageClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips,
    vfx
)
import os
import random
import time

video_width = 720
video_height = 1280

class VideoGenerator:
    def __init__(self):
        self.image_dir = "crews/image_agent/generated_images"
        self.quotes_file = "crews/quote_agent/quotes.md"
        self.output_dir = "video_output"
        
        # Create output directory if doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
    def get_random_images(self, num_images=4):
        """Get random images from image directory"""
        available_images = [f for f in os.listdir(self.image_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
        return random.sample(available_images, min(num_images, len(available_images)))
    
    def get_random_quote(self):
        """Get random quote from quotes file and format it"""
        with open(self.quotes_file, 'r') as file:
            quotes = [line.strip() for line in file if line.strip()]
            raw_quote = random.choice(quotes)
        
        # Split the quote into its components and format it
        # Format is: "quote" - "source" - "author"
        parts = raw_quote.split('" - "')
        quote = parts[0].strip('"')  # Remove quotes from the quote
        author = parts[2].strip('"')  # Remove quotes from author name
        
        # Combine quote and author in desired format
        formatted_quote = f'"{quote}"\n\n- {author}'
        return formatted_quote

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
                clip = ImageClip(img_path).with_duration(2)  # Each image shows for 2 seconds
                clips.append(clip)
            
            text_clip = TextClip(
                text=quote,
                size=(800, None),  # Width of the text box; height is auto-determined
                font_size=60,      # Font size in points
                color='white',     # Text color
                font='assets/JosefinSans-Bold.ttf',  # Path to your font file
                method='caption',  # Ensures text wrapping within the specified width
                text_align='center',  # Center-aligns the text within the text box
                stroke_color='grey',  # Adds a black outline for better readability
                stroke_width=2,     # Thickness of the outline
                interline=10,
                margin=(20, 20)    # Adds a 20-pixel margin horizontally and vertically
            ).with_duration(8)      # Duration of the text clip in seconds
            
            # Center the text
            text_clip = text_clip.with_position(('center', 'center'))

            # Logo creation
            logo = (ImageClip("assets/wordbook.png")
                    .with_duration(8)
                    .resized(height=160)  # Resize first
                    .with_position((80, 80)))  # x=60 from left, y=-80 from bottom


            
            ##########################################
            #####       START OF "HOOK"       ######## <- to be replaced with static IMAGES 
            ##########################################    AI agent will determine which hook works best.
            
            # Create logo and wordbook text combination
            logo_clip = (ImageClip("assets/wordbook.png")
                        .resized(height=80)
                        .with_duration(3))
            
            wordbook_text = (TextClip(
                text="WordBook",
                font_size=60,
                color="white",
                font="assets/JosefinSans-Regular.ttf")
                .with_duration(3)
                .with_position((lambda t: (logo_clip.w + 20, 10))))
            
            logo_with_text = (CompositeVideoClip([logo_clip, wordbook_text], size=(video_width, video_height))
                            .with_position(('center', 400))
                            .with_duration(3))
            
            # Create promotional text
            promo_text = (TextClip(
                text="If you liked this,\n\nYou will LOVE my\n\napp WordBook\n\nGet it now!",
                font_size=60,
                color="white",
                font="assets/JosefinSans-Regular.ttf",
                method='caption',
                interline=25,
                size=(800, None),
                text_align='center')
                .with_duration(3)
                .with_position(('center', 600)))
            
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
                logo_with_text.with_start(8),  
                promo_text.with_start(8)      
            ]) 

            
            output_path = os.path.join(self.output_dir, f"output_{int(time.time())}.mp4")
            
            print("Writing video file...")
            final_video.write_videofile(
                output_path, 
                fps=24, 
                codec='libx264',
                audio=False
            )
            
            print(f"Video created successfully: {output_path}")
            
        except Exception as e:
            print(f"Error creating video: {e}")
            raise

if __name__ == "__main__":
    generator = VideoGenerator()
    generator.create_video()
