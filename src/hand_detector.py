import cv2
import mediapipe as mp

# 一次性初始化 Mediapipe Hands 和繪圖工具
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils


def detect_index_finger_position(frame):
    """
    偵測單張影像中食指的位置，返回 (x, y) 像素座標。
    接收的參數是 BGR 格式的 frame，並在其上繪製偵測結果。
    """
    # 將 BGR 轉為 RGB 供 Mediapipe 使用
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    index_position = None

    if result.multi_hand_landmarks:
        # 只取第一隻手
        hand_landmarks = result.multi_hand_landmarks[0]
        # 繪製手部關鍵點
        mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # 食指尖端 (landmark 8)
        index_tip = hand_landmarks.landmark[8]
        h, w, _ = frame.shape
        x, y = int(index_tip.x * w), int(index_tip.y * h)
        index_position = (x, y)

        # 在影像上標示食指位置
        cv2.circle(frame, (x, y), 10, (0, 255, 0), cv2.FILLED)
        cv2.putText(frame,
                    f"Index: ({x},{y})",
                    (x + 10, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2)

    return index_position


def close_detector():
    """
    釋放 Mediapipe Hands 資源
    """
    hands.close()

def detect_finger_positions(frame, finger_indices=[8]):
    """
    偵測多隻手的指定手指位置，並在畫面上標示出來。
    
    Parameters:
        frame: 目前攝影機擷取的畫面 (BGR)
        finger_indices: List[int]，欲偵測的 Mediapipe landmark index（預設為食指 = 8）
    
    Returns:
        List of (x, y) 座標點，依照順序回傳所有符合的手指位置。
    """
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    positions = []

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            h, w, _ = frame.shape
            for idx in finger_indices:
                landmark = hand_landmarks.landmark[idx]
                x, y = int(landmark.x * w), int(landmark.y * h)
                positions.append((x, y))

                # 畫圓點與文字標籤
                cv2.circle(frame, (x, y), 8, (0, 255, 0), cv2.FILLED)
                cv2.putText(frame,
                            f"{idx}",
                            (x + 5, y - 5),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (0, 255, 0),
                            1)

    return positions
