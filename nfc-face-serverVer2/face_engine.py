import json
import sys
import os
import time
from pathlib import Path
import numpy as np
import cv2

FACE_DATA_DIR = Path(__file__).parent / "face_data" 
FACE_DATA_DIR.mkdir(exist_ok=True)


def _user_face_dir(user_id): 
    path = FACE_DATA_DIR / f"user_{user_id}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _face_detector(): 
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    if not os.path.exists(cascade_path):
        raise FileNotFoundError(f"Cascade file not found: {cascade_path}")
    return cv2.CascadeClassifier(cascade_path)


def _detect_face(gray_image): 
    gray_image = cv2.equalizeHist(gray_image)
    detector = _face_detector()
    faces = detector.detectMultiScale(
        gray_image,
        scaleFactor=1.1,
        minNeighbors=6,
        minSize=(100, 100)
    )

    if len(faces) == 0:
        return None

    x, y, w, h = max(faces, key=lambda rect: rect[2]*rect[3])
    face = gray_image[y:y + h, x:x + w]
    face = cv2.resize(face, (200, 200))
    return face


def _capture_camera_faces(frames_to_capture=15, max_frames=100): #this one findss the best face photos and returns for accuracy
    video = cv2.VideoCapture(0)

    if not video.isOpened():
        return None, "Unable to open camera"

    faces = []
    attempts = 0

    while len(faces) < frames_to_capture and attempts < max_frames:
        attempts += 1

        ret, frame = video.read()

        if not ret or frame is None:
            time.sleep(0.1)
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        face = _detect_face(gray)

        if face is not None:
            faces.append(face)

            # small time delay so frames are not identical
            time.sleep(0.08)

    video.release()

    if not faces:
        return None, "No face detected in camera feed"

    return faces, None


def _save_face_sample(user_id, face_image, index=None):
    folder = _user_face_dir(user_id)

    filename = f"face_{int(time.time() * 1000)}"

    if index is not None:
        filename += f"_{index}"

    filename += ".png"
    path = folder / filename
    cv2.imwrite(str(path), face_image)
    return path


def _collect_face_samples(user_id):
    folder = _user_face_dir(user_id)
    return sorted(folder.glob("face_*.png"))


def _train_recognizer(user_id):
    samples = []
    labels = []

    paths = _collect_face_samples(user_id)

    for path in paths:
        image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)

        if image is None:
            continue

        samples.append(image)
        labels.append(abs(hash(user_id)) % 100000)

    if not samples:
        return None

    recognizer = cv2.face.LBPHFaceRecognizer_create(
        radius=2,
        neighbors=12,
        grid_x=8,
        grid_y=8
    )

    recognizer.train(samples, np.array(labels, dtype=np.int32))
    return recognizer


def _predict_face(recognizer, face_image, user_id, threshold=115.0): #this part verifies face with a confidence percentgae 
    label, raw_distance = recognizer.predict(face_image)
    # Better confidence calcu
    confidence = max(
        0.0,
        min(100.0, 100.0 - (raw_distance * 0.7))
    )
    verified = (
    int(label) == abs(hash(user_id)) % 100000
    and raw_distance <= threshold
    )
    return verified, confidence, raw_distance


def _load_image(image_path):
    if not image_path or not os.path.exists(image_path):
        return None, "Image file does not exist"
    image = cv2.imread(image_path)
    if image is None:
        return None, "Unable to read image file"
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face = _detect_face(gray)
    if face is None:
        return None, "No face detected in image"
    return face, None


def register_user_face(user_id, image_path=None): #register face from img 
    faces = []
    if image_path:
        face, error = _load_image(image_path)
        if face is None:
            return json.dumps({
                "success": False,
                "verified": False,
                "message": error
            })
        faces.append(face)
    else:
        faces, error = _capture_camera_faces(frames_to_capture=15)

        if faces is None:
            return json.dumps({
                "success": False,
                "verified": False,
                "message": error
            })
    for index, face in enumerate(faces):
        _save_face_sample(user_id, face, index=index)

    return json.dumps({
        "success": True,
        "message": f"Face registered for user {user_id}",
        "samples_saved": len(faces)
    })
