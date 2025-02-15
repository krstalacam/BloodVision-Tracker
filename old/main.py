import ctypes
from ctypes import wintypes
from PIL import Image
import win32gui
def capture_window(window_title, output_filename="window_capture.png"):
    # Pencereyi bul
    hwnd = win32gui.FindWindow(None, window_title)
    if not hwnd:
        raise Exception(f"Pencere bulunamadı: {window_title}")

    # Pencere boyutlarını al
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top

    # Ekran görüntüsü için device context oluştur
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    # Bitmap oluştur
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)

    saveDC.SelectObject(saveBitMap)

    # Pencere içeriğini kopyala
    saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

    # Bitmap'i PIL Image'e dönüştür
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)

    img = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr,
        'raw',
        'BGRX',
        0,
        1
    )

    # Görüntüyü kaydet (dikey olarak çevir)
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(output_filename)
    print(f"Ekran görüntüsü kaydedildi: {output_filename}")

    # Bellek temizliği
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)


# Örnek kullanım
capture_window("Hesap Makinesi", "hesap_capture.png")