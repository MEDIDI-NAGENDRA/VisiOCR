import cv2
import numpy as np
from django.core.files.uploadedfile import InMemoryUploadedFile

def decode_qr(image):
    """
    Decodes a QR code image and returns the extracted text.

    Args:
        image: An image file containing a QR code.

    Returns:
        A string of the decoded text if successful, or None if not.
    """
    try:
        # Convert the image to a NumPy array
        img_array = np.frombuffer(image.read(), np.uint8)
        
        # Read the image using OpenCV
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        # Initialize the QRCode detector
        detector = cv2.QRCodeDetector()
        
        # Detect and decode the QR code
        data, vertices_array, _ = detector.detectAndDecode(img)
        
        if vertices_array is not None:
            print(f"QR Code Data: {data}")  # Debugging log
            return data
        else:
            print("No QR code detected.")  # Debugging log
            return None
    except Exception as e:
        print(f"Error decoding QR code: {e}")
        return None

