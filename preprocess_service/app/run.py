from fastapi import FastAPI, UploadFile
from fastapi.responses import StreamingResponse
from PIL import Image
from io import BytesIO
import uvicorn
from preprocessing import process_img
from utils import logger


app = FastAPI()


@app.post("/recieve_transform")
async def receive_transform(image: UploadFile):
    try:
        logger('Image received to be transformed.')
        pil_image = Image.open(BytesIO(image.file.read()))
        inference_img = process_img(pil_image)

        logger('Image transformation complete.')
        processed_image_buffer = BytesIO()
        inference_img.save(processed_image_buffer, format="JPEG")
        processed_image_buffer.seek(0)

        return StreamingResponse(processed_image_buffer, media_type="image/jpeg")
    except Exception as e:
        return {"Error": f"Failed to process image {e}"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == '__main__':
    uvicorn.run('run:app', host="0.0.0.0", port=5002)