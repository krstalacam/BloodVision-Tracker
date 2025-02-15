import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog
from PyQt5.QtCore import Qt, QRect, QTimer, QPropertyAnimation, pyqtProperty, QTime
from PyQt5.QtGui import QPainter, QColor, QScreen, QCursor

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
        return selected_screen_index, screens[selected_screen_index].geometry()
    else:
        return None, None

class RedPathWindow(QMainWindow):
    def __init__(self, screen_index, screen_geometry):
        super().__init__()

        self.screen_index = screen_index
        self.selected_screen_geometry = screen_geometry
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(self.selected_screen_geometry)

        self.timer = QTimer()
        self.timer.timeout.connect(self.checkMousePosition)
        self.timer.start(16)  # ~60 FPS

        self.expansion_radius = 5
        self._fade_alpha = 0  # Başlangıçta görünmez
        self._fade_delay = 1100  # Kırmızı kaybolduktan sonra 3 saniye bekleme süresi
        self._active_regions = []  # Aktif kırmızı bölgeler

        self.fade_animation = QPropertyAnimation(self, b"fade_alpha")
        self.fade_animation.setDuration(1000)  # Geçiş süresi
        self.fade_animation.setStartValue(255)
        self.fade_animation.setEndValue(0)
        self.fade_animation.setLoopCount(-1)  # Sonsuz döngü, ama sadece yavaşça kapanacak

    @pyqtProperty(int)
    def fade_alpha(self):
        return self._fade_alpha

    @fade_alpha.setter
    def fade_alpha(self, value):
        self._fade_alpha = value
        self.update()

    def is_red_pixel(self, pixel_color):
        red = pixel_color.red()
        green = pixel_color.green()
        blue = pixel_color.blue()
        return red > 30 and red > green * 1.4 and red > blue * 1.4 and (blue > green * 1.1 or green > blue * 1.1)

    def check_surrounding_pixels(self, image, center_x, center_y):
        for dx in range(-self.expansion_radius, self.expansion_radius + 1):
            for dy in range(-self.expansion_radius, self.expansion_radius + 1):
                x = center_x + dx
                y = center_y + dy
                if (0 <= x < image.width() and 0 <= y < image.height()):
                    if self.is_red_pixel(image.pixelColor(x, y)):
                        return True
        return False

    def paintEvent(self, event):
        screen = QApplication.screens()[self.screen_index]
        screenshot = screen.grabWindow(0, self.selected_screen_geometry.x(), self.selected_screen_geometry.y(),
                                       self.selected_screen_geometry.width(), self.selected_screen_geometry.height())
        image = screenshot.toImage()

        painter = QPainter(self)

        # Sabit siyahlık
        painter.setBrush(QColor(0, 0, 0, 220))  # Yarı saydam gri
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

        self.red_regions = []
        self.path_regions = []

        for x in range(0, image.width(), 10):
            for y in range(0, image.height(), 10):
                pixel_color = image.pixelColor(x, y)
                if self.is_red_pixel(pixel_color):
                    self.red_regions.append(QRect(x, y, 10, 10))

        for region in self.red_regions:
            path_buffer = 20  # Kırmızı yolun etrafında algılanacak tampon mesafesi
            adjusted_region = region.adjusted(-path_buffer, -path_buffer, path_buffer, path_buffer)
            self.path_regions.append(adjusted_region)

        painter.setCompositionMode(QPainter.CompositionMode_Clear)

        for region in self.path_regions:
            fade_color = QColor(0, 0, 0, self._fade_alpha)
            painter.setBrush(fade_color)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.drawEllipse(region)

        painter.end()

    def checkMousePosition(self):
        try:
            # Global cursor pozisyonunu al
            cursor_pos = QCursor.pos()

            # Global pozisyonu pencere içindeki pozisyona çevir
            local_pos = self.mapFromGlobal(cursor_pos)

            # Ekran görüntüsünü al
            screen = QApplication.screens()[self.screen_index]
            screenshot = screen.grabWindow(0)

            if self.selected_screen_geometry != screen.geometry():
                screenshot = screenshot.copy(
                    self.selected_screen_geometry.x(),
                    self.selected_screen_geometry.y(),
                    self.selected_screen_geometry.width(),
                    self.selected_screen_geometry.height()
                )

            image = screenshot.toImage()

            # Mouse pozisyonunun çevresini kontrol et
            red_detected = self.check_surrounding_pixels(image, local_pos.x(), local_pos.y())

            # Kırmızı algılandığında
            if red_detected:
                # Eğer kırmızı yeni algılandıysa
                self._active_regions.append({
                    "region": QRect(local_pos.x(), local_pos.y(), 10, 10),
                    "start_time": QTime.currentTime()
                })
                self.update()

            # Aktif bölgeleri kontrol et ve zamanlayıcıyı uygula
            current_time = QTime.currentTime()
            for active_region in list(self._active_regions):
                elapsed_time = active_region["start_time"].msecsTo(current_time)
                if elapsed_time > self._fade_delay:
                    # Kırmızı kaybolduysa, bu bölgeyi listeden çıkar
                    self._active_regions.remove(active_region)

            # Fade alpha değeri yalnızca kırmızı kalmadığında değişir
            if not self._active_regions:
                self._fade_alpha = max(self._fade_alpha - 5, 0)
                self.update()

        except Exception as e:
            print(f"Hata oluştu: {e}")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    screen_index, selected_geometry = choose_screen(app)
    if screen_index is None:
        sys.exit()

    window = RedPathWindow(screen_index, selected_geometry)
    window.show()
    sys.exit(app.exec_())
