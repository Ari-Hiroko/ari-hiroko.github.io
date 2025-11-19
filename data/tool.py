import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import configparser

# === 1. 全局设置 ===
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

CONFIG_FILE = "index_tool_config.ini"

# 字体配置
FONT_MAIN = ("Microsoft YaHei UI", 14)
FONT_BOLD = ("Microsoft YaHei UI", 14, "bold")
FONT_TREE = ("Microsoft YaHei UI", 12)
FONT_HEADER = ("Microsoft YaHei UI", 13, "bold")

class NavigationEditor(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("站点目录编辑工具")
        self.geometry("1200x850")
        
        self.project_root = ""
        self.data_file_path = ""
        
        # 状态追踪变量 (修复抽搐的核心)
        self._buttons_active = False 
        
        # === 布局配置 ===
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=4)
        self.grid_rowconfigure(0, weight=1)

        # === 样式配置 ===
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Treeview", 
                             background="#2b2b2b", 
                             foreground="white", 
                             fieldbackground="#2b2b2b", 
                             bordercolor="#2b2b2b",
                             font=FONT_TREE,
                             rowheight=32)
        self.style.configure("Treeview.Heading", 
                             font=FONT_HEADER,
                             background="#3a3a3a",
                             foreground="white",
                             relief="flat")
        self.style.map('Treeview', background=[('selected', '#1f538d')])

        # ===========================
        # 左侧区域：文件树
        # ===========================
        self.left_frame = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.left_frame.grid_rowconfigure(2, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        self.lbl_left = ctk.CTkLabel(self.left_frame, text="1. 项目浏览", font=FONT_BOLD)
        self.lbl_left.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.btn_root = ctk.CTkButton(self.left_frame, text="选择根目录", font=FONT_MAIN, height=36, command=self.select_root_dir)
        self.btn_root.grid(row=1, column=0, padx=15, pady=10, sticky="ew")

        self.file_tree = ttk.Treeview(self.left_frame, show="tree", selectmode="browse")
        self.file_tree.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        
        self.tree_scroll = ctk.CTkScrollbar(self.left_frame, command=self.file_tree.yview)
        self.tree_scroll.grid(row=2, column=1, sticky="ns", pady=10)
        self.file_tree.configure(yscrollcommand=self.tree_scroll.set)
        
        self.file_tree.bind("<<TreeviewSelect>>", self.on_file_tree_click)

        # ===========================
        # 右侧区域
        # ===========================
        self.right_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.right_frame.grid_rowconfigure(3, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # --- Top: 加载/保存 ---
        self.top_bar = ctk.CTkFrame(self.right_frame)
        self.top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        self.lbl_right = ctk.CTkLabel(self.top_bar, text="2. 数据管理", font=FONT_BOLD)
        self.lbl_right.pack(side="left", padx=20, pady=15)

        self.btn_load = ctk.CTkButton(self.top_bar, text="加载数据文件", font=FONT_MAIN, height=36, command=self.load_data_file)
        self.btn_load.pack(side="left", padx=10)

        self.lbl_file_status = ctk.CTkLabel(self.top_bar, text="未加载文件", font=FONT_MAIN, text_color="gray")
        self.lbl_file_status.pack(side="left", padx=10)

        self.btn_save = ctk.CTkButton(self.top_bar, text="💾 保存更改到文件", font=FONT_BOLD, height=36, fg_color="#2EA043", hover_color="#238636", state="disabled", command=self.save_file)
        self.btn_save.pack(side="right", padx=20)

        # --- Middle: 编辑表单 ---
        self.form_frame = ctk.CTkFrame(self.right_frame)
        self.form_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        self.form_frame.grid_columnconfigure(1, weight=1)

        ENTRY_HEIGHT = 38

        ctk.CTkLabel(self.form_frame, text="标题:", font=FONT_MAIN).grid(row=0, column=0, padx=15, pady=10, sticky="e")
        self.entry_title = ctk.CTkEntry(self.form_frame, placeholder_text="页面显示的文字", font=FONT_MAIN, height=ENTRY_HEIGHT)
        self.entry_title.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self.form_frame, text="路径:", font=FONT_MAIN).grid(row=1, column=0, padx=15, pady=10, sticky="e")
        self.entry_path = ctk.CTkEntry(self.form_frame, placeholder_text="点击左侧文件自动填入", font=FONT_MAIN, height=ENTRY_HEIGHT)
        self.entry_path.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self.form_frame, text="提示:", font=FONT_MAIN).grid(row=2, column=0, padx=15, pady=10, sticky="e")
        self.entry_tooltip = ctk.CTkEntry(self.form_frame, placeholder_text="鼠标悬停提示 (Title)", font=FONT_MAIN, height=ENTRY_HEIGHT)
        self.entry_tooltip.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        # --- 按钮区 ---
        self.btn_box = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.btn_box.grid(row=3, column=1, sticky="ew", padx=10, pady=10)
        
        # 左侧：编辑操作
        self.btn_clear = ctk.CTkButton(self.btn_box, text="🧹 清空", font=FONT_MAIN, height=36, width=80, fg_color="gray", hover_color="#555", command=self.clear_inputs)
        self.btn_clear.pack(side="left", padx=5)

        self.btn_add = ctk.CTkButton(self.btn_box, text="➕ 新增", font=FONT_BOLD, height=36, width=100, command=self.add_new_row)
        self.btn_add.pack(side="left", padx=5)

        self.btn_update = ctk.CTkButton(self.btn_box, text="📝 更新", font=FONT_MAIN, height=36, width=100, fg_color="#D97706", hover_color="#B45309", state="disabled", command=self.update_selected_row)
        self.btn_update.pack(side="left", padx=5)
        
        self.btn_del = ctk.CTkButton(self.btn_box, text="🗑️ 删除", font=FONT_MAIN, height=36, width=80, fg_color="#da3633", hover_color="#b91c1c", state="disabled", command=self.delete_row)
        self.btn_del.pack(side="left", padx=5)

        # 右侧：排序操作
        self.sort_box = ctk.CTkFrame(self.btn_box, fg_color="transparent")
        self.sort_box.pack(side="right", padx=5)

        self.btn_up = ctk.CTkButton(self.sort_box, text="⬆️ 上移", font=FONT_MAIN, height=36, width=80, fg_color="#4B5563", hover_color="#374151", state="disabled", command=self.move_up)
        self.btn_up.pack(side="left", padx=5)

        self.btn_down = ctk.CTkButton(self.sort_box, text="⬇️ 下移", font=FONT_MAIN, height=36, width=80, fg_color="#4B5563", hover_color="#374151", state="disabled", command=self.move_down)
        self.btn_down.pack(side="left", padx=5)
        
        self.btn_sort_az = ctk.CTkButton(self.sort_box, text="🔤 A-Z", font=FONT_MAIN, height=36, width=80, fg_color="#4B5563", hover_color="#374151", command=self.sort_az_confirm)
        self.btn_sort_az.pack(side="left", padx=5)


        # --- Bottom: Data Table ---
        self.data_tree = ttk.Treeview(self.right_frame, columns=("title", "path", "tooltip"), show="headings")
        self.data_tree.heading("title", text="标题 (Text)")
        self.data_tree.heading("path", text="路径 (Href)")
        self.data_tree.heading("tooltip", text="提示 (Tooltip)")
        
        self.data_tree.column("title", width=250)
        self.data_tree.column("path", width=350)
        self.data_tree.column("tooltip", width=250)

        self.data_tree.grid(row=3, column=0, sticky="nsew")
        
        self.data_scroll = ctk.CTkScrollbar(self.right_frame, command=self.data_tree.yview)
        self.data_scroll.grid(row=3, column=1, sticky="ns")
        self.data_tree.configure(yscrollcommand=self.data_scroll.set)
        
        self.data_tree.bind("<<TreeviewSelect>>", self.on_data_tree_click)
        self.data_tree.bind("<Button-1>", self.on_data_tree_blank_click)

        self.load_settings_from_ini()

    # ... (Config and Tree Logic remains same) ...
    def save_settings_to_ini(self):
        config = configparser.ConfigParser()
        config['PATHS'] = {
            'project_root': self.project_root,
            'data_file_path': self.data_file_path
        }
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                config.write(f)
        except Exception as e:
            print(f"配置保存失败: {e}")

    def load_settings_from_ini(self):
        if not os.path.exists(CONFIG_FILE): return
        config = configparser.ConfigParser()
        try:
            config.read(CONFIG_FILE, encoding='utf-8')
            if 'PATHS' in config:
                saved_root = config['PATHS'].get('project_root', '')
                if saved_root and os.path.exists(saved_root):
                    self.project_root = saved_root
                    self.btn_root.configure(text=f"根目录: {os.path.basename(saved_root)}")
                    self.populate_file_tree(saved_root)
                
                saved_data = config['PATHS'].get('data_file_path', '')
                if saved_data and os.path.exists(saved_data):
                    self.data_file_path = saved_data
                    self.lbl_file_status.configure(text=os.path.basename(saved_data))
                    self.btn_save.configure(state="normal")
                    self.parse_file()
        except Exception: pass

    def select_root_dir(self):
        path = filedialog.askdirectory(title="选择网站根目录")
        if path:
            self.project_root = path
            self.btn_root.configure(text=f"根目录: {os.path.basename(path)}")
            self.populate_file_tree(path)
            self.save_settings_to_ini()

    def populate_file_tree(self, root_path):
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        root_node = self.file_tree.insert("", "end", text=os.path.basename(root_path), open=True)
        self._process_directory(root_node, root_path)

    def _process_directory(self, parent_node, path):
        try:
            items = os.listdir(path)
            items.sort(key=lambda x: (not os.path.isdir(os.path.join(path, x)), x))
            for item in items:
                if item.startswith('.'): continue
                abs_path = os.path.join(path, item)
                is_dir = os.path.isdir(abs_path)
                oid = self.file_tree.insert(parent_node, "end", text=item, open=False, values=(abs_path,))
                if is_dir:
                    self._process_directory(oid, abs_path)
        except PermissionError: pass

    def on_file_tree_click(self, event):
        if not self.project_root: return
        selected_id = self.file_tree.selection()
        if not selected_id: return
        item_values = self.file_tree.item(selected_id[0], "values")
        if not item_values: return
        abs_path = item_values[0]
        if os.path.isdir(abs_path): return
        try:
            rel_path = os.path.relpath(abs_path, self.project_root).replace('\\', '/')
            self.entry_path.delete(0, "end")
            self.entry_path.insert(0, rel_path)
            if not self.entry_title.get():
                filename = os.path.splitext(os.path.basename(abs_path))[0]
                self.entry_title.insert(0, filename)
                self.entry_tooltip.insert(0, filename)
        except ValueError: pass

    def load_data_file(self):
        path = filedialog.askopenfilename(filetypes=[("Data Files", "*.json *.txt"), ("All Files", "*.*")])
        if path:
            self.data_file_path = path
            self.lbl_file_status.configure(text=os.path.basename(path))
            self.btn_save.configure(state="normal")
            self.parse_file()
            self.save_settings_to_ini()

    def parse_file(self):
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        try:
            with open(self.data_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            for line in lines:
                line = line.strip()
                if not line: continue
                parts = [p.strip() for p in line.split('|')]
                if len(parts) < 2: continue
                t, p = parts[0], parts[1]
                tp = parts[2] if len(parts) > 2 else t
                self.data_tree.insert("", "end", values=(t, p, tp))
        except Exception as e:
            messagebox.showerror("加载失败", str(e))

    def on_data_tree_click(self, event):
        selected = self.data_tree.selection()
        if not selected:
            self._toggle_buttons(False)
            return
        
        # === 修复点：只在状态真正改变时才刷新按钮 ===
        self._toggle_buttons(True)
        
        values = self.data_tree.item(selected[0], "values")
        self.entry_title.delete(0, "end")
        self.entry_title.insert(0, values[0])
        self.entry_path.delete(0, "end")
        self.entry_path.insert(0, values[1])
        self.entry_tooltip.delete(0, "end")
        self.entry_tooltip.insert(0, values[2])

    def on_data_tree_blank_click(self, event):
        if self.data_tree.identify_row(event.y) == "":
            self.clear_inputs()

    def clear_inputs(self):
        self.entry_title.delete(0, "end")
        self.entry_path.delete(0, "end")
        self.entry_tooltip.delete(0, "end")
        self.data_tree.selection_remove(self.data_tree.selection())
        self._toggle_buttons(False)

    # ===========================
    # 核心修复：防抖动控制逻辑
    # ===========================
    def _toggle_buttons(self, enable):
        # 如果当前状态和请求的状态一致，直接返回，拒绝重绘
        if self._buttons_active == enable:
            return
        
        # 更新状态
        self._buttons_active = enable
        st = "normal" if enable else "disabled"
        
        # 执行配置
        self.btn_update.configure(state=st)
        self.btn_del.configure(state=st)
        self.btn_up.configure(state=st)
        self.btn_down.configure(state=st)

    def get_inputs(self):
        t = self.entry_title.get().strip()
        p = self.entry_path.get().strip()
        tp = self.entry_tooltip.get().strip() or t
        return t, p, tp

    def add_new_row(self):
        t, p, tp = self.get_inputs()
        if not t or not p:
            messagebox.showwarning("提示", "标题和路径不能为空")
            return
        self.data_tree.insert("", "end", values=(t, p, tp))
        self.clear_inputs()
        self.data_tree.yview_moveto(1)

    def update_selected_row(self):
        selected = self.data_tree.selection()
        if not selected: return
        t, p, tp = self.get_inputs()
        if not t or not p: return
        self.data_tree.item(selected[0], values=(t, p, tp))
        messagebox.showinfo("提示", "更新成功")

    def delete_row(self):
        selected = self.data_tree.selection()
        if selected:
            self.data_tree.delete(selected[0])
            self.clear_inputs()

    def move_up(self):
        selected = self.data_tree.selection()
        if not selected: return
        for item in selected:
            index = self.data_tree.index(item)
            if index > 0:
                self.data_tree.move(item, '', index - 1)
                self.data_tree.see(item)

    def move_down(self):
        selected = self.data_tree.selection()
        if not selected: return
        for item in reversed(selected):
            index = self.data_tree.index(item)
            total = len(self.data_tree.get_children())
            if index < total - 1:
                self.data_tree.move(item, '', index + 1)
                self.data_tree.see(item)

    def sort_az_confirm(self):
        if not self.data_tree.get_children(): return
        ans = messagebox.askyesno("确认排序", "确定要按【标题】首字母重排吗？")
        if ans:
            l = [(self.data_tree.set(k, "title"), k) for k in self.data_tree.get_children('')]
            try:
                l.sort(key=lambda t: int(t[0]) if t[0].isdigit() else t[0])
            except ValueError:
                l.sort()
            for index, (val, k) in enumerate(l):
                self.data_tree.move(k, '', index)

    def save_file(self):
        if not self.data_file_path: return
        lines = []
        for item in self.data_tree.get_children():
            vals = self.data_tree.item(item, "values")
            lines.append(f"{vals[0]} | {vals[1]} | {vals[2]}")
        try:
            with open(self.data_file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            messagebox.showinfo("成功", "文件已保存！")
        except Exception as e:
            messagebox.showerror("保存失败", str(e))

if __name__ == "__main__":
    app = NavigationEditor()
    app.mainloop()