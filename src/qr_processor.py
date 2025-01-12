from pyzbar.pyzbar import decode
from PIL import Image
from dataclasses import dataclass
from typing import Optional

@dataclass
class QRResult:
    receipt_number: Optional[str] = None
    total_amount: Optional[float] = None
    receipt_date: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None

class QRProcessor:
    def scan_qr_code(self, image_path: str) -> Optional[str]:
        try:
            image = Image.open(image_path)
            decoded_objects = decode(image)
            
            if not decoded_objects:
                return None
                
            return decoded_objects[0].data.decode('utf-8')
            
        except Exception as e:
            raise Exception(f"Error scanning QR code: {str(e)}")

    def process_qr_data(self, qr_data: str) -> QRResult:
        try:
            parts = qr_data.split(',')
            
            return QRResult(
                receipt_number=parts[3],
                total_amount=float(parts[4]),
                receipt_date=parts[5]
            )
        except (IndexError, ValueError) as e:
            return QRResult(success=False, error_message=f"Error parsing QR data: {str(e)}")

    def process_image(self, image_path: str) -> QRResult:
        try:
            qr_data = self.scan_qr_code(image_path)
            if qr_data is None:
                return QRResult(success=False, error_message="No QR code found or failed to scan")
                
            return self.process_qr_data(qr_data)
            
        except Exception as e:
            return QRResult(success=False, error_message=str(e))