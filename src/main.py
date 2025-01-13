from invoice_processor import InvoiceProcessor

def main():
    processor = InvoiceProcessor()
    folder_path = './data'
    
    print(f"Processing invoices in folder: {folder_path}")
    results_map, failed_files = processor.process_folder(folder_path)
    
    # Print successful results
    print("\nProcessed Invoices:")
    for invoice_number, result in results_map.items():
        print(f"\nInvoice Number: {invoice_number}")
        if result.ocr_result:
            print(f"OCR Amount: {result.ocr_result.amount}")
            print(f"OCR Tax Amount: {result.ocr_result.tax_amount}")
        if result.qr_result:
            print(f"QR Total Amount: {result.qr_result.total_amount}")
            print(f"QR Date: {result.qr_result.receipt_date}")
    
    # Print summary
    print(f"\nTotal invoices processed successfully: {len(results_map)}")
    
    # Print failed files
    if failed_files:
        print("\nFailed to process the following files:")
        for fail in failed_files:
            print(f"File: {fail['filename']}")
            print(f"Reason: {fail['reason']}")
        print(f"\nTotal failed files: {len(failed_files)}")

if __name__ == "__main__":
    main()