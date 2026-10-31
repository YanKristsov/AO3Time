from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QPushButton, QLabel, QFileDialog,
                             QComboBox, QProgressBar, QMessageBox)
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('AO3Time')
        self.setMinimumSize(700, 500)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        layout.addWidget(QLabel('Ссылки AO3 (по одной на строку или загрузить .txt):'))
        self.text_links = QTextEdit()
        layout.addWidget(self.text_links)
        
        hl = QHBoxLayout()
        self.btn_load = QPushButton('Загрузить из .txt')
        self.btn_clear = QPushButton('Очистить')
        hl.addWidget(self.btn_load)
        hl.addWidget(self.btn_clear)
        hl.addStretch()
        layout.addLayout(hl)
        
        layout.addWidget(QLabel('Формат выдачи:'))
        self.combo_format = QComboBox()
        self.combo_format.addItems(['PDF для каждого', 'ZIP со всеми PDF'])
        layout.addWidget(self.combo_format)
        
        self.btn_start = QPushButton('Скачать')
        layout.addWidget(self.btn_start)
        
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        self.btn_load.clicked.connect(self.load_file)
        self.btn_clear.clicked.connect(self.text_links.clear)
    
    def load_file(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Выбрать .txt', '', 'Текстовые файлы (*.txt);;Все файлы (*.*)')
        if not path:
            return
        try:
            with open(path, encoding='utf-8') as f:
                self.text_links.setPlainText(f.read())
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', str(e))
