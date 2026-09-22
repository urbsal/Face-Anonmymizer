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

### Anonymization Method Used 
In the developed application Gaussian Blue and Pixelation method were used in both images and real time camera frames. 
When the subject face is near the camera or if the images quality is good the application work better. And the application work well with JPG, JPEG and PNG images as well as real time camera frames. 

During testing, it was observed that the application had difficulty detecting faces when the face was covered or partially blocked. It also had difficulty detecting faces that were very far from the camera. In these situations, the application could not reliably detect and anonymize the faces in real-time camera frames or uploaded images.

### Multiple Face and No Face Handling
This application can handle multiple faces and anonymize them in uploaded images or from the camera frames. Each detected face is processed separately. If the uploaded images or camera frame does not contain faces, the application showed "no face detected" and, no anonymization is applie
The basic idea behind anonymization process is that the model detect each face in the images or camera frame and provides the coordinates of each detected face. These coordinates are then used for further blurring or pixelation using OpenCV.  

Own images and live camera frames were used for testing. The results of the images were not published before anonymization. Any unknown sources data has not been used while testing this application.
However, anonymization is not guaranteed to provide complete privacy, especially when face is not detected correctly.  

### Sources Or Documents Used 
MediaPipe offical document were used to understand the concept of BlazeFace-based model. All the libraries mentioned above were used in this project. For testing purposes, my own test images and real-time camera frames were used to evaluate the face detection and anonymization process. 






