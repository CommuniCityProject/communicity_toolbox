from enum import Enum, unique
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
import seaborn as sns

from toolbox.Structures import BoundingBox, Keypoints, SegmentationMask


@unique
class TextPosition(Enum):
    TOP_LEFT = "TOP_LEFT"
    TOP_RIGHT = "TOP_RIGHT"
    BOTTOM_LEFT = "BOTTOM_LEFT"
    BOTTOM_RIGHT = "BOTTOM_RIGHT"

    def __str__(self):
        return self.name


def draw_text(
    image: np.ndarray,
    text: str,
    position: Tuple[int, int],
    color=(255, 255, 255),
    scale: int = 2,
    thickness: int = 2,
    background: bool = False,
    bg_color: Tuple[int, int, int] = (0, 0, 255),
    bg_alpha: Optional[float] = 0.5,
    line_space: int = 15,
    direction: TextPosition = TextPosition.BOTTOM_RIGHT
) -> np.ndarray:
    """Draw text on an image.

    Args:
        image (np.ndarray): A BGR uint8 image of shape (H, W, 3).
        text (str): The text to draw.
        position (Tuple[int, int]): (x, y) absolute image coordinates where
            draw the text.
        color (tuple, optional): BGR color of the text.
            Defaults to (255,255,255).
        scale (int, optional): Text scale. Defaults to 2.
        thickness (int, optional): Text thickness. Defaults to 2.
        background (bool, optional): Set a solid color as a background on the
            area occupied by the text. Defaults to False.
        bg_color (Tuple[int, int, int], optional): Background BGR color.
            Defaults to (0,0,255).
        bg_alpha (Optional[float]): Transparency of the background, where
            1.0 is completely opaque and 0 is transparent. Defaults to None.
        line_space (int, optional): Spacing between lines. Defaults to 15.
        direction (TextPosition, optional): Text position relative to the
            text origin. Defaults to TextPosition.BOTTOM_RIGHT.

    Returns:
        np.ndarray: The image with the text inserted.
    """
    if not text:
        return image

    font = cv2.FONT_HERSHEY_SIMPLEX
    lines = text.splitlines()
    max_text = max(lines, key=lambda x: len(x))
    (text_w, text_h), _ = cv2.getTextSize(max_text, font, scale, thickness)

    if direction is TextPosition.BOTTOM_RIGHT:
        x, y = position
    else:
        raise NotImplementedError

    if background:
        box_h = (text_h + (scale * line_space)) * (len(lines)-1)

        margin = 10
        xmin = max(x, 0)
        ymin = max(y - text_h - margin, 0)
        xmax = min(x + text_w, image.shape[1])
        ymax = min(y + box_h + margin, image.shape[0])

        if bg_alpha:
            rect = np.full((ymax-ymin, xmax-xmin, 3), bg_color, dtype="uint8")
            image[ymin:ymax, xmin:xmax, :] = cv2.addWeighted(
                image[ymin:ymax, xmin:xmax, :],
                1-bg_alpha,
                rect,
                bg_alpha,
                0
            )
        else:
            cv2.rectangle(
                image,
                (xmin, ymin),
                (xmax, ymax),
                bg_color,
                -1
            )

    for i, line in enumerate(lines):
        dy = i * (text_h + scale * line_space)
        cv2.putText(
            image, line, (x, y+dy), font, scale, color, thickness, cv2.LINE_AA)
    return image


