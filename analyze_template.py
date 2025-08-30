import fitz  # PyMuPDF
import sys
import os

template_path = 'templates/Batpharma-resume.pdf'

try:
    # Open the PDF
    doc = fitz.open(template_path)
    print(f'PDF has {len(doc)} pages')
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # Get page dimensions
        rect = page.rect
        print(f'\nPage {page_num + 1} dimensions: {rect.width} x {rect.height} points')
        
        # Extract all text content
        full_text = page.get_text()
        print("Full text content:")
        print("=" * 50)
        print(full_text)
        print("=" * 50)
        
        # Get all text with coordinates
        text_instances = page.get_text('words')
        print(f'Found {len(text_instances)} text instances')
        
        for i, instance in enumerate(text_instances):
            x0, y0, x1, y1, word, block_no, line_no, word_no = instance
            print(f'Text "{word}" at position ({x0:.1f}, {y0:.1f}) to ({x1:.1f}, {y1:.1f})')
        
        # Check for images
        image_list = page.get_images()
        print(f'Found {len(image_list)} images on page {page_num + 1}')
        
        # Look for potential signature area (bottom right)
        page_height = rect.height
        page_width = rect.width
        bottom_right_area = fitz.Rect(page_width * 0.7, page_height * 0.8, page_width, page_height)
        
        print(f"Bottom right area coordinates: ({page_width * 0.7:.1f}, {page_height * 0.8:.1f}) to ({page_width:.1f}, {page_height:.1f})")
        
        # Check for text in bottom right
        bottom_right_text = page.get_textbox(bottom_right_area)
        if bottom_right_text.strip():
            print(f'Bottom right text: "{bottom_right_text.strip()}"')
        
        # Check for images in bottom right
        for img_idx, img in enumerate(image_list):
            img_rect = page.get_image_bbox(img)
            print(f'Image {img_idx} bbox: {img_rect}')
            if img_rect.intersects(bottom_right_area):
                print(f'Image {img_idx} is in bottom right area!')
    
    doc.close()
    
except Exception as e:
    print(f'Error analyzing PDF: {e}')
    import traceback
    traceback.print_exc()
