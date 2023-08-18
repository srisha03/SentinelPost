import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import os
import hashlib

class ImageGenerator:

    def __init__(self, model_id="CompVis/stable-diffusion-v1-4", device="cuda", image_dir="images"):
        self.pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
        self.pipe = self.pipe.to(device)
        self.image_dir = image_dir
        os.makedirs(self.image_dir, exist_ok=True)

    def generate_image(self, article):
        prompt = article.title
        pil_image = self.pipe(prompt).images[0].convert("RGBA")

        # Generate a unique filename using a hash of the article title
        hashed_title = hashlib.md5(article.title.encode()).hexdigest()
        image_filename = os.path.join(self.image_dir, f"{hashed_title}.png")
        pil_image.save(image_filename, format="PNG")

        return image_filename
    
class Article:
    def __init__(self, title):
        self.title = title
        self.image = ''

if __name__ == "__main__":
    image_generator = ImageGenerator()
    sample_article = Article("a photo of a man free falling towards the earth, vibrant colours, oil painting")

    image_filename = image_generator.generate_image(sample_article)
    print(f"Generated image saved as: {image_filename}")

    pil_img = Image.open(image_filename)
    pil_img.show()