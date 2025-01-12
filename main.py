from paddleocr import PaddleOCR, draw_ocr
import cv2
import re

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

def extract_number_from_text(text):
    """Extract number from text, handling both integer and decimal formats"""
    number_match = re.search(r'\d+\.?\d*', text)
    print(f"number_match: {number_match}")
    if number_match:
        return float(number_match.group())
    return None

def is_valid_amount_pair(amount1, amount2):
    """Check if two amounts have a valid relationship"""
    if amount1 == 0 or amount2 == 0:
        return False
        
    # Check if one is not 33x bigger than the other, China's lowest tax rate is 3%
    if amount1 > amount2:
        ratio = amount1 / amount2
        if ratio > 33:
            return False
    else:
        ratio = amount2 / amount1
        if ratio > 33:
            return False
    
    # Check if one is not 97% smaller than the other
    smaller = min(amount1, amount2)
    bigger = max(amount1, amount2)
    if smaller < (bigger * 0.03):  # 97% smaller
        return False
        
    return True

def extract_invoice_data(texts, confidences):
    result_map = {}
    
    # Find invoice number (发票号码)
    for i, text in enumerate(texts):
        if '发票号码' in text:
            number_match = re.search(r'\d+', text)
            if number_match:
                invoice_number = number_match.group()
                result_map['invoice_number'] = invoice_number
                break
    
    # Look for amounts from back to front
    for i in range(len(texts)-1, -1, -1):
        text = texts[i]
        current_text = texts[i]
        print(f"current_text: {current_text}")
        
        # Check if text starts with Y or ¥ and contains numbers
        if (text.startswith('Y') or text.startswith('¥')):
            print(f"text starts with Y or ¥: {text}")
            amount = extract_number_from_text(text)
            print(f"amount: {amount}")
            if amount is not None:
                result_map['amount'] = amount
                
                # Check numbers before and after for tax amount
                if i > 0 and i < len(texts) - 1:
                    prev_text = texts[i-1]
                    next_text = texts[i+1]
                    
                    # Extract numbers from adjacent texts
                    prev_amount = extract_number_from_text(prev_text)
                    next_amount = extract_number_from_text(next_text)
                    
                    # Check previous text
                    if prev_amount is not None and not (prev_text.startswith('Y') or prev_text.startswith('¥')):
                        if is_valid_amount_pair(amount, prev_amount):
                            result_map['tax_amount'] = prev_amount
                            break
                            
                    # Check next text
                    if next_amount is not None and not (next_text.startswith('Y') or next_text.startswith('¥')):
                        if is_valid_amount_pair(amount, next_amount):
                            result_map['tax_amount'] = next_amount
                            break
    
    return result_map

# Initialize PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='ch')

# Read image
# img_path = './data/receipt5.jpg'
img_path = './raw_data/07cb74596eccb66556ebbcf1d02cd8ed.jpg'
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
        print(f"Amount: {value}")
    elif key == 'tax_amount':
        print(f"Tax Amount: {value}")