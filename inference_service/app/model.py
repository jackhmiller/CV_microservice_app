from typing import Union
import torch
from torchvision.models import resnet50, ResNet50_Weights
from torchvision.models.segmentation import fcn_resnet50, FCN_ResNet50_Weights
from torchvision.models.detection import fasterrcnn_resnet50_fpn_v2, FasterRCNN_ResNet50_FPN_V2_Weights
from torchvision.utils import draw_bounding_boxes
from torchvision.transforms.functional import to_pil_image
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
from utils import logger


MODEL_PARAMS = {
	'classification':
		{'weights': ResNet50_Weights.DEFAULT, 'model': resnet50},
	'detection':
		{'weights': FasterRCNN_ResNet50_FPN_V2_Weights.DEFAULT, 'model': fasterrcnn_resnet50_fpn_v2},
	'segmentation':
		{'weights': FCN_ResNet50_Weights.DEFAULT, 'model': fcn_resnet50}
}


def do_inference_task(img: Image.Image, task: str) -> Union[str, torch.Tensor]:
	img = transforms.ToTensor()(img)
	logger.info(f"Performing {task}")
	if task == 'classification':
		category = Classifier(img).run_inference()
		return category
	elif task == 'detection':
		img = ObjectDetector(img).run_inference()
		return img
	elif task == 'segmentation':
		mask = Segmentation(img).run_inference()
		return mask


class BaseModel:
	def __init__(self, img: torch.Tensor):
		self.img = img


class Classifier(BaseModel):
	def __init__(self, img: torch.Tensor):
		super().__init__(img)
		self.weights = MODEL_PARAMS['classification']['weights']

	def run_inference(self) -> str:
		model = MODEL_PARAMS['classification']['model'](weights=self.weights)
		model.eval()
		preprocess = self.weights.transforms()
		batch = preprocess(self.img).unsqueeze(0)
		prediction = model(batch).squeeze(0).softmax(0)
		class_id = prediction.argmax().item()
		score = prediction[class_id].item()
		logger.info(f"Classification score: {score}")
		category_name = self.weights.meta["categories"][class_id]
		return category_name


class Segmentation(BaseModel):
	def __init__(self, img: torch.Tensor):
		super().__init__(img)
		self.weights = MODEL_PARAMS['segmentation']['weights']

	def run_inference(self) -> torch.Tensor:
		model = MODEL_PARAMS['segmentation']['model'](weights=self.weights)
		model.eval()

		preprocess = self.weights.transforms()
		batch = preprocess(self.img).unsqueeze(0)

		prediction = model(batch)["out"]
		normalized_masks = prediction.softmax(dim=1)
		class_to_idx = {cls: idx for (idx, cls) in enumerate(self.weights.meta["categories"])}
		mask = normalized_masks[0, class_to_idx["person"]]
		return mask


class ObjectDetector(BaseModel):
	def __init__(self, img: torch.Tensor):
		super().__init__(img)
		self.weights = MODEL_PARAMS['detection']['weights']

	def run_inference(self) -> torch.Tensor:
		model = MODEL_PARAMS['detection']['model'](weights=self.weights, box_score_thresh=0.9)
		model.eval()
		preprocess = self.weights.transforms()

		batch = [preprocess(self.img)]

		prediction = model(batch)[0]
		labels = [self.weights.meta["categories"][i] for i in prediction["labels"]]
		box = draw_bounding_boxes(self.img, boxes=prediction["boxes"],
								  labels=labels,
								  colors="red",
								  width=4, font_size=30)
		im = to_pil_image(box.detach())
		return im
