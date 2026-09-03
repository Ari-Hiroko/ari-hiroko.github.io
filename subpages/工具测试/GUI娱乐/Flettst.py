import flet as ft

def main(page: ft.Page):
   funk = ft.Text(value="Hell, World!", size=30, color="blue")
   page.add(funk)
   def refresh_0(e):
      funk.value = "Hello, Flet!"
      page.update()
   btn1 = ft.Button(content="刷新", on_click=refresh_0)
   page.add(btn1)
ft.run(main)