import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog
from PyQt5.QtCore import Qt, QRect, QTimer
from PyQt5.QtGui import QPainter, QColor, QScreen

def choose_screen(app):
    screens = app.screens()
    screen_options = [f"Ekran {i + 1}: {screen.geometry()}" for i, screen in enumerate(screens)]

    dialog = QInputDialog()
    dialog.setWindowTitle("Ekran Seçimi")
    dialog.setLabelText("Görüntülenecek ekranı seçin:")
    dialog.setComboBoxItems(screen_options)
    dialog.resize(300, 100)

    if dialog.exec_() == QInputDialog.Accepted:
        selected_index = dialog.textValue()
        selected_screen_index = screen_options.index(selected_index)
        return screens[selected_screen_index].geometry()
    else:
        return None

class RedPathWindow(QMainWindow):
    def __init__(self, screen_geometry):
        super().__init__()

        self.selected_screen_geometry = screen_geometry
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(self.selected_screen_geometry)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16)

        self.fade_alpha = 100
        self.target_alpha = 0
        self.fade_speed = 100

        self.red_regions = []
        self.path_regions = []

    def paintEvent(self, event):
        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(0, self.selected_screen_geometry.x(), self.selected_screen_geometry.y(),
                                       self.selected_screen_geometry.width(), self.selected_screen_geometry.height())
        image = screenshot.toImage()

        painter = QPainter(self)

        painter.setBrush(QColor(0, 0, 0, 220))  # Yarı saydam gri
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

        self.red_regions.clear()
        self.path_regions.clear()

        for x in range(0, image.width(), 10):
            for y in range(0, image.height(), 10):
                pixel_color = image.pixelColor(x, y)
                red = pixel_color.red()
                green = pixel_color.green()
                blue = pixel_color.blue()

                if red > 30 and red > green * 1.4 and red > blue * 1.4:  # Kırmızı, yeşil ve maviden %30 daha fazlaysa
                    if blue > green * 1.1 or green > blue * 1.1:
                        self.red_regions.append(QRect(x, y, 10, 10))

        for region in self.red_regions:
            path_buffer = 20  # Kırmızı yolun etrafında algılanacak tampon mesafesi
            self.path_regions.append(region.adjusted(-path_buffer, -path_buffer, path_buffer, path_buffer))

        painter.setCompositionMode(QPainter.CompositionMode_Clear)
        for region in self.path_regions:
            painter.fillRect(region, QColor(0, 0, 0, 0))

        painter.end()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    selected_geometry = choose_screen(app)
    if not selected_geometry:
        sys.exit()

    window = RedPathWindow(selected_geometry)
    window.show()
    sys.exit(app.exec_())
