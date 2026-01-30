
import face_recognition
import cv2
import numpy as np

print("Imports successful")

try:
    # Create a blank image
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    # This should not fail if library is installed
    encodings = face_recognition.face_encodings(img)
    print("face_recognition.face_encodings called successfully")
except Exception as e:
    print(f"Error: {e}")
