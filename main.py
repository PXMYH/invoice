from paddleocr import PaddleOCR, draw_ocr
import cv2
import re

def process_ocr_result(raw_result):
    # Initialize lists to store separated components
    bboxes = []
    texts = []
    confidences = []
    
    # Process each detection in the result
    for detection in raw_result[0]:
        bbox = detection[0]  # First element is bbox coordinates
        text = detection[1][0]  # First element of second tuple is text
        confidence = detection[1][1]  # Second element of second tuple is confidence
        
        bboxes.append(bbox)
        texts.append(text)
        confidences.append(confidence)
    
    return bboxes, texts, confidences

def extract_invoice_data(texts, confidences):
    result_map = {}
    
    # Find invoice number (发票号码)
    for i, text in enumerate(texts):
        if '发票号码' in text:
            # Extract the number using regex
            number_match = re.search(r'\d+', text)
            if number_match:
                invoice_number = number_match.group()
                result_map[invoice_number] = None
                break
    
    # Look for amount from back to front
    for i in range(len(texts)-1, -1, -1):
        text = texts[i]
        confidence = confidences[i]
        
        # Check if confidence meets threshold
        if confidence < 0.85:
            continue
            
        # Check if text starts with Y or ¥ and contains numbers
        if (text.startswith('Y') or text.startswith('¥')):
            # Extract number using regex
            number_match = re.search(r'\d+\.?\d*', text)
            if number_match:
                amount = float(number_match.group())
                # Update the map with the first matching amount found
                if invoice_number in result_map:
                    result_map[invoice_number] = amount
                    break
    
    return result_map

# Initialize PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='ch')

# Read image
# img_path = './data/receipt5.jpg'
img_path = './raw_data/3eea28e4cb243595ff8d0b5671cd3ad7.jpg'
print(f"Image path set to {img_path}")
img = cv2.imread(img_path)
print(f"Loaded receipt image, proceed to OCR ...")

# Perform OCR
raw_result = ocr.ocr(img, cls=True)

# Process results
bboxes, texts, confidences = process_ocr_result(raw_result)

# Print processed results for debugging
print("\nProcessed OCR Results:")
for i, (text, conf) in enumerate(zip(texts, confidences)):
    print(f"{i+1}. Text: {text:<30} Confidence: {conf:.4f}")

# Extract invoice data
invoice_map = extract_invoice_data(texts, confidences)

# Print final map
print("\nFinal Invoice Map:")
for invoice_num, amount in invoice_map.items():
    print(f"Invoice Number: {invoice_num}")
    print(f"Amount: {amount}")