def draw_bounding_box(
    image: np.ndarray,
    box: Optional[BoundingBox],
    thickness: int = 2,
    color: Tuple[int, int, int] = (0, 0, 255),
    text: Optional[str] = None,
    text_scale: int = 2,
    text_thickness: int = 2,
    text_color: Tuple[int, int, int] = (0, 0, 0),
    text_background: bool = True,
    text_bg_color: Optional[Tuple[int, int, int]] = None,
    text_bg_alpha: Optional[float] = None,
    text_line_space: int = 15,
    text_box_position: TextPosition = TextPosition.TOP_LEFT,
    text_direction: TextPosition = TextPosition.BOTTOM_RIGHT
) -> np.ndarray:
    """Draw a bounding box and optional text on an image.

    Args:
        image (np.ndarray): A BGR uint8 image of shape (H, W, 3).
        box (Optional[BoundingBox]): A BoundingBox object.
        thickness (int, optional): Box line thickness. Defaults to 2.
        color (Tuple[int, int, int], optional): BGR line color.
            Defaults to (0,0,255).
        text (Optional[str], optional): Optional text to set along the
            bounding box. Defaults to None.
        text_scale (int, optional): Text scale. Defaults to 2.
        text_thickness (int, optional): Text thickness. Defaults to 2.
        text_color (Tuple[int, int, int], optional): BGR text color.
            Defaults to (0,0,0).
        text_background (bool, optional): Set a solid color as a background on
            the area occupied by the text. Defaults to True.
        text_bg_color (Optional[Tuple[int, int, int]], optional): Text 
            background BGR color. If None, the bounding box color will be used.
            Defaults to None.
        text_bg_alpha Optional[float]: Transparency of the text background,
            where 1.0 is completely opaque and 0 is transparent.
            Defaults to None.
        text_line_space (int, optional): Spacing between text lines.
            Defaults to 15.
        text_box_position (TextPosition, optional): The text position relative
            to the bounding box. Defaults to TextPosition.TOP_LEFT.
        text_direction (TextPosition, optional): Direction of the text.
            Defaults to TextPosition.BOTTOM_RIGHT.

    Returns:
        np.ndarray: The created image.
    """
    # Draw the bounding box
    if box is not None:
        xmin, ymin, xmax, ymax = box.get_xyxy(
            absolute=True,
            image_width=image.shape[1],
            image_height=image.shape[0]
        )
        image = cv2.rectangle(
            image,
            (xmin, ymin),
            (xmax, ymax),
            color,
            thickness
        )

    # Draw the text
    if text:
        if text_box_position is TextPosition.TOP_LEFT:
            x, y = xmin, ymin
        else:
            raise NotImplementedError

        text_bg_color = color if text_bg_color is None else text_bg_color

        image = draw_text(
            image=image,
            text=text,
            position=(x, y),
            color=text_color,
            scale=text_scale,
            thickness=text_thickness,
            background=text_background,
            bg_color=text_bg_color,
            bg_alpha=text_bg_alpha,
            line_space=text_line_space,
            direction=text_direction
        )
    return image


def draw_mask(
    image: np.ndarray,
    mask: SegmentationMask,
    color: Optional[Tuple[int, int, int]] = (0, 0, 255),
    alpha: float = 0.5,
    color_by_label: bool = False,
    label_id: Optional[int] = None,
    colors_list: Optional[List[Tuple[int, int, int]]] = None
) -> np.ndarray:
    """Draw a segmentation mask on an image.

    Args:
        image (np.ndarray): A BGR uint8 image of shape (H, W, 3).
        mask (SegmentationMask): A SegmentationMask object.
        color (Optional[Tuple[int, int, int]]): Color of the mask.
            Defaults to (0,0,255).
        alpha (float, optional): Transparency of the mask, where
            1.0 is completely opaque and 0 is transparent. Defaults to 0.5.
        color_by_label (bool, optional): Set the mask color by its ``label_id``.
            Defaults to False.
        label_id (Optional[int], optional): label id associated with the mask;
            used to chose the color. Defaults to None.
        colors_list (Optional[List[Tuple[int, int, int]]], optional): Custom
            list of colors to chose when ``color_by_label`` is set to True.
            If it is None, a seaborn palette is used. Defaults to None.

    Returns:
        np.ndarray: The image with the plotted mask.
    """
    mask = mask.mask
    mask_pixels = image[mask]

    if color_by_label:
        if colors_list is None:
            color = sns.color_palette(None, label_id+1)[label_id]
            color_mask = np.full_like(mask_pixels, [int(i*255) for i in color])
        else:
            color_mask = np.full_like(mask_pixels, colors_list[label_id])
    else:
        color_mask = np.full_like(mask_pixels, color)

    image[mask] = cv2.addWeighted(mask_pixels, 1-alpha, color_mask, alpha, 0)

    return image


