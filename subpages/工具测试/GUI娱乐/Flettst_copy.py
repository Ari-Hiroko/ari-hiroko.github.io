import flet as ft


def main(page: ft.Page):
   page.theme_mode = ft.ThemeMode.SYSTEM
   page.adaptive = True
   page.title = "大家好啊，我是说的道理"
   # page.window.width = 400
   # page.window.height = 300
   num = 1
   funk = ft.Text(value=f"棍母的数量为：{num}", size=30,
                  color="blue", text_align=ft.TextAlign.CENTER)

   page_dialog = ft.AlertDialog(
       title=ft.Text("重置成功！"),
   )
   # 增加

   def add_num(e):
      nonlocal num
      num = num*2
      funk.value = f"棍母的数量为：{num}"
      page.update()

   # 减少
   def subtract_num(e):
      nonlocal num
      if num > 0:
         num -= 1
         funk.value = f"棍母的数量为：{num}"
         page.update()

   def alert(e):
      page.overlay.append(page_dialog)
      page_dialog.open = True
      page.update()

   btn1_0 = ft.FilledButton(content=ft.Text("减少"), on_click=subtract_num)
   btn2 = ft.FilledButton(content=ft.Text("增加"), on_click=add_num)
   btn_stack = ft.Row(controls=[btn1_0, btn2], spacing=10,
                      alignment=ft.MainAxisAlignment.CENTER)
   btn3 = ft.FilledButton(content=ft.Text("重置"), on_click=alert)
   text1 = ft.Text("电棍笑传之ccb", size=50, color="gray",
                   weight=ft.FontWeight.BOLD)

   page.add(
       ft.Column(
           controls=[
               ft.Divider(height=20, color="transparent"),
               text1,
               ft.Divider(height=20, color="transparent"),
               funk,
               ft.Divider(height=20, color="transparent"),
               btn_stack,
               ft.Divider(height=20, color="transparent"),
               btn3,
               ft.Divider(height=20, color="transparent"),
           ],
           horizontal_alignment=ft.CrossAxisAlignment.CENTER,
       )
   )

   page.add(
       ft.TextField
       (
           "这是一个匿名函数",
           color="gray",
           bgcolor="gray",
           border_color="white",
           border_radius=100,
           width=300,
           border_width=0.75,
           align=ft.Alignment(x=0, y=0)
       )
   )

   page.update()


ft.run(main)
