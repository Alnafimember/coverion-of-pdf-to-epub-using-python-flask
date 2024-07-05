#PDF to EPUB Converter with Flask
This project is a web application built with Flask that allows users to convert PDF documents into EPUB format. 
The conversion utilizes PyPDF2 for parsing the PDF files and ebooklib for creating the EPUB files.

Features
Upload PDF files through a web interface
Convert uploaded PDFs to EPUB format
Download the converted EPUB files

---------------------------------

Installation
Clone the repository:
git clone https://github.com/your-username/pdf-to-epub-flask.git
cd pdf-to-epub-flask
Create a virtual environment and activate it:

----------------------------------

python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
Install the required dependencies:

----------------------------------

pip install -r requirements.txt
Usage
Run the Flask application:

----------------------------------

flask run
Open your web browser and go to http://127.0.0.1:5000/

Upload a PDF file and download the converted EPUB file.