def draw_coco_keypoints(
    image: np.ndarray,
    keypoints: Keypoints.COCOKeypoints,
    color: Optional[Tuple[int, int, int]] = (0, 0, 255),
    color_by_label: bool = False,
    color_mapping: Optional[Dict[str, Tuple[int, int, int]]] = None,
    keypoint_radius: Optional[int] = 5,
    connection_rules: Optional[List[Tuple[str,
                                          str, Tuple[int, int, int]]]] = None,
    line_thickness: int = 3,
    show_names: bool = False,
    show_conf: bool = True,
    show_keypoints: bool = True,
    show_connections: bool = True,
    text_scale: int = 2,
    text_thickness: int = 2,
    text_color: Tuple[int, int, int] = (255, 255, 255),
    text_bg_color: Optional[Tuple[int, int, int]] = None,
    text_bg_alpha: Optional[float] = None
) -> np.ndarray:
    """Draw keypoints and its connections on an image.

    Args:
        image (np.ndarray): A BGR uint8 image of shape (H, W, 3).
        keypoints (Keypoints.COCOKeypoints): A Keypoints object.
        color (Optional[Tuple[int, int, int]], optional): Color of the
            keypoints. Defaults to None.
        color_by_label (bool, optional): Set the keypoints colors by its label.
            Defaults to False.
        color_mapping (Optional[Dict[str, Tuple[int, int, int]]], optional):
            Mapping between keypoint names and its color. Defaults to None.
        keypoint_radius (Optional[int], optional): Radius of the keypoints.
            Defaults to 5.
        connection_rules (Optional[List[Tuple[str, str, Tuple[int, int, int]]]], optional):
            List of connections rules
            (keypoints_name_a, keypoints_name_b, (B, G, R)) Defaults to None.
        line_thickness (int, optional): Keypoints line thickness. Defaults to 3.
        show_names (bool, optional): Show the names of the keypoints.
            Defaults to False.
        show_conf (bool, optional): Show the keypoint confidence along with its
            name. Defaults no True.
        show_keypoints (bool, optional): Show the keypoints circles.
            Defaults to True.
        show_connections (bool, optional): Show the connection lines.
            Defaults to True.
        text_scale (int, optional): Text scale. Defaults to 2.
        text_thickness (int, optional): Text thickness. Defaults to 2.
        text_color (Tuple[int, int, int], optional): Text color.
            Defaults to (255,255,255).
        text_bg_color (Optional[Tuple[int, int, int]], optional): Color of the
            text background. Defaults to None.
        text_bg_alpha (Optional[float], optional): Transparency of the text
            background, where 1.0 is completely opaque and 0 is transparent.
            Defaults to None.

    Returns:
        np.ndarray: The image with the plotted mask.
    """
    visible_kps = Keypoints.keypoints_dict_to_absolute(
        keypoints.visible_keypoints,
        image.shape[1],
        image.shape[0]
    )

    # Draw keypoints connections
    if show_connections:
        assert connection_rules is not None
        for (na, nb, ab_color) in connection_rules:
            if na in visible_kps and nb in visible_kps:
                (xa, ya, ca) = visible_kps[na]
                (xb, yb, cb) = visible_kps[nb]
                image = cv2.line(
                    image,
                    (int(xa), int(ya)),
                    (int(xb), int(yb)),
                    ab_color if color_by_label else color,
                    line_thickness
                )
    # Draw keypoints
    for name, (x, y, conf) in visible_kps.items():
        pos = (int(x), int(y))
        if show_keypoints:
            image = cv2.circle(
                image,
                pos,
                keypoint_radius,
                color_mapping[name] if color_by_label else color,
                -1
            )
        if show_names:
            text = f"{name}"
            if show_conf:
                text += f"({conf:.2f})"
            draw_text(
                image=image,
                text=text,
                position=pos,
                color=text_color,
                scale=text_scale,
                thickness=text_thickness,
                background=text_bg_color is not None,
                bg_color=text_bg_color,
                bg_alpha=text_bg_alpha
            )
    return image
