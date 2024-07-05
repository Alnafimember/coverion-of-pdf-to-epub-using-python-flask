import os
import io
from flask import Flask, send_file
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF
from ebooklib import epub
from PIL import Image

app = Flask(__name__)

@app.route('/api/convert_file/<file>', methods=['GET'])
def convert_pdf_to_epub_api(file):
    # Ensure the file name is secure
    file = secure_filename(file)

    # Paths for the PDF and EPUB files
    pdf_path = os.path.join(app.root_path, 'static', file)
    epub_path = os.path.join(app.root_path, 'static', os.path.splitext(file)[0] + '.epub')

    # Open the PDF document
    try:
        doc = fitz.open(pdf_path)
    except FileNotFoundError:
        return "Error: PDF file not found!", 404
    except Exception as e:
        return f"Error: {e}", 500

    # Create a new EPUB book
    book = epub.EpubBook()
    book.set_title(os.path.splitext(os.path.basename(pdf_path))[0])
    book.set_language('en')
    book.add_author("Converted by Python Script")

    # Initialize a variable to track if any content was added
    content_added = False
    chapters = []

    # Process each page in the PDF document
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")

        # Replace newlines with <br> tags and wrap paragraphs with <p> tags
        formatted_text = ""
        for line in text.split('\n'):
            if line.strip():
                formatted_text += f"<p>{line.strip()}</p>"

        images = page.get_images(full=True)

        # Check if there is any meaningful content on the page
        if formatted_text or images:
            content_added = True

            # Create chapter content with text and images
            chapter_content = f"""
            <!DOCTYPE html>
            <html>
              <head>
                <title>Page {page_num + 1}</title>
              </head>
              <body>
                {formatted_text}
            """

            # Add images to chapter content and also add images to the book
            for img_index, img in enumerate(images):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image_filename = f"image_{page_num + 1}_{img_index}.{image_ext}"
                image_path = os.path.join(app.root_path, 'static', image_filename)

                # Use Pillow to correctly save the image
                image = Image.open(io.BytesIO(image_bytes))
                image.save(image_path)

                # Add image to chapter content
                chapter_content += f'<img src="{image_filename}" alt="Image {img_index + 1}"/>'

                # Add image to EPUB book
                image_item = epub.EpubItem(file_name=image_filename, media_type=f"image/{image_ext}", content=image_bytes)
                book.add_item(image_item)

            chapter_content += "</body></html>"

            # Create a chapter
            chapter_title = f'Page {page_num + 1}'
            chapter_filename = f'page_{page_num + 1}.xhtml'
            chapter = epub.EpubHtml(title=chapter_title, file_name=chapter_filename, lang='en')
            chapter.content = chapter_content

            # Add chapter to the book
            book.add_item(chapter)
            chapters.append(chapter)

    # Check if any content was added to the book
    if not content_added:
        return "Error: No content found in the PDF!", 500

    # Define Table Of Contents
    book.toc = tuple(epub.Link(chapter.file_name, chapter.title, chapter.file_name) for chapter in chapters)

    # Add default NCX and Nav file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Define CSS style
    style = '''
    @namespace epub "http://www.idpf.org/2007/ops";
    body { font-family: Cambria, Liberation Serif, serif; }
    h1 { text-align: left; text-transform: uppercase; font-weight: 200; }
    img { max-width: 100%; height: auto; } /* Ensure images fit within the reader's screen */
    '''
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)

    # Add CSS file
    book.add_item(nav_css)

    # Basic spine
    book.spine = ['nav'] + chapters

    # Write the EPUB book to file
    epub.write_epub(epub_path, book, {})

    return send_file(epub_path, as_attachment=True, download_name=os.path.basename(epub_path))

if __name__ == '__main__':
    app.run(debug=True)

