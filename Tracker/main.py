import cv2
import mediapipe as mp
from collections import deque

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("Webcam failed")
    exit()

positions = deque(maxlen=10)
gesture_cooldown = 0
last_move = ""
move_sequence = []

def detect_movement(positions):
    if len(positions) < 8:
        return None

    dx = positions[-1][0] - positions[0][0]
    dy = positions[-1][1] - positions[0][1]
    print(f"dx: {dx}, dy: {dy}")

    if abs(dx) > abs(dy):
        if dx > 80:
            return "right"
        elif dx < -80:
            return "left"
    else:
        if dy > 80:
            return "down"
        elif dy < -80:
            return "up"
    return None

def detect_front_back(handLms):
    palm_down = handLms.landmark[0].y < handLms.landmark[9].y
    return "F" if palm_down else "F'"

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks and results.multi_handedness:
        for handLms, handInfo in zip(results.multi_hand_landmarks, results.multi_handedness):
            label = handInfo.classification[0].label
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

            if label != "Right":
                continue 

            cx = int(handLms.landmark[8].x * w)
            cy = int(handLms.landmark[8].y * h)
            positions.append((cx, cy))

            if gesture_cooldown == 0:
                move = detect_movement(positions)

                if move:
                    last_move = ""
                    if cx > 2 * w // 3:
                        if move == "down":
                            last_move = "L"
                        elif move == "up":
                            last_move = "L'"
                    elif cx < w // 3:
                        if move == "up":
                            last_move = "R"
                        elif move == "down":
                            last_move = "R'"
                    elif cy < h // 3:
                        if move == "left":
                            last_move = "U"
                        elif move == "right":
                            last_move = "U'"
                    elif cy > 2 * h // 3:
                        if move == "left":
                            last_move = "D"
                        elif move == "right":
                            last_move = "D'"
                    else:
                        if move in ["up", "down"]:
                            last_move = detect_front_back(handLms)

                    if last_move:
                        print("Move Detected:", last_move)
                        move_sequence.append(last_move)
                        gesture_cooldown = 40

    if gesture_cooldown > 0:
        gesture_cooldown -= 1

    cv2.line(frame, (w // 3, 0), (w // 3, h), (200, 200, 200), 2)
    cv2.line(frame, (2 * w // 3, 0), (2 * w // 3, h), (200, 200, 200), 2)
    cv2.line(frame, (0, h // 3), (w, h // 3), (200, 200, 200), 2)
    cv2.line(frame, (0, 2 * h // 3), (w, 2 * h // 3), (200, 200, 200), 2)

    cv2.putText(frame, f"Last Move: {last_move}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 100, 100), 2)
    cv2.putText(frame, f"Sequence: {' '.join(move_sequence[-8:])}", (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imshow("Rubik's Cube Gesture Tracker", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
