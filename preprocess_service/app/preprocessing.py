import numpy as np
from PIL import Image
import torchvision.transforms as transforms


def process_img(img: Image.Image) -> Image.Image:
	"""
	Image transformation function using pytorch transformations
	:param img:
	:return: transformed image to be passed to DL model
	"""
	transform = transforms.Compose([transforms.Resize(256),
                                    transforms.CenterCrop(224),
                                    transforms.ToTensor(),
                                    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                                         std=[0.229, 0.224, 0.225])])
	processed_img = transform(img)
	return transforms.ToPILImage()(processed_img)


def crop(img: Image.Image, x: int, y: int, width: int, height: int,) -> Image.Image:
	"""
	Manual cropping function according to passed dimensions.
	:param img:
	:param x:
	:param y:
	:param width:
	:param height:
	:return:
	"""
	return img.crop((x, y, width + x, height + y))


def resize(img: Image.Image, width: int, height: int, resample: int = 1) -> Image.Image:
    """
    Manual resizing function according to passed dimensions.
    :param img:
    :param width:
    :param height:
    :param resample:
    :return:
    """
    return img.resize((width, height), resample=resample)
