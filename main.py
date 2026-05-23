from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
from omr_engine import process_omr_answers
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="OMR REST API Microservice")

# Allow CORS if called from frontend (e.g. PHP CodeIgniter)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/scan-ljk")
async def scan_ljk(
    file: UploadFile = File(...),
    id_peserta: str = Form(default=""),
    program_studi: str = Form(default=""),
    waktu_kuliah: str = Form(default="")
):
    try:
        # 1. Read file into numpy array
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image file")

        logger.info(f"Processing image {file.filename} for peserta {id_peserta}")

        # 2. Process answers using OMR engine
        jawaban = process_omr_answers(image)
        
        # 3. Return formatted JSON response
        return {
            "status": "success",
            "data_peserta": {
                "nomor_peserta": id_peserta,
                "program_studi": program_studi,
                "waktu_kuliah": waktu_kuliah
            },
            "jawaban": jawaban
        }
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "OMR Microservice is running. Send POST request to /api/v1/scan-ljk"}
