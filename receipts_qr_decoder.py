#!/usr/bin/env python3

from pyzbar.pyzbar import decode
from PIL import Image
import os

def scan_qr_code(image_path):
    try:
        image = Image.open(image_path)
        decoded_objects = decode(image)
        
        if not decoded_objects:
            return None
            
        # We only process the first QR code found
        qr_data = decoded_objects[0].data.decode('utf-8')
        print(f"QR Data: {qr_data}")
        return qr_data
        
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")
        return None

def process_qr_data(qr_data):
    try:
        # Split the QR data by comma
        parts = qr_data.split(',')
        
        # Extract required fields
        receipt_number = parts[3]
        total_amount = float(parts[4])
        receipt_date = parts[5]
        
        return {
            'receipt_number': receipt_number,
            'total_amount': total_amount,
            'receipt_date': receipt_date
        }
    except (IndexError, ValueError) as e:
        print(f"Error parsing QR data: {str(e)}")
        return None

def process_receipts(folder_path):
    # Dictionary to store results
    receipts_map = {}
    # List to store failed files and their reasons
    failed_files = []
    
    # Get list of all files in the directory
    try:
        files = os.listdir(folder_path)
    except Exception as e:
        print(f"Error accessing folder {folder_path}: {str(e)}")
        return receipts_map, failed_files
    
    # Process each file
    for filename in files:
        # Skip hidden files and non-image files
        if filename.startswith('.') or not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue
            
        full_path = os.path.join(folder_path, filename)
        print(f"\nProcessing: {filename}")
        
        # Scan QR code
        qr_data = scan_qr_code(full_path)
        if qr_data is None:
            failed_files.append({
                'filename': filename,
                'reason': 'No QR code found or failed to scan'
            })
            continue
            
        # Process QR data
        receipt_data = process_qr_data(qr_data)
        if receipt_data is None:
            failed_files.append({
                'filename': filename,
                'reason': 'Failed to parse QR data'
            })
            continue
            
        # Store in map
        receipts_map[receipt_data['receipt_number']] = receipt_data
        
    return receipts_map, failed_files

# Process all receipts in the data folder
folder_path = './raw_data'
receipts_map, failed_files = process_receipts(folder_path)

# Print successful results
print("\nProcessed Receipts:")
for receipt_number, data in receipts_map.items():
    print(f"\nReceipt Number: {receipt_number}")
    print(f"Total Amount: {data['total_amount']}")
    print(f"Receipt Date: {data['receipt_date']}")

# Print summary
print(f"\nTotal receipts processed successfully: {len(receipts_map)}")

# Print failed files
if failed_files:
    print("\nFailed to process the following files:")
    for fail in failed_files:
        print(f"File: {fail['filename']}")
        print(f"Reason: {fail['reason']}")
    print(f"\nTotal failed files: {len(failed_files)}")