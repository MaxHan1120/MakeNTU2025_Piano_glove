import cv2
import numpy as np

def generate_keyboard_mapping(screen_width, pixel_per_cm):
    white_key_width = pixel_per_cm * 2.4
    black_key_width = pixel_per_cm * 2.0

    note_sequence = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E',
                     'F', 'F#', 'G', 'G#']
    all_notes = []
    for i in range(88):
        name = note_sequence[i % 12]
        octave = (i + 9) // 12
        all_notes.append(f"{name}{octave}")

    middle_c_index = all_notes.index("C4")

    # 預估畫面內能放幾個白鍵
    num_white_keys = int(screen_width // white_key_width)
    if num_white_keys % 2 == 0:
        left_white = num_white_keys // 2
        right_white = num_white_keys // 2 - 1
    else:
        left_white = right_white = num_white_keys // 2

    white_key_indices = []
    i = middle_c_index
    while len(white_key_indices) < left_white:
        i -= 1
        if "#" not in all_notes[i]:
            white_key_indices.insert(0, i)
    i = middle_c_index
    if "#" not in all_notes[i]:
        white_key_indices.append(i)
    i = middle_c_index + 1
    while len(white_key_indices) < num_white_keys:
        if "#" not in all_notes[i]:
            white_key_indices.append(i)
        i += 1

    selected_notes = [all_notes[i] for i in white_key_indices]

    white_keys = []
    black_keys = []
    current_left = (screen_width - white_key_width * len(selected_notes)) // 2

    for note in selected_notes:
        left = int(current_left)
        right = int(current_left + white_key_width)
        white_keys.append({"note": note, "left": left, "right": right})
        current_left += white_key_width

    for i in range(len(white_keys) - 1):
        left_note = white_keys[i]["note"]
        if left_note[:-1] in ['C', 'D', 'F', 'G', 'A']:
            octave = left_note[-1]
            black_note = f"{left_note[:-1]}#{octave}"
            if black_note in all_notes:
                center = (white_keys[i]["right"] + white_keys[i + 1]["left"]) // 2
                black_keys.append({
                    "note": black_note,
                    "left": int(center - black_key_width // 2),
                    "right": int(center + black_key_width // 2)
                })

    return white_keys, black_keys, selected_notes[0], selected_notes[-1]


def find_note_by_position(x, y, white_keys, black_keys, screen_height):
    for key in black_keys:  # 黑鍵優先判斷
        if key["left"] <= x < key["right"] and y < int(screen_height * 0.6):
            return key["note"]
    for key in white_keys:
        if key["left"] <= x < key["right"]:
            return key["note"]
    return None
