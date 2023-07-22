import cv2
import numpy as np
import torch

import torchreid
from torchreid.utils import FeatureExtractor

IMG_SIZE = 250
MAX_SCAN_NUM = 100
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def put_text(frame, txt, pos):
    return cv2.putText(
        frame, txt, pos, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA
    )


def put_face_rectangle(frame):
    h, w = frame.shape[:-1]
    start_point = (w // 2 - IMG_SIZE // 2, h // 2 - IMG_SIZE // 2)
    end_point = (w // 2 + IMG_SIZE // 2, h // 2 + IMG_SIZE // 2)
    face = frame.copy()[start_point[1] : end_point[1], start_point[0] : end_point[0]]
    frame_flipped = cv2.rectangle(frame, start_point, end_point, (0, 0, 255), 2)

    return face, frame_flipped, start_point, end_point


def scan_face(frame, i):
    face, frame_flipped, start_point, end_point = put_face_rectangle(frame)

    frame_flipped = cv2.flip(frame, 1)
    text_pos = (start_point[0] - 5, start_point[1] - 5)
    frame_flipped = put_text(frame_flipped, "Scanning...", text_pos)

    perc = int(100 * i / MAX_SCAN_NUM)

    perc_pos = (text_pos[0] + 170, text_pos[1])
    frame_flipped = put_text(frame_flipped, f"{perc}%", perc_pos)

    return face, frame_flipped


def load_model():
    return FeatureExtractor(
        model_name="osnet_x1_0",
        model_path="model_training/models/retrain_osnet_x1_0/model/users_data.pth.tar-10",
        image_size=(IMG_SIZE, IMG_SIZE),
        device=DEVICE,
        verbose=False,
    )


def compare_encodings(login_user_encs, name):
    user_encs = np.load(f"database/user_encodings/{name}.npy")
    login_user_encs = np.array(login_user_encs)
    dists = (((user_encs - login_user_encs) ** 2) <= 0.63).mean()
    print(f"conf={round(dists * 100)}%")

    return False#dists >= 0.8


# if __name__ == "__main__":
#     from pathlib import Path

#     model = load_model()
#     image_paths = Path("model_training/data/camera_captures")
#     for user_path in image_paths.rglob("*"):
#         name = user_path.name
#         print(f"Saving encodings for {name}: ", end="")
#         pic_folder_paths = list(user_path.rglob("*png"))
#         pic_folder_paths = [x.as_posix() for x in pic_folder_paths]
#         encodings = model(pic_folder_paths)
#         encodings = np.array(encodings)
#         np.save(f"database/user_encodings/{name}", encodings)
#         print("done")
