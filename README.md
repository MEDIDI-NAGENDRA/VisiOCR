# VisiOCR Project

This project involves extracting and validating information from AADHAR or PAN documents using OCR (Optical Character Recognition) and storing validated data into a MySQL database.

**⦿ Requirements**

• Python 3.x

• OpenCV

• Tesseract-OCR

• pytesseract

• PIL (Pillow)

• NumPy

• MySQL Connector

• MySQL Server


**⦿ Installation**
1. Install Tesseract-OCR from here (https://github.com/tesseract-ocr/tesseract).


2. Install the required Python packages:
   
   pip install opencv-python pytesseract pillow numpy mysql-connector-python


4. Set the path to the Tesseract executable in your code:
   
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Adjust as necessary


6. Set up MySQL Server and create a database named `VisiOCR`.


**⦿ Usage**

1. Clone the repository:
   
   git clone https://github.com/MEDIDI-NAGENDRA/VisiOCR.git


3. Navigate to the project directory:
   
   cd VisiOCR


5. Run the main script:
   
   python main.py

**⦿ License**

This project is licensed under the MIT License. See the LICENSE file for details.
