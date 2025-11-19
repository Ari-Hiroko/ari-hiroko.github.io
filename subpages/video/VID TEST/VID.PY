import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import configparser
import json
import re
import os
import shutil
from datetime import datetime

# --- 配置文件处理器 (无变化) ---
CONFIG_FILE = 'config.ini'
config = configparser.ConfigParser()

def load_config():
    if not os.path.exists(CONFIG_FILE): create_default_config()
    config.read(CONFIG_FILE, encoding='utf-8')
    
def create_default_config():
    config['Settings'] = {
        'default_author': 'Your Name', 'video_list_path': '',
        'ev_files_output_path': '', 'video_output_path': '',
        'video_web_path_prefix': '/vid/'
    }
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f: config.write(f)

def save_config(author, list_path, ev_path, vid_path, vid_prefix):
    config['Settings'] = {
        'default_author': author, 'video_list_path': list_path,
        'ev_files_output_path': ev_path, 'video_output_path': vid_path,
        'video_web_path_prefix': vid_prefix
    }
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f: config.write(f)

class VideoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # --- 主题与美学设置 ---
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=("#F0F2F5", "#1C1C1C")) # 柔和的浅灰/深灰背景

        # --- 字体定义 ---
        self.main_font = ctk.CTkFont(family="Microsoft YaHei UI", size=13)
        self.bold_font = ctk.CTkFont(family="Microsoft YaHei UI", size=16, weight="bold")
        self.small_font = ctk.CTkFont(family="Microsoft YaHei UI", size=12)

        self.video_list_data = []
        self.next_ev_number = 1
        self.edit_mode = False
        self.editing_ev_info = {}

        self.title("视频投稿与编辑应用 (Fluent UI)")
        self.geometry("950x1000") # 调整窗口以适应新样式

        load_config()
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- 1. 配置区域 (带阴影效果) ---
        config_shadow = ctk.CTkFrame(self, fg_color=("#DBDEE2", "#242424"), corner_radius=12)
        config_shadow.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="ew")
        config_frame = ctk.CTkFrame(config_shadow, corner_radius=10, fg_color=("#FFFFFF", "#2B2B2B"))
        config_frame.pack(fill="both", expand=True, padx=1, pady=1)
        config_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(config_frame, text="配置", font=self.bold_font).grid(row=0, column=0, columnspan=3, padx=15, pady=(15, 10), sticky="w")
        
        # ... 配置项，应用新字体
        ctk.CTkLabel(config_frame, text="默认作者:", font=self.main_font).grid(row=1, column=0, padx=15, pady=5, sticky="w")
        self.author_var = tk.StringVar(value=config['Settings'].get('default_author', ''))
        ctk.CTkEntry(config_frame, textvariable=self.author_var, font=self.main_font).grid(row=1, column=1, columnspan=2, padx=15, pady=5, sticky="ew")
        ctk.CTkLabel(config_frame, text="video_list.js 路径:", font=self.main_font).grid(row=2, column=0, padx=15, pady=5, sticky="w")
        self.video_list_path_var = tk.StringVar(value=config['Settings'].get('video_list_path', ''))
        ctk.CTkEntry(config_frame, textvariable=self.video_list_path_var, font=self.main_font).grid(row=2, column=1, padx=15, pady=5, sticky="ew")
        ctk.CTkButton(config_frame, text="浏览...", width=80, command=self.browse_videolist, font=self.main_font).grid(row=2, column=2, padx=(0,15), pady=5)
        ctk.CTkLabel(config_frame, text="EV.js 输出目录:", font=self.main_font).grid(row=3, column=0, padx=15, pady=5, sticky="w")
        self.ev_path_var = tk.StringVar(value=config['Settings'].get('ev_files_output_path', ''))
        ctk.CTkEntry(config_frame, textvariable=self.ev_path_var, font=self.main_font).grid(row=3, column=1, padx=15, pady=5, sticky="ew")
        ctk.CTkButton(config_frame, text="浏览...", width=80, command=self.browse_ev_path, font=self.main_font).grid(row=3, column=2, padx=(0,15), pady=5)
        ctk.CTkLabel(config_frame, text="视频文件输出目录:", font=self.main_font).grid(row=4, column=0, padx=15, pady=5, sticky="w")
        self.video_output_path_var = tk.StringVar(value=config['Settings'].get('video_output_path', ''))
        ctk.CTkEntry(config_frame, textvariable=self.video_output_path_var, font=self.main_font).grid(row=4, column=1, padx=15, pady=5, sticky="ew")
        ctk.CTkButton(config_frame, text="浏览...", width=80, command=self.browse_video_output_path, font=self.main_font).grid(row=4, column=2, padx=(0,15), pady=5)
        ctk.CTkLabel(config_frame, text="视频Web路径前缀:", font=self.main_font).grid(row=5, column=0, padx=15, pady=5, sticky="w")
        self.video_web_prefix_var = tk.StringVar(value=config['Settings'].get('video_web_path_prefix', '/vid/'))
        ctk.CTkEntry(config_frame, textvariable=self.video_web_prefix_var, font=self.main_font).grid(row=5, column=1, columnspan=2, padx=15, pady=5, sticky="ew")

        action_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        action_frame.grid(row=6, column=0, columnspan=3, padx=15, pady=(10, 15), sticky="ew")
        ctk.CTkButton(action_frame, text="读取并解析 video_list.js", height=35, command=self.load_and_parse_videolist, font=self.main_font).pack(side="left", padx=(0,10))
        self.status_label = ctk.CTkLabel(action_frame, text="请先选择并读取 video_list.js", text_color=("#1A73E8", "#8AB4F8"), font=self.main_font)
        self.status_label.pack(side="left", padx=10)
        ctk.CTkButton(action_frame, text="保存配置", width=100, fg_color=("#757575", "#505050"), hover_color=("#616161", "#404040"), command=self.save_current_config, font=self.main_font).pack(side="right")
        self.theme_switch = ctk.CTkSwitch(action_frame, text="深色模式", command=lambda: ctk.set_appearance_mode("dark" if self.theme_switch.get() else "light"), font=self.main_font)
        self.theme_switch.pack(side="right", padx=15)
        
        # --- 2. 视频信息区域 (带阴影效果) ---
        details_shadow = ctk.CTkFrame(self, fg_color=("#DBDEE2", "#242424"), corner_radius=12)
        details_shadow.grid(row=2, column=0, padx=15, pady=(5, 15), sticky="nsew")
        self.details_frame = ctk.CTkFrame(details_shadow, corner_radius=10, fg_color=("#FFFFFF", "#2B2B2B"))
        self.details_frame.pack(fill="both", expand=True, padx=1, pady=1)
        self.details_frame.grid_columnconfigure(1, weight=1)
        self.details_frame.grid_rowconfigure(4, weight=1)

        self.edit_frame = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        self.edit_frame.grid(row=0, column=0, columnspan=3, padx=15, pady=15, sticky="ew")
        self.edit_frame.grid_columnconfigure(1, weight=1)
        self.edit_frame.grid_remove()
        ctk.CTkLabel(self.edit_frame, text="编辑现有视频:", font=self.main_font).grid(row=0, column=0, padx=(0, 10))
        self.edit_selector_combo = ctk.CTkComboBox(self.edit_frame, state='readonly', width=300, font=self.main_font)
        self.edit_selector_combo.grid(row=0, column=1, sticky="ew")
        ctk.CTkButton(self.edit_frame, text="加载", width=70, command=self.load_ev_for_editing, font=self.main_font).grid(row=0, column=2, padx=10)

        ctk.CTkLabel(self.details_frame, text="选择源视频文件:", font=self.main_font).grid(row=1, column=0, padx=15, pady=5, sticky="w")
        self.source_video_path_var = tk.StringVar()
        self.source_video_entry = ctk.CTkEntry(self.details_frame, textvariable=self.source_video_path_var, font=self.main_font)
        self.source_video_entry.grid(row=1, column=1, sticky="ew", padx=15)
        self.source_video_button = ctk.CTkButton(self.details_frame, text="选择...", width=80, command=self.browse_source_video, font=self.main_font)
        self.source_video_button.grid(row=1, column=2, padx=(0,15))
        
        ctk.CTkLabel(self.details_frame, text="视频标题:", font=self.main_font).grid(row=2, column=0, padx=15, pady=5, sticky="w")
        self.title_var = tk.StringVar()
        self.title_entry = ctk.CTkEntry(self.details_frame, textvariable=self.title_var, font=self.main_font)
        self.title_entry.grid(row=2, column=1, columnspan=2, padx=15, pady=5, sticky="ew")
        
        ctk.CTkLabel(self.details_frame, text="视频简介:", font=self.main_font).grid(row=3, column=0, padx=15, pady=5, sticky="nw")
        self.desc_text = ctk.CTkTextbox(self.details_frame, height=100, corner_radius=8, font=self.main_font)
        self.desc_text.grid(row=3, column=1, columnspan=2, padx=15, pady=5, sticky="ew")
        
        self.sidebar_scroll_frame = ctk.CTkScrollableFrame(self.details_frame, label_text="侧边栏卡片", label_font=self.main_font, corner_radius=10)
        self.sidebar_scroll_frame.grid(row=4, column=0, columnspan=3, padx=15, pady=15, sticky="nsew")
        self.add_card_button = ctk.CTkButton(self.sidebar_scroll_frame, text="✚ 添加卡片", command=self.add_sidebar_card_ui, font=self.main_font)
        self.add_card_button.pack(anchor="w", pady=5, padx=5)
        
        bottom_bar = ctk.CTkFrame(self, corner_radius=0, height=60, fg_color="transparent")
        bottom_bar.grid(row=3, column=0, sticky="ew")
        bottom_bar.grid_columnconfigure(0, weight=1); bottom_bar.grid_columnconfigure(2, weight=1)

        self.action_button = ctk.CTkButton(bottom_bar, text="---", height=35, command=self.process_submission, font=self.main_font)
        self.action_button.grid(row=0, column=1, padx=10, pady=10)
        self.reset_button = ctk.CTkButton(bottom_bar, text="---", height=35, fg_color="#D32F2F", hover_color="#B71C1C", command=self.reset_to_new_mode, font=self.main_font)
        self.reset_button.grid(row=0, column=2, padx=10, pady=10, sticky="w")
        
        self.toggle_details_frame("disabled")

    # ... (Rest of the methods are mostly logic and don't need UI changes)

    def save_current_config(self):
        save_config(
            self.author_var.get(), self.video_list_path_var.get(),
            self.ev_path_var.get(), self.video_output_path_var.get(),
            self.video_web_prefix_var.get()
        )
        messagebox.showinfo("成功", "配置已成功保存到 config.ini 文件。")
    
    def toggle_details_frame(self, state, is_editing=False):
        widgets_to_check = self.details_frame.winfo_children()[:]
        while widgets_to_check:
            widget = widgets_to_check.pop(0)
            widgets_to_check.extend(widget.winfo_children())
            try:
                widget.configure(state=state)
            except (ValueError, TypeError, tk.TclError):
                pass

        if state == "normal":
            self.add_card_button.configure(state="normal")

        self.action_button.configure(state=state)
        self.reset_button.configure(state=state)
        
        video_select_state = "disabled" if is_editing else state
        self.source_video_entry.configure(state=video_select_state)
        self.source_video_button.configure(state=video_select_state)

    def add_sidebar_card_ui(self, title="", content=""):
        card_frame = ctk.CTkFrame(self.sidebar_scroll_frame, border_width=1, border_color=("#E0E0E0", "#404040"))
        card_frame.pack(fill="x", expand=True, pady=5, padx=5)
        card_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(card_frame, text="标题:", font=self.main_font).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        title_entry = ctk.CTkEntry(card_frame, placeholder_text="卡片标题", font=self.main_font)
        title_entry.grid(row=0, column=1, padx=(0,10), pady=5, sticky="ew")
        title_entry.insert(0, title)
        
        ctk.CTkLabel(card_frame, text="内容:", font=self.main_font).grid(row=1, column=0, padx=10, pady=5, sticky="nw")
        content_text = ctk.CTkTextbox(card_frame, height=80, font=self.small_font)
        content_text.grid(row=1, column=1, padx=(0,10), pady=(0,5), sticky="ew")
        content_text.insert("1.0", content)
        
        remove_btn = ctk.CTkButton(card_frame, text="✕", width=28, height=28, fg_color="transparent", text_color=("gray20", "gray80"), hover_color=("#F0F0F0", "#303030"),
                                   command=lambda f=card_frame: f.destroy())
        remove_btn.grid(row=0, column=2, padx=(0,5), pady=5)

    def get_sidebar_cards_data(self):
        sidebar_cards = []
        for frame in self.sidebar_scroll_frame.winfo_children():
            if isinstance(frame, ctk.CTkFrame):
                title_widget = None; content_widget = None
                for widget in frame.winfo_children():
                    if isinstance(widget, ctk.CTkEntry): title_widget = widget
                    elif isinstance(widget, ctk.CTkTextbox): content_widget = widget
                if title_widget and content_widget:
                    sidebar_cards.append({"title": title_widget.get(), "content": content_widget.get("1.0", "end-1c").strip()})
        return sidebar_cards

    def load_and_parse_videolist(self):
        filepath = self.video_list_path_var.get()
        if not os.path.exists(filepath): messagebox.showerror("错误", f"文件不存在: {filepath}"); return
        try:
            with open(filepath, 'r', encoding='utf-8') as f: content = f.read()
            match = re.search(r'const\s+videoList\s*=\s*(\[[\s\S]*?\]);?', content, re.MULTILINE)
            if not match: raise ValueError("未找到 'const videoList = [...]'")
            json_str = match.group(1).strip()
            self.video_list_data = json.loads(re.sub(r',\s*([\]}])', r'\1', json_str))
            
            self.populate_edit_selector()
            self.edit_frame.grid()
            self.reset_to_new_mode()
        except Exception as e:
            messagebox.showerror("解析错误", f"无法解析 video_list.js。\n错误详情: {e}")
            self.toggle_details_frame("disabled")
            self.edit_frame.grid_remove()

    def load_ev_for_editing(self):
        selected_title = self.edit_selector_combo.get()
        if not selected_title: messagebox.showwarning("提示", "请先从下拉菜单中选择一个视频。"); return
        video_info = next((item for item in self.video_list_data if item['title'] == selected_title), None)
        if not video_info: return
        ev_js_dir = self.ev_path_var.get() or os.path.dirname(self.video_list_path_var.get())
        ev_file_path = os.path.join(ev_js_dir, os.path.basename(video_info['data_file']))
        if not os.path.exists(ev_file_path): messagebox.showerror("错误", f"找不到对应的文件: {ev_file_path}"); return
        try:
            with open(ev_file_path, 'r', encoding='utf-8') as f: content = f.read()
            def get_val(key):
                m = re.search(rf'{key}\s*:\s*"(.*?)"', content, re.DOTALL)
                return m.group(1).replace("\\n", "\n") if m else ""
            sidebar_match = re.search(r'sidebarCards\s*:\s*(\[[\s\S]*?\])', content)
            cards_str = sidebar_match.group(1) if sidebar_match else "[]"
            sidebar_cards = json.loads(re.sub(r',\s*([\]}])', r'\1', cards_str))
            self.switch_to_edit_mode(video_info, ev_file_path, get_val, sidebar_cards)
        except Exception as e: messagebox.showerror("加载错误", f"无法解析 {video_info['id']}.js 文件。\n{e}")

    def switch_to_new_mode(self):
        self.edit_mode = False; self.editing_ev_info = {}
        self.next_ev_number = len(self.video_list_data) + 1
        self.clear_form()
        self.status_label.configure(text=f"当前模式: 新建 (ID 将为 EV{self.next_ev_number})", text_color=("#1A73E8", "#8AB4F8"))
        self.action_button.configure(text="生成文件并移动视频")
        self.reset_button.configure(text="清空表单")
        self.toggle_details_frame("normal")

    def switch_to_edit_mode(self, video_info, file_path, val_getter, cards):
        self.edit_mode = True; self.editing_ev_info = {**video_info, 'full_path': file_path}
        self.clear_form()
        self.title_var.set(val_getter('title'))
        self.desc_text.insert("1.0", val_getter('description'))
        self.author_var.set(val_getter('author'))
        for card in cards: self.add_sidebar_card_ui(card.get('title', ''), card.get('content', ''))
        self.status_label.configure(text=f"当前模式: 编辑 {video_info['id']}", text_color=("#8E24AA", "#D055FF"))
        self.action_button.configure(text="保存更改")
        self.reset_button.configure(text="切换到新建模式")
        self.toggle_details_frame("normal", is_editing=True)

    def reset_to_new_mode(self):
        self.edit_selector_combo.set(''); self.switch_to_new_mode()

    def process_submission(self):
        if self.edit_mode: self.save_edited_files()
        else: self.generate_new_files()

    def save_edited_files(self):
        if not self.title_var.get(): messagebox.showwarning("提示", "视频标题不能为空！"); return
        author = self.author_var.get(); title = self.title_var.get()
        description = self.desc_text.get("1.0", "end-1c").strip().replace("\n", "\\n")
        sidebar_cards = self.get_sidebar_cards_data()
        
        with open(self.editing_ev_info['full_path'], 'r', encoding='utf-8') as f: old_content = f.read()
        src_match = re.search(r'videoSrc\s*:\s*"(.*?)"', old_content)
        video_src_path = src_match.group(1) if src_match else ""
        ev_file_content = f"""/** ... */\nconst config = {{\n    title: "{title}",\n    id: "{self.editing_ev_info['id']}",\n    date: "{self.editing_ev_info['date']}",\n    author: "{author}",\n    videoSrc: "{video_src_path}",\n    poster: "", \n    description: "{description}",\n    sidebarCards: {json.dumps(sidebar_cards, indent=4, ensure_ascii=False)}\n}};"""
        try:
            with open(self.editing_ev_info['full_path'], 'w', encoding='utf-8') as f: f.write(ev_file_content)
        except Exception as e: messagebox.showerror("写入错误", f"无法写入文件 {self.editing_ev_info['full_path']}\n{e}"); return
        for item in self.video_list_data:
            if item['id'] == self.editing_ev_info['id']: item['title'] = f"{item['id']} {title}"; item['author'] = author; break
        self.write_videolist_file()
        messagebox.showinfo("成功", f"{self.editing_ev_info['id']} 的信息已成功更新！")
        self.load_and_parse_videolist()

    def generate_new_files(self):
        if not self.title_var.get(): messagebox.showwarning("提示", "视频标题不能为空！"); return
        source_video = self.source_video_path_var.get()
        if not source_video: messagebox.showwarning("提示", "请选择一个源视频文件！"); return
        new_ev_id = f"EV{self.next_ev_number}"
        _, video_extension = os.path.splitext(source_video)
        new_video_filename = f"{new_ev_id}{video_extension}"
        dest_video_path = os.path.join(self.video_output_path_var.get(), new_video_filename)
        try: shutil.move(source_video, dest_video_path)
        except Exception as e: messagebox.showerror("视频移动失败", f"错误: {e}"); return
        today = datetime.now().strftime("%Y-%m-%d")
        author = self.author_var.get(); title = self.title_var.get()
        description = self.desc_text.get("1.0", "end-1c").strip().replace("\n", "\\n")
        sidebar_cards = self.get_sidebar_cards_data()
        video_web_path = f"/{self.video_web_prefix_var.get().strip('/')}/{new_video_filename}"
        ev_file_content = f"""/** ... */\nconst config = {{\n    title: "{title}",\n    id: "{new_ev_id}",\n    date: "{today}",\n    author: "{author}",\n    videoSrc: "{video_web_path}",\n    poster: "", \n    description: "{description}",\n    sidebarCards: {json.dumps(sidebar_cards, indent=4, ensure_ascii=False)}\n}};"""
        ev_filename = os.path.join(self.ev_path_var.get(), f"{new_ev_id}.js")
        try:
            with open(ev_filename, 'w', encoding='utf-8') as f: f.write(ev_file_content)
        except Exception as e: messagebox.showerror("写入错误", f"无法写入文件 {ev_filename}\n{e}"); return
        self.video_list_data.append({"id": new_ev_id, "title": f"{new_ev_id} {title}", "author": author, "date": today, "data_file": f"js/{new_ev_id}.js"})
        self.write_videolist_file()
        messagebox.showinfo("成功", "所有操作已成功完成！")
        self.load_and_parse_videolist()
    
    def write_videolist_file(self):
        updated_list_str = json.dumps(self.video_list_data, indent=4, ensure_ascii=False)
        content = f"// 这是一个包含所有视频元数据的数组。\n// 导航站将读取这个列表来生成视频卡片。\nconst videoList = {updated_list_str};\n// 当您投稿新视频时，请在此处添加新的条目"
        try:
            with open(self.video_list_path_var.get(), 'w', encoding='utf-8') as f: f.write(content)
        except Exception as e: messagebox.showerror("写入错误", f"无法更新文件 {self.video_list_path_var.get()}\n{e}"); return

    def clear_form(self):
        self.title_var.set(""); self.source_video_path_var.set("")
        self.desc_text.delete("1.0", "end")
        for widget in self.sidebar_scroll_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame): widget.destroy()

    def populate_edit_selector(self):
        self.edit_selector_combo.configure(values=[item['title'] for item in self.video_list_data])
        self.edit_selector_combo.set('')

    def browse_videolist(self):
        path = filedialog.askopenfilename(title="选择 video_list.js", filetypes=(("JS", "*.js"),))
        if path: self.video_list_path_var.set(path); self.ev_path_var.set(os.path.dirname(path))
    def browse_ev_path(self):
        path = filedialog.askdirectory(title="选择 EV.js 输出目录")
        if path: self.ev_path_var.set(path)
    def browse_video_output_path(self):
        path = filedialog.askdirectory(title="选择视频文件输出目录")
        if path: self.video_output_path_var.set(path)
    def browse_source_video(self):
        path = filedialog.askopenfilename(title="选择视频文件", filetypes=(("视频", "*.mp4 *.mov *.avi *.mkv"),))
        if path: self.source_video_path_var.set(path)
    
    def on_closing(self):
        self.save_current_config()
        self.destroy()

if __name__ == "__main__":
    app = VideoApp()
    app.mainloop()