from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import ctypes
from ctypes import wintypes
from PIL import Image

class RedHighlightOverlay(QtWidgets.QWidget):
    def __init__(self, screen_geometry):
        super().__init__()
        self.screen_geometry = screen_geometry
        self.processed_image = None
        self.initUI()

        # Timer başlat (30 FPS)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.process_red_pixels)
        self.timer.start(1)

    def initUI(self):
        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.WindowStaysOnTopHint |
            QtCore.Qt.WindowType.Tool
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(self.screen_geometry)
        self.make_window_clickthrough()

    def make_window_clickthrough(self):
        hwnd = self.winId()
        hwnd = int(hwnd)
        styles = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, styles | 0x00000020 | 0x00080000)

    def process_red_pixels(self):
        try:
            # Monitör geometrisini al
            x, y, width, height = self.screen_geometry.getRect()
            screenshot = self.capture_screen(x, y, width, height)

            # Görüntüyü kırmızı piksellere göre işleme
            screenshot = screenshot.convert("RGBA")
            pixels = screenshot.load()

            for i in range(screenshot.width):
                for j in range(screenshot.height):
                    r, g, b, a = pixels[i, j]
                    if not (r > 150 and g < 100 and b < 100):  # Kırmızı olmayan pikselleri siyah yap
                        pixels[i, j] = (0, 0, 0, 155)

            # Görüntüyü PyQt için QPixmap'e dönüştür
            image_data = screenshot.tobytes("raw", "RGBA")
            qimage = QtGui.QImage(image_data, screenshot.width, screenshot.height, QtGui.QImage.Format_RGBA8888)
            self.processed_image = QtGui.QPixmap.fromImage(qimage)
            self.update()
        except Exception as e:
            print(f"Hata oluştu: {e}")

    def capture_screen(self, x, y, width, height):
        # ctypes tür tanımları
        hdc = ctypes.windll.user32.GetDC(0)
        memdc = ctypes.windll.gdi32.CreateCompatibleDC(hdc)
        bitmap = ctypes.windll.gdi32.CreateCompatibleBitmap(hdc, width, height)
        ctypes.windll.gdi32.SelectObject(memdc, bitmap)

        # Ekran görüntüsünü alırken overlay'in etkisini göz ardı et
        ctypes.windll.gdi32.BitBlt(memdc, 0, 0, width, height, hdc, x, y, 0x00CC0020)

        # Bitmap verisini belleğe kopyala
        bmpinfo = (ctypes.c_ubyte * (width * height * 4))()
        ctypes.windll.gdi32.GetBitmapBits(bitmap, len(bmpinfo), bmpinfo)

        # Bellekten görüntüyü oluştur
        image = Image.frombuffer("RGBA", (width, height), bmpinfo, "raw", "BGRA", 0, 1)

        # Kullanılan nesneleri serbest bırak
        ctypes.windll.gdi32.DeleteObject(bitmap)
        ctypes.windll.gdi32.DeleteDC(memdc)
        ctypes.windll.user32.ReleaseDC(0, hdc)

        return image

    def paintEvent(self, event):
        if self.processed_image:
            painter = QtGui.QPainter(self)
            painter.drawPixmap(0, 0, self.processed_image)
            painter.end()


def choose_screen(app):
    screens = app.screens()
    screen_options = [f"Ekran {i + 1}: {screen.geometry()}" for i, screen in enumerate(screens)]

    dialog = QtWidgets.QInputDialog()
    dialog.setWindowTitle("Ekran Seçimi")
    dialog.setLabelText("Görüntülenecek ekranı seçin:")
    dialog.setComboBoxItems(screen_options)
    dialog.resize(300, 100)

    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        selected_index = dialog.textValue()
        selected_screen_index = screen_options.index(selected_index)
        return screens[selected_screen_index].geometry()
    else:
        return None


def main():
    app = QtWidgets.QApplication(sys.argv)
    selected_screen_geometry = choose_screen(app)
    if not selected_screen_geometry:
        print("Ekran seçilmedi. Çıkılıyor.")
        sys.exit(0)

    overlay = RedHighlightOverlay(selected_screen_geometry)
    overlay.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
