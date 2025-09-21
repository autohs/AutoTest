# server_app.py

import sys
import socket
import threading
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QLineEdit, QPushButton, QListWidget)
from PySide6.QtCore import Signal, QThread, QObject, Slot
import os

class UdpFileServer(QObject):
    message_received = Signal(str)

    def __init__(self, port):
        super().__init__()
        self.port = port
        self.running = False
        self.sock = None
        self.receiving_file = False
        self.file_path = None
        self.file_handle = None

    @Slot()
    def run(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind(('0.0.0.0', self.port))
            self.sock.settimeout(1.0) # 논블로킹을 위한 타임아웃 설정
            self.running = True
            self.message_received.emit(f"서버가 포트 {self.port}에서 대기 중입니다.")
            
            while self.running:
                try:
                    data, addr = self.sock.recvfrom(1024)
                    # 수신된 데이터가 텍스트 메시지인지 확인
                    try:
                        message = data.decode('utf-8')
                        if message.startswith("START_FILE:"):
                            filename = "rx_" + message.replace("START_FILE:", "").strip()
                            self.file_path = os.path.join(os.getcwd(), filename)
                            self.file_handle = open(self.file_path, 'wb')
                            self.receiving_file = True
                            self.message_received.emit(f"파일 '{filename}' 수신을 시작합니다...")
                            print("file name")
                        elif message == "END_FILE":
                            print("end_file1")
                            if self.receiving_file and self.file_handle:
                                print("end_file2")
                                self.file_handle.close()
                                self.file_handle = None
                                self.receiving_file = False
                                self.message_received.emit(f"파일 '{os.path.basename(self.file_path)}' 수신 및 저장이 완료되었습니다.")
                                self.file_path = None
                        else:
                            #print("rx1",data,"\n")
                            if self.receiving_file and self.file_handle:
                                print("rx2",data,"\n")
                                self.file_handle.write(data)
                                self.message_received.emit(f"데이터 패킷을 수신했습니다. ({len(data)} bytes)")

                            
                    except UnicodeDecodeError:
                        # 텍스트로 디코딩할 수 없는 경우, 파일 데이터로 간주
                        print("rx2",data,"\n")
                        
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        self.message_received.emit(f"오류: {e}")
                    self.running = False
        except Exception as e:
            self.message_received.emit(f"시작 오류: {e}")
            self.running = False
        finally:
            if self.sock:
                self.sock.close()
            self.message_received.emit("서버가 중지되었습니다.")

    def stop_server(self):
        self.running = False
        if self.sock:
            self.sock.close()
        if self.file_handle:
            self.file_handle.close()

class ServerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UDP 파일 서버")
        self.setGeometry(100, 100, 450, 400)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        self.port_layout = QHBoxLayout()
        self.port_label = QLabel("포트:")
        self.port_edit = QLineEdit("12345")
        self.start_button = QPushButton("서버 시작")
        self.stop_button = QPushButton("서버 중지")
        self.stop_button.setEnabled(False)
        self.port_layout.addWidget(self.port_label)
        self.port_layout.addWidget(self.port_edit)
        self.port_layout.addWidget(self.start_button)
        self.port_layout.addWidget(self.stop_button)
        self.layout.addLayout(self.port_layout)
        
        self.message_list = QListWidget()
        self.layout.addWidget(self.message_list)
        
        self.start_button.clicked.connect(self.start_server)
        self.stop_button.clicked.connect(self.stop_server)
        
        self.server_thread = None
        self.server_worker = None

    @Slot()
    def start_server(self):
        port_text = self.port_edit.text()
        if not port_text.isdigit():
            self.message_list.addItem("오류: 유효한 포트 번호를 입력하세요.")
            return

        port = int(port_text)
        self.server_thread = QThread()
        self.server_worker = UdpFileServer(port)
        self.server_worker.moveToThread(self.server_thread)
        self.server_thread.started.connect(self.server_worker.run)
        self.server_worker.message_received.connect(self.update_log)
        self.server_thread.start()
        
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.port_edit.setEnabled(False)

    @Slot()
    def stop_server(self):
        if self.server_worker:
            self.server_worker.stop_server()
            self.server_thread.quit()
            self.server_thread.wait()
            self.server_worker = None
            self.server_thread = None
            
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.port_edit.setEnabled(True)

    @Slot(str)
    def update_log(self, message):
        self.message_list.addItem(message)

    def closeEvent(self, event):
        self.stop_server()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ServerGUI()
    window.show()
    sys.exit(app.exec())
