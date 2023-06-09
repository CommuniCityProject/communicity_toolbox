from .age_gender import AgeGenderPredictor as age_gender
from .emotions_hse import EmotionsClassifier as emotions_hse
from .face_detector_retinaface import FaceDetector as face_detector_retinaface
from .face_detector_ultraface import FaceDetector as face_detector_ultraface
from .face_recognition_facenet import \
    FaceRecognition as face_recognition_facenet

try:
    from .detectron2 import Detectron2
except:
    print("Warning: Detectron2 not found.")
    Detectron2 = None

model_catalog = {
    "age_gender": age_gender,
    "face_detector_ultraface": face_detector_ultraface,
    "detectron2": Detectron2,
    "emotions_hse": emotions_hse,
    "face_recognition_facenet": face_recognition_facenet,
    "face_detector_retinaface": face_detector_retinaface
}
