import time
import joblib
import cv2
import mediapipe as mp
import numpy as np
from collections import deque
from statistics import mean
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# --- CONFIGURATION ---
model = joblib.load("gesture_classifier_full.pkl")

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

print("\nChoose evaluation mode:")
print("[1] ML Gesture Classification")
print("[2] CV Swipe Detection")
print("[3] Both (Comparison)")
mode_input = input("Enter 1, 2, or 3: ").strip()
mode_ml = mode_input in ["1", "3"]
mode_cv = mode_input in ["2", "3"]

label_map = {
    "r": "R", "R": "R'", "l": "L", "L": "L'",
    "u": "U", "U": "U'", "d": "D", "D": "D'",
    "f": "F", "F": "F'", "b": "B", "B": "B'"
}

predictions_ml = []
predictions_cv = []
actual_labels = []
times_ml = []
times_cv = []

positions = deque(maxlen=10)

def draw_swipe_zones(frame, w, h):
    cv2.line(frame, (w // 3, 0), (w // 3, h), (200, 200, 200), 2)
    cv2.line(frame, (2 * w // 3, 0), (2 * w // 3, h), (200, 200, 200), 2)
    cv2.line(frame, (0, h // 3), (w, h // 3), (200, 200, 200), 2)
    cv2.line(frame, (0, 2 * h // 3), (w, 2 * h // 3), (200, 200, 200), 2)

    cv2.putText(frame, "LEFT", (10, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 255), 2)
    cv2.putText(frame, "RIGHT", (w - 100, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 255), 2)
    cv2.putText(frame, "TOP", (w // 2 - 30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 255, 100), 2)
    cv2.putText(frame, "BOTTOM", (w // 2 - 60, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 255, 100), 2)
    cv2.putText(frame, "CENTER", (w // 2 - 50, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

def detect_swipe(positions, cx, cy, w, h):
    if len(positions) < 8:
        return None
    dx = positions[-1][0] - positions[0][0]
    dy = positions[-1][1] - positions[0][1]

    if cx < w // 3:
        if dy < -80: return "R"
        elif dy > 80: return "R'"
    elif cx > 2 * w // 3:
        if dy > 80: return "L"
        elif dy < -80: return "L'"
    elif cy < h // 3:
        if dx < -80: return "U"
        elif dx > 80: return "U'"
    elif cy > 2 * h // 3:
        if dx < -80: return "D"
        elif dx > 80: return "D'"
    else:
        if dy < -80: return "F"
        elif dy > 80: return "F'"
    return None

cap = cv2.VideoCapture(1)
print("\nHold gesture, press label key (r R u U f F ...) — press 'q' to quit\n")

label = ""

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    if mode_cv:
        draw_swipe_zones(frame, w, h)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

            lm_list = [coord for lm in handLms.landmark for coord in (lm.x, lm.y, lm.z)]

            if mode_ml:
                start_ml = time.time()
                ml_pred = model.predict([lm_list])[0]
                end_ml = time.time()
                cv2.putText(frame, f"ML: {ml_pred}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            else:
                ml_pred = None
                start_ml = end_ml = 0

            if mode_cv:
                cx = int(handLms.landmark[8].x * w)
                cy = int(handLms.landmark[8].y * h)
                positions.append((cx, cy))
                start_cv = time.time()
                cv_pred = detect_swipe(positions, cx, cy, w, h)
                end_cv = time.time()
                if cv_pred:
                    cv2.putText(frame, f"CV: {cv_pred}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)
            else:
                cv_pred = None
                start_cv = end_cv = 0

            if label:
                mapped = label_map.get(label, None)
                if mapped:
                    actual_labels.append(mapped)
                    predictions_ml.append(ml_pred or "None")
                    predictions_cv.append(cv_pred or "None")
                    times_ml.append(end_ml - start_ml)
                    times_cv.append(end_cv - start_cv)
                    print(f"[{mapped}] → ML: {ml_pred}, CV: {cv_pred}")
                label = ""

    cv2.imshow("Evaluation", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif chr(key) in label_map:
        label = chr(key)

cap.release()
cv2.destroyAllWindows()

# --- Results ---
print("\nEvaluation Results")

if mode_ml:
    correct_ml = sum(p == t for p, t in zip(predictions_ml, actual_labels))
    print(f"ML Accuracy: {correct_ml}/{len(actual_labels)} ({100 * correct_ml / len(actual_labels):.1f}%)")
    print(f"ML Avg Latency: {mean(times_ml)*1000:.1f} ms")

if mode_cv:
    valid_cv = [(p, t) for p, t in zip(predictions_cv, actual_labels) if p != "None"]
    correct_cv = sum(p == t for p, t in valid_cv)

    if valid_cv:
        print(f"CV Accuracy: {correct_cv}/{len(valid_cv)} ({100 * correct_cv / len(valid_cv):.1f}%)")
        print(f"CV Avg Latency: {mean(times_cv)*1000:.1f} ms")
    else:
        print("CV Accuracy: No valid predictions")
