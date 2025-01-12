from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from ocr_processor import OCRProcessor, OCRResult
from qr_processor import QRProcessor, QRResult
import os

@dataclass
class ProcessingResult:
    ocr_result: Optional[OCRResult] = None
    qr_result: Optional[QRResult] = None
    success: bool = True
    error_message: Optional[str] = None

class InvoiceProcessor:
    def __init__(self):
        self.ocr_processor = OCRProcessor()
        self.qr_processor = QRProcessor()
        
    def process_file(self, image_path: str) -> ProcessingResult:
        result = ProcessingResult()
        
        # Process OCR
        ocr_result = self.ocr_processor.process_image(image_path)
        result.ocr_result = ocr_result
        
        # Process QR
        qr_result = self.qr_processor.process_image(image_path)
        result.qr_result = qr_result
        
        # Determine overall success
        result.success = ocr_result.success and qr_result.success
        
        # Collect error messages
        errors = []
        if not ocr_result.success and ocr_result.error_message:
            errors.append(f"OCR Error: {ocr_result.error_message}")
        if not qr_result.success and qr_result.error_message:
            errors.append(f"QR Error: {qr_result.error_message}")
            
        if errors:
            result.error_message = "; ".join(errors)
            
        return result

    def process_folder(self, folder_path: str) -> Tuple[Dict[str, ProcessingResult], List[Dict]]:
        results_map = {}
        failed_files = []
        
        try:
            files = [f for f in os.listdir(folder_path) 
                    if not f.startswith('.') and 
                    f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                    
            for filename in files:
                full_path = os.path.join(folder_path, filename)
                print(f"\nProcessing: {filename}")
                
                result = self.process_file(full_path)
                
                # Use invoice number from either OCR or QR as key
                invoice_number = (result.ocr_result.invoice_number if result.ocr_result else None) or \
                               (result.qr_result.receipt_number if result.qr_result else None)
                
                if invoice_number and result.success:
                    results_map[invoice_number] = result
                else:
                    failed_files.append({
                        'filename': filename,
                        'reason': result.error_message or "Unknown error"
                    })
                    
            return results_map, failed_files
            
        except Exception as e:
            return results_map, [{'filename': folder_path, 'reason': f"Error accessing folder: {str(e)}"}]