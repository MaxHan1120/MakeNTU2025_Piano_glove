# src/calibration.py

import cv2
import mediapipe as mp

def calibrate_pixel_to_cm():
    """
    啟動攝影機，偵測拇指與小指的 pixel 距離，讓使用者輸入真實距離，計算 pixel/cm。
    """

    # Mediapipe 手部模型初始化
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7
    )
    mp_draw = mp.solutions.drawing_utils

    # 開啟攝影機
    cap = cv2.VideoCapture(0)

    print("📏 請將你的拇指和小指打開，呈現最大張開姿勢")
    print("📸 按 'c' 鍵截圖進行校正")

    pixel_distance = None

    while True:
        ret, frame = cap.read() #ret 是回傳是否有抓到照片 frame會是一個矩陣 包含每個pixel的顏色(rgb)
        if not ret:
            print("❌ 無法讀取攝影機影像")
            break

        # 翻轉畫面
        frame = cv2.flip(frame, 1) #0 是垂直翻轉, 1是水平翻轉, -1是上下左右都翻轉

        # Mediapipe 處理
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  #cv2讀的資訊是bgr 需要做一個轉換
        result = hands.process(rgb_frame) #視覺辨識手部的位置 

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                thumb_tip = hand_landmarks.landmark[4]
                pinky_tip = hand_landmarks.landmark[20]

                h, w, _ = frame.shape
                thumb_pos = (int(thumb_tip.x * w), int(thumb_tip.y * h))
                pinky_pos = (int(pinky_tip.x * w), int(pinky_tip.y * h))

                cv2.circle(frame, thumb_pos, 10, (255, 0, 0), cv2.FILLED)
                cv2.circle(frame, pinky_pos, 10, (255, 0, 0), cv2.FILLED)
                cv2.line(frame, thumb_pos, pinky_pos, (0, 255, 0), 2)

                pixel_distance = ((thumb_pos[0] - pinky_pos[0])**2 + (thumb_pos[1] - pinky_pos[1])**2)**0.5

                cv2.putText(frame, f"Pixel Distance: {int(pixel_distance)}", (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)    #顯示pixel distance在畫面上

        cv2.imshow("Calibration", frame)

        key = cv2.waitKey(1)
        if key == ord('c') and pixel_distance is not None:
            break
        elif key == ord('q'):
            pixel_distance = None
            break

    cap.release()
    cv2.destroyAllWindows()

    if pixel_distance is None:
        print("⚠️ 校正失敗，沒有正確取得距離")
        return None

    # ❗❗❗ 加這段：請使用者自己輸入真實距離（單位：cm）
    while True:
        try:
            true_distance_cm = float(input("請輸入拇指到小指的實際距離 (單位 cm)："))
            if true_distance_cm <= 0:
                print("⚠️ 請輸入一個正的數字喵～")
                continue
            break
        except ValueError:
            print("⚠️ 請輸入正確的數字喵～")

    pixel_per_cm = pixel_distance / true_distance_cm

    print(f"✅ 校正完成！每公分大約是 {pixel_per_cm:.2f} pixels")
    return pixel_per_cm
