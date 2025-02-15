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

class FadingRegion:
    def __init__(self, rect):
        self.rect = rect
        self.alpha = 255  # Başlangıç alfa değeri

    def fade(self):
        self.alpha = max(0, self.alpha - 20)  # Alfa değerini daha hızlı azalt

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

        self.fading_regions = []

    def paintEvent(self, event):
        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(0, self.selected_screen_geometry.x(), self.selected_screen_geometry.y(),
                                       self.selected_screen_geometry.width(), self.selected_screen_geometry.height())
        image = screenshot.toImage()

        painter = QPainter(self)

        # Sabit siyahlık
        painter.setBrush(QColor(0, 0, 0, 200))  # Yarı saydam siyah
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

        new_red_regions = []

        for x in range(0, image.width(), 10):
            for y in range(0, image.height(), 10):
                pixel_color = image.pixelColor(x, y)
                red = pixel_color.red()
                green = pixel_color.green()
                blue = pixel_color.blue()

                if red > 10 and red > green * 1.4 and red > blue * 1.4:  # Kırmızı, yeşil ve maviden %30 daha fazlaysa
                    if blue > green * 1.1 or green > blue * 1.1:
                        new_red_regions.append(QRect(x, y, 10, 10))

        # Yeni kırmızı bölgeleri fading listesine ekle
        for rect in new_red_regions:
            if not any(region.rect == rect for region in self.fading_regions):
                self.fading_regions.append(FadingRegion(rect))

        # Mevcut fading bölgelerini çiz ve fade uygula
        for region in self.fading_regions[:]:
            if region.alpha > 0:
                fade_color = QColor(255, 0, 0, region.alpha)  # Kırmızı bölgeler görünür
                painter.setBrush(fade_color)
                painter.setRenderHint(QPainter.Antialiasing)
                painter.drawEllipse(region.rect)
                region.fade()

            if region.alpha == 0:
                self.fading_regions.remove(region)  # Alfa 0 olduğunda bölgeyi kaldır

        painter.end()

    def mousePressEvent(self, event):
        for region in self.fading_regions:
            if region.rect.contains(event.pos()):
                self.setAttribute(Qt.WA_TransparentForMouseEvents, True)  # Tıklama olayını pencerenin arkasına ilet
                return
        super().mousePressEvent(event)

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
