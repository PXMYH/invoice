from paddleocr import PaddleOCR, draw_ocr
import cv2
import re
from typing import List, Dict, Tuple

def process_ocr_result(raw_result):
    # Initialize lists to store separated components
    bboxes = []
    texts = []
    confidences = []
    
    # Process each detection in the result and filter by confidence
    for detection in raw_result[0]:
        bbox = detection[0] # First element is bbox coordinates
        text = detection[1][0] # First element of second tuple is extracted text
        confidence = detection[1][1] # Second element of second tuple is confidence
        
        # Only include results with confidence >= 0.85
        if confidence >= 0.85:
            bboxes.append(bbox)
            texts.append(text)
            confidences.append(confidence)
    
    return bboxes, texts, confidences

def extract_number_from_text(text: str) -> float:
    """Extract number from text, handling both integer and decimal formats"""
    # Remove any spaces from the text first
    text = text.replace(' ', '')
    
    # If the text starts with any form of RMB symbol, remove it before extracting the number
    if any(text.startswith(symbol) for symbol in ['¥', '￥', 'Y']):
        text = text[1:]
    
    number_match = re.search(r'\d+\.?\d*', text)
    if number_match:
        return float(number_match.group())
    return None

def is_valid_amount_pair(amount1: float, amount2: float) -> bool:
    """
    Check if two amounts have a valid relationship for amount/tax pairs.
    Valid range is when smaller amount is between 3% and 50% of larger amount.
    """
    if amount1 == 0 or amount2 == 0:
        return False
        
    larger = max(amount1, amount2)
    smaller = min(amount1, amount2)
    percentage = (smaller / larger) * 100

    # Check if percentage falls within valid range (3% to 50%)
    return 3 <= percentage <= 50

def find_best_amount_tax_pair(amounts: List[float]) -> Tuple[float, float]:
    """
    Take only the first two amounts found and check if they form a valid pair.
    Returns (amount, tax) tuple, or (None, None) if no valid pair found.
    """
    if len(amounts) < 2:
        return None, None

    # Only take first two amounts
    first_two = amounts[:2]
    
    if is_valid_amount_pair(first_two[0], first_two[1]):
        larger = max(first_two[0], first_two[1])
        smaller = min(first_two[0], first_two[1])
        return larger, smaller
    
    return None, None

def extract_invoice_data(texts: List[str], confidences: List[float]) -> Dict:
    result_map = {}
    potential_amounts = []
    
    # Find invoice number (发票号码)
    for i, text in enumerate(texts):
        if '发票号码' in text:
            number_match = re.search(r'\d+', text)
            if number_match:
                result_map['invoice_number'] = number_match.group()
                break
    
    # First pass: collect all amounts with RMB symbols
    for i, text in enumerate(texts):
        text = text.strip()
        print(f"Processing text: {text}")
        
        if any(text.startswith(symbol) for symbol in ['¥', '￥', 'Y']):
            print(f"Found amount text: {text}")
            amount = extract_number_from_text(text)
            if amount is not None:
                print(f"Extracted amount: {amount}")
                potential_amounts.append(amount)

    # Second pass: find nearby numbers that could be tax amounts
    for i, text in enumerate(texts):
        text = text.strip()
        # Skip texts that start with RMB symbols
        if any(text.startswith(symbol) for symbol in ['¥', '￥', 'Y']):
            continue
            
        amount = extract_number_from_text(text)
        if amount is not None:
            potential_amounts.append(amount)
            print(f"Found potential tax amount: {amount}")

    print(f"All potential amounts found: {potential_amounts}")
    
    # Find the best amount/tax pair
    if potential_amounts:
        amount, tax = find_best_amount_tax_pair(potential_amounts)
        if amount is not None and tax is not None:
            result_map['amount'] = amount
            result_map['tax_amount'] = tax
    
    return result_map

# Initialize PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='ch')

# Read image
# img_path = './raw_data/3eea28e4cb243595ff8d0b5671cd3ad7.jpg' # no tax amount found, tax amount decoded is 136 67, therefore marked as invalid, amount is decoded correctly
# img_path = './raw_data/07cb74596eccb66556ebbcf1d02cd8ed.jpg' # ok
# img_path = './raw_data/55d3348ca242446ec0f4d4caddc36ece.jpg' # incorrect tax amount
# img_path = './raw_data/71de01566ca0b5fb23a8b31279e8e47f.jpg' # ok
# img_path = './raw_data/7463ef205bea896c99a5ad2d0078697e.jpg' # ok
img_path = './raw_data/22688c7ae67007e3ce5b83ba3a52c377.jpg' # no tax amount found, tax amount decoded as ￥7261Z Confidence: 0.7562
# img_path = './raw_data/c09c35d3c6fb9cb829bfc66f663af87b.jpg' #ok
# img_path = './raw_data/e06ba400cae7baef5b08aea66e3f8bc5.jpg' # ok
print(f"Image path set to {img_path}")
img = cv2.imread(img_path)
print(f"Loaded receipt image, proceed to OCR ...")

# Perform OCR
raw_result = ocr.ocr(img, cls=True)

# Process results
bboxes, texts, confidences = process_ocr_result(raw_result)

# Print processed results for debugging
print("\nProcessed OCR Results (Confidence >= 85%):")
for i, (text, conf) in enumerate(zip(texts, confidences)):
    print(f"{i+1}. Text: {text:<30} Confidence: {conf:.4f}")

# Extract invoice data
invoice_map = extract_invoice_data(texts, confidences)

# Print final map
print("\nFinal Invoice Map:")
for key, value in invoice_map.items():
    if key == 'invoice_number':
        print(f"Invoice Number: {value}")
    elif key == 'amount':
        print(f"Amount: ¥{value}")
    elif key == 'tax_amount':
        print(f"Tax Amount: ¥{value}")