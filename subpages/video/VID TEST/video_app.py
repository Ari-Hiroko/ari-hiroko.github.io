import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import configparser
import json
import re
import os
import shutil
from datetime import datetime

# --- 配置文件处理器 ---
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

class VideoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.video_list_data = []
        self.next_ev_number = 1
        self.sidebar_frames = []
        self.edit_mode = False
        self.editing_ev_info = {}

        self.title("视频投稿与编辑应用")
        self.geometry("850x980") # 再次增加窗口大小

        style = ttk.Style(self); style.theme_use('clam')
        load_config()
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        # --- 重构布局：底部按钮栏 + 顶部内容区 ---
        self.bottom_frame = ttk.Frame(self, padding="10")
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.top_frame = ttk.Frame(self, padding="10")
        self.top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # --- 1. 配置区域 (位于顶部) ---
        config_frame = ttk.LabelFrame(self.top_frame, text="配置", padding="10")
        config_frame.pack(fill=tk.X, expand=False, pady=5)
        
        # ... 配置项 ...
        ttk.Label(config_frame, text="默认作者:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.author_var = tk.StringVar(value=config['Settings'].get('default_author', ''))
        ttk.Entry(config_frame, textvariable=self.author_var, width=50).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(config_frame, text="video_list.js 路径:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.video_list_path_var = tk.StringVar(value=config['Settings'].get('video_list_path', ''))
        ttk.Entry(config_frame, textvariable=self.video_list_path_var).grid(row=1, column=1, sticky="ew")
        ttk.Button(config_frame, text="浏览...", command=self.browse_videolist).grid(row=1, column=2, padx=5)
        ttk.Label(config_frame, text="EV.js 输出目录:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.ev_path_var = tk.StringVar(value=config['Settings'].get('ev_files_output_path', ''))
        ttk.Entry(config_frame, textvariable=self.ev_path_var).grid(row=2, column=1, sticky="ew")
        ttk.Button(config_frame, text="浏览...", command=self.browse_ev_path).grid(row=2, column=2, padx=5)
        ttk.Label(config_frame, text="视频文件输出目录:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.video_output_path_var = tk.StringVar(value=config['Settings'].get('video_output_path', ''))
        ttk.Entry(config_frame, textvariable=self.video_output_path_var).grid(row=3, column=1, sticky="ew")
        ttk.Button(config_frame, text="浏览...", command=self.browse_video_output_path).grid(row=3, column=2, padx=5)
        ttk.Label(config_frame, text="视频Web路径前缀:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.video_web_prefix_var = tk.StringVar(value=config['Settings'].get('video_web_path_prefix', '/vid/'))
        ttk.Entry(config_frame, textvariable=self.video_web_prefix_var).grid(row=4, column=1, sticky="ew")
        ttk.Button(config_frame, text="保存配置", command=self.save_current_config).grid(row=5, column=2, padx=5, pady=10)
        config_frame.columnconfigure(1, weight=1)

        load_frame = ttk.Frame(self.top_frame); load_frame.pack(fill=tk.X, pady=5, padx=0)
        ttk.Button(load_frame, text="读取并解析 video_list.js", command=self.load_and_parse_videolist).pack(side=tk.LEFT)
        self.status_label = ttk.Label(load_frame, text="请先选择并读取 video_list.js", foreground="blue")
        self.status_label.pack(side=tk.LEFT, padx=10)

        # --- 编辑区域 ---
        self.edit_frame = ttk.LabelFrame(self.top_frame, text="编辑现有视频", padding="10")
        ttk.Label(self.edit_frame, text="选择视频进行编辑:").pack(side=tk.LEFT, padx=5)
        self.edit_selector_combo = ttk.Combobox(self.edit_frame, state='readonly', width=50)
        self.edit_selector_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(self.edit_frame, text="加载以进行编辑", command=self.load_ev_for_editing).pack(side=tk.LEFT, padx=5)

        # --- 表单区域 ---
        self.details_frame = ttk.LabelFrame(self.top_frame, text="视频信息", padding="10")
        self.details_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # ... (表单内容与之前相同)
        self.source_video_label = ttk.Label(self.details_frame, text="选择源视频文件:")
        self.source_video_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.source_video_path_var = tk.StringVar()
        self.source_video_entry = ttk.Entry(self.details_frame, textvariable=self.source_video_path_var, state='readonly')
        self.source_video_entry.grid(row=0, column=1, sticky="ew")
        self.source_video_button = ttk.Button(self.details_frame, text="选择视频...", command=self.browse_source_video)
        self.source_video_button.grid(row=0, column=2, padx=5)
        ttk.Label(self.details_frame, text="视频标题:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.title_var = tk.StringVar()
        ttk.Entry(self.details_frame, textvariable=self.title_var).grid(row=1, column=1, columnspan=2, sticky="ew", pady=5)
        ttk.Label(self.details_frame, text="视频简介 (支持换行):").grid(row=2, column=0, padx=5, pady=5, sticky="nw")
        self.desc_text = tk.Text(self.details_frame, height=5, width=60)
        self.desc_text.grid(row=2, column=1, columnspan=2, sticky="ew", pady=5)
        self.details_frame.columnconfigure(1, weight=1)
        sidebar_main_frame = ttk.LabelFrame(self.details_frame, text="侧边栏卡片", padding="10")
        sidebar_main_frame.grid(row=3, column=0, columnspan=3, sticky="nsew", pady=10)
        self.details_frame.rowconfigure(3, weight=1)
        self.add_card_button = ttk.Button(sidebar_main_frame, text="✚ 添加卡片", command=self.add_sidebar_card_ui)
        self.add_card_button.pack(anchor="w", pady=5)
        canvas = tk.Canvas(sidebar_main_frame); scrollbar = ttk.Scrollbar(sidebar_main_frame, orient="vertical", command=canvas.yview); self.scrollable_frame = ttk.Frame(canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw"); canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True); scrollbar.pack(side="right", fill="y")
        
        # --- 操作按钮 (位于底部) ---
        self.action_button = ttk.Button(self.bottom_frame, text="---", command=self.process_submission)
        self.action_button.pack(side=tk.LEFT, padx=10, ipady=5)
        self.reset_button = ttk.Button(self.bottom_frame, text="---", command=self.reset_to_new_mode)
        self.reset_button.pack(side=tk.LEFT, padx=10, ipady=5)
        
        self.toggle_details_frame(tk.DISABLED)

    def save_current_config(self):
        save_config(self.author_var.get(), self.video_list_path_var.get(), self.ev_path_var.get(), self.video_output_path_var.get(), self.video_web_prefix_var.get())
        messagebox.showinfo("成功", "配置已保存到 config.ini")

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
            self.edit_frame.pack(fill=tk.X, expand=False, pady=5, before=self.details_frame) # 显示编辑区
            self.reset_to_new_mode() # 默认进入新建模式
        except Exception as e:
            messagebox.showerror("解析错误", f"无法解析 video_list.js。\n错误详情: {e}")
            self.toggle_details_frame(tk.DISABLED)
            self.edit_frame.pack_forget()

    def populate_edit_selector(self):
        self.edit_selector_combo['values'] = [item['title'] for item in self.video_list_data]
        self.edit_selector_combo.set('')

    def load_ev_for_editing(self):
        selected_title = self.edit_selector_combo.get()
        if not selected_title: messagebox.showwarning("提示", "请先从下拉菜单中选择一个视频。"); return

        video_info = next((item for item in self.video_list_data if item['title'] == selected_title), None)
        if not video_info: return

        ev_js_dir = self.ev_path_var.get() or os.path.dirname(self.video_list_path_var.get())
        # 从 data_file 中提取文件名，兼容 'js/EV1.js' 和 'EV1.js' 格式
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
            
            # --- 进入编辑模式 ---
            self.switch_to_edit_mode(video_info, ev_file_path, get_val, sidebar_cards)

        except Exception as e: messagebox.showerror("加载错误", f"无法解析 {video_info['id']}.js 文件。\n{e}")

    def clear_form(self):
        """仅清空表单内容"""
        self.title_var.set("")
        self.source_video_path_var.set("")
        self.desc_text.delete("1.0", tk.END)
        for frame in self.sidebar_frames: frame.destroy()
        self.sidebar_frames.clear()

    def switch_to_new_mode(self):
        """切换到新建模式"""
        self.edit_mode = False
        self.editing_ev_info = {}
        self.next_ev_number = len(self.video_list_data) + 1
        
        self.clear_form()
        
        self.status_label.config(text=f"当前模式: 新建 (ID 将为 EV{self.next_ev_number})", foreground="blue")
        self.action_button.config(text="生成文件并移动视频")
        self.reset_button.config(text="清空表单")
        self.toggle_details_frame(tk.NORMAL)
        
    def switch_to_edit_mode(self, video_info, file_path, val_getter, cards):
        """切换到编辑模式并填充数据"""
        self.edit_mode = True
        self.editing_ev_info = {**video_info, 'full_path': file_path}
        
        self.clear_form()
        
        # 填充数据
        self.title_var.set(val_getter('title'))
        self.desc_text.insert("1.0", val_getter('description'))
        self.author_var.set(val_getter('author'))
        for card in cards:
            self.add_sidebar_card_ui(card.get('title', ''), card.get('content', ''))
        
        self.status_label.config(text=f"当前模式: 编辑 {video_info['id']}", foreground="purple")
        self.action_button.config(text="保存更改")
        self.reset_button.config(text="切换到新建模式")
        self.toggle_details_frame(tk.NORMAL, is_editing=True)
        
    def reset_to_new_mode(self):
        """按钮调用的函数，总是切换到新建模式"""
        self.edit_selector_combo.set('') # 清空下拉菜单选择
        self.switch_to_new_mode()

    def process_submission(self):
        if self.edit_mode: self.save_edited_files()
        else: self.generate_new_files()

    def save_edited_files(self):
        if not self.title_var.get(): messagebox.showwarning("提示", "视频标题不能为空！"); return
        
        author = self.author_var.get(); title = self.title_var.get()
        description = self.desc_text.get("1.0", tk.END).strip().replace("\n", "\\n")
        sidebar_cards = [{"title": f.winfo_children()[1].get(), "content": f.winfo_children()[3].get("1.0", tk.END).strip()} for f in self.sidebar_frames]
        
        with open(self.editing_ev_info['full_path'], 'r', encoding='utf-8') as f: old_content = f.read()
        src_match = re.search(r'videoSrc\s*:\s*"(.*?)"', old_content)
        video_src_path = src_match.group(1) if src_match else ""

        ev_file_content = f"""/** ... */\nconst config = {{\n    title: "{title}",\n    id: "{self.editing_ev_info['id']}",\n    date: "{self.editing_ev_info['date']}",\n    author: "{author}",\n    videoSrc: "{video_src_path}",\n    poster: "", \n    description: "{description}",\n    sidebarCards: {json.dumps(sidebar_cards, indent=4, ensure_ascii=False)}\n}};"""
        
        try:
            with open(self.editing_ev_info['full_path'], 'w', encoding='utf-8') as f: f.write(ev_file_content)
        except Exception as e: messagebox.showerror("写入错误", f"无法写入文件 {self.editing_ev_info['full_path']}\n{e}"); return

        for item in self.video_list_data:
            if item['id'] == self.editing_ev_info['id']:
                item['title'] = f"{item['id']} {title}"; item['author'] = author; break
        
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
        description = self.desc_text.get("1.0", tk.END).strip().replace("\n", "\\n")
        sidebar_cards = [{"title": f.winfo_children()[1].get(), "content": f.winfo_children()[3].get("1.0", tk.END).strip()} for f in self.sidebar_frames]
        
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

    def toggle_details_frame(self, state, is_editing=False):
        for child in self.details_frame.winfo_children():
            try: child.configure(state=state)
            except tk.TclError:
                if child.winfo_children(): # Handle containers like frames
                    for grandchild in child.winfo_children():
                        try: grandchild.configure(state=state)
                        except tk.TclError: pass
        self.action_button.configure(state=state)
        self.reset_button.configure(state=state)
        
        video_select_state = tk.DISABLED if is_editing else state
        self.source_video_label.configure(state=video_select_state)
        self.source_video_entry.configure(state=video_select_state)
        self.source_video_button.configure(state=video_select_state)

    def add_sidebar_card_ui(self, title="", content=""):
        card_frame = ttk.Frame(self.scrollable_frame, padding=5, relief="groove", borderwidth=1); card_frame.pack(fill=tk.X, expand=True, pady=5, padx=5)
        ttk.Label(card_frame, text="卡片标题:").grid(row=0, column=0, sticky="w"); title_entry = ttk.Entry(card_frame); title_entry.grid(row=0, column=1, sticky="ew", padx=5); title_entry.insert(0, title)
        ttk.Label(card_frame, text="卡片内容:").grid(row=1, column=0, sticky="nw"); content_text = tk.Text(card_frame, height=3); content_text.grid(row=1, column=1, sticky="ew", padx=5); content_text.insert("1.0", content)
        remove_btn = ttk.Button(card_frame, text="移除", command=lambda f=card_frame: self.remove_sidebar_card_ui(f)); remove_btn.grid(row=0, column=2, padx=5)
        card_frame.columnconfigure(1, weight=1); self.sidebar_frames.append(card_frame)

    def remove_sidebar_card_ui(self, frame_to_remove):
        frame_to_remove.destroy(); self.sidebar_frames.remove(frame_to_remove)
    
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