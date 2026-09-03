import tkinter as tk
from tkinter import ttk
import sv_ttk
import pywinstyles

def main():
    root = tk.Tk()
    root.title("阿米诺斯")
    root.geometry("600x800")

    # 1. 必须先应用主题
    sv_ttk.set_theme("dark")

    # 2. 设置 Windows 11 标准暗色背景色 (注意：这是云母效果的底层色)
    # 稍微调低一点亮度，可以让 pywinstyles 的效果更明显
    bg_color = "#121212" 
    root.configure(bg=bg_color)

    # 3. 强制让 ttk 样式库也使用这个颜色
    style = ttk.Style()
    style.configure("TFrame", background=bg_color)
    style.configure("TLabel", background=bg_color, foreground="white")

    # 4. 【核心】应用 pywinstyles
    root.update()
    # 使用 mica 效果，并强制标题栏和背景同步
    pywinstyles.apply_style(root, "mica")
    pywinstyles.change_header_color(root, color=bg_color)
    pywinstyles.change_border_color(root, color=bg_color)

    # 5. 这里的 Frame 现在就会呈现出深邃的暗色，且带有 pywinstyles 的质感
    frame = ttk.Frame(root, padding=30)
    frame.pack(expand=True, fill="both")

    ttk.Label(frame, text="Mica + Dark Theme", font=("Segoe UI", 20, "bold")).pack(pady=20)
    ttk.Button(frame, text="这就是你要的效果").pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()