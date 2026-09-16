# Real-Time Kinematic Analysis

## Overview
This repository contains the source code for an Edge-AI system capable of real-time human movement analysis and kinematic telemetry. Originally designed as a "Virtual Physiotherapist", the system leverages *Computer Vision* and *Machine Learning* to track human joints, calculate critical angles dynamically, and stream live feedback to a web-based dashboard.

Awarded 1st place out of 8 engineering projects presented at Politecnico di Milano.

## Relevance to Motorsport Engineering
While originally developed for healthcare, the computer vision architecture and mathematical models in this project explore concepts that are highly translatable to motorsport applications, such as:
* **Pit-Stop Kinematic Analysis:** Using pose estimation to track mechanics' movements and optimise pit-stop routines down to the millisecond.
* **Driver Ergonomics:** Real-time assessment of driver posture, steering angles, and physical strain inside the cockpit.
* **Live Visual Telemetry:** The asynchronous web dashboard mimics pit-wall telemetry screens, handling high-frequency data polling and instant visual warnings.

## System Architecture

### 1. Computer Vision & Biomechanics Engine (`biomeccanica.py`)
* **Libraries:** `OpenCV` (cv2), `MediaPipe` (Pose Estimation), `math`.
* **Features:** 
  * Tracks 33 3D-landmarks on the human body in real-time.
  * Uses pure trigonometric functions (`math.atan2`) to calculate dynamic joint angles (knee, hip, shoulder).
  * Implements a state-machine to detect motion phases (e.g., concentric/eccentric) and flags postural errors instantly.

### 2. Edge AI Web Server (`app.py`)
* **Libraries:** `Flask`, `threading`, `numpy`.
* **Features:**
  * Handles continuous MJPEG video streaming (`/video_feed`).
  * Thread-safe global state management using Mutex Locks (`threading.Lock()`) to prevent data corruption between the video processing thread and API requests.
  * Exposes lightweight REST APIs (`/data`) for real-time telemetry polling.

### 3. Telemetry Dashboard (`index.html`)
* **Tech:** `HTML5`, `CSS3` (Glassmorphism UI), `JavaScript` (ES6).
* **Features:**
  * Asynchronous data polling (220ms intervals) to update kinematic data without lagging the video stream.
  * Automated CSV Report generation compiling session accuracy, rep targets, and specific biomechanical compensations.
  * Audio feedback integration via Web Speech API.

## Project Structure
* `app.py`: Main Flask server and thread manager.
* `biomeccanica.py`: Core mathematical engine for angle calculations and pose evaluation.
* `config.py`: Centralised configuration for specific kinematic targets and thresholds.
* `templates/index.html`: The frontend telemetry dashboard.
