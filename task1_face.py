import os
import cv2
import numpy as np
import streamlit as st
from PIL import Image
import mediapipe as mp

# ---------------------------------------------------------
# Optional Raspberry Pi camera import
# ---------------------------------------------------------
try:
    from picamera2 import Picamera2
    CAMERA_AVAILABLE = True
    CAMERA_ERROR = ""
except Exception as e:
    CAMERA_AVAILABLE = False
    CAMERA_ERROR = str(e)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
MODEL_PATH = os.path.join(os.path.dirname(__file__), "detector.tflite")

FACE_PADDING = 0.35

# Gaussian blur strength
BLUR_SIZE = 111

# Pixelation strength
PIXEL_SIZE = 16

RECTANGLE_THICKNESS = 3


# ---------------------------------------------------------
# Streamlit page
# ---------------------------------------------------------
st.set_page_config(
    page_title="Face Anonymizer",
    page_icon="__",
    layout="wide"
)

st.title("Face Anonymizer")
st.write(
    "Detect and anonymize faces in images or using the Raspberry Pi camera."
)


# ---------------------------------------------------------
# Check detector model
# ---------------------------------------------------------
if not os.path.exists(MODEL_PATH):
    st.error(
        f"Face detector model was not found:\n\n{MODEL_PATH}"
    )
    st.stop()


# ---------------------------------------------------------
# Create MediaPipe face detector
# ---------------------------------------------------------
@st.cache_resource
def create_detector():

    BaseOptions = mp.tasks.BaseOptions
    FaceDetector = mp.tasks.vision.FaceDetector
    FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
    RunningMode = mp.tasks.vision.RunningMode

    options = FaceDetectorOptions(
        base_options=BaseOptions(
            model_asset_path=MODEL_PATH
        ),
        running_mode=RunningMode.IMAGE,
        min_detection_confidence=0.5
    )

    return FaceDetector.create_from_options(options)


try:
    detector = create_detector()

except Exception as e:
    st.error(
        f"Could not load the face detector:\n\n{e}"
    )
    st.stop()


# ---------------------------------------------------------
# Create camera
# ---------------------------------------------------------
@st.cache_resource
def create_camera():

    if not CAMERA_AVAILABLE:
        raise RuntimeError(CAMERA_ERROR)

    camera = Picamera2()

    camera_config = camera.create_preview_configuration(
        main={
            "size": (1280, 720),
            "format": "RGB888"
        }
    )

    camera.configure(camera_config)

    return camera


# ---------------------------------------------------------
# Calculate enlarged face area
# ---------------------------------------------------------
def get_face_box(
    detection,
    frame_width,
    frame_height
):

    bbox = detection.bounding_box

    x = int(bbox.origin_x)
    y = int(bbox.origin_y)

    width = int(bbox.width)
    height = int(bbox.height)

    padding_x = int(width * FACE_PADDING)
    padding_y = int(height * FACE_PADDING)

    x1 = max(0, x - padding_x)
    y1 = max(0, y - padding_y)

    x2 = min(
        frame_width,
        x + width + padding_x
    )

    y2 = min(
        frame_height,
        y + height + padding_y
    )

    return x1, y1, x2, y2


# ---------------------------------------------------------
# Gaussian blur
# ---------------------------------------------------------
def apply_gaussian_blur(
    frame,
    x1,
    y1,
    x2,
    y2
):

    face = frame[y1:y2, x1:x2]

    if face.size == 0:
        return

    blurred = cv2.GaussianBlur(
        face,
        (BLUR_SIZE, BLUR_SIZE),
        0
    )

    frame[y1:y2, x1:x2] = blurred


# ---------------------------------------------------------
# Pixelation
# ---------------------------------------------------------
def apply_pixelation(
    frame,
    x1,
    y1,
    x2,
    y2
):

    face = frame[y1:y2, x1:x2]

    if face.size == 0:
        return

    height, width = face.shape[:2]

    # Prevent very small regions from causing problems
    small_width = max(1, width // PIXEL_SIZE)
    small_height = max(1, height // PIXEL_SIZE)

    # Make the face very small
    small = cv2.resize(
        face,
        (small_width, small_height),
        interpolation=cv2.INTER_LINEAR
    )

    # Enlarge using nearest-neighbour interpolation
    pixelated = cv2.resize(
        small,
        (width, height),
        interpolation=cv2.INTER_NEAREST
    )

    frame[y1:y2, x1:x2] = pixelated


# ---------------------------------------------------------
# Detect and anonymize faces
# ---------------------------------------------------------
def anonymize_frame(
    frame,
    method
):

    try:

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=frame
        )

        result = detector.detect(mp_image)

    except Exception as e:

        raise RuntimeError(
            f"Face detection failed: {e}"
        )

    face_count = len(result.detections)

    frame_height, frame_width = frame.shape[:2]

    for detection in result.detections:

        x1, y1, x2, y2 = get_face_box(
            detection,
            frame_width,
            frame_height
        )

        # Apply selected anonymization method
        if method == "Gaussian Blur":

            apply_gaussian_blur(
                frame,
                x1,
                y1,
                x2,
                y2
            )

        elif method == "Pixelation":

            apply_pixelation(
                frame,
                x1,
                y1,
                x2,
                y2
            )

        # Draw red rectangle
        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (255, 0, 0),
            RECTANGLE_THICKNESS
        )

    return frame, face_count


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------
st.sidebar.header("Input Source")

