# api.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .invoice_processor import InvoiceProcessor  # Changed to relative import
import tempfile
import os
from typing import List
import shutil
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Invoice Processing API",
    description="API for processing invoices using OCR and QR codes",
    version="1.0.0"
)

# Add this after creating the FastAPI app
# app.mount("/static", StaticFiles(directory="./src/static"), name="static")
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def read_root():
    return FileResponse(static_dir + "/index.html")


# Initialize the processor once at startup
processor = InvoiceProcessor()

class QRResponse(BaseModel):
    receipt_number: str | None
    total_amount: float | None
    receipt_date: str | None

class OCRResponse(BaseModel):
    invoice_number: str | None
    amount: float | None
    tax_amount: float | None

class ProcessingResponse(BaseModel):
    filename: str
    success: bool
    error_message: str | None
    ocr_result: OCRResponse | None
    qr_result: QRResponse | None
    processed_at: datetime

@app.post("/process-invoices/", response_model=List[ProcessingResponse])
async def process_invoices(files: List[UploadFile] = File(...)):
    """
    Process multiple invoice images and extract information using OCR and QR codes.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    results = []

    try:
        # Save and process each file
        for upload_file in files:
            temp_path = os.path.join(temp_dir, upload_file.filename)
            
            # Save uploaded file
            with open(temp_path, "wb") as f:
                contents = await upload_file.read()
                f.write(contents)

            # Process the file
            result = processor.process_file(temp_path)
            
            # Convert to response model
            processing_response = ProcessingResponse(
                filename=upload_file.filename,
                success=result.success,
                error_message=result.error_message,
                processed_at=datetime.now(),
                ocr_result=OCRResponse(
                    invoice_number=result.ocr_result.invoice_number,
                    amount=result.ocr_result.amount,
                    tax_amount=result.ocr_result.tax_amount
                ) if result.ocr_result else None,
                qr_result=QRResponse(
                    receipt_number=result.qr_result.receipt_number,
                    total_amount=result.qr_result.total_amount,
                    receipt_date=result.qr_result.receipt_date
                ) if result.qr_result else None
            )
            
            results.append(processing_response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Cleanup temporary files
        shutil.rmtree(temp_dir)

    return results

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "healthy", "timestamp": datetime.now()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9845)