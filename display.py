import sys
import json
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QTableWidget, 
                               QTableWidgetItem, QLabel, QPushButton, QMessageBox, 
                               QHBoxLayout, QSpacerItem, QSizePolicy, QLineEdit, QComboBox)
from PySide6.QtCore import Qt, QSize, QTimer

import win32api
import win32con

# 색상 상수 정의
SUCCESS_COLOR = Qt.GlobalColor.green
DEFAULT_COLOR = Qt.GlobalColor.white

# Pywin32를 사용하여 지원 해상도/주사율/색상 깊이를 가져오는 함수
def get_supported_display_modes():
    """Retrieves all supported display modes for all attached monitors."""
    modes = {}
    device_num = 0
    while True:
        try:
            device = win32api.EnumDisplayDevices(None, device_num)
            print("device:",device)
            if device.StateFlags & win32con.DISPLAY_DEVICE_ATTACHED_TO_DESKTOP:
                device_name = device.DeviceString
                print("name:",device_name)
                
                current_settings = win32api.EnumDisplaySettings(device.DeviceName, win32con.ENUM_CURRENT_SETTINGS)
                
                device_modes = []
                mode_num = 0
                while True:
                    try:
                        settings = win32api.EnumDisplaySettings(device.DeviceName, mode_num)
                        
                        mode_data = {
                            'device_name': device.DeviceName,
                            'width': settings.PelsWidth,
                            'height': settings.PelsHeight,
                            'frequency': settings.DisplayFrequency,
                            'bits_per_pixel': settings.BitsPerPel,
                            'current': False
                        }
                        
                        # Compare against current settings to mark the active mode
                        if (settings.PelsWidth == current_settings.PelsWidth and
                            settings.PelsHeight == current_settings.PelsHeight and
                            settings.DisplayFrequency == current_settings.DisplayFrequency):
                            mode_data['current'] = True
                        
                        device_modes.append(mode_data)
                        
                        mode_num += 1
                    except win32api.error:
                        break
                modes[device_name] = device_modes
            device_num += 1
        except win32api.error:
            break
    return modes

