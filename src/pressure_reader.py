# pressure_reader.py
import serial
import threading
import time

# 串列埠參數
SERIAL_PORT = 'COM4'
BAUD_RATE = 9600

# 壓力數值（共五指）
value = [0, 0, 0, 0, 0]

# 初始化序列連線
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # 給 Arduino 一點時間初始化
except serial.SerialException:
    print(f"❌ 無法開啟序列埠 {SERIAL_PORT}")
    ser = None

def read_serial_loop():
    global value
    if ser is None:
        return
    while True:
        try:
            line = ser.readline().decode('utf-8').strip()
            values = line.split(",")
            if len(values) == 5:
                value = [int(v) for v in values]
        except:
            pass  # 忽略錯誤避免中斷 thread

def     get_finger_pressure(index):
    """取得指定手指的壓力值，index = 0~4"""
    if 0 <= index < 5:
        return value[index]
    else:
        raise ValueError("Finger index must be between 0 and 4.")

def update_finger_pressures():
    """這是保留給相容舊版的主程式用的，不需要做任何事"""
    pass

# 啟動背景讀取 thread
if ser is not None:
    thread = threading.Thread(target=read_serial_loop, daemon=True)
    thread.start()
