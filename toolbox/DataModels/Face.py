from typing import Optional

from pydantic import Field
from toolbox.Structures import BoundingBox, Emotion, Gender

from .BaseModel import BaseModel
from .DataModelsCatalog import register_data_model


@register_data_model
class Face(BaseModel):
    """This entity stores information about a face, such as its estimated
    age, gender or identity. It is intended to be used with computer vision
    algorithms to infer common properties from a facial image.

    Attributes:
        id (str)
        dateObserved (datetime)
        type (str)
        image (str)
        bounding_box (BoundingBox)
        detection_confidence (float)
        age (float)
        gender (Gender)
        gender_confidence (float)
        emotion (Emotion)
        emotion_confidence (float)
        features (list)
        recognition_domain (str)
        recognized (bool)
        recognized_person (str)
        features_algorithm (str)
        recognized_distance (float)
    """

    __rel_attrs__ = {"image"}
    __context__ = set()

    type: str = Field("Face")

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
        description="The estimated age of the face"
    )
    gender: Optional[Gender] = Field(
        None,
        description="The inferred gender of the face"
    )
    gender_confidence: Optional[float] = Field(
        None,
        description="Confidence of the gender classification",
        alias="genderConfidence"
    )
    emotion: Optional[Emotion] = Field(
        None,
        description="The inferred emotion of the face"
    )
    emotion_confidence: Optional[float] = Field(
        None,
        description="Confidence of the emotion classification",
        alias="emotionConfidence"
    )
    features: Optional[list] = Field(
        None,
        description="Facial features extracted with a computer vision "
        "algorithm used for face recognition tasks",
    )
    features_algorithm: Optional[str] = Field(
        None,
        description="Name of the algorithm used to generate the features",
        alias="featuresAlgorithm"
    )
    recognition_domain: Optional[str] = Field(
        None,
        description="The face recognition domain. I.e. name of the group of "
        "people to recognize",
        alias="recognitionDomain"
    )
    recognized: Optional[bool] = Field(
        False,
        description="Flags whether a face recognition task has been performed",
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

    class Config:
        schema_extra = {
            "description": "This entity stores information about a face, such "
            "as its estimated age, gender or identity. It is intended to "
            "be used with computer vision algorithms to infer common "
            "properties from a facial image"
        }
