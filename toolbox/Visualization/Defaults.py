from copy import deepcopy

from toolbox.Visualization import utils


COCO_KEYPOINTS_COLORS = {
    "left_ear": (255, 0, 255),
    "right_ear": (255, 255, 0),
    "left_eye": (223, 0, 255),
    "right_eye": (223, 255, 0),
    "nose": (255, 255, 255),
    "left_shoulder": (191, 0, 255),
    "right_shoulder": (191, 255, 0),
    "left_elbow": (159, 0, 255),
    "right_elbow": (159, 255, 0),
    "left_wrist": (127, 0, 255),
    "right_wrist": (127, 255, 0),
    "left_hip": (95, 0, 255),
    "right_hip": (95, 255, 0),
    "left_knee": (63, 0, 255),
    "right_knee": (63, 255, 0),
    "left_ankle": (31, 0, 255),
    "right_ankle": (31, 255, 0)
}


COCO_KEYPOINTS_CONNECTION_RULES = [
    # face
    ("left_ear", "left_eye", (239, 0, 255)),
    ("right_ear", "right_eye", (239, 235, 0)),
    ("left_eye", "nose", (255, 0, 255)),
    ("nose", "right_eye", (255, 255, 0)),
    # upper-body
    ("left_shoulder", "right_shoulder", (191, 255, 255)),
    ("left_shoulder", "left_elbow", (175, 0, 255)),
    ("right_shoulder", "right_elbow", (175, 255, 0)),
    ("left_elbow", "left_wrist", (143, 0, 255)),
    ("right_elbow", "right_wrist", (143, 255, 0)),
    # lower-body
    ("left_hip", "right_hip", (95, 255, 255)),
    ("left_hip", "left_knee", (63, 0, 255)),
    ("right_hip", "right_knee", (63, 255, 0)),
    ("left_knee", "left_ankle", (47, 0, 255)),
    ("right_knee", "right_ankle", (47, 255, 0)),
    # upper-lower-body connections
    ("left_shoulder", "left_hip", (143, 0, 255)),
    ("right_shoulder", "right_hip", (143, 255, 0)),
    ("nose", "left_shoulder", (223, 0, 255)),
    ("nose", "right_shoulder", (223, 255, 0)),
]


class Defaults:
    # Image
    image_width = None
    image_height = None
    # Text
    text_color = (255, 255, 255)
    text_scale = 1
    text_thickness = 1
    text_background = True
    text_bg_color = (224, 56, 84)
    text_bg_alpha = 0.75
    text_line_space = 15
    text_direction = utils.TextPosition.BOTTOM_RIGHT
    # BoundingBox
    box_thickness = 2
    box_color = (224, 56, 84)
    box_text_position = utils.TextPosition.TOP_LEFT
    # Segmentation mask
    mask_color = (21, 57, 255)
    mask_alpha = 0.75
    mask_color_by_label = True
    mask_colors_list = None
    mask_show_box = True
    mask_show_label = True
    mask_show_conf = True
    # Keypoints
    kp_color = (0, 0, 255)
    kp_color_by_label = True
    kp_radius = 5
    kp_line_thickness = 3
    kp_show_kp = True
    kp_show_connections = True
    kp_show_name = False
    kp_show_conf = True
    kp_show_box = True
    kp_show_detection_conf = True
    COCO_KEYPOINTS_CONNECTION_RULES = COCO_KEYPOINTS_CONNECTION_RULES
    COCO_KEYPOINTS_COLORS = COCO_KEYPOINTS_COLORS
    # Face DataModels
    face_show_conf = True
    face_show_age = True
    face_show_gender = True
    face_show_gender_conf = True
    face_show_emotion = True
    face_show_emotion_conf = True
    face_show_recognized_person = True
    face_show_recognized_dist = True

    @staticmethod
    def dict() -> dict:
        """Return the default attributes as a dict.
        """
        return deepcopy(
            {k: v for k, v in Defaults.__dict__.items()
             if not k.startswith("_") and k != "dict"}
        )