def verify_user_face(user_id, image_path=None, threshold=115.0):
    recognizer = _train_recognizer(user_id)
    if recognizer is None:
        return json.dumps({
            "success": False,
            "verified": False,
            "message": f"No registered face found for user {user_id}"
        })

    face, error = _load_image(image_path)
    if face is None:
        return json.dumps({
            "success": False,
            "verified": False,
            "message": error
        })
    verified, confidence, raw_distance = _predict_face(
        recognizer,
        face,
        user_id,
        threshold
    )
    return json.dumps({
        "success": True,
        "verified": verified,
        "confidence": round(confidence, 2),
        "distance": round(raw_distance, 2),
        "message": f"Face {'verified' if verified else 'not verified'}"
    })

def verify_face_from_camera(user_id, frames_to_capture=8, threshold=90.0): 
    recognizer = _train_recognizer(user_id)
    if recognizer is None:
        return json.dumps({
            "success": False,
            "verified": False,
            "message": f"No registered face found for user {user_id}"
        })

    faces, error = _capture_camera_faces(
        frames_to_capture=frames_to_capture,
        max_frames=frames_to_capture * 12
    )

    if faces is None:
        return json.dumps({
            "success": False,
            "verified": False,
            "message": error
        })
    results = []
    for face in faces:
        verified, confidence, raw_distance = _predict_face(
            recognizer,
            face,
            user_id,
            threshold
        )
        results.append((verified, confidence, raw_distance))

    distances = [d for _, _, d in results]
    avg_distance = float(np.mean(distances))
    best_distance = float(min(distances))
    confidences = [c for _, c, _ in results]
    avg_confidence = float(np.mean(confidences))

    verified = (
        best_distance <= 75
        and avg_distance <= 90
    )

    return json.dumps({
        "success": True,
        "verified": verified,
        "confidence": round(avg_confidence, 2),
        "distance": round(avg_distance, 2),
        "best_distance": round(best_distance, 2),
        "frames_analyzed": len(results),
        "message": f"Face {'verified' if verified else 'not verified'}"
    })

def encode_face_from_camera(user_id, frames_to_capture=15): #this is just register image but not verify
    faces, error = _capture_camera_faces(
        frames_to_capture=frames_to_capture
    )
    if faces is None:
        return json.dumps({
            "success": False,
            "verified": False,
            "message": error
        })
    for index, face in enumerate(faces):
        _save_face_sample(user_id, face, index=index)
    return json.dumps({
        "success": True,
        "message": f"Face registered for user {user_id}",
        "frames_used": len(faces)
    })


def _usage_and_exit():
    print(json.dumps({
        "error": "Usage: python face_engine.py <command> [args]"
    }))
    sys.exit(1)



if __name__ == "__main__":
    if len(sys.argv) < 2:
        _usage_and_exit()

    command = sys.argv[1]
    if command == "register":
        if len(sys.argv) < 3:
            _usage_and_exit()
        user_id = sys.argv[2]
        image_path = sys.argv[3] if len(sys.argv) > 3 else None
        print(register_user_face(user_id, image_path))
    elif command == "verify":
        if len(sys.argv) < 3:
            _usage_and_exit()
        user_id = sys.argv[2]
        image_path = sys.argv[3] if len(sys.argv) > 3 else None
        print(verify_user_face(user_id, image_path))
    elif command=="register_camera":
        if len(sys.argv) < 3:
            _usage_and_exit()
        user_id = sys.argv[2]
        frames = int(sys.argv[3]) if len(sys.argv) > 3 else 15
        print(encode_face_from_camera(user_id, frames))
    elif command== "verify_camera":
        if len(sys.argv) < 3:
            _usage_and_exit()
        user_id = sys.argv[2]
        frames = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        print(verify_face_from_camera(user_id, frames))
    else:
        print(json.dumps({
            "error": f"Unknown command: {command}"
        }))

        sys.exit(1)