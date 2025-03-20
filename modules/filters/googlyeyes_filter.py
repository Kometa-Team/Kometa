from modules import util
from retinaface import RetinaFace
from PIL import Image
from math import acos, sqrt, pi
import random
import math
import cv2
import numpy as np

logger = util.logger


def circles_overlap_at_least_percentage(r, p1, p2, pct):
    """
    Determines if two circles overlap by at least the specified percentage.

    This function calculates the area of overlap between two circles of equal radius
    and compares it to the specified percentage threshold. The calculation uses
    geometric formulas to compute the intersection area of two circles.

    Args:
        r: Radius of both circles
        p1: Center position of first circle as (x, y)
        p2: Center position of second circle as (x, y)
        pct: Minimum percentage overlap required (0-100)

    Returns:
        True if the circles overlap by at least the specified percentage, False otherwise
    """
    if p1 is None or p2 is None:
        return False

    d = math.dist(p1, p2)
    circle_area = pi * r * r

    if d >= 2 * r:
        # No overlap - centers are too far apart (distance ≥ 2*radius)
        overlap_area = 0
    elif d <= 0:
        # Circles are coincident (same center) - complete overlap
        overlap_area = circle_area
    else:
        # Partial overlap case - use the formula for area of intersection of two circles
        # Formula: 2r²cos⁻¹(d/2r) - (d/2)√(4r² - d²)
        overlap_area = 2 * r ** 2 * acos(d / (2 * r)) - 0.5 * d * sqrt(4 * r ** 2 - d ** 2)

    # Calculate overlap as a percentage of total circle area
    percent_overlap = (overlap_area / circle_area) * 100

    return percent_overlap >= pct


def overlap_center(r, p1, p2):
    """
    Calculates the center point of the overlapping region between two circles.

    When two circles of equal radius overlap, this function finds the midpoint
    between their centers, which approximates the center of the overlapping area.
    This is a simplification that works well for the googly eyes filter.

    Args:
        r: Radius of both circles
        p1: Center position of first circle as (x, y)
        p2: Center position of second circle as (x, y)

    Returns:
        A tuple (x, y) representing the center coordinates of the overlapping region,
        or None if the circles do not overlap
    """
    if p1 is None or p2 is None:
        return None

    d = math.dist(p1, p2)

    if d >= 2 * r:
        return None  # No overlap

    # For two circles with equal radius, the intersection is symmetric,
    # and the centroid of the overlapping region is approximated by the midpoint.
    mid_x = (p1[0] + p2[0]) // 2
    mid_y = (p1[1] + p2[1]) // 2
    return mid_x, mid_y


