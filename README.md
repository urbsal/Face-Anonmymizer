# Face-Anonymizer
This repository is mainly developed for face anonymization project. 
### Source Code and Setup Instructions

The source code for the face anonymization application is written in Python. The application was developed and tested on Raspberry Pi OS using Raspberry Pi with Pi Camera (camera module). The goal of the application is to detect the human faces in images and in real-time camera frames and anonymizes the detected faces. 

The application used a the virtual environment called face_app_venv and python verison 3.13.5 was used in this environment. 

### Used Libraries 

The application uses MediaPipe for face detection. It uses a BlazeFace-based face detection model stored in TensorFlow Lite (.tflite) format. In the application, the model file is named detector.tflite.

The main libraries used in this application are:

MediaPipe - for detecting the face position
OpenCV - for image processing and anonymization
NumPy - for image data processing
Picamera2 - for accessing the Raspberry Pi camera 
Streamlit - for the UI
Pillow - for handling uploaded images 

### Setup 
Note: The virtual environment for this project was created and tested on a Raspberry Pi running Raspberry Pi OS. Therefore, these instructions are intended for Debian-based operating systems, including Raspberry Pi OS. 

First, create a virtual environment for this application using the following command:
python3 -m venv ~/face_app_venv

Next : Activate the virtual environment with: 
source ~/face_app_venv/bin/activate

After activating virtual environment, the required libraries can be installed using:
pip install mediapipe opencv-python numpy pillow streamlit picamera2







