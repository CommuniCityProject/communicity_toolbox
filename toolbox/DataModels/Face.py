from typing import Optional

from pydantic import Field

from toolbox.Structures import BoundingBox, Emotion, Gender

from .BaseModel import BaseModel
from .DataModelsCatalog import register_data_model


@register_data_model
class Face(BaseModel):
    """This data model stores information about a face, such as its estimated
    age, gender or identity. It is intended to be used with computer vision
    algorithms to infer common properties from a facial image.
    """

    __rel_attrs__ = {"image"}
    __context__ = set()

    #: The data model type ("Face"). Should not be changed.
    type: str = Field("Face")

    #: Id of the source image
    image: Optional[str] = Field(
        None,
        description="Id of the source image"
    )

    #: Bounding box of the detected face
    bounding_box: Optional[BoundingBox] = Field(
        None,
        description="Bounding box of the detected face",
        alias="boundingBox"
    )

    #: Confidence of the face detection
    detection_confidence: Optional[float] = Field(
        None,
        description="Confidence of the face detection",
        alias="detectionConfidence"
    )

    #: The estimated age of the face
    age: Optional[float] = Field(
        None,
        description="The estimated age of the face"
    )

    #: The inferred gender of the face
    gender: Optional[Gender] = Field(
        None,
        description="The inferred gender of the face"
    )

    #: Confidence of the gender classification
    gender_confidence: Optional[float] = Field(
        None,
        description="Confidence of the gender classification",
        alias="genderConfidence"
    )

    #: The inferred emotion of the face
    emotion: Optional[Emotion] = Field(
        None,
        description="The inferred emotion of the face"
    )

    #: Confidence of the emotion classification
    emotion_confidence: Optional[float] = Field(
        None,
        description="Confidence of the emotion classification",
        alias="emotionConfidence"
    )

    #: Facial features extracted with a computer vision
    #: algorithm used for face recognition tasks
    features: Optional[list] = Field(
        None,
        description="Facial features extracted with a computer vision "
        "algorithm used for face recognition tasks",
    )

    #: Name of the algorithm used to generate the features
    features_algorithm: Optional[str] = Field(
        None,
        description="Name of the algorithm used to generate the features",
        alias="featuresAlgorithm"
    )

    #: The face recognition domain. I.e. name of the group of 
    #: people to recognize
    recognition_domain: Optional[str] = Field(
        None,
        description="The face recognition domain. I.e. name of the group of "
        "people to recognize",
        alias="recognitionDomain"
    )

    #: Flags whether a face recognition task has been performed
    recognized: Optional[bool] = Field(
        False,
        description="Flags whether a face recognition task has been performed",
    )

    #: Distance between the extracted features and the 
    #: most similar face on the dataset. Less distance means more
    #: similarity
    recognized_distance: Optional[float] = Field(
        None,
        description="Distance between the extracted features and the "
        "most similar face on the dataset. Less distance means more "
        "similarity",
        alias="recognizedDistance"
    )

    #: Name or id of the recognized person
    recognized_person: Optional[str] = Field(
        None,
        description="Name or id of the recognized person",
        alias="recognizedPerson"
    )

    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "description": "This entity stores information about a face, such "
            "as its estimated age, gender or identity. It is intended to "
            "be used with computer vision algorithms to infer common "
            "properties from a facial image"
        }
