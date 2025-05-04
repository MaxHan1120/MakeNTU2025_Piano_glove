from calibration import calibrate_pixel_to_cm
from new_screen_mapper import generate_keyboard_mapping, find_note_by_position
from hand_detector import close_detector, detect_finger_positions
from new_sound_manager import SoundManager
from pressure_reader import get_finger_pressure

import cv2
import time

def get_camera_resolution():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ 無法開啟攝影機")
        return None, None
    ret, frame = cap.read()
    if not ret:
        print("❌ 無法讀取攝影機影像")
        cap.release()
        return None, None
    height, width, _ = frame.shape
    cap.release()
    return width, height

def main():
    print("🎹 Piano Glove 系統啟動中...")

    print("\n[步驟1] 啟動手指長度校正")
    pixel_per_cm = calibrate_pixel_to_cm()
    if pixel_per_cm is None:
        print("⚠️ 校正失敗，程式結束")
        return

    print("\n[步驟2] 自動偵測畫面大小")
    screen_width, screen_height = get_camera_resolution()
    if screen_width is None:
        return

    print("\n[步驟3] 產生鍵盤 mapping")
    white_keys, black_keys, lowest_note, highest_note = generate_keyboard_mapping(screen_width, pixel_per_cm)

    print("\n[步驟4] 載入音效合成器")
    sound_manager = SoundManager()

    # ✨ 新增：預先生成畫面中所有可用 note 的 waveform
    all_notes_on_screen = [key["note"] for key in white_keys + black_keys]
    sound_manager.preload_notes(all_notes_on_screen)

    print("\n[步驟5] 開始畫面與偵測")
    cap = cv2.VideoCapture(0)
    flash_keys = {}  # note → (time, volume)

    finger_indices = [4, 8, 12, 16, 20]
    finger_map = {4: 0, 8: 1, 12: 2, 16: 3, 20: 4}
    active_notes = set()  # 當前正在播放的 note 集合

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        current_time = time.time()

        finger_positions = detect_finger_positions(frame, finger_indices=finger_indices)
        current_notes = set()

        if finger_positions:
            for landmark_index, (x, y) in zip(finger_indices, finger_positions):
                note = find_note_by_position(x, y, white_keys, black_keys, screen_height)
                pressure_index = finger_map.get(landmark_index)

                if note and pressure_index is not None:
                    current_notes.add(note)
                    pressure = get_finger_pressure(pressure_index)
                    volume = min(1.0, (pressure - 10) / (100.0 - 20.0))

                    if pressure > 20:
                        sound_manager.volumes[note] = volume 
                        
                        if note not in active_notes:
                            sound_manager.play_note(note, volume=volume)
                            active_notes.add(note)
                        else:
                            pass
                        flash_keys[note] = (current_time, volume)
                    else:
                        if note in active_notes:
                            sound_manager.stop_note(note)
                            active_notes.remove(note)

        # 偵測離開畫面或未按壓者，停止播放
        for note in list(active_notes):
            if note not in current_notes:
                sound_manager.stop_note(note)
                active_notes.remove(note)

        # 清除過期的閃燈
        for note in list(flash_keys.keys()):
            timestamp, _ = flash_keys[note]
            if current_time - timestamp >= 0.3:
                del flash_keys[note]

        # === 建立 overlay 圖層 ===
        overlay = frame.copy()

        for key in white_keys:
            note = key["note"]
            if note in flash_keys:
                _, volume = flash_keys[note]
                brightness = int(60 + volume * 40)
                color = (180, 180, brightness)
            else:
                color = (230, 230, 230)

            cv2.rectangle(overlay, (key["left"], 0), (key["right"], screen_height), color, -1)
            cv2.rectangle(overlay, (key["left"], 0), (key["right"], screen_height), (0, 0, 0), 1)
            center = (key["left"] + key["right"]) // 2
            cv2.putText(overlay, note, (center - 15, screen_height - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        for key in black_keys:
            note = key["note"]
            if note in flash_keys:
                _, volume = flash_keys[note]
                brightness = int(40 + volume * 80)
                color = (brightness, brightness, brightness)
            else:
                color = (0, 0, 0)

            cv2.rectangle(overlay, (key["left"], 0), (key["right"], int(screen_height * 0.6)), color, -1)
            center = (key["left"] + key["right"]) // 2
            cv2.putText(overlay, note, (center - 15, int(screen_height * 0.6) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        # 疊加 overlay
        alpha = 0.4
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        # 顯示畫面
        cv2.imshow("Piano Glove 🎹", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    close_detector()
    print("🎶 Piano Glove 結束～喵 🎶")

if __name__ == "__main__":
    main()
