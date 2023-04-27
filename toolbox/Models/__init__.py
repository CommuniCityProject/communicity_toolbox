from .age_gender import AgeGenderPredictor as age_gender
from .face_detector_ultraface import FaceDetector as face_detector_ultraface
from .face_detector_mtcnn import FaceDetector as face_detector_mtcnn
from .detectron2 import Detectron2
from .emotions_hse import EmotionsClassifier as emotions_hse
from .face_recognition_facenet import FaceRecognition as face_recognition_facenet
from .face_detector_retinaface import FaceDetector as face_detector_retinaface

model_catalog = {
    "age_gender": age_gender,
    "face_detector_ultraface": face_detector_ultraface,
    "face_detector_mtcnn": face_detector_mtcnn,
    "detectron2": Detectron2,
    "emotions_hse": emotions_hse,
    "face_recognition_facenet": face_recognition_facenet,
    "face_detector_retinaface": face_detector_retinaface
}

