import customtkinter
import customtkinter as ctk
import pywinstyles


def sam():
   root = ctk.CTk()
   root.title("阿米诺斯")
   root.geometry("600x600")
   root.update()
   pywinstyles.apply_style(root, "mica")

   root.grid_columnconfigure(0, weight=1)
   root.grid_columnconfigure(1, weight=3)
   root.grid_columnconfigure(2, weight=1)

   mother = ctk.CTkFrame(root, width=400, height=400)
   mother.grid(row=0, column=0, padx=20, pady=20)
   mother2 = ctk.CTkFrame(root, width=400, height=400)
   mother2.grid(row=0, column=2, padx=20, pady=20)
   pywinstyles.set_opacity(mother.winfo_id(), color="#000001", value=1)
   pywinstyles.set_opacity(mother2.winfo_id(), color="#000001", value=0.8)
   button = ctk.CTkButton(root, text="一德格拉米", command=lambda: print("按钮被点击了！"))
   pywinstyles.set_opacity(button.winfo_id(), color="#000001", value=0.8)
   button.grid(row=0, column=1, padx=20, pady=20)
   accent_button = ctk.CTkButton(
       master=root,
       text="主要按钮",
       corner_radius=6,
       border_width=1,
       fg_color=("#0067C0", "#60CDFF"),  # 经典的 Windows 蓝色
       border_color=("#005FB8", "#45A9D6"),
       text_color=("white", "black"),
       hover_color=("#1975C5", "#6ED3FF"),
       font=ctk.CTkFont(family="Segoe UI Variable Display",
                        size=12, weight="bold")
   )
   accent_button.grid(row=1, column=1, padx=20, pady=20)
   root.mainloop()


if __name__ == "__main__":
   sam()
