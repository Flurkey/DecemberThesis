# Rubik’s Cube Algorithm Solver (Thesis Project)

This repository contains the implementation for my BSc (Hons) Software Development dissertation:  
**“Rubik’s Cube Algorithm Solver” – Neil Azzopardi (December 2025)**
=======
# Rubik’s Cube Algorithmic Solver (Thesis Project)

This repository contains the implementation for my BSc (Hons) Software Development dissertation:  
**“Rubik’s Cube Algorithmic Solver” – Neil Azzopardi (September 2025)**

The project integrates:
- **Image processing** for cube state detection,
- **Algorithmic computation** using the Beginner’s Method,
- **User interaction** through a step-by-step UI,
- **Hand gesture recognition** for validating cube moves.

## Repository Structure

This repository has two main branches, each representing a core part of the system:

### `main` (UI Solver)
- Implements cube **state detection**, **colour recognition**, and **solver integration**.
- Uses **Eitan Hanson’s open-source solver** (Beginner’s Method) for pedagogical clarity.
- Provides a **2D UI** showing the cube state and step-by-step solution.
- Related thesis sections:
  - *Methodology*: 3.10.1 Cube State Detection & Solver Integration, 3.10.2 User Interface  
  - *Analysis*: 4.2 Colour Detection Accuracy, 4.3 Solver Success Rate  

### `HandGesture`
- Implements **gesture recognition experiments**.
- Two approaches compared:
  - **Rule-based computer vision** (index finger swipe detection).
  - **Machine learning classifier** (Random Forest on MediaPipe landmarks, ~94% accuracy).
- Related thesis sections:
  - *Methodology*: 3.10.3 Gesture Recognition System  
  - *Analysis*: 4.4 Gesture Recognition Performance  

---

## How to Run

### 1. Clone the repo
git clone https://github.com/Flurkey/DecemberThesis.git
cd DecemberThesis
