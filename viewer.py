import sys
import os
import datetime
import shutil
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                               QLineEdit, QPushButton, QComboBox, QListWidget,
                               QListWidgetItem, QTableWidget, QTableWidgetItem,
                               QFileDialog, QHeaderView, QSplitter, QMenu,
                               QAbstractItemView, QLabel, QTreeView)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QSize, Qt, QDir
from PySide6.QtWidgets import QFileSystemModel

# 클립보드에 복사/잘라내기 상태를 저장하는 전역 변수
clipboard_files = []
is_cut_operation = False

# 이미지를 표시하는 뷰어 위젯
class ImageViewer(QWidget):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle(os.path.basename(image_path))
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout(self)
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)
        
        self.load_image(image_path)
    
    def load_image(self, image_path):
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)

# 파일 목록을 표시하고 관리하는 위젯
class ViewerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.current_folder = ""
        self.image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
        
        self.initUI()
    
    def initUI(self):
        main_layout = QVBoxLayout(self)
        
        folder_layout = QHBoxLayout()
        self.folder_path_edit = QLineEdit(self)
        self.folder_path_edit.setReadOnly(True)
        self.select_folder_button = QPushButton("폴더 선택", self)
        self.select_folder_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_path_edit)
        folder_layout.addWidget(self.select_folder_button)
        
        option_layout = QHBoxLayout()
        self.view_option_combo = QComboBox(self)
        self.view_option_combo.addItem("큰 아이콘")
        self.view_option_combo.addItem("보통 아이콘")
        self.view_option_combo.addItem("작은 아이콘")
        self.view_option_combo.addItem("자세히")
        self.view_option_combo.currentIndexChanged.connect(self.change_view_mode)
        option_layout.addWidget(self.view_option_combo)
        option_layout.addStretch()

        self.image_list_widget = QListWidget(self)
        self.image_list_widget.setResizeMode(QListWidget.Adjust)
        self.image_list_widget.setSpacing(10)
        self.image_list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.image_list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.image_list_widget.customContextMenuRequested.connect(self.show_context_menu)
        self.image_list_widget.itemDoubleClicked.connect(self.open_image_viewer)

        self.image_table_widget = QTableWidget(self)
        self.image_table_widget.setColumnCount(4)
        self.image_table_widget.setHorizontalHeaderLabels(["이름", "날짜", "유형", "크기"])
        self.image_table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.image_table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.image_table_widget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.image_table_widget.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.image_table_widget.verticalHeader().hide()
        self.image_table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.image_table_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.image_table_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.image_table_widget.customContextMenuRequested.connect(self.show_context_menu)
        self.image_table_widget.cellDoubleClicked.connect(self.open_image_viewer_table)

        self.image_table_widget.hide()

        main_layout.addLayout(folder_layout)
        main_layout.addLayout(option_layout)
        main_layout.addWidget(self.image_list_widget)
        main_layout.addWidget(self.image_table_widget)
    
    def open_image_viewer(self, item):
        file_path = os.path.join(self.current_folder, item.text())
        if os.path.isfile(file_path):
            self.viewer = ImageViewer(file_path)
            self.viewer.show()

    def open_image_viewer_table(self, row, column):
        file_name = self.image_table_widget.item(row, 0).text()
        file_path = os.path.join(self.current_folder, file_name)
        if os.path.isfile(file_path):
            self.viewer = ImageViewer(file_path)
            self.viewer.show()

    def show_context_menu(self, pos):
        menu = QMenu(self)
        copy_action = menu.addAction("복사")
        cut_action = menu.addAction("잘라내기")
        paste_action = menu.addAction("붙여넣기")
        
        if self.image_list_widget.isVisible() and not self.image_list_widget.selectedItems():
            copy_action.setEnabled(False)
            cut_action.setEnabled(False)
        elif self.image_table_widget.isVisible() and not self.image_table_widget.selectedItems():
            copy_action.setEnabled(False)
            cut_action.setEnabled(False)
            
        if not clipboard_files:
            paste_action.setEnabled(False)

        action = menu.exec(self.mapToGlobal(pos))
        
        if action == copy_action:
            self.copy_cut_files(is_cut=False)
        elif action == cut_action:
            self.copy_cut_files(is_cut=True)
        elif action == paste_action:
            self.paste_files()
    
    def copy_cut_files(self, is_cut):
        global clipboard_files, is_cut_operation
        
        selected_files = []
        if self.image_list_widget.isVisible():
            for item in self.image_list_widget.selectedItems():
                selected_files.append(os.path.join(self.current_folder, item.text()))
        elif self.image_table_widget.isVisible():
            for item in self.image_table_widget.selectedItems():
                if item.column() == 0:
                    selected_files.append(os.path.join(self.current_folder, item.text()))
        
        if selected_files:
            clipboard_files = selected_files
            is_cut_operation = is_cut
    
    def paste_files(self):
        global clipboard_files, is_cut_operation
        
        if not clipboard_files or not self.current_folder:
            return
            
        for file_path in clipboard_files:
            file_name = os.path.basename(file_path)
            destination_path = os.path.join(self.current_folder, file_name)
            
            if file_path == destination_path:
                base, ext = os.path.splitext(file_name)
                counter = 1
                while os.path.exists(destination_path):
                    destination_path = os.path.join(self.current_folder, f"{base} - 복사본({counter}){ext}")
                    counter += 1

            if is_cut_operation:
                shutil.move(file_path, destination_path)
            else:
                shutil.copy2(file_path, destination_path)

        clipboard_files = []
        is_cut_operation = False
        self.load_images_from_folder(self.current_folder)

    def select_folder(self):
        folder_dialog = QFileDialog(self)
        folder_dialog.setFileMode(QFileDialog.Directory)
        
        if folder_dialog.exec():
            selected_folder = folder_dialog.selectedFiles()[0]
            self.load_images_from_folder(selected_folder)
    
    def load_images_from_folder(self, folder_path):
        if not os.path.isdir(folder_path):
            return
            
        self.current_folder = folder_path
        self.folder_path_edit.setText(self.current_folder)
        
        current_view_name = self.view_option_combo.currentText()
        if current_view_name == "자세히":
            self.load_table_view()
        else:
            self.load_list_view(current_view_name)
    
    def load_list_view(self, view_name):
        self.image_list_widget.clear()
        
        icon_size = 128
        if view_name == "보통 아이콘":
            icon_size = 64
        elif view_name == "작은 아이콘":
            icon_size = 32
            
        self.image_list_widget.setIconSize(QSize(icon_size, icon_size))
        self.image_list_widget.setViewMode(QListWidget.IconMode)

        for file_name in os.listdir(self.current_folder):
            file_path = os.path.join(self.current_folder, file_name)
            if os.path.isfile(file_path) and file_name.lower().endswith(self.image_extensions):
                item = QListWidgetItem()
                item.setText(file_name)
                
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    icon = QIcon(pixmap.scaled(icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    item.setIcon(icon)
                
                self.image_list_widget.addItem(item)

    def load_table_view(self):
        self.image_table_widget.setRowCount(0)
        
        for file_name in os.listdir(self.current_folder):
            file_path = os.path.join(self.current_folder, file_name)
            if os.path.isfile(file_path) and file_name.lower().endswith(self.image_extensions):
                row_position = self.image_table_widget.rowCount()
                self.image_table_widget.insertRow(row_position)

                file_size_bytes = os.path.getsize(file_path)
                file_mod_time = os.path.getmtime(file_path)
                file_type = os.path.splitext(file_name)[1].lstrip('.').upper() + " 파일"
                size_str = self.format_file_size(file_size_bytes)
                date_str = datetime.datetime.fromtimestamp(file_mod_time).strftime('%Y-%m-%d %H:%M')

                name_item = QTableWidgetItem(file_name)
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    icon = QIcon(pixmap.scaled(22, 22, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    name_item.setIcon(icon)
                
                self.image_table_widget.setItem(row_position, 0, name_item)
                self.image_table_widget.setItem(row_position, 1, QTableWidgetItem(date_str))
                self.image_table_widget.setItem(row_position, 2, QTableWidgetItem(file_type))
                self.image_table_widget.setItem(row_position, 3, QTableWidgetItem(size_str))
    
    def format_file_size(self, size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
            
    def change_view_mode(self, index):
        view_name = self.view_option_combo.itemText(index)
        if view_name == "자세히":
            self.image_list_widget.hide()
            self.image_table_widget.show()
        else:
            self.image_list_widget.show()
            self.image_table_widget.hide()
            
        if self.current_folder:
            self.load_images_from_folder(self.current_folder)


# 메인 윈도우 클래스 (폴더 트리와 파일 목록 뷰 포함)
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 이미지 탐색기")
        self.setGeometry(100, 100, 1200, 600)
        
        main_layout = QHBoxLayout(self)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # 왼쪽: 폴더 트리 (전체 PC 디렉토리)
        self.folder_tree = QTreeView()
        self.file_system_model = QFileSystemModel()
        self.file_system_model.setFilter(QDir.Dirs | QDir.NoDotAndDotDot)
        self.file_system_model.setRootPath("")  # 전체 PC의 루트로 설정
        
        self.folder_tree.setModel(self.file_system_model)
        self.folder_tree.setRootIndex(self.file_system_model.index(""))
        
        # 파일 이름 열만 보이도록 설정 (0은 파일 이름, 1~3은 숨기기)
        for i in range(1, self.file_system_model.columnCount()):
            self.folder_tree.hideColumn(i)
        
        # 오른쪽: 파일 목록 뷰어
        self.file_viewer = ViewerWidget()
        
        # 뷰어 간 연결: 폴더 선택 시 파일 목록 갱신
        self.folder_tree.clicked.connect(self.on_folder_selected)
        
        splitter.addWidget(self.folder_tree)
        splitter.addWidget(self.file_viewer)
        
        splitter.setStretchFactor(0, 1)  # 폴더 트리 1배
        splitter.setStretchFactor(1, 2)  # 파일 목록 2배
        
        main_layout.addWidget(splitter)
        
        # 초기 폴더 설정
        self.file_viewer.load_images_from_folder(QDir.homePath())
        

    def on_folder_selected(self, index):
        # 선택된 인덱스에서 실제 폴더 경로 가져오기
        path = self.file_system_model.filePath(index)
        if os.path.isdir(path):
            self.file_viewer.load_images_from_folder(path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    explorer = MainWindow()
    explorer.show()
    sys.exit(app.exec())