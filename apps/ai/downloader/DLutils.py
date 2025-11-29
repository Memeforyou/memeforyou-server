from PIL import Image
from pydantic import BaseModel

class IndvImageURL(BaseModel):
    original_url: str
    src_url: str

class ImageDL(BaseModel):
    success: bool
    width: int
    height: int

def download_image(url: str, save_path: str):
    """
    Download image to given path by url.
    """
    pass

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