class GooglyEyes:
    """
    A filter that adds googly eyes to faces detected in images.

    This filter uses RetinaFace for face detection and places cartoonish googly
    eyes on the detected eye positions. The size of the eyes is proportional to
    the detected face size, and they can be optionally rotated randomly for a
    more dynamic effect.
    """
    default_size_factor = 25
    default_rotate = False
    default_confidence = 90
    size_factor_variable = "size_factor"
    rotate_variable = "rotate"
    confidence_variable = "confidence"

    @staticmethod
    def check_preconditions(size_factor, rotate, confidence):
        """
        Validates that the filter parameters are within acceptable ranges.

        This method ensures all parameters passed to the GooglyEyes filter
        are valid and within expected ranges before creating an instance.
        Invalid parameters will log errors and raise ValueError exceptions.

        Args:
            size_factor: Controls eye size (must be between 1-100)
            rotate: Whether to randomly rotate eyes (must be boolean)
            confidence: Detection confidence threshold (must be between 0-100)

        Raises:
            ValueError: If any parameter fails validation
        """
        if int(size_factor) <= 0 or int(size_factor) > 100:
            logger.error(f"Invalid size_factor for googlyeyes: {size_factor}, not in range 0 > size_factor <= 100")
            raise ValueError

        if not isinstance(rotate, bool):
            logger.error(f"Invalid confidence for rotate: {rotate}, not true or false")
            raise ValueError

        if int(confidence) < 0 or int(confidence) > 100:
            logger.error(f"Invalid confidence for googlyeyes: {confidence}, not in range 0 >= confidence <= 100")
            raise ValueError

    def __init__(self, eye_image, size_factor: int = default_size_factor, rotate: bool = default_rotate,
                 confidence: int = default_confidence) -> None:
        GooglyEyes.check_preconditions(size_factor, rotate, confidence)
        self.size_factor = size_factor
        self.rotate = rotate
        self.confidence = confidence
        self.eye_image = eye_image

    def draw_eye(self, image, radius, position):
        """
        Draws a googly eye on the image at the specified position.

        This method places a googly eye image onto the target image. The eye
        can be optionally rotated randomly if the rotate flag is set. The eye
        is sized according to the radius parameter and centered at the given position.

        Args:
            image: The destination image to draw on
            radius: The radius of the eye in pixels
            position: The center position (x, y) where the eye should be placed
                     If None, no eye will be drawn
        """
        if position is None:
            return

        eye_image = self.eye_image

        if self.rotate:
            eye_image = eye_image.rotate(random.randint(0, 360))

        eye_image = eye_image.resize((radius * 2, radius * 2))

        # Calculate the top-left position for pasting
        paste_position = (position[0] - radius, position[1] - radius)

        image.paste(eye_image, paste_position, mask=eye_image)

    def filter(self, poster: Image) -> Image:
        """
        Applies the googly eyes filter to the input image.

        This is the main filter method that:
        1. Pads the image to help with face detection near edges
        2. Detects faces and facial landmarks using RetinaFace
        3. Determines appropriate eye size based on face dimensions
        4. Places googly eyes on detected eye positions
        5. Handles special cases like eye overlap

        Args:
            poster: The original image to apply the filter to

        Returns:
            The modified image with googly eyes added to detected faces
        """
        try:
            # Create a padded version of the poster with white background
            # This increases the chance of finding faces near edges and improves detection
            padded_poster = Image.new('RGB', (poster.width * 2, poster.height * 2), 'white')
            top_left = ((padded_poster.width - poster.width) // 2, (padded_poster.height - poster.height) // 2)
            padded_poster.paste(poster, top_left)

            # Convert PIL image to OpenCV format (RGB to BGR for RetinaFace)
            rgb_array = np.array(padded_poster)
            bgr_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)

            faces = RetinaFace.detect_faces(bgr_array, threshold=self.confidence * 0.01)

            for face_idx in faces:
                face = faces[face_idx]

                fx = face["facial_area"][0]  # Left
                fy = face["facial_area"][1]  # Top
                fw = face["facial_area"][2] - fx  # Width
                fh = face["facial_area"][3] - fy  # Height

                # Calculate eye radius based on face dimensions and size_factor
                # The formula scales the eye size proportionally to face size
                # Face area = width * height
                # We take sqrt to get a dimension measure, then scale with size_factor
                face_area = fw * fh
                eye_radius = int(math.sqrt(face_area * self.size_factor * 0.001))

                # Ensure eye radius is at least 5 pixels to avoid tiny eyes
                eye_radius = max(5, eye_radius)

                left_eye_position = None
                right_eye_position = None

                if len(face["landmarks"]["left_eye"]) == 2:
                    lex = int(face["landmarks"]["left_eye"][0])
                    ley = int(face["landmarks"]["left_eye"][1])
                    left_eye_position = (lex - top_left[0], ley - top_left[1])

                if len(face["landmarks"]["right_eye"]) == 2:
                    rex = int(face["landmarks"]["right_eye"][0])
                    rey = int(face["landmarks"]["right_eye"][1])
                    right_eye_position = (rex - top_left[0], rey - top_left[1])

                # Check if eyes are close together and overlap significantly
                # This happens with profile views or when face is partially off-image
                if circles_overlap_at_least_percentage(eye_radius, left_eye_position, right_eye_position, 25):
                    # Find the center of the overlap and draw a single slightly larger eye
                    center_position = overlap_center(eye_radius, left_eye_position, right_eye_position)
                    self.draw_eye(poster, int(eye_radius * 1.15), center_position)
                else:
                    self.draw_eye(poster, eye_radius, left_eye_position)
                    self.draw_eye(poster, eye_radius, right_eye_position)

            return poster
        except Exception as e:
            logger.error(f"Error in googly eyes filter: {str(e)}")
            return poster
