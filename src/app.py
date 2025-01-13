# app.py

import streamlit as st
import os
import tempfile
from invoice_processor import InvoiceProcessor
from typing import List

# Initialize the InvoiceProcessor at startup, outside the main flow
@st.cache_resource
def get_invoice_processor():
    return InvoiceProcessor()

def save_uploaded_files(uploaded_files) -> List[str]:
    """Save uploaded files to temporary directory and return their paths"""
    temp_dir = tempfile.mkdtemp()
    file_paths = []
    
    for uploaded_file in uploaded_files:
        # Create a temporary file path
        temp_path = os.path.join(temp_dir, uploaded_file.name)
        
        # Save uploaded file
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            st.write(f"Saved file: {os.path.basename(temp_path)}")
            
        file_paths.append(temp_path)
    
    return temp_dir, file_paths

def main():
    st.title("Invoice Processing System")
    st.write("Upload invoice images to extract information using OCR and QR codes.")

    # Get the processor instance
    processor = get_invoice_processor()

    # File uploader
    uploaded_files = st.file_uploader(
        "Choose invoice images", 
        accept_multiple_files=True,
        type=['png', 'jpg', 'jpeg']
    )

    if uploaded_files:
        # Save uploaded files to temporary directory
        temp_dir, file_paths = save_uploaded_files(uploaded_files)
        
        # Process the files
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Process each file
        for idx, file_path in enumerate(file_paths):
            status_text.write(f"Processing: {os.path.basename(file_path)}")
            result = processor.process_file(file_path)
            results.append((os.path.basename(file_path), result))
            progress_bar.progress((idx + 1) / len(file_paths))

        status_text.empty()
        progress_bar.empty()

        # Display results
        st.header("Processing Results")
        
        # Create tabs for Success and Failures
        tab1, tab2 = st.tabs(["Successful", "Failed"])
        
        with tab1:
            successful = [(f, r) for f, r in results if r.success]
            if successful:
                for filename, result in successful:
                    with st.expander(f"📄 {filename}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("OCR Results")
                            if result.ocr_result:
                                st.write(f"Invoice Number: {result.ocr_result.invoice_number}")
                                st.write(f"Amount: ¥{result.ocr_result.amount}")
                                st.write(f"Tax Amount: ¥{result.ocr_result.tax_amount}")
                            
                        with col2:
                            st.subheader("QR Code Results")
                            if result.qr_result:
                                st.write(f"Receipt Number: {result.qr_result.receipt_number}")
                                st.write(f"Total Amount: ¥{result.qr_result.total_amount}")
                                st.write(f"Date: {result.qr_result.receipt_date}")
            else:
                st.info("No successfully processed invoices")

        with tab2:
            failed = [(f, r) for f, r in results if not r.success]
            if failed:
                for filename, result in failed:
                    with st.expander(f"❌ {filename}"):
                        st.error(result.error_message)
            else:
                st.success("No failed invoices!")

        # Cleanup temporary files
        import shutil
        shutil.rmtree(temp_dir)

        # Show summary
        st.header("Summary")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Successfully Processed", len([r for f, r in results if r.success]))
        with col2:
            st.metric("Failed", len([r for f, r in results if not r.success]))

if __name__ == "__main__":
    main()