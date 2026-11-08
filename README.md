# Interactive Drawing

**Draw in the air. Create on screen.**

Interactive Drawing is a real-time hand gesture drawing application built with Python, OpenCV, and MediaPipe.

The application uses a webcam to track hand movements, allowing users to draw, select colors, create geometric shapes, and erase drawings without using a mouse or touchscreen.

## Features

- **Hand Tracking** - Detects and tracks both hands using MediaPipe.
- **Air Drawing** - Draw by moving your index finger in front of the webcam.
- **Live Camera Canvas** - Draw directly over the webcam feed.
- **Color Palette** - Choose from 24 colors using hand gestures.
- **Geometric Shapes** - Create lines, rectangles, circles, and triangles.
- **Shape Preview** - Preview shapes before confirming them.
- **Eraser** - Erase drawings using your left hand.
- **Adjustable Eraser** - Change the eraser size using finger gestures.
- **Two-Hand Controls** - Use each hand for different actions.

## How It Works

1. OpenCV captures video from the webcam.
2. MediaPipe detects up to two hands and tracks 21 landmarks per hand.
3. The application recognizes gestures using finger angles and distances between landmarks.
4. Recognized gestures are used to control drawing, menus, shapes, and the eraser.
5. OpenCV displays the results over the live camera feed.

Drawings are stored using separate image and mask layers, allowing them to be erased without affecting the webcam image.

## Gesture Controls

### Right Hand

| Gesture | Action |
|---------|--------|
| Index finger extended | Draw or preview a shape |
| Open palm (0.5 seconds) | Open color palette |
| Pinch inside color palette | Select color |
| Pinch while previewing | Confirm shape |

### Left Hand

| Gesture | Action |
|---------|--------|
| Open palm (0.5 seconds) | Open shapes menu |
| Pinch inside shapes menu | Select drawing tool |
| Index finger extended, thumb folded | Erase |
| Index finger and thumb extended | Resize eraser |

### Drawing Tools

- Free Draw
- Line
- Rectangle
- Circle
- Triangle

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `C` | Clear canvas |
| `F` | Toggle fullscreen |
| `Q` | Quit application |

## Tech Stack

- **Python 3.12** - Application logic
- **OpenCV** - Video capture and drawing
- **MediaPipe** - Hand tracking
- **NumPy** - Image and mask processing

## Installation

### Requirements

- Python 3.12
- Webcam
- Git (optional)

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/Interactive-Drawing.git
cd Interactive-Drawing
```

### 2. Create a Virtual Environment

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. MediaPipe Model

Make sure `hand_landmarker.task` is located in the project folder.

If the model is missing, download it from the [MediaPipe documentation](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker) and save it as `hand_landmarker.task`.

### 5. Run the Application

```bash
python main.py
```

## Project Structure

```text
Interactive-Drawing/
├── main.py
├── hand_tracking.py
├── gestures.py
├── drawing.py
├── color_palette.py
├── shapes.py
├── shape_menu.py
├── hand_landmarker.task
├── requirements.txt
├── .gitignore
└── README.md
```
