import flet as ft

def main(page: ft.Page):
    page.window_title_bar_buttons_visible = True
    page.theme_mode = ft.ThemeMode.DARK
    # 强制使用 Segoe UI Variable，这是 Win11 的标准字体
    page.fonts = {"SegoeUI": "/fonts/SegoeUIVariable.ttf"} 
    page.theme = ft.Theme(font_family="SegoeUI")

    # 定义一个 Fluent 风格的输入框
    fluent_input = ft.TextField(
        label="Fluent 输入框",
        border_radius=4,
        border_color="white24",
        focused_border_color="blue", # Win11 主题蓝色
        bgcolor="white10",
        text_size=14,
        content_padding=10,
    )

    page.add(
        ft.Column([
            ft.Text("系统设置", size=28, weight="bold"),
            fluent_input,
            ft.Button(
                "确认",
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=4), # 放弃圆角，改用小方角
                    color="white",
                    bgcolor="blue",
                )
            )
        ])
    )

ft.app(target=main)
