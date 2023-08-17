import torch
from diffusers import StableDiffusionPipeline
import base64

# model_id = "CompVis/stable-diffusion-v1-4"
# device = "cuda"

# pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
# pipe = pipe.to(device)

class ImageGenerator:

    def __init__(self, model_id="CompVis/stable-diffusion-v1-4", device="cuda"):
        self.pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
        self.pipe = self.pipe.to(device)

    def generate_image(self, article):
        prompt = article.title
        image = self.pipe(prompt).images[0]
        base64_string = base64.b64encode(image.tobytes()).decode()  # Assuming image has a method tobytes()
        article.image = base64_string
        # convert base 64 string to image
        return article
        
class Article:
    def __init__(self, title):
        self.title = title

if __name__ == "__main__":
    image_generator = ImageGenerator()
    sample_article = Article("This is a test title")
    article_image = image_generator.generate_image(sample_article)
    base64_encoded_image = article_image.image