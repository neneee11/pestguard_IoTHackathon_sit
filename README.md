# pestguard_IoTHackathon_sit
ai/iot->smarthome

## Face Recognition System Setup

### Prerequisites
- Python 3.x
- Required packages: `face_recognition`, `opencv-python`, `numpy`, `pickle`

### Installation
```bash
# Install CMake (required for dlib)
brew install cmake

# Install dlib via conda (if using Anaconda)
conda install -c conda-forge dlib

# Install face_recognition
pip install face_recognition opencv-python numpy
```

### Setup Instructions

1. **Create Dataset Structure**
   ```
   test/
     └── dataset/
         ├── person1/
         │   ├── image1.jpg
         │   └── image2.jpg
         └── person2/
             └── image1.jpg
   ```

2. **Encode Faces** (Run this first!)
   ```bash
   cd test
   python encode_faces.py
   ```
   This will create `encodings.pickle` file with face encodings from your dataset.

3. **Run Face Recognition System**
   ```bash
   cd test
   python run_system.py
   ```
   Press 'q' to quit the camera window.

### Notes
- Make sure images contain clear faces
- Supported image formats: .jpg, .jpeg, .png, .bmp
- The system will show "Unknown" for faces not in the database
