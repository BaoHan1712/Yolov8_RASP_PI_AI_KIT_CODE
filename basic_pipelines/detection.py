import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import os
import numpy as np
import cv2
import hailo
from cover.utils import *
from cover.send_uart import *
# import serial

# ser = serial.Serial('/dev/ttyUSB0', 115200)

from hailo_apps_infra.hailo_rpi_common import (
    get_caps_from_pad,
    get_numpy_from_buffer,
    app_callback_class,
)
from hailo_apps_infra.detection_pipeline import GStreamerDetectionApp

# -----------------------------------------------------------------------------------------------
# User-defined class to be used in the callback function
# -----------------------------------------------------------------------------------------------
class user_app_callback_class(app_callback_class):
    def __init__(self):
        super().__init__()
        self.prev_frame_time = 0
        self.new_frame_time = 0
        self.ser = 1

# -----------------------------------------------------------------------------------------------
# User-defined callback function
# -----------------------------------------------------------------------------------------------
def visualize_detections(frame, basket_detected, backboard_detected, basket_info, backboard_info, conf, distance):
    """Hiển thị kết quả phát hiện lên frame"""
    offset = None
    direction = None

    if basket_detected:
        x1, y1, x2, y2, id = map(int, basket_info)
        w, h = x2 - x1, y2 - y1
        cx, cy = x1 + w // 2, y1 + h // 2
        
        # Lay offset
        offset = calculator_offset_stm32(frame, cx, x1, y2)
        # position = calculate_position(frame, cx)
        direction = auto_drive(frame, offset, 2)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
        draw_plus_sign(frame,(cx,cy),5,(0,255,0),1)
        cv2.putText(frame, f'basket {conf}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    elif backboard_detected:
        x1, y1, x2, y2, id = map(int, backboard_info)
        w, h = x2 - x1, y2 - y1
        cx, cy = x1 + w // 2, y1 + h // 2

        # Lay offset
        offset = calculator_offset_stm32(frame, cx, x1, y2)
        # position = calculate_position(frame, cx)
        direction = auto_drive(frame, offset, 2)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
        draw_plus_sign(frame,(cx,cy),5,(0,255,0),1)
        cv2.putText(frame, f'backboard {conf}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    return offset, direction


def send_offset_stm(offset,direction, ser):
    """Truyền dữ liệu khoảng cách và độ lệch xuống STM32"""
    if offset is not None:
        offset = int(offset)
    else:
        offset = 100

    if direction is not None:
        direction = int(direction)
    else:
        direction = 4

    create_stm32_message_1(offset, direction, ser)


def app_callback(pad, info, user_data):
    buffer = info.get_buffer()
    if buffer is None:
        return Gst.PadProbeReturn.OK

    # Lấy thông tin frame
    format, width, height = get_caps_from_pad(pad)
    
    # Lấy frame từ buffer
    frame = None
    if user_data.use_frame and format is not None and width is not None and height is not None:
        frame = get_numpy_from_buffer(buffer, format, width, height)
        

    # Lấy detections từ buffer
    detections = np.empty((0, 6))
    roi = hailo.get_roi_from_buffer(buffer)
    hailo_detections = roi.get_objects_typed(hailo.HAILO_DETECTION)

    # Chuyển đổi detections từ Hailo sang định dạng yêu cầu
    for detection in hailo_detections:
        bbox = detection.get_bbox()
        confidence = detection.get_confidence()
        label = detection.get_label()
        
        if confidence > 0.5:  # Ngưỡng tin cậy
            x1 = int(bbox.xmin() * width)
            y1 = int(bbox.ymin() * height) 
            x2 = int(bbox.xmax() * width)
            y2 = int(bbox.ymax() * height)
            conf = int(confidence * 100)
            class_id = 1 if label == "basket" else 0  
            
            new_detection = np.array([x1, y1, x2, y2, conf, class_id])
            detections = np.vstack((detections, new_detection))

    # Xử lý detections
    basket_detected, backboard_detected, basket_info, backboard_info, conf, num_objects = process_detections_no_track(detections)
    
    if frame is not None:
        # Hiển thị kết quả
        offset_2, direction = visualize_detections(frame, basket_detected, backboard_detected, basket_info, backboard_info, conf, 11)
        
        # Gửi dữ liệu xuống STM32
        # send_offset_stm(offset_2, direction, ser)

        # Tính và hiển thị FPS
        user_data.new_frame_time = cv2.getTickCount()
        fps = cv2.getTickFrequency() / (user_data.new_frame_time - user_data.prev_frame_time)
        user_data.prev_frame_time = user_data.new_frame_time
        cv2.putText(frame, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

        # Chuyển frame sang BGR để hiển thị
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        user_data.set_frame(frame)

    return Gst.PadProbeReturn.OK

if __name__ == "__main__":
    user_data = user_app_callback_class()
    app = GStreamerDetectionApp(app_callback, user_data)
    app.run()
