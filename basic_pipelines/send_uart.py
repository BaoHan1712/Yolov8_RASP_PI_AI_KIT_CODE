import struct
from utils import *

def calculator_offset_stm32(frame, cx, x1, y2):
    number =1
    offset = offset_backboard(frame, cx)
    """  Tính độ lệch của rổ
        offset < 0 -> map sang 1-99
        offset = 0 -> map thành 100  -
        offset > 0 -> map sang 101-254"""
    
    if offset <= -number:
        # Map giá trị âm sang 1
        mapped_value =max(0, min(99, int(offset) + 100))
        cv2.putText(frame, f'lech trai: {abs(offset)} px', (x1, y2 + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    elif offset >= number:
        # Map giá trị dương sang 101-254 
        mapped_value = max(101, min(200, int(offset) + 100))
        
        cv2.putText(frame, f'lech phai: {abs(offset)} px', (x1, y2 + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    else:
        mapped_value = 100
        cv2.putText(frame, f'chuan', (x1, y2 + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    return mapped_value

def create_stm32_message_1(offset, distance, position, ser):
    """
    Tạo gói tin với cấu trúc:
    - Start Byte: 0x02
    - Data1: Offset (1 byte)
    - Data2: Distance (2 bytes) 
    - Data3: Position (2 bytes) - Có dấu
    - Checksum: Tổng modulo 256
    - End Byte: 0x03
    """
    # Kiểm tra và gán giá trị mặc định nếu tham số là None
    offset = 100 if offset is None else max(1, min(200, int(offset)))
    distance = 55555 if distance is None else max(2, min(65510, int(distance)))
    if position is None:
        position = 555
    
    # Chuyển position thành số 16-bit có dấu
    position_bytes = position.to_bytes(2, byteorder='big', signed=True)
    
    header = 0x02
    end_byte = 0x03
    
    # Tính checksum với position_bytes
    checksum = (header + offset + (distance >> 8) + (distance & 0xFF) + 
               position_bytes[0] + position_bytes[1]) % 256
    
    try:
        packet = (struct.pack(">B", header) + 
                 struct.pack(">B", offset) + 
                 struct.pack(">H", distance) + 
                 position_bytes +  # Sử dụng bytes có dấu
                 struct.pack(">B", checksum) + 
                 struct.pack(">B", end_byte))
        # ser.write(packet)
        print(f"Offset: {offset}, Distance: {distance}, Position: {position}")
    except struct.error as e:
        print(f"Error creating STM32 message: {e}")
        print(f"Offset: {offset}, Distance: {distance}, Position: {position}")
