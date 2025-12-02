from PIL import Image
from pydantic import BaseModel
import requests
import io
from loguru import logger
import os

class IndvImageURL(BaseModel):
    original_url: str
    src_url: str

class ImageDL(BaseModel):
    success: bool
    width: int
    height: int

def download_image(url: str, save_path: str) -> ImageDL:
    """
    Download image to given path by url.
    Returns an ImageDL object indicating success and image dimensions.
    """
    try:
        # Send a GET request to the URL with a timeout
        resp = requests.get(url, stream=True, timeout=10)
        resp.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # Read the image content into an in-memory buffer
        img_bytes = io.BytesIO(resp.content)
        
        # Open the image using PIL to get dimensions and save
        with Image.open(img_bytes) as image:
            width, height = image.size
            
            # Ensure the image is in a saveable format (like RGB for JPEG)
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
                
            # Ensure the directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # Save the image to the specified path as JPEG
            image.save(save_path, 'jpeg')

        return ImageDL(success=True, width=width, height=height)

    except Exception as e:
        logger.error(f"Failed to download or process image from {url}: {e}")
        return ImageDL(success=False, width=0, height=0)


def convert_to_jpg():
    """
    Convert image format to jpg if it has different extension.
    """
    pass

def minsize_filter():
    """
    Filter image by minimum size
    """
    pass