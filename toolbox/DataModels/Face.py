from typing import List, Optional

from pydantic import Field

from toolbox.Structures import BoundingBox, Emotion, Gender

from .BaseModel import BaseModel
from .DataModelsCatalog import register_data_model


@register_data_model
class Face(BaseModel):
    """Data model intended to store information about a face.

    Attributes:
        id (str): Unique identifier of the entity.
        dateObserved (datetime): Entity creation time.
        image (Image): Source image.
        bounding_box (BoundingBox): Bounding box of the detected face.
        detection_confidence (float): Confidence of the face detection.
        age (float): Predicted age.
        gender (Gender): Predicted gender.
        gender_confidence (float): Confidence of the gender classification.
        emotion (Emotion): Predicted emotion.
        emotion_confidence (float): Confidence of the emotion classification.
        features (list): Feature vector.
        recognition_domain (str): Name of the group of people to recognize.
        recognized (bool): If a face recognition has been performed.
        recognized_person (str): Name or id of the recognized person.
        features_algorithm (str): Name of the algorithm used to generate
            the features.
        recognized_distance (float): Distance between the extracted features
            and the most similar face on the dataset.

    Methods:
        get_context() -> List[str]
        pretty()

    Properties (read-only):    
        entity_type (str): Name of the entity type.
    """
    __entity_type__ = "Face"

    image: Optional[str] = Field(
        None,
        description="Id of the source image"
    )
    bounding_box: Optional[BoundingBox] = Field(
        None,
        description="Bounding box of the detected face",
        alias="boundingBox"
    )
    detection_confidence: Optional[float] = Field(
        None,
        description="Confidence of the face detection",
        alias="detectionConfidence"
    )
    age: Optional[float] = Field(
        None,
        description="Predicted age"
    )
    gender: Optional[Gender] = Field(
        None,
        description="Predicted gender"
    )
    gender_confidence: Optional[float] = Field(
        None,
        description="Confidence of the gender classification",
        alias="genderConfidence"
    )
    emotion: Optional[Emotion] = Field(
        None,
        description="Predicted emotion"
    )
    emotion_confidence: Optional[float] = Field(
        None,
        description="Confidence of the emotion classification",
        alias="emotionConfidence"
    )
    features: Optional[list] = Field(
        None,
        description="Feature vector",
    )
    features_algorithm: Optional[str] = Field(
        None,
        description="Name of the algorithm used to generate the features",
        alias="featuresAlgorithm"
    )
    recognition_domain: Optional[str] = Field(
        None,
        description="Name of the group of people to recognize",
        alias="recognitionDomain"
    )
    recognized: Optional[bool] = Field(
        False,
        description="If a face recognition has been performed",
    )
    recognized_distance: Optional[float] = Field(
        None,
        description="Distance between the extracted features and the "
        "most similar face on the dataset. Less distance means more "
        "similarity",
        alias="recognizedDistance"
    )
    recognized_person: Optional[str] = Field(
        None,
        description="Name or id of the recognized person",
        alias="recognizedPerson"
    )

    __rel_attrs__ = {"image"}

    def get_context(self) -> List[str]:
        return []

    class Config:
        schema_extra = {
            "description": "Data model intended to store information about "
            "a face."
        }