# import os
# import io
# from flask import Flask, send_file
# from werkzeug.utils import secure_filename
# import fitz  # PyMuPDF
# from ebooklib import epub
# from PIL import Image
# import pytesseract
# import cv2
# import numpy as np
#
# app = Flask(__name__)
#
# def preprocess_image(image_path):
#     # Load the image using OpenCV
#     image_cv = cv2.imread(image_path)
#
#     # Convert to grayscale
#     gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
#
#     # Apply noise removal with a Gaussian filter
#     gray = cv2.GaussianBlur(gray, (5, 5), 0)
#
#     # Apply thresholding to preprocess the image
#     _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
#
#     # Apply dilation and erosion to remove noise further
#     kernel = np.ones((1, 1), np.uint8)
#     thresh = cv2.dilate(thresh, kernel, iterations=1)
#     thresh = cv2.erode(thresh, kernel, iterations=1)
#
#     # Save the preprocessed image to a temporary file
#     preprocessed_image_path = "/mnt/data/preprocessed_image_enhanced.png"
#     cv2.imwrite(preprocessed_image_path, thresh)
#
#     return preprocessed_image_path
#
# @app.route('/api/convert_file/<file>', methods=['GET'])
# def convert_pdf_to_epub_api(file):
#     # Ensure the file name is secure
#     file = secure_filename(file)
#
#     # Paths for the PDF and EPUB files
#     pdf_path = os.path.join(app.root_path, 'static', file)
#     epub_path = os.path.join(app.root_path, 'static', os.path.splitext(file)[0] + '.epub')
#
#     # Open the PDF document
#     try:
#         doc = fitz.open(pdf_path)
#     except FileNotFoundError:
#         return "Error: PDF file not found!", 404
#     except Exception as e:
#         return f"Error: {e}", 500
#
#     # Create a new EPUB book
#     book = epub.EpubBook()
#     book.set_title(os.path.splitext(os.path.basename(pdf_path))[0])
#     book.set_language('en')
#     book.add_author("Converted by Python Script")
#
#     # Initialize a variable to track if any content was added
#     content_added = False
#     chapters = []
#
#     # Process each page in the PDF document
#     for page_num in range(len(doc)):
#         page = doc.load_page(page_num)
#         text = page.get_text("text")
#
#         # Replace newlines with <br> tags and wrap paragraphs with <p> tags
#         formatted_text = ""
#         for line in text.split('\n'):
#             if line.strip():
#                 formatted_text += f"<p>{line.strip()}</p>"
#
#         images = page.get_images(full=True)
#
#         # Check if there is any meaningful content on the page
#         if formatted_text or images:
#             content_added = True
#
#             # Create chapter content with text and images
#             chapter_content = f"""
#             <!DOCTYPE html>
#             <html>
#               <head>
#                 <title>Page {page_num + 1}</title>
#               </head>
#               <body>
#                 {formatted_text}
#             """
#
#             # Add images to chapter content and also add images to the book
#             for img_index, img in enumerate(images):
#                 xref = img[0]
#                 base_image = doc.extract_image(xref)
#                 image_bytes = base_image["image"]
#                 image_ext = base_image["ext"]
#                 image_filename = f"image_{page_num + 1}_{img_index}.{image_ext}"
#                 image_path = os.path.join(app.root_path, 'static', image_filename)
#
#                 # Use Pillow to correctly save the image
#                 image = Image.open(io.BytesIO(image_bytes))
#                 image.save(image_path)
#
#                 # Add image to chapter content
#                 chapter_content += f'<img src="{image_filename}" alt="Image {img_index + 1}"/>'
#
#                 # Add image to EPUB book
#                 image_item = epub.EpubItem(file_name=image_filename, media_type=f"image/{image_ext}", content=image_bytes)
#                 book.add_item(image_item)
#
#             chapter_content += "</body></html>"
#
#             # Create a chapter
#             chapter_title = f'Page {page_num + 1}'
#             chapter_filename = f'page_{page_num + 1}.xhtml'
#             chapter = epub.EpubHtml(title=chapter_title, file_name=chapter_filename, lang='en')
#             chapter.content = chapter_content
#
#             # Add chapter to the book
#             book.add_item(chapter)
#             chapters.append(chapter)
#
#     # Check if any content was added to the book
#     if not content_added:
#         return "Error: No content found in the PDF!", 500
#
#     # Define Table Of Contents
#     book.toc = tuple(epub.Link(chapter.file_name, chapter.title, chapter.file_name) for chapter in chapters)
#
#     # Add default NCX and Nav file
#     book.add_item(epub.EpubNcx())
#     book.add_item(epub.EpubNav())
#
#     # Define CSS style
#     style = '''
#     @namespace epub "http://www.idpf.org/2007/ops";
#     body { font-family: Cambria, Liberation Serif, serif; }
#     h1 { text-align: left; text-transform: uppercase; font-weight: 200; }
#     img { max-width: 100%; height: auto; } /* Ensure images fit within the reader's screen */
#     '''
#     nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
#
#     # Add CSS file
#     book.add_item(nav_css)
#
#     # Basic spine
#     book.spine = ['nav'] + chapters
#
#     # Write the EPUB book to file
#     epub.write_epub(epub_path, book, {})
#
#     return send_file(epub_path, as_attachment=True, download_name=os.path.basename(epub_path))
#
# if __name__ == '__main__':
#     app.run(debug=True)
