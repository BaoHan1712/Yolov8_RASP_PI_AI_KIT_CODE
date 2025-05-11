import cv2
import numpy as np

def nothing(x):
    pass

# Tạo cửa sổ và trackbars để điều chỉnh giá trị HSV
cv2.namedWindow("Trackbars")
cv2.createTrackbar("Low H", "Trackbars", 0, 179, nothing)
cv2.createTrackbar("High H", "Trackbars", 10, 179, nothing)
cv2.createTrackbar("Low S", "Trackbars", 100, 255, nothing)
cv2.createTrackbar("High S", "Trackbars", 255, 255, nothing)
cv2.createTrackbar("Low V", "Trackbars", 100, 255, nothing)
cv2.createTrackbar("High V", "Trackbars", 255, 255, nothing)

cap = cv2.VideoCapture(0)  # Mở webcam

while True:
    ret, frame = cap.read()
    if not ret:
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # Chuyển sang không gian màu HSV

    # Đọc giá trị từ trackbars
    l_h = cv2.getTrackbarPos("Low H", "Trackbars")
    h_h = cv2.getTrackbarPos("High H", "Trackbars")
    l_s = cv2.getTrackbarPos("Low S", "Trackbars")
    h_s = cv2.getTrackbarPos("High S", "Trackbars")
    l_v = cv2.getTrackbarPos("Low V", "Trackbars")
    h_v = cv2.getTrackbarPos("High V", "Trackbars")

    # Tạo mask lọc màu đỏ (do màu đỏ nằm ở cả hai đầu của Hue trong HSV)
    lower_red1 = np.array([l_h, l_s, l_v])
    upper_red1 = np.array([h_h, h_s, h_v])
    
    lower_red2 = np.array([170, l_s, l_v])
    upper_red2 = np.array([179, h_s, h_v])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    mask = mask1 + mask2  # Kết hợp cả hai vùng màu đỏ
    result = cv2.bitwise_and(frame, frame, mask=mask)

    # Hiển thị kết quả
    cv2.imshow("Original", frame)
    cv2.imshow("Mask", mask)
    cv2.imshow("Result", result)

    if cv2.waitKey(1) & 0xFF == 27:  # Nhấn 'Esc' để thoát
        break

cap.release()
cv2.destroyAllWindows()
