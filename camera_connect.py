# import cv2

# ip_camera_url = 'http://169.254.117.229:8016/video'

# cap = cv2.VideoCapture(ip_camera_url)

# if not cap.isOpened():
#     print("IP카메라에 접속할 수 없습니다.")
#     exit()

# while True:
#     ret, frame = cap.read()

#     if not ret:
#         print("프레임을 읽어올 수 없습니다.")
#         break

#     cv2.imshow("IP camera stream", frame)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()

import cv2

# IP 카메라의 URL을 설정합니다. (예: rtsp://username:password@camera_ip:port/stream)
ip_camera_url = "rtsp://admin:yonsei1!@192.168.0.56:8554/stream"
# ip_camera_url = 'http://192.168.0.56'

# 비디오 캡처 객체를 생성하여 IP 카메라 스트림을 읽습니다.
cap = cv2.VideoCapture(ip_camera_url)

if not cap.isOpened():
    print("Error: Cannot open IP camera stream")
    exit()







while True:
    # 프레임을 읽어옵니다.
    ret, frame = cap.read()

    if not ret:
        print("Error: Cannot read frame from IP camera stream")
        break

    # 프레임을 화면에 표시합니다.
    cv2.imshow("IP Camera Stream", frame)

    # 'q' 키를 누르면 종료합니다.
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 자원을 해제하고 창을 닫습니다.
cap.release()
cv2.destroyAllWindows()