input_mode = st.sidebar.radio(
    "Choose input",
    [
        " Image",
        "Live Camera"
    ]
)

st.sidebar.divider()

st.sidebar.header("Anonymization")

method = st.sidebar.radio(
    "Choose anonymization method",
    [
        "Gaussian Blur",
        "Pixelation"
    ]
)

if method == "Gaussian Blur":

    st.sidebar.info(
        f"Gaussian blur strength: {BLUR_SIZE}"
    )

else:

    st.sidebar.info(
        f"Pixelation block size: {PIXEL_SIZE}"
    )

st.sidebar.write(
    f"Face padding: {int(FACE_PADDING * 100)}%"
)


# =========================================================
# IMAGE MODE
# =========================================================
if input_mode == " Image":

    st.header(" Image Anonymization")

    uploaded_file = st.file_uploader(
        "Upload a JPG or PNG image",
        type=[
            "jpg",
            "jpeg",
            "png"
        ]
    )

    if uploaded_file is None:

        st.info(
            "Please upload an image to begin."
        )

    else:

        if st.button(
            "Anonymize Faces",
            type="primary",
            use_container_width=True
        ):

            try:

                # Open uploaded image
                pil_image = Image.open(
                    uploaded_file
                ).convert("RGB")

                # Convert to NumPy array
                rgb_image = np.array(
                    pil_image
                )

                # Anonymize
                result_image, face_count = anonymize_frame(
                    rgb_image.copy(),
                    method
                )

                # Store ONLY the anonymized result
                st.session_state["image_result"] = result_image
                st.session_state["image_face_count"] = face_count
                st.session_state["image_method"] = method

            except Exception as e:

                st.error(
                    f"Could not process the image:\n\n{e}"
                )

    # Display only anonymized result
    if "image_result" in st.session_state:

        st.divider()

        st.subheader("Anonymized Result")

        result = st.session_state["image_result"]
        face_count = st.session_state["image_face_count"]
        result_method = st.session_state["image_method"]

        if face_count == 0:

            st.warning(
                "No faces were detected in this image."
            )

        else:

            st.success(
                f"{face_count} face(s) anonymized "
                f"using {result_method}."
            )

        # IMPORTANT:
        # We display only the anonymized image.
        st.image(
            result,
            channels="RGB",
            width="stretch"
        )

        # Convert result to PNG for download
        result_pil = Image.fromarray(result)

        import io

        download_buffer = io.BytesIO()

        result_pil.save(
            download_buffer,
            format="PNG"
        )

        st.download_button(
            "Download Anonymized Image",
            data=download_buffer.getvalue(),
            file_name="anonymized_image.png",
            mime="image/png",
            use_container_width=True
        )


# =========================================================
# CAMERA MODE
# =========================================================
else:

    st.header(" Raspberry Pi Live Camera")

    if not CAMERA_AVAILABLE:

        st.error(
            "Raspberry Pi camera is not available."
        )

        st.code(CAMERA_ERROR)

    else:

        st.info(
            "The camera feed is processed in real time. "
            "Faces are anonymized before being displayed."
        )

        col1, col2 = st.columns(2)

        with col1:

            start_camera = st.button(
                " Start Camera",
                type="primary",
                use_container_width=True
            )

        with col2:

            stop_camera = st.button(
                " Stop Camera",
                use_container_width=True
            )

        if start_camera:

            st.session_state["camera_running"] = True

        if stop_camera:

            st.session_state["camera_running"] = False

        if "camera_running" not in st.session_state:

            st.session_state["camera_running"] = False

        if st.session_state["camera_running"]:

            try:

                camera = create_camera()

                camera.start()

                video_placeholder = st.empty()
                count_placeholder = st.empty()

                while st.session_state["camera_running"]:

                    # Capture camera frame
                    frame = camera.capture_array()

                    # Make sure the frame is RGB
                    frame = frame.copy()

                    # Anonymize frame
                    result_frame, face_count = anonymize_frame(
                        frame,
                        method
                    )

                    # Display anonymized frame
                    video_placeholder.image(
                        result_frame,
                        channels="RGB",
                        width="stretch"
                    )

                    if face_count == 0:

                        count_placeholder.info(
                            "No faces detected."
                        )

                    else:

                        count_placeholder.success(
                            f"{face_count} face(s) detected "
                            f"and anonymized using {method}."
                        )

                camera.stop()

            except Exception as e:

                st.session_state["camera_running"] = False

                st.error(
                    f"Camera error:\n\n{e}"
                )
