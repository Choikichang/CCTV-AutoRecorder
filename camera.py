import sys
import cv2
import numpy as np
import pyautogui
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QSpinBox, QFileDialog, QLineEdit, QMessageBox
from PyQt5.QtCore import QRect, QTimer, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QPainter, QPen, QColor
import os

class ScreenRecorder(QThread):
    frame_captured = pyqtSignal(np.ndarray)

    def __init__(self, rect, fps):
        super().__init__()
        self.rect = rect
        self.fps = fps
        self.recording = False

    def run(self):
        self.recording = True
        while self.recording:
            img = pyautogui.screenshot(region=(self.rect.x(), self.rect.y(), self.rect.width(), self.rect.height()))
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            self.frame_captured.emit(frame)
            self.msleep(int(1000 / self.fps))

    def stop(self):
        self.recording = False
        self.wait()

class RecorderApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.rect = QRect(100, 100, 640, 480)  # 기본 사각형 영역
        self.recording = False
        self.updating_rect = False
        self.stop_timer = QTimer(self)  # Stop timer 초기화

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Screen Recorder')

        # 사각형 영역 설정을 위한 스핀박스
        self.x_spinbox = QSpinBox(self)
        self.x_spinbox.setRange(0, 1920)
        self.x_spinbox.setValue(100)
        self.y_spinbox = QSpinBox(self)
        self.y_spinbox.setRange(0, 1080)
        self.y_spinbox.setValue(100)
        self.width_spinbox = QSpinBox(self)
        self.width_spinbox.setRange(0, 1920)
        self.width_spinbox.setValue(640)
        self.height_spinbox = QSpinBox(self)
        self.height_spinbox.setRange(0, 1080)
        self.height_spinbox.setValue(480)

        # 프레임 속도 설정을 위한 스핀박스
        self.fps_spinbox = QSpinBox(self)
        self.fps_spinbox.setRange(1, 60)
        self.fps_spinbox.setValue(10)

        # 공장기호 입력을 위한 라인 에디트
        self.factory_edit = QLineEdit(self)
        self.factory_edit.setPlaceholderText('공장 기호 입력 (예: 서서울 SS)')

        # Batch 번호 입력을 위한 라인 에디트
        self.date_edit = QLineEdit(self)
        self.date_edit.setPlaceholderText('연월일 입력')

        # Batch 번호 입력을 위한 라인 에디트
        self.batch_edit = QLineEdit(self)
        self.batch_edit.setPlaceholderText('배치 번호 입력')

        # 슬럼프 수치 입력을 위한 라인 에디트
        self.slump_edit = QLineEdit(self)
        self.slump_edit.setPlaceholderText('슬럼프 수치 입력')

        # 강도 입력을 위한 라인 에디트
        self.strength_edit = QLineEdit(self)
        self.strength_edit.setPlaceholderText('강도 입력')

        # 이전 배치 슬럼프 입력을 위한 라인 에디트
        self.previous_edit = QLineEdit(self)
        self.previous_edit.setPlaceholderText('이전 배치 슬럼프 입력')

        # 카메라 종류 입력을 위한 라인 에디트
        self.camera_edit = QLineEdit(self)
        self.camera_edit.setText('01')

        # 슬럼프 측정값 입력을 위한 라인 에디트
        self.real_slump_edit = QLineEdit(self)
        self.real_slump_edit.setText('000')

        # 추가 정보 입력을 위한 라인 에디트
        self.additional_edit = QLineEdit(self)
        self.additional_edit.setText('000')

        # 저장 경로를 위한 라인 에디트와 버튼
        self.path_edit = QLineEdit(self)
        self.browse_btn = QPushButton('Browse', self)
        self.browse_btn.clicked.connect(self.browse_path)

        # 영역 업데이트 버튼
        self.update_rect_btn = QPushButton('Update Rect', self)
        self.update_rect_btn.clicked.connect(self.enable_update_rect)

        # 녹화 시작 및 중지 버튼
        self.start_btn = QPushButton('Start Recording', self)
        self.start_btn.clicked.connect(self.start_recording)
        self.stop_btn = QPushButton('Stop Recording', self)
        self.stop_btn.clicked.connect(self.stop_recording)
        self.stop_btn.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(QLabel('X:'))
        layout.addWidget(self.x_spinbox)
        layout.addWidget(QLabel('Y:'))
        layout.addWidget(self.y_spinbox)
        layout.addWidget(QLabel('Width:'))
        layout.addWidget(self.width_spinbox)
        layout.addWidget(QLabel('Height:'))
        layout.addWidget(self.height_spinbox)
        layout.addWidget(QLabel('FPS:'))
        layout.addWidget(self.fps_spinbox)

        layout.addWidget(QLabel('공장 기호:'))
        layout.addWidget(self.factory_edit)
        layout.addWidget(QLabel('연월일 :'))
        layout.addWidget(self.date_edit)
        layout.addWidget(QLabel('배치 번호 :'))
        layout.addWidget(self.batch_edit)
        layout.addWidget(QLabel('슬럼프 수치 :'))
        layout.addWidget(self.slump_edit)
        layout.addWidget(QLabel('강도 :'))
        layout.addWidget(self.strength_edit)
        layout.addWidget(QLabel('이전 배치 슬럼프 :'))
        layout.addWidget(self.previous_edit)
        layout.addWidget(QLabel('카메라 종류 :'))
        layout.addWidget(self.camera_edit)        
        layout.addWidget(QLabel('슬럼프 측정 값 :'))
        layout.addWidget(self.real_slump_edit)
        layout.addWidget(QLabel('추가 정보 :'))
        layout.addWidget(self.additional_edit)

        layout.addWidget(QLabel('Save Path:'))
        layout.addWidget(self.path_edit)
        layout.addWidget(self.browse_btn)
        layout.addWidget(self.update_rect_btn)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.recorder = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.out = None

        self.stop_timer.timeout.connect(self.stop_recording)  # Stop timer timeout 연결

    def enable_update_rect(self):
        self.updating_rect = True

    def browse_path(self):
        save_path = QFileDialog.getExistingDirectory(self, 'Select Directory')
        if save_path:
            self.path_edit.setText(save_path)

    def start_recording(self):
        save_path = self.path_edit.text()

        factory_name = self.factory_edit.text()
        date_number = self.date_edit.text()
        batch_number = self.batch_edit.text()
        slump_number = self.slump_edit.text()
        strength_number = self.strength_edit.text()
        previous_slump_number = self.previous_edit.text()
        camera_number = self.camera_edit.text()
        real_slump_number = self.real_slump_edit.text()
        additional_number = self.additional_edit.text()


        if not save_path:
            QMessageBox.warning(self, 'Error', 'Browse 를 통해 저장경로를 선택하세요.')
            return

        if not factory_name:
            QMessageBox.warning(self, 'Error', '공장 기호를 입력하세요.')
            return
        
        if not date_number:
            QMessageBox.warning(self, 'Error', '동영상 촬영 날짜를 입력하세요 6자리.')
            return

        if not batch_number:
            QMessageBox.warning(self, 'Error', '배치 번호를 입력하세요.')
            return
        
        if not slump_number:
            QMessageBox.warning(self, 'Error', '슬럼프 값을 입력하세요.')
            return
                
        if not strength_number:
            QMessageBox.warning(self, 'Error', '강도 값을 입력하세요.')
            return
        
        if not previous_slump_number:
            QMessageBox.warning(self, 'Error', '이전 배치 슬럼프 값을 입력하세요.')
            return
        
        if not camera_number:
            QMessageBox.warning(self, 'Error', '카메라 번호를 입력하세요.')
            return
        
        if not real_slump_number:
            QMessageBox.warning(self, 'Error', '슬럼프 측정값을 입력하세요.')
            return

        if not additional_number:
            QMessageBox.warning(self, 'Error', '추가 정보를 입력하세요.')
            return

        save_file = os.path.join(save_path, f'{factory_name}_{date_number}_B{batch_number}_S{slump_number}_M{strength_number}_\
(P{previous_slump_number})_C{camera_number}_T{real_slump_number}_A{additional_number}.avi')

        self.rect = QRect(self.x_spinbox.value(), self.y_spinbox.value(), self.width_spinbox.value(), self.height_spinbox.value())
        fps = self.fps_spinbox.value()
        self.recorder = ScreenRecorder(self.rect, fps)
        self.recorder.frame_captured.connect(self.show_frame)
        self.recorder.start()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        # 비디오 저장 설정
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.out = cv2.VideoWriter(save_file, fourcc, fps, (self.rect.width(), self.rect.height()))

        self.stop_timer.start(14000)  # 10초 후에 녹화 중지

    def stop_recording(self):
        if self.recorder:
            self.recorder.stop()
            self.recorder = None
        if self.out:
            self.out.release()
            self.out = None
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.stop_timer.stop()  # 타이머 중지

    def show_frame(self, frame):
        if self.out:
            self.out.write(frame)
        # OpenCV로 화면에 표시
        cv2.imshow('Recording', frame)
        cv2.waitKey(1)

    def update_frame(self):
        if self.recorder:
            self.recorder.capture_frame()

    def closeEvent(self, event):
        self.stop_recording()
        cv2.destroyAllWindows()
        event.accept()

    def mousePressEvent(self, event):
        if self.updating_rect and event.button() == Qt.LeftButton:
            self.x_spinbox.setValue(event.x())
            self.y_spinbox.setValue(event.y())
            self.updating_rect = False

    def mouseReleaseEvent(self, event):
        pass

    def paintEvent(self, event):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RecorderApp()
    ex.show()
    sys.exit(app.exec_())