def save_display_info_to_json(data):
    """Saves the display information to a JSON file with unique, incrementing keys."""
    json_data = {}
    key_counter = 1
    
    for device_name, modes_list in data.items():
        for mode_data in modes_list:
            json_data[str(key_counter)] = {
                'device_name': mode_data['device_name'],
                'width': mode_data['width'],
                'height': mode_data['height'],
                'frequency': mode_data['frequency'],
                'bits_per_pixel': mode_data['bits_per_pixel'],
                'current': mode_data['current']
            }
            key_counter += 1
    
    try:
        with open("displayInfo.json", "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=4)
        print("디스플레이 정보가 'displayInfo.json' 파일에 성공적으로 저장되었습니다.")
    except Exception as e:
        print(f"JSON 파일 저장 중 오류가 발생했습니다: {e}")

def get_current_display_info():
    """Gets the current display resolution, frequency, and bit depth."""
    info_list = []
    device_num = 0
    while True:
        try:
            device = win32api.EnumDisplayDevices(None, device_num)
            if device.StateFlags & win32con.DISPLAY_DEVICE_ATTACHED_TO_DESKTOP:
                settings = win32api.EnumDisplaySettings(device.DeviceName, win32con.ENUM_CURRENT_SETTINGS)
                info = (
                    f"[{device.DeviceString}] "
                    f"현재 해상도: {settings.PelsWidth}x{settings.PelsHeight}, "
                    f"주사율: {settings.DisplayFrequency}Hz, "
                    f"색상 깊이: {settings.BitsPerPel}bit"
                )
                info_list.append(info)
            device_num += 1
        except win32api.error:
            break
    return "\n".join(info_list)

class DisplayInfoApp(QWidget):
    def __init__(self):
        super().__init__()
        
        display_data = get_supported_display_modes()
        save_display_info_to_json(display_data)
        self.supported_modes_list = self.flatten_modes(display_data)

        self.initUI()
        self.populate_device_combo(display_data)
        self.populate_table_widget(display_data)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.change_next_setting)
        
        self.current_setting_index = 0
        self.previous_mode_data = None
        self.auto_change_active = False

    def initUI(self):
        self.setWindowTitle('디스플레이 설정 변경')
        self.setGeometry(100, 100, 1000, 500)
        self.setFocusPolicy(Qt.StrongFocus)

        main_layout = QVBoxLayout()
        
        top_layout = QHBoxLayout()
        
        # Display selection combo box
        self.device_combo = QComboBox()
        self.device_combo.setFixedWidth(200)
        
        # Current info label
        self.current_info_label = QLabel()
        self.current_info_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px; border: 1px solid gray;")
        
        # Time setting widgets
        time_setting_layout = QHBoxLayout()
        time_label = QLabel("자동 변경 시간(초):")
        self.time_edit = QLineEdit()
        self.time_edit.setText("10")
        self.time_edit.setFixedWidth(50)
        
        time_setting_layout.addWidget(time_label)
        time_setting_layout.addWidget(self.time_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.manual_change_button = QPushButton("선택하여 설정 변경")
        self.manual_change_button.clicked.connect(self.on_manual_change_clicked)
        self.manual_change_button.setFixedSize(QSize(150, 40))
        
        self.auto_change_button = QPushButton("자동 변경 시작")
        self.auto_change_button.clicked.connect(self.toggle_auto_change)
        self.auto_change_button.setFixedSize(QSize(150, 40))
        
        button_layout.addWidget(self.manual_change_button)
        button_layout.addWidget(self.auto_change_button)
        
        top_layout.addWidget(self.device_combo)
        top_layout.addWidget(self.current_info_label)
        top_layout.addLayout(time_setting_layout)
        top_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum))
        top_layout.addLayout(button_layout)
        
        main_layout.addLayout(top_layout)

        title_label = QLabel("지원하는 디스플레이 모드 목록:")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(title_label)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(7)
        self.table_widget.setHorizontalHeaderLabels(['키', '디스플레이', '너비', '높이', '주사율', '색상 깊이', '현재 설정'])
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.itemDoubleClicked.connect(self.on_table_item_double_clicked)
        
        main_layout.addWidget(self.table_widget)

        self.update_current_info_label()
        
        self.setLayout(main_layout)
    
    def populate_device_combo(self, supported_modes):
        """Populates the combo box with device names and connects its signal."""
        self.device_combo.clear()
        
        # Add an option to show all devices
        self.device_combo.addItem("모든 디스플레이", userData=None)
        
        # Add each unique device name to the combo box
        for device_name in supported_modes.keys():
            self.device_combo.addItem(device_name, userData=device_name)
        
        # Connect the signal to the filtering function
        self.device_combo.currentIndexChanged.connect(self.filter_table_by_device)
        
    def filter_table_by_device(self, index):
        """Filters the table to show only modes for the selected device."""
        selected_device_name = self.device_combo.itemData(index)
        
        supported_modes = get_supported_display_modes()
        self.populate_table_widget(supported_modes, filter_device=selected_device_name)

    def flatten_modes(self, data):
        """Converts the nested dictionary of modes into a single flat list."""
        modes_list = []
        for device_modes in data.values():
            print("device_modes:",device_modes)
            modes_list.extend(device_modes)
        return modes_list

    def keyPressEvent(self, event):
        """Handles key press events, specifically the ESC key."""
        if event.key() == Qt.Key.Key_Escape:
            self.stop_auto_change()
            QMessageBox.information(self, "자동 변경 중지", "ESC 키가 눌러져 자동 변경이 중지되었습니다.")
        super().keyPressEvent(event)

    def on_manual_change_clicked(self):
        selected_row = self.table_widget.currentRow()
        if selected_row >= 0:
            mode_data = self.table_widget.item(selected_row, 0).data(Qt.UserRole + 1)
            if mode_data:
                reply = QMessageBox.question(self, '설정 변경 확인', 
                                             f"해상도를 {mode_data['width']}x{mode_data['height']}에 주사율 {mode_data['frequency']}Hz, 색상 깊이 {mode_data['bits_per_pixel']}bit로 변경하시겠습니까?",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.apply_display_settings_logic(mode_data)
            else:
                QMessageBox.warning(self, "오류", "선택된 항목의 정보를 가져올 수 없습니다.")
        else:
            QMessageBox.warning(self, "경고", "목록에서 항목을 선택해주세요.")

    def toggle_auto_change(self):
        if self.auto_change_active:
            self.stop_auto_change()
        else:
            self.start_auto_change()

    def start_auto_change(self):
        if not self.supported_modes_list:
            QMessageBox.warning(self, "경고", "변경 가능한 디스플레이 모드가 없습니다.")
            return

        try:
            interval_sec = int(self.time_edit.text())
            if interval_sec <= 0:
                interval_sec = 10
        except ValueError:
            QMessageBox.warning(self, "경고", "유효한 숫자를 입력하세요. 기본값(10초)으로 설정됩니다.")
            interval_sec = 10
            self.time_edit.setText("10")

        self.timer.setInterval(interval_sec * 1000)
        
        self.auto_change_active = True
        self.auto_change_button.setText("자동 변경 중지 (ESC)")
        self.manual_change_button.setEnabled(False)
        self.device_combo.setEnabled(False)
        
        selected_row = self.table_widget.currentRow()
        if selected_row >= 0:
            self.current_setting_index = selected_row
        else:
            self.current_setting_index = 0

        self.previous_mode_data = self.supported_modes_list[self.current_setting_index]
        self.timer.start()
        self.change_next_setting()

    def stop_auto_change(self):
        self.timer.stop()
        self.auto_change_active = False
        self.auto_change_button.setText("자동 변경 시작")
        self.manual_change_button.setEnabled(True)
        self.device_combo.setEnabled(True)

    def change_next_setting(self):
        if self.current_setting_index >= len(self.supported_modes_list):
            self.stop_auto_change()
            QMessageBox.information(self, "자동 변경 완료", "모든 디스플레이 설정 변경을 완료했습니다.")
            return

        next_mode = self.supported_modes_list[self.current_setting_index]
        
        current_display_settings = win32api.EnumDisplaySettings(next_mode['device_name'], win32con.ENUM_CURRENT_SETTINGS)
        self.previous_mode_data = {
            'device_name': next_mode['device_name'],
            'width': current_display_settings.PelsWidth,
            'height': current_display_settings.PelsHeight,
            'frequency': current_display_settings.DisplayFrequency,
            'bits_per_pixel': current_display_settings.BitsPerPel
        }

        success = self.apply_display_settings_logic(next_mode)
        
        if not success:
            QMessageBox.critical(self, "설정 변경 오류", "설정 변경에 실패했습니다. 이전 설정으로 복구합니다.")
            self.revert_to_previous_setting()
            self.stop_auto_change()
            return
            
        self.current_setting_index += 1

    def revert_to_previous_setting(self):
        if self.previous_mode_data:
            self.apply_display_settings_logic(self.previous_mode_data)
            self.update_current_info_label()
            self.populate_table_widget(get_supported_display_modes())

    def update_current_info_label(self):
        """현재 정보를 가져와 라벨을 업데이트합니다."""
        current_info = get_current_display_info()
        self.current_info_label.setText(current_info)

    def populate_table_widget(self, supported_modes, filter_device=None):
        self.table_widget.setSortingEnabled(False)
        
        if not supported_modes:
            QMessageBox.warning(self, "오류", "지원하는 디스플레이 정보를 가져올 수 없습니다.")
            return

        self.table_widget.setRowCount(0)
        row_count = 0
        key_counter = 1
        
        for device_name, modes_list in supported_modes.items():
            if filter_device and device_name != filter_device:
                continue
                
            for mode_data in modes_list:
                self.table_widget.insertRow(row_count)
                
                key_item = QTableWidgetItem(f"{key_counter}")
                key_item.setData(Qt.UserRole + 1, mode_data)
                
                width_item = QTableWidgetItem(f"{mode_data['width']}")
                height_item = QTableWidgetItem(f"{mode_data['height']}")
                frequency_item = QTableWidgetItem(f"{mode_data['frequency']}")
                bits_item = QTableWidgetItem(f"{mode_data['bits_per_pixel']}")
                
                self.table_widget.setItem(row_count, 0, key_item)
                self.table_widget.setItem(row_count, 1, QTableWidgetItem(device_name))
                self.table_widget.setItem(row_count, 2, width_item)
                self.table_widget.setItem(row_count, 3, height_item)
                self.table_widget.setItem(row_count, 4, frequency_item)
                self.table_widget.setItem(row_count, 5, bits_item)
                
                current_status = '✔' if mode_data['current'] else ''
                current_item = QTableWidgetItem(current_status)
                current_item.setTextAlignment(Qt.AlignCenter)
                self.table_widget.setItem(row_count, 6, current_item)
                
                is_current_row = mode_data['current']
                
                for col in range(self.table_widget.columnCount()):
                    item = self.table_widget.item(row_count, col)
                    if item:
                        item.setBackground(SUCCESS_COLOR if is_current_row else DEFAULT_COLOR)
                
                row_count += 1
                key_counter += 1
        
        self.table_widget.resizeColumnsToContents()
        self.table_widget.setSortingEnabled(True)

    def on_table_item_double_clicked(self, item):
        row = item.row()
        mode_data = self.table_widget.item(row, 0).data(Qt.UserRole + 1)
        if not mode_data:
            return

        reply = QMessageBox.question(self, '설정 변경 확인', 
                                     f"해상도를 {mode_data['width']}x{mode_data['height']}에 주사율 {mode_data['frequency']}Hz, 색상 깊이 {mode_data['bits_per_pixel']}bit로 변경하시겠습니까?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.apply_display_settings_logic(mode_data)

    def apply_display_settings_logic(self, mode_data):
        try:
            dm = win32api.EnumDisplaySettings(mode_data['device_name'], 0)
            dm.PelsWidth = mode_data['width']
            dm.PelsHeight = mode_data['height']
            dm.DisplayFrequency = mode_data['frequency']
            dm.BitsPerPel = mode_data['bits_per_pixel']
            
            result = win32api.ChangeDisplaySettingsEx(mode_data['device_name'], dm, 0)
            
            if result == win32con.DISP_CHANGE_SUCCESSFUL:
                print("설정 변경 성공")
                self.update_current_info_label()
                updated_data = get_supported_display_modes()
                self.populate_table_widget(updated_data)
                return True
            else:
                print(f"설정 변경 실패: {result}")
                return False
        except Exception as e:
            print(f"설정 변경 중 오류: {e}")
            return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DisplayInfoApp()
    ex.show()
    sys.exit(app.exec())
