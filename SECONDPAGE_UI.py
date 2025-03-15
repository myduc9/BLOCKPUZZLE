import sys
import json
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QMessageBox, QPushButton, \
   QSpacerItem, QSizePolicy
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt
from SECONDPAGE import BlockPuzzleLogic, GRID_SIZE, BLOCK_SIZE, DARK_BLUE, YELLOW
from SETTING_UI import SettingScreen


USER_DATA_FILE = "user_data.json"


def load_user_data():
   try:
       with open(USER_DATA_FILE, "r") as file:
           return json.load(file)
   except (FileNotFoundError, json.JSONDecodeError):
       return {}


def save_user_data(user_data):
   with open(USER_DATA_FILE, "w") as file:
       json.dump(user_data, file)


class BlockPuzzle(QWidget):
   def __init__(self, username, user_data):
       super().__init__()
       self.setWindowTitle("Block Puzzle Game")
       self.setGeometry(100, 100, 900, 700)


       self.username = username
       self.user_data = user_data


       if username not in user_data:
           user_data[username] = {"score": 0, "theme": 1}


       self.score = user_data[username]["score"]
       self.high_score = user_data.get(username, {}).get("score", 0)  # Lấy đúng high score khi mở lại
       self.logic = BlockPuzzleLogic(self)
       self.initUI()


   def initUI(self):
       layout = QVBoxLayout(self)


       # Score layout
       score_layout = QHBoxLayout()
       self.current_score_label = QLabel(f"Current score: {self.logic.score}")
       self.current_score_label.setFixedHeight(40)
       self.current_score_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
       self.current_score_label.setStyleSheet(
           f"font-size: 18px; color: {YELLOW.name()}; background-color: {DARK_BLUE.name()}; padding: 10px;")
       score_layout.addWidget(self.current_score_label)


       self.high_score_label = QLabel(f"High score: {self.high_score}")
       self.high_score_label.setFixedHeight(40)
       self.high_score_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
       self.high_score_label.setStyleSheet(
           f"font-size: 18px; color: {YELLOW.name()}; background-color: {DARK_BLUE.name()}; padding: 10px;")
       score_layout.addWidget(self.high_score_label)


       score_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))


       # Settings button
       self.settings_button = QPushButton("Setting")
       self.settings_button.setFixedSize(120, 50)
       self.settings_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
       self.settings_button.setStyleSheet(f"background-color: {DARK_BLUE.name()}; color: white; border: none;")
       self.settings_button.clicked.connect(self.open_settings)
       score_layout.addWidget(self.settings_button)


       layout.addLayout(score_layout)


       # Grid container
       grid_container = QVBoxLayout()
       grid_container.setAlignment(Qt.AlignmentFlag.AlignCenter)


       self.grid_frame = QLabel()
       self.grid_pixmap = QPixmap(GRID_SIZE * BLOCK_SIZE, GRID_SIZE * BLOCK_SIZE)
       self.grid_frame.setPixmap(self.grid_pixmap)
       self.grid_frame.setFixedSize(GRID_SIZE * BLOCK_SIZE, GRID_SIZE * BLOCK_SIZE)
       self.logic.draw_grid()
       grid_container.addWidget(self.grid_frame)


       layout.addLayout(grid_container)


       self.block_options_layout = QHBoxLayout()
       layout.addLayout(self.block_options_layout)


       self.logic.generate_new_blocks()
       self.setLayout(layout)




   def open_settings(self):
       self.settings_window = SettingScreen(self)
       self.settings_window.show()


   def restart_game(self):
       """Khởi động lại game mà không bị lỗi treo"""
       self.logic = BlockPuzzleLogic(self)
       self.high_score = self.user_data[self.username]["score"]
       self.update_score()


       # Xóa hết khối cũ trên giao diện
       for i in reversed(range(self.block_options_layout.count())):
           widget = self.block_options_layout.itemAt(i).widget()
           if widget:
               widget.deleteLater()


       self.logic.generate_new_blocks()
       self.logic.draw_grid()


   def update_score(self):
       self.current_score_label.setText(f"Current score: {self.logic.score}")
       if self.logic.score > self.high_score:
           self.high_score = self.logic.score
           self.high_score_label.setText(f"High score: {self.high_score}")
       self.user_data[self.username]["score"] = max(self.user_data[self.username]["score"], self.logic.score)
       save_user_data(self.user_data)

   def show_game_over(self):
       from THIRDPAGE import ThirdPage  # Import bên trong hàm để tránh vòng lặp

       QMessageBox.information(self, "Game Over", "Hết chỗ trống để đặt khối rồi bạn ơi, chia buồn nha! :<")
       self.update_score()  # Lưu điểm trước khi chuyển trang

       # Mở trang ThirdPage
       self.third_page = ThirdPage(self.logic.score, username=self.username, user_data=self.user_data)
       self.third_page.show()

       # Đóng trang hiện tại
       self.hide()

   def return_to_main(self):
       """Quay lại màn hình chính"""
       from FIRSTPAGE_UI import MainGame  # Import nội tuyến để tránh circular import
       self.first_page = MainGame()
       self.first_page.show()
       self.close()  # Đóng cửa sổ hiện tại


if __name__ == "__main__":
   app = QApplication(sys.argv)
   user_data = load_user_data()
   test_username = "TestUser"
   window = BlockPuzzle(test_username, user_data)
   window.show()
   sys.exit(app.exec())
