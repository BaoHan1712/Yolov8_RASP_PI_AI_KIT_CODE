import cv2 
import numpy as np
from cover.color_utils import *

def offset_backboard(frame_2,cx):
    """Tính toán trung tâm khung hình"""
    frame_center_x = frame_2.shape[1] // 2
    cv2.line(frame_2, (frame_center_x, 0), (frame_center_x, frame_2.shape[0]), (0, 255, 0), 1)
    offset = cx - frame_center_x
    return offset


def draw_plus_sign(image, center, size=10, color=(0, 0, 255), thickness=2):
    """
    Vẽ dấu cộng (+) trên hình ảnh.

    Parameters:
        image (numpy.ndarray): Ảnh cần vẽ dấu cộng.
        center (tuple): Tọa độ trung tâm của dấu cộng (cx, cy).
        size (int): Kích thước của dấu cộng (độ dài mỗi nhánh).
        color (tuple): Màu sắc của dấu cộng (BGR).
        thickness (int): Độ dày của đường vẽ.
    """
    cx, cy = center
    # Vẽ đường ngang
    cv2.line(image, (cx - size, cy), (cx + size, cy), color, thickness)
    # Vẽ đường dọc
    cv2.line(image, (cx, cy - size), (cx, cy + size), color, thickness)

def calculate_position(frame, cx):
    """
        position: Giá trị từ -1350 đến 450, trong đó:
        - Từ trái đến tâm: -450 đến 450 
        - Từ tâm đến phải: -1350 đến -450
    """
    frame_width = frame.shape[1]
    frame_center = frame_width // 2
    cv2.line(frame, (frame_center, 0), (frame_center, frame.shape[0]), (0, 255, 0), 1)
    offset = cx - frame_center

    if cx < frame_center:  # Bên trái tâm (-450 đến 450)
        position = np.interp(cx, [0, frame_center], [-450, 450])
    else:  # Bên phải tâm (-1350 đến -450) 
        position = np.interp(cx, [frame_center, frame_width], [-1350, -450])
    
    # Hiển thị giá trị vị trí
    cv2.putText(frame, f'Pos: {int(position)}', (cx, 100), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    
    return int(position)

## Nhan dien khong co dung mau

def process_detections(detections, tracker):
    """Xử lý detections và trả về thông tin đối tượng được phát hiện"""
    basket_detected = False
    backboard_detected = False
    basket_info = None
    backboard_info = None
    conf = None

    if detections.shape[0] > 0:
        basket_detections = detections[detections[:, 5] == 1]  
        backboard_detections = detections[detections[:, 5] == 0] 
        

        # Xử lý basket nếu có
        if basket_detections.shape[0] > 0:
            track_result = tracker.update(basket_detections[:1].astype(np.float32))
            if track_result.shape[0] > 0:
                basket_detected = True
                basket_info = track_result[0]
                conf = int(basket_detections[0][4])

        # Xử lý backboard nếu không có basket
        elif backboard_detections.shape[0] > 0:
            track_result = tracker.update(backboard_detections[:1].astype(np.float32))
            if track_result.shape[0] > 0:
                backboard_detected = True
                backboard_info = track_result[0]
                conf = int(backboard_detections[0][4])

    return basket_detected, backboard_detected, basket_info, backboard_info, conf

def auto_drive(frame, offset_2, num_objects):
    """
    Điều khiển hướng di chuyển của robot
    Args:
        frame: Khung hình hiện tại
        offset_2: Độ lệch của vật thể (1-99: lệch trái, 100: chuẩn, 101-254: lệch phải)
        num_objects: Số lượng vật thể phát hiện được
    Returns:
        direction: 1-đi thẳng, 2-đi trái, 3-đi phải, 4-không có vật
    """
    if offset_2 is None:
        cv2.putText(frame, "Khong co vat", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        return 4
        
    # Nếu vật ở giữa (độ lệch từ 98-102)
    if 98 <= offset_2 <= 102:
        cv2.putText(frame, "Di thang", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        return 1
        
    # Nếu vật lệch trái (offset < 98)
    elif offset_2 < 98:
        cv2.putText(frame, "Di phai", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        return 3
        
    # Nếu vật lệch phải (offset > 102) 
    else:
        cv2.putText(frame, "Di trai", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        return 2

def process_detections_no_track(detections):
    """Xử lý detections"""
    basket_detected = False
    backboard_detected = False
    basket_info = None
    backboard_info = None
    conf = None
    num_objects = 0

    if detections.shape[0] > 0:
        basket_detections = detections[detections[:, 5] == 1]  
        backboard_detections = detections[detections[:, 5] == 0] 
        
        # Xử lý basket nếu có
        if basket_detections.shape[0] > 0:
            basket_detected = True
            x1, y1, x2, y2 = map(int, basket_detections[0][:4])
            basket_info = np.array([x1, y1, x2, y2, 1])  # ID mặc định là 1
            conf = int(basket_detections[0][4])
            num_objects += 1

        # Xử lý backboard nếu không có basket
        elif backboard_detections.shape[0] > 0:
            backboard_detected = True
            x1, y1, x2, y2 = map(int, backboard_detections[0][:4])
            backboard_info = np.array([x1, y1, x2, y2, 1])  # ID mặc định là 1
            conf = int(backboard_detections[0][4])
            num_objects += 1

    return basket_detected, backboard_detected, basket_info, backboard_info, conf, num_objects