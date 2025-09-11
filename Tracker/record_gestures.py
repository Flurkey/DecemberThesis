import cv2
import mediapipe as mp
import pandas as pd

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

all_data = []
gesture_label = ""
save_path = "real_gesture_data.csv"

valid_keys = {
    'r': "R", 'R': "R'",
    'u': "U", 'U': "U'",
    'f': "F", 'F': "F'",
    'l': "L", 'L': "L'",
    'd': "D", 'D': "D'",
    'b': "B", 'B': "B'"
}

cap = cv2.VideoCapture(1)
print("Press: r R u U f F l L d D b B to label a gesture")
print("Press 's' to save, 'q' to quit")

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

            landmarks = []
            for lm in handLms.landmark:
                landmarks.extend([lm.x, lm.y, lm.z])

            if gesture_label and len(landmarks) == 63:
                all_data.append(landmarks + [gesture_label])
                print(f"Sample saved: {gesture_label}")
                gesture_label = ""

    if gesture_label:
        cv2.putText(frame, f"Labeling: {gesture_label}", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Rubik's Cube Gesture Recorder", frame)

    key = cv2.waitKey(1) & 0xFF
    char = chr(key)
    if char in valid_keys:
        gesture_label = valid_keys[char]
    elif key == ord('s') and all_data:
        df = pd.DataFrame(all_data, columns=[f"{a}{i}" for i in range(21) for a in "xyz"] + ["label"])
        df.to_csv(save_path, index=False)
        print(f"Data saved to {save_path}")
        all_data.clear()
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
