# Piano Glove Project 🎹🧤

## 專案簡介

本專案為 2025 年台大電機 MakeNTU 黑客松作品，榮獲「大會獎 - Best Application」以及「英飛凌企業獎 - 第二名」。  
本專案旨在打造一套融合視覺辨識與壓力感測的「鋼琴手套」系統。  
使用者透過手機攝影機追蹤手指位置，搭配 PSoC6 開發版以及壓力感測數據，完成隨時隨地彈奏虛擬鋼琴的體驗。  
投影片以及 demo 影片：https://reurl.cc/AM9ymj

---

## 目錄
- [專案簡介](#專案簡介)
- [系統功能概覽](#系統功能概覽)
- [專案結構](#專案結構)
- [執行流程](#執行流程)
- [開發環境需求](#開發環境需求)
- [安裝方法](#安裝方法)
- [目前進度](#目前進度)
- [目前限制](#目前限制)
- [未來擴充方向](#未來擴充方向)
- [專案成員與分工](#專案成員與分工)
- [版本紀錄](最近更新紀錄（簡要）)

---


## 系統功能概覽
- 📷 **攝影機追蹤**：即時偵測手指位置（Mediapipe 實作）
- 🖐️ **多指偵測**：支援多指同時追蹤
- 📏 **尺寸校正**：使用者輸入拇指與小指實際距離，自動計算 pixel/cm 比例
- 🎹 **畫面鍵盤映射**：根據螢幕寬度自動分割白鍵與黑鍵區域
- 🎵 **音效播放**：依據手指位置與壓力輸出對應音符
- 📦 **嵌入式感測器整合**：PSoC6 負責讀取壓力值並透過 UART 傳送給主程式
- 🖨️ **3D 列印手套元件**：提供 STL 檔案以利組裝與實體裝置製作

---

## 專案結構
```plaintext
piano_glove_project/
├── src/
│   ├── ADC_basic_1/             # PSoC6 韌體專案（用於壓力感測與資料傳輸）
│   ├── calibration.py           # 校正手指長度比例
│   ├── hand_detector.py         # 手部關鍵點偵測（Mediapipe）
│   ├── main.py                  # 主控制流程
│   ├── new_screen_mapper.py     # 畫面分割與音符映射
│   ├── new_sound_manager.py     # 音效管理模組
│   └── pressure_reader.py       # 透過 UART 讀取壓力資料
├── 3D_printer.zip               # 手套設計用的 3D 列印檔案（STL 格式）
├── README.md                    # 專案說明文件
```
---

## 執行流程
啟動程式

🖐️ 使用者輸入拇指～小指實際距離（cm）

📷 攝影機自動抓取 pixel 距離

📏 計算 pixel/cm ➜ 評估畫面實際寬度

🎹 自動建立白鍵與黑鍵的映射位置

🖐️ 偵測手指座標（目前整合食指與壓力感測）

🎵 若手指有按壓且落在特定區域 ➜ 播放對應音符

---

## 開發環境需求
Python 3.9+

PSoC Creator / ModusToolbox（編譯嵌入式韌體）

必要 Python 套件：
```

numpy

scipy

opencv-python

mediapipe

sounddevice
```

---

## 安裝方法
建議使用虛擬環境，並手動安裝必要套件：
```
pip install numpy scipy opencv-python mediapipe sounddevice
```

---

## 目前進度
[✅] 攝影機串接（DroidCam）

[✅] 校正系統（拇指～小指距離 ➜ pixel/cm）

[✅] 多指追蹤與壓力感測整合完成

[✅] 根據壓力大小控制音量（音符播放與實體感測器同步）

[✅] 黑鍵視覺標示與音符播放功能

[✅] 和弦支援（多音同時播放）

[✅] 畫面鍵盤映射與視覺渲染（白鍵與黑鍵）

[✅] 壓力感測器上傳資料串接完成（PSoC → UART → Python）


---

## 目前限制
⚡ 目前仍需有線傳輸：PSoC6 需透過 USB 進行資料傳輸，尚未支援無線傳輸方式（如藍牙或 Wi-Fi）

📉 壓力感測靈敏度有限：目前使用的壓力感測元件靈敏度不足，難以精準辨識不同按壓強度，可能影響音量或表現力的即時性

---

## 未來擴充方向
📶 加入藍牙模組：將 PSoC6 傳輸介面升級為藍牙連線，實現無線資料傳輸並提升使用便利性

📱 將系統封裝為行動 App 或 Web UI

🎵 擴充更多演奏技巧（滑音、抖音等）

🎹 開放自由定義音階/調性

🧠 結合機器學習，自動辨識彈奏曲風或進行智能補音


---

## 專案成員與分工

| 姓名 | 負責內容 |
|------|----------|
| 韓裕民 | 🎹 主程式架構、手勢辨識與視覺追蹤系統 |
| 吳毅恩 | 🧤 壓力感測模組整合與 PSoC 韌體開發 |
| 劉又慈 | 🖨️ 手套結構設計與 3D 列印模型製作 |
| 許米棋 | 🖨️ 手套結構設計與 3D 列印模型製作 |

---

## 最近更新紀錄（簡要）
- 2025/05/05：補上 `3D_printer.zip` 說明與 3D 列印元件資料夾結構
- 2025/05/05：補上 成員分工與獎項~


