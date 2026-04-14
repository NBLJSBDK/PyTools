# from pynput import mouse
# from datetime import datetime
# from pathlib import Path
# from PIL import ImageGrab  # pip install pillow

# def save_clipboard_image():
#     img = ImageGrab.grabclipboard()
#     if img is None:
#         print("⚠️ 剪贴板中没有图片。")
#         return
#     ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
#     filename = Path(f"{ts}.png")
#     img.save(filename, "PNG")
#     print(f"✅ 已保存：{filename.name}")

# def on_click(x, y, button, pressed):
#     from pynput.mouse import Button
#     if pressed and button == Button.right:
#         save_clipboard_image()

# def main():
#     print("=== 鼠标右键保存剪贴板图像 ===")
#     print("提示：点击鼠标右键将尝试保存剪贴板中的图片。")
#     print("按 Ctrl+C 退出程序。")
    
#     with mouse.Listener(on_click=on_click) as listener:
#         listener.join()

# if __name__ == "__main__":
#     main()


from pynput import keyboard
from datetime import datetime
from pathlib import Path
from PIL import ImageGrab  # pip install pillow

def save_clipboard_image():
    img = ImageGrab.grabclipboard()
    if img is None:
        print("⚠️ 剪贴板中没有图片。")
        return
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    filename = Path(f"{ts}.png")
    img.save(filename, "PNG")
    print(f"✅ 已保存：{filename.name}")

def main():
    print("=== Ctrl+V 保存剪贴板图像 ===")
    print("提示：按 Ctrl+V 将尝试保存剪贴板中的图片。")
    print("按 Ctrl+C 退出程序。")

    # 监听 Ctrl+V
    with keyboard.GlobalHotKeys({'<ctrl>+v': save_clipboard_image}) as listener:
        listener.join()

if __name__ == "__main__":
    main()
