import sys
import socket
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QLineEdit, QPushButton, QListWidget, QFileDialog)
from PySide6.QtCore import Slot

class ClientGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UDP 파일 클라이언트")
        self.setGeometry(600, 100, 450, 400)

        self.udp_socket = None
        self.selected_file_path = None
        self.target_address = None
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # 서버 주소 입력 위젯
        self.address_layout = QHBoxLayout()
        self.ip_label = QLabel("서버 IP:")
        self.ip_edit = QLineEdit("127.0.0.1")
        self.port_label = QLabel("포트:")
        self.port_edit = QLineEdit("12345")
        self.address_layout.addWidget(self.ip_label)
        self.address_layout.addWidget(self.ip_edit)
        self.address_layout.addWidget(self.port_label)
        self.address_layout.addWidget(self.port_edit)
        self.layout.addLayout(self.address_layout)

        # 파일 선택 및 전송 위젯
        self.file_layout = QHBoxLayout()
        self.select_button = QPushButton("파일 선택")
        self.file_path_label = QLabel("선택된 파일: 없음")
        self.file_layout.addWidget(self.select_button)
        self.file_layout.addWidget(self.file_path_label)
        self.layout.addLayout(self.file_layout)

        self.send_button = QPushButton("파일 전송")
        self.send_button.setEnabled(False)
        self.layout.addWidget(self.send_button)

        # 상태 메시지 리스트 위젯
        self.status_list = QListWidget()
        self.layout.addWidget(self.status_list)

        # 시그널과 슬롯 연결
        self.select_button.clicked.connect(self.select_file)
        self.send_button.clicked.connect(self.send_file)

    @Slot()
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "파일 선택")
        if file_path:
            self.selected_file_path = file_path
            self.file_path_label.setText(f"선택된 파일: {os.path.basename(file_path)}")
            self.send_button.setEnabled(True)
            self.status_list.addItem(f"'{os.path.basename(file_path)}' 파일이 선택되었습니다.")

    @Slot()
    def send_file(self):
        if not self.selected_file_path:
            self.status_list.addItem("오류: 먼저 파일을 선택하세요.")
            return

        ip_address = self.ip_edit.text()
        port_text = self.port_edit.text()
        if not ip_address or not port_text.isdigit():
            self.status_list.addItem("오류: 유효한 서버 주소와 포트를 입력하세요.")
            return

        port = int(port_text)
        self.target_address = (ip_address, port)
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                filename = os.path.basename(self.selected_file_path)
                
                start_message = f"START_FILE:{filename}"
                s.sendto(start_message.encode('utf-8'), self.target_address)
                self.status_list.addItem(f"파일 전송 시작: '{filename}'")
                
                with open(self.selected_file_path, 'rb') as f:
                    while True:
                        chunk = f.read(1024)
                        if not chunk:
                            break
                        s.sendto(chunk, self.target_address)
                
                s.sendto("END_FILE".encode('utf-8'), self.target_address)
                self.status_list.addItem("파일 전송이 완료되었습니다.")
                self.status_list.addItem("서버의 저장을 확인하세요.")
                
        except Exception as e:
            self.status_list.addItem(f"전송 오류: {e}")

    def closeEvent(self, event):
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClientGUI()
    window.show()
    sys.exit(app.exec())