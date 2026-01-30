import face_recognition
import cv2
import numpy as np
import librosa
from scipy.spatial.distance import cosine

def get_face_encoding(image_path):
    """Load an image and return the face encoding."""
    try:
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        if len(encodings) > 0:
            return encodings[0]
        return None
    except Exception as e:
        print(f"Error encoding face: {e}")
        return None

def verify_face(registered_img_path, live_image_bytes):
    """Compare a registered image with a live captured image."""
    reg_encoding = get_face_encoding(registered_img_path)
    if reg_encoding is None:
        return False, "Registered face not found/encoded"

    # Convert bytes to cv2 image
    try:
        nparr = np.frombuffer(live_image_bytes, np.uint8)
        live_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if live_img is None:
            return False, "Failed to decode live image"

        live_img_rgb = cv2.cvtColor(live_img, cv2.COLOR_BGR2RGB)
        live_encodings = face_recognition.face_encodings(live_img_rgb)
        
        if len(live_encodings) == 0:
            return False, "No face detected in live feed"

        match = face_recognition.compare_faces([reg_encoding], live_encodings[0], tolerance=0.6)
        distance = face_recognition.face_distance([reg_encoding], live_encodings[0])[0]
        
        if match[0]:
            return True, f"Match found (Distance: {distance:.2f})"
        else:
            return False, "Face does not match registered profile"
    except Exception as e:
        print(f"Server-side error in verify_face: {e}")
        return False, f"Auth Error: {str(e)}"

def extract_voice_features(audio_path):
    """Extract MFCC features from an audio file."""
    try:
        y, sr = librosa.load(audio_path, sr=None)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        return np.mean(mfcc.T, axis=0)
    except Exception as e:
        print(f"Error extracting voice features: {e}")
        return None

def verify_voice(registered_voice_path, live_audio_path):
    """Compare registered voice features with live audio pattern."""
    reg_features = extract_voice_features(registered_voice_path)
    if reg_features is None:
        return False, "Registered voice sample invalid"

    live_features = extract_voice_features(live_audio_path)
    if live_features is None:
        return False, "Live voice sample invalid"

    # Cosine similarity (1 - distance)
    dist = cosine(reg_features, live_features)
    similarity = 1 - dist
    
    # Threshold for voice matching (can be tuned)
    is_match = similarity > 0.85
    if is_match:
        return True, f"Voice Match (Similarity: {similarity:.2f})"
    else:
        return False, "Voice pattern does not match registered profile"
