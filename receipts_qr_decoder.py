#!/usr/bin/env python3

from pyzbar.pyzbar import decode
from PIL import Image

def scan_qr_code(image_path):
    try:
        # Open and decode QR code
        image = Image.open(image_path)
        decoded_objects = decode(image)
        
        # Return empty if no QR codes found
        if not decoded_objects:
            return "No QR codes found in the image"
        
        # Process results
        results = []
        for obj in decoded_objects:
            qr_data = obj.data.decode('utf-8')
            results.append(qr_data)
            
        return results
        
    except FileNotFoundError:
        return f"Error: Could not find image file: {image_path}"
    except Exception as e:
        return f"Error processing image: {str(e)}"

# Set your image path here
image_path = "./data/receipt1.jpg"  # Replace with your actual image path

# Run the QR code scanner
results = scan_qr_code(image_path)

# Print results
if isinstance(results, list):
    print(f"\nFound {len(results)} QR code(s):")
    for i, data in enumerate(results, 1):
        print(f"\nQR Code #{i}:")
        print(f"Data: {data}")
else:
    print(results)  # Print error message if any