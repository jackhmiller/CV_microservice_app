import uvicorn
from io import BytesIO
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
import torchvision.transforms as transforms
from model import do_inference_task
from PIL import Image
import httpx
import uuid
import requests
import os
from psycopg2 import OperationalError
from utils import logger, write_to_db, allowed_file, DatabaseConnection

app = FastAPI()
PREPROCESSING_URL = "http://localhost:5002/recieve_transform"
DB_URL = f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@postgres-service:5432/{os.environ['POSTGRES_DB']}"


@app.post("/inference")
async def inference(image: UploadFile, task: str):
	image_id = uuid.uuid4().hex
	if not allowed_file(image.filename):
		return {"error""": "This file type is not allowed"}
	try:
		response = requests.post(PREPROCESSING_URL, files={'image': image.file, 'filename': image.filename})
		if response.status_code == 200:
			write_to_db(DB_URL, image.filename, image_id, task, 'passed')
			logger.info("Image sent and processed successfully")
			image = Image.open(BytesIO(response.content))
			prediction = do_inference_task(task=task,
										   img=image)

			if task != 'classification':
				prediction_PIL = transforms.ToPILImage()(prediction)
				image_prediction_buffer = BytesIO()
				prediction_PIL.save(image_prediction_buffer, format="JPEG")
				image_prediction_buffer.seek(0)

				return StreamingResponse(image_prediction_buffer, media_type="image/jpeg")
			else:
				return JSONResponse(content=prediction)
	except Exception as e:
		write_to_db(DB_URL, image.filename, image_id, task, 'failed')
		return {"Error": f"Failed to process image or perform inference {e}"}


def check_database():
	"""
	Database health check
	"""
	try:
		DatabaseConnection(DB_URL)
		return True
	except OperationalError:
		return False


async def check_external_service():
	"""
	Check to make sure the image processing service is running.
	"""
	async with httpx.AsyncClient() as client:
		try:
			response = await client.get(PREPROCESSING_URL)
			return response.status_code == 200
		except httpx.RequestError:
			return False

	
@app.get("/health")
async def health_check():
	"""
	Health/liveness check of the service and its corresponding dependencies.
	"""
	database_status = check_database()
	external_service_status = await check_external_service()
	if external_service_status and database_status:
		return {"status": "ok"}
	else:
		details = []
		if not database_status:
			details.append("Database is not healthy")
		if not external_service_status:
			details.append("Image processing service is not healthy")

		raise HTTPException(status_code=503, detail={"status": "error", "details": details})


if __name__ == "__main__":
	uvicorn.run('run:app', host="0.0.0.0", port=5001)