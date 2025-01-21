from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import openai
import os
import requests
from datetime import datetime

class DallEToolInput(BaseModel):
    """Input schema for DALL-E image generation."""
    prompt: str = Field(..., description="The prompt to generate an image from.")
    word: str = Field(..., description="The word associated with this image.")

class DallETool(BaseTool):
    name: str = "DALL-E Image Generator"
    description: str = (
        "A tool that generates images using DALL-E based on text prompts "
        "and saves them to the images directory."
    )
    args_schema: Type[BaseModel] = DallEToolInput

    def _run(self, prompt: str, word: str) -> str:
        try:
            # Create images directory if it doesn't exist
            os.makedirs("generated_images", exist_ok=True)

            # Generate image using DALL-E
            response = openai.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1792",  
                quality="standard",
                n=1,
            )

            # Get image URL
            image_url = response.data[0].url

            # Download the image
            image_response = requests.get(image_url)
            
            # Generate filename using word and timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_images/{word}_{timestamp}.png"
            
            # Save the image
            with open(filename, "wb") as f:
                f.write(image_response.content)

            return f"Successfully generated and saved image for '{word}' at {filename}"

        except Exception as e:
            return f"Error generating image: {str(e)}" 