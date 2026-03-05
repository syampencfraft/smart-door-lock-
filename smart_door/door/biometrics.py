import face_recognition
import cv2
import numpy as np
import librosa
import librosa.effects
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

import traceback

def extract_voice_features( audio_path):
    """Extract MFCC features + Deltas with normalization."""
    try:
        # Load audio
        y, sr = librosa.load(audio_path, sr=22050)
        duration = librosa.get_duration(y=y, sr=sr)
        print(f"VOICE DEBUG: Loaded {audio_path}, Duration: {duration:.2f}s, SR: {sr}")
        
        # Normalize audio volume
        y = librosa.util.normalize(y)
        
        # Trim silence (less aggressive to avoid clipping quiet speech)
        y_trimmed, _ = librosa.effects.trim(y, top_db=30)
        trimmed_duration = librosa.get_duration(y=y_trimmed, sr=sr)
        print(f"VOICE DEBUG: Trimmed Duration: {trimmed_duration:.2f}s")
        
        if len(y_trimmed) < sr * 0.3: # At least 0.3s of audio needed
            print("VOICE DEBUG: Audio too short after trimming.")
            return None

        # Pre-emphasis
        y_filt = librosa.effects.preemphasis(y_trimmed)
        
        # Extract features
        mfccs = librosa.feature.mfcc(y=y_filt, sr=sr, n_mfcc=20)
        delta_mfccs = librosa.feature.delta(mfccs)
        delta2_mfccs = librosa.feature.delta(mfccs, order=2)
        
        # Use mean AND standard deviation
        features = np.concatenate((
            np.mean(mfccs, axis=1),
            np.std(mfccs, axis=1),
            np.mean(delta_mfccs, axis=1),
            np.mean(delta2_mfccs, axis=1)
        ))
        
        # Standardize the feature vector
        features = (features - np.mean(features)) / (np.std(features) + 1e-6)
        
        print(f"VOICE DEBUG: Feature vector shape: {features.shape}")
        return features
    except Exception as e:
        print(f"VOICE DEBUG ERROR: {str(e)}")
        traceback.print_exc()
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
    
    # DEBUG LOGGING - Crucial for tuning
    print(f"VOICE DEBUG: Similarity Score = {similarity:.4f}")
    
    # Threshold for voice matching (Temporarily lower to 0.65 for debugging)
    is_match = similarity > 0.65
    if is_match:
        return True, f"Voice Match (Similarity: {similarity:.4f})"
    else:
        return False, f"Voice mismatch (Similarity: {similarity:.4f})"
