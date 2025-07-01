import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import numpy as np
import cv2

class ValorantVisionAISuggester:
    def __init__(self, device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(self.device)

    def suggest(self, frame: np.ndarray) -> str:
        """Generate a suggestion for Valorant based on a screen capture (BGR numpy array)"""
        # Convert BGR (OpenCV) to RGB (PIL)
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        prompt = "What should I do next in Valorant?"
        inputs = self.processor(image, prompt, return_tensors="pt").to(self.device)
        out = self.model.generate(**inputs, max_new_tokens=30)
        suggestion = self.processor.decode(out[0], skip_special_tokens=True)
        return suggestion
