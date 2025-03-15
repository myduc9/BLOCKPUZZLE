import random
from PyQt6.QtGui import QPainter, QPen, QColor, QPixmap
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import QLabel

# Constants
GRID_SIZE = 8
BLOCK_SIZE = 50

# Colors
WHITE = QColor(255, 255, 255)
DARK_BLUE = QColor(27, 27, 58)
YELLOW = QColor(255, 215, 0)
GREEN = QColor(102, 255, 102)
RED = QColor(255, 102, 102)
BLUE = QColor(102, 102, 255)
ORANGE = QColor(255, 165, 0)
PURPLE = QColor(128, 0, 128)


class DraggableBlock(QLabel):
    def __init__(self, shape, color, parent):
        super().__init__(parent)
        self.shape = shape
        self.color = color
        self.block_size = BLOCK_SIZE
        self.setFixedSize(len(shape[0]) * self.block_size, len(shape) * self.block_size)
        self.pixmap = QPixmap(self.size())
        self.pixmap.fill(Qt.GlobalColor.transparent)
        self.draw_block()
        self.setPixmap(self.pixmap)
        self.dragging = False
        self.original_position = self.pos()

    def draw_block(self):
        painter = QPainter(self.pixmap)
        painter.setBrush(self.color)
        for row in range(len(self.shape)):
            for col in range(len(self.shape[row])):
                if self.shape[row][col] == 1:
                    painter.drawRect(col * self.block_size, row * self.block_size, self.block_size, self.block_size)
        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_start_position = event.pos()
            self.original_position = self.pos()

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.mapToParent(event.pos() - self.drag_start_position))

    def mouseReleaseEvent(self, event):
        if self.dragging:
            self.dragging = False
            parent = self.parent()
            if parent:
                x = round((self.x() - parent.grid_frame.x()) / BLOCK_SIZE)
                y = round((self.y() - parent.grid_frame.y()) / BLOCK_SIZE)
                if parent.logic.is_valid_position(self.shape, x, y):
                    parent.logic.place_block(self, x, y)
                    parent.logic.check_and_clear_lines()
                else:
                    self.move(self.original_position)  # Trả về vị trí ban đầu nếu đặt sai
            parent.logic.check_game_over()


class BlockPuzzleLogic:
    def __init__(self, ui):
        self.ui = ui
        self.grid = [[None] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.score = 0

    def draw_grid(self):
        self.ui.grid_pixmap.fill(DARK_BLUE)
        painter = QPainter(self.ui.grid_pixmap)
        pen = QPen(WHITE)
        painter.setPen(pen)
        for i in range(GRID_SIZE + 1):
            painter.drawLine(i * BLOCK_SIZE, 0, i * BLOCK_SIZE, GRID_SIZE * BLOCK_SIZE)
            painter.drawLine(0, i * BLOCK_SIZE, GRID_SIZE * BLOCK_SIZE, i * BLOCK_SIZE)
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col]:
                    painter.fillRect(col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, self.grid[row][col])
        painter.end()
        self.ui.grid_frame.setPixmap(self.ui.grid_pixmap)

    def reset_game(self):
        """Đặt lại trò chơi về trạng thái ban đầu."""
        self.grid = [[None] * GRID_SIZE for _ in range(GRID_SIZE)]  # Reset lưới
        self.score = 0  # Reset điểm số
        self.ui.update_score()  # Cập nhật điểm số trên giao diện
        self.generate_new_blocks()  # Tạo lại các khối mới
        self.draw_grid()  # Vẽ lại lưới

    def place_block(self, block, x, y):
        for row in range(len(block.shape)):
            for col in range(len(block.shape[row])):
                if block.shape[row][col] == 1:
                    self.grid[y + row][x + col] = block.color
        self.score += sum(sum(row) for row in block.shape)
        self.ui.update_score()
        self.ui.block_options_layout.removeWidget(block)
        block.deleteLater()
        self.draw_grid()
        if not any(self.ui.block_options_layout.itemAt(i) for i in range(self.ui.block_options_layout.count())):
            self.generate_new_blocks()

    def is_valid_position(self, shape, x, y):
        if x < 0 or y < 0 or x + len(shape[0]) > GRID_SIZE or y + len(shape) > GRID_SIZE:
            return False
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col] == 1 and self.grid[y + row][x + col]:
                    return False
        return True

    def check_and_clear_lines(self):
        full_rows = [i for i in range(GRID_SIZE) if all(self.grid[i])]
        full_cols = [i for i in range(GRID_SIZE) if all(self.grid[j][i] for j in range(GRID_SIZE))]
        for row in full_rows:
            self.grid[row] = [None] * GRID_SIZE
        for col in full_cols:
            for row in range(GRID_SIZE):
                self.grid[row][col] = None
        self.draw_grid()

    def check_game_over(self):
        for i in range(self.ui.block_options_layout.count()):
            block = self.ui.block_options_layout.itemAt(i).widget()
            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    if self.is_valid_position(block.shape, x, y):
                        return
        self.ui.show_game_over()

    def generate_new_blocks(self):
        shapes = [
            [[1, 1, 1], [0, 1, 0]],
            [[1, 1], [1, 1]],
            [[1, 1, 1, 1]],
            [[1], [1], [1], [1]],
            [[1, 1, 1], [1, 0, 0]],
            [[0, 1, 0], [1, 1, 1]],
            [[1, 1, 0], [0, 1, 1]],
            [[1, 0], [1, 0], [1, 1]],
            [[1, 1, 1], [1, 0, 0]],
        ]
        colors = [GREEN, RED, BLUE, ORANGE, PURPLE]
        for _ in range(3):
            block = DraggableBlock(random.choice(shapes), random.choice(colors), self.ui)
            self.ui.block_options_layout.addWidget(block)

    def get_score(self):
        return self.score