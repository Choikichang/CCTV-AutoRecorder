from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
import cv2
import time
import os
from collections import deque
from optical_flow import PouringDetector  # 예측 모듈 임포트
import sys

class CameraApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Camera IP or Video File Input")

        self.label = QLabel("Enter Camera IP or Video Path:", self)
        self.line_edit = QLineEdit(self)
        self.button = QPushButton("Start Streaming or Video", self)
        self.button.clicked.connect(self.start_streaming_or_video)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

        self.input_source = None
        self.frame_buffer = deque(maxlen=10)
        self.prediction_results = deque(maxlen=10)
        self.cap = None

        # 상태 관리 변수들
        self.recording = False
        self.record_start_time = None
        self.current_video_writer = None
        self.last_false_time = None
        self.video_file_path = None  # 녹화 파일 경로를 초기화
        self.count = 0

        # 예측기 초기화
        self.detector = PouringDetector(motion_threshold=0.1, buffer_frames=30)

    def start_streaming_or_video(self):
        self.input_source = self.line_edit.text()
        if self.input_source:
            if self.input_source.startswith("rtsp://"):
                # IP 카메라 스트리밍
                path_video = f"rtsp://admin:yonsei1!@{self.input_source}/trackID=1"
            else:
                # 동영상 파일 경로로 처리
                path_video = self.input_source
            self.capture_video(path_video)

    def capture_video(self, path_video):
        self.cap = cv2.VideoCapture(path_video)
        if not self.cap.isOpened():
            print("Failed to open video or camera stream.")
            return

        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("End of video or failed to read frame.")
                    break

                # 예측 및 결과 처리
                self.run_prediction(frame)

                cv2.imshow('Video/Camera Stream', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            self.cap.release()
            cv2.destroyAllWindows()

    def run_prediction(self, frame):
        result = self.detector.detect_pouring(frame)  # 새로운 모듈에서 예측 호출
        self.prediction_results.append(result)

        true_count = self.prediction_results.count(True)
        false_count = self.prediction_results.count(False)

        if not self.recording and true_count >= 2:
            self.start_recording(frame)

        if self.recording and false_count >= 5:
            self.stop_recording()
            self.check_and_discard_video()

    def start_recording(self, frame):
        self.recording = True
        self.record_start_time = time.time()
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        self.video_file_path = f'output_{timestamp}.mp4'  # 타임스탬프를 사용한 파일명
        self.current_video_writer = cv2.VideoWriter(
            self.video_file_path, 
            cv2.VideoWriter_fourcc(*'X264'), 
            20.0, 
            (frame.shape[1], frame.shape[0])
        )
        print("Recording started.")
        for frame in self.frame_buffer:
            self.current_video_writer.write(frame)

    def stop_recording(self):
        if self.current_video_writer:
            self.current_video_writer.release()
            self.current_video_writer = None
        self.recording = False
        self.last_false_time = time.time()
        print("Recording stopped.")

        recording_duration = self.last_false_time - self.record_start_time
        if recording_duration < 5:  # 5초 미만일 경우
            print(f"Recording duration was {recording_duration} seconds, checking for discard...")
            self.check_and_discard_video(force_discard=True)
        else:
            print("Recording stopped, video saved.")
            self.check_and_discard_video(force_discard=False)

    def check_and_discard_video(self, force_discard=False):
        # 녹화 중지 후 5초 
        self.recording = False
        self.record_start_time = None
        self.current_video_writer = None
        self.last_false_time = None
        if force_discard:
            if os.path.exists(self.video_file_path):
                os.remove(self.video_file_path)
                print("Video discarded.")
            self.video_file_path = None
        else:
            self.video_file_path = None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    camera_app = CameraApp()
    camera_app.show()
    sys.exit(app.exec_())
