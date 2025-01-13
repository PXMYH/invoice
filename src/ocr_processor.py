from paddleocr import PaddleOCR
import cv2
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class OCRResult:
    invoice_number: Optional[str] = None
    amount: Optional[float] = None
    tax_amount: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None

class OCRProcessor:
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, lang='ch')
        
    def process_ocr_result(self, raw_result) -> Tuple[List, List, List]:
        bboxes, texts, confidences = [], [], []
        
        for detection in raw_result[0]:
            bbox, (text, confidence) = detection[0], detection[1]
            
            if confidence >= 0.85:
                bboxes.append(bbox)
                texts.append(text)
                confidences.append(confidence)
        
        return bboxes, texts, confidences

    def extract_number_from_text(self, text: str) -> Optional[float]:
        text = text.replace(' ', '')
        
        if any(text.startswith(symbol) for symbol in ['¥', '￥', 'Y']):
            text = text[1:]
        
        number_match = re.search(r'\d+\.?\d*', text)
        return float(number_match.group()) if number_match else None

    def is_valid_amount_pair(self, amount1: float, amount2: float) -> bool:
        if amount1 == 0 or amount2 == 0:
            return False
            
        larger = max(amount1, amount2)
        smaller = min(amount1, amount2)
        percentage = (smaller / larger) * 100
        
        return 3 <= percentage <= 50

    def find_best_amount_tax_pair(self, amounts: List[float]) -> Tuple[Optional[float], Optional[float]]:
        if len(amounts) < 2:
            return None, None

        first_two = amounts[:2]
        
        if self.is_valid_amount_pair(first_two[0], first_two[1]):
            larger = max(first_two[0], first_two[1])
            smaller = min(first_two[0], first_two[1])
            return larger, smaller
        
        return None, None

    def process_image(self, image_path: str) -> OCRResult:
        try:
            img = cv2.imread(image_path)
            print("Processing image: ", image_path)
            if img is None:
                return OCRResult(success=False, error_message=f"Failed to load image: {image_path}")

            raw_result = self.ocr.ocr(img, cls=True)
            print("Raw OCR result: ", raw_result)
            bboxes, texts, confidences = self.process_ocr_result(raw_result)
            
            result = OCRResult()
            potential_amounts = []
            
            # Find invoice number
            for text in texts:
                if '发票号码' in text:
                    number_match = re.search(r'\d+', text)
                    if number_match:
                        result.invoice_number = number_match.group()
                        break
            
            # Collect amounts
            for text in texts:
                text = text.strip()
                if any(text.startswith(symbol) for symbol in ['¥', '￥', 'Y']):
                    amount = self.extract_number_from_text(text)
                    if amount is not None:
                        potential_amounts.append(amount)

            # Find tax amounts
            for text in texts:
                text = text.strip()
                if not any(text.startswith(symbol) for symbol in ['¥', '￥', 'Y']):
                    amount = self.extract_number_from_text(text)
                    if amount is not None:
                        potential_amounts.append(amount)

            # Find best amount/tax pair
            if potential_amounts:
                amount, tax = self.find_best_amount_tax_pair(potential_amounts)
                result.amount = amount
                result.tax_amount = tax
                
                if amount is None or tax is None:
                    result.error_message = "Could not find valid amount/tax pair"
            else:
                result.error_message = "No amounts found in the image"

            result.success = bool(result.amount and result.tax_amount)
            return result
            
        except Exception as e:
            return OCRResult(success=False, error_message=str(e))