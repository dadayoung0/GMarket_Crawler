import sys
from crawl import Gmarket
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QTextBrowser, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        title_label = QLabel('GMarket Crawler', self)
        title_label.setAlignment(Qt.AlignCenter)
        title_font = title_label.font()
        title_font.setPointSize(20)
        title_label.setFont(title_font)

        main_text = QTextBrowser(self)
        main_text.append('G마켓 크롤링 프로그램입니다.')
        main_text.append('크롤링한 데이터는 .xlsx 형식으로 지정한 경로에 저장됩니다.')
        main_text.append('프로그램을 시작하려면 \'시작하기\' 버튼을 눌러주세요.')
        main_text.append('\n-- 2021.11.11에 작성')

        start_button = QPushButton('시작하기', self)
        start_button.clicked.connect(self.first_step)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(start_button)
        hbox.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(title_label)
        vbox.addStretch(1)
        vbox.addWidget(main_text)
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        vbox.addStretch(1)

        self.setLayout(vbox)
        self.setWindowTitle('GMarket Crawler')
        self.resize(500, 400)
        self.show()

    def first_step(self):
        print("first step!!")
        # gmk = Gmarket()
        # btn = QPushButton('Quit', self)
        # btn.move(50, 50)
        # btn.resize(btn.sizeHint())
        # btn.clicked.connect(QCoreApplication.instance().quit)
        pass


if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MyApp()
   sys.exit(app.exec_())
