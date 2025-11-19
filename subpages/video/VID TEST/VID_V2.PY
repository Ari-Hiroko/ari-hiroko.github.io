import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import configparser
import json
import re
import os
import shutil
from datetime import datetime
import sys

# --- 1. DPI 适配 ---
if sys.platform.startswith("win"):
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception: pass

# --- 配置文件处理 ---
CONFIG_FILE = 'config.ini'
config = configparser.ConfigParser()

def load_config():
    if not os.path.exists(CONFIG_FILE): create_default_config()
    config.read(CONFIG_FILE, encoding='utf-8')
    
def create_default_config():
    config['Settings'] = {
        'default_author': 'Your Name', 
        'video_list_path': '',
        'ev_files_output_path': '', 
        'video_output_path': '',
        'video_web_path_prefix': '/vid/',
        'theme': 'System'
    }
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f: config.write(f)

def save_config(author, list_path, ev_path, vid_path, vid_prefix, theme):
    config['Settings'] = {
        'default_author': author, 
        'video_list_path': list_path,
        'ev_files_output_path': ev_path, 
        'video_output_path': vid_path,
        'video_web_path_prefix': vid_prefix,
        'theme': theme
    }
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f: config.write(f)

# --- 动画缓动函数 ---
def ease_out_quart(t):
    return 1 - pow(1 - t, 4)

# --- UI 主类 ---
class VideoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 加载配置
        load_config()
        self.cfg = config['Settings']
        
        # --- 主题初始化 ---
        init_theme = self.cfg.get('theme', 'System')
        ctk.set_appearance_mode(init_theme)
        ctk.set_default_color_theme("blue")
        
        self.title("Video Manager Pro")
        self.geometry("1100x850")
        self.minsize(1000, 750)

        # --- 配色方案 ---
        self.colors = {
            "bg_app":       ("#FAFAFA", "#18181B"),
            "bg_card":      ("#FFFFFF", "#27272A"),
            "border":       ("#E4E4E7", "#3F3F46"),
            "border_hover": ("#A1A1AA", "#71717A"),
            "text_h":       ("#18181B", "#F4F4F5"),
            "text_p":       ("#3F3F46", "#D4D4D8"),
            "text_sub":     ("#A1A1AA", "#71717A"),
            "primary":      ("#2563EB", "#3B82F6"),
            "primary_hov":  ("#1D4ED8", "#2563EB"),
            "danger":       ("#EF4444", "#EF4444"),
            "input_bg":     ("#FFFFFF", "#3F3F46"),
            "accent_bg":    ("#F4F4F5", "#3F3F46"),
            "nav_text_def": ("#52525B", "#A1A1AA"),
            # 分段按钮专用颜色
            "seg_unselected": ("#FFFFFF", "#3F3F46"), # 浅色模式下纯白
            "seg_text":       ("#3F3F46", "#D4D4D8"),
        }

        # 字体定义
        self.fonts = {
            "h1": ctk.CTkFont(family="Microsoft YaHei UI", size=20, weight="bold"),
            "h2": ctk.CTkFont(family="Microsoft YaHei UI", size=14, weight="bold"),
            "body": ctk.CTkFont(family="Microsoft YaHei UI", size=13),
            "small": ctk.CTkFont(family="Microsoft YaHei UI", size=12),
            "ui": ctk.CTkFont(family="Segoe UI", size=13),
            "nav": ctk.CTkFont(family="Microsoft YaHei UI", size=14, weight="bold"),
        }

        # 变量初始化
        self.var_author = tk.StringVar(value=self.cfg.get('default_author', ''))
        self.var_path_list = tk.StringVar(value=self.cfg.get('video_list_path', ''))
        self.var_path_ev = tk.StringVar(value=self.cfg.get('ev_files_output_path', ''))
        self.var_path_vid = tk.StringVar(value=self.cfg.get('video_output_path', ''))
        self.var_web_prefix = tk.StringVar(value=self.cfg.get('video_web_path_prefix', '/vid/'))
        self.var_theme = tk.StringVar(value=init_theme)

        # 数据初始化
        self.video_list_data = []
        self.next_ev_number = 1
        self.edit_mode = False
        self.editing_ev_info = {}
        self.nav_buttons = {}
        
        # 界面构建
        self.configure(fg_color=self.colors["bg_app"])
        self.setup_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.after(100, self.check_initial_status)

    def check_initial_status(self):
        if self.var_path_list.get():
            self.load_and_parse_videolist()
        else:
            self.animate_nav("settings")
            messagebox.showinfo("欢迎", "请先配置 video_list.js 路径。")

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ================= 1. 顶部导航栏 =================
        self.header = ctk.CTkFrame(self, height=70, fg_color=self.colors["bg_card"], corner_radius=0)
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_columnconfigure(1, weight=1)

        # Logo
        ctk.CTkLabel(self.header, text="VIDEO MANAGER", font=("Segoe UI Black", 18), text_color=self.colors["text_h"]).grid(row=0, column=0, padx=35, pady=20)

        # 导航容器
        self.nav_container = ctk.CTkFrame(self.header, fg_color="transparent", height=70, width=220)
        self.nav_container.grid(row=0, column=1, sticky="e", padx=40)
        
        self.nav_indicator = ctk.CTkFrame(self.nav_container, height=4, width=50, fg_color=self.colors["primary"], corner_radius=2)
        self.nav_indicator.place(x=0, y=55)

        self.nav_items = {
            "work":     {"label": "工作台", "x_btn": 10,  "x_ind": 25},
            "settings": {"label": "设置",   "x_btn": 100, "x_ind": 115}
        }

        for key, val in self.nav_items.items():
            btn = ctk.CTkButton(self.nav_container, text=val["label"], width=80, height=40,
                                fg_color="transparent", hover_color=self.colors["accent_bg"],
                                text_color=self.colors["nav_text_def"], font=self.fonts["ui"],
                                command=lambda k=key: self.animate_nav(k))
            btn.place(x=val["x_btn"], y=15)
            self.nav_buttons[key] = btn

        # ================= 2. 内容区域 =================
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.grid(row=1, column=0, sticky="nsew", padx=35, pady=25)
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

        self.frame_work = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.frame_settings = ctk.CTkFrame(self.content_area, fg_color="transparent")

        self.setup_work_ui()
        self.setup_settings_ui()
        
        self.current_nav = None
        self.animate_nav("work")

    def animate_nav(self, target):
        if target == self.current_nav: return
        
        for key, btn in self.nav_buttons.items():
            if key == target: btn.configure(text_color=self.colors["primary"], font=self.fonts["nav"])
            else: btn.configure(text_color=self.colors["nav_text_def"], font=self.fonts["ui"])

        if target == "work":
            self.frame_settings.grid_remove()
            self.frame_work.grid(row=0, column=0, sticky="nsew")
        else:
            self.frame_work.grid_remove()
            self.frame_settings.grid(row=0, column=0, sticky="nsew")

        start_x = self.nav_items[self.current_nav]["x_ind"] if self.current_nav else self.nav_items[target]["x_ind"]
        end_x = self.nav_items[target]["x_ind"]
        self.current_nav = target
        self.animation_step = 0
        self.animate_indicator(start_x, end_x)

    def animate_indicator(self, start, end):
        total_frames = 20
        if self.animation_step > total_frames:
            self.nav_indicator.place(x=end, y=55)
            return
        t = self.animation_step / total_frames
        eased_t = ease_out_quart(t)
        current_x = start + (end - start) * eased_t
        self.nav_indicator.place(x=current_x, y=55)
        self.animation_step += 1
        self.after(10, lambda: self.animate_indicator(start, end))

    # ================= 3. 工作台 (修复布局/遮挡) =================
    def setup_work_ui(self):
        self.frame_work.grid_columnconfigure(0, weight=7)
        self.frame_work.grid_columnconfigure(1, weight=3)
        self.frame_work.grid_rowconfigure(1, weight=1)

        # --- Toolbar ---
        # 修复2：高度增加至 76px，留出呼吸空间
        toolbar = ctk.CTkFrame(self.frame_work, height=76, fg_color=self.colors["bg_card"], corner_radius=10, border_width=1, border_color=self.colors["border"])
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        toolbar.grid_propagate(False)

        # 左侧
        ctk.CTkLabel(toolbar, text="●", text_color="#10B981", font=("Arial", 20)).pack(side="left", padx=(25, 10))
        self.status_label = ctk.CTkLabel(toolbar, text="准备就绪", font=self.fonts["h2"], text_color=self.colors["text_h"])
        self.status_label.pack(side="left", anchor="center")

        # 右侧控件组
        # 修复2：fg_color="transparent" 使背景透明
        # 修复2：控件高度设为 30px，远小于工具栏 76px，垂直居中
        ctrl_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        ctrl_frame.pack(side="right", padx=25, pady=5, anchor="center") 

        # 修复3：文字与下拉框增加间距 padx=(0, 15)
        ctk.CTkLabel(ctrl_frame, text="编辑模式:", font=self.fonts["body"], text_color=self.colors["text_sub"]).pack(side="left", padx=(0, 15))
        
        # 下拉框
        self.edit_selector = ctk.CTkComboBox(ctrl_frame, width=200, height=30, 
                                             font=self.fonts["body"], dropdown_font=self.fonts["body"],
                                             state="readonly",
                                             # 颜色策略：使用透明/工具栏背景色，消除色块感
                                             fg_color=self.colors["bg_card"], 
                                             button_color=self.colors["bg_card"], 
                                             border_color=self.colors["border"], 
                                             button_hover_color=self.colors["accent_bg"],
                                             text_color=self.colors["text_p"],
                                             dropdown_fg_color=self.colors["bg_card"], 
                                             dropdown_hover_color=self.colors["accent_bg"], 
                                             dropdown_text_color=self.colors["text_p"])
        self.edit_selector.set("请先加载列表")
        self.edit_selector.pack(side="left")

        # 加载按钮
        ctk.CTkButton(ctrl_frame, text="加载", width=60, height=30, font=self.fonts["body"], 
                      fg_color="transparent", border_width=1, border_color=self.colors["border"], 
                      text_color=self.colors["text_p"], hover_color=self.colors["accent_bg"],
                      command=self.load_ev_for_editing).pack(side="left", padx=(12, 0))

        # 刷新按钮
        ctk.CTkButton(ctrl_frame, text="↻", width=30, height=30, font=("Arial", 20),
                      fg_color="transparent", text_color=self.colors["text_sub"], hover_color=self.colors["accent_bg"],
                      command=self.load_and_parse_videolist).pack(side="left", padx=(8, 0))

        # --- 主表单 ---
        form_card = ctk.CTkFrame(self.frame_work, fg_color=self.colors["bg_card"], corner_radius=10, border_width=1, border_color=self.colors["border"])
        form_card.grid(row=1, column=0, sticky="nsew", padx=(0, 20))
        form_card.grid_columnconfigure(1, weight=1)
        form_card.grid_rowconfigure(4, weight=1)

        def add_row(row, label):
            ctk.CTkLabel(form_card, text=label, font=self.fonts["h2"], text_color=self.colors["text_p"]).grid(row=row, column=0, sticky="nw", padx=30, pady=(30 if row==0 else 25, 5))

        add_row(0, "源视频")
        vid_box = ctk.CTkFrame(form_card, fg_color="transparent")
        vid_box.grid(row=0, column=1, sticky="ew", padx=30, pady=(30, 5))
        vid_box.grid_columnconfigure(0, weight=1)
        
        self.var_source_vid = tk.StringVar()
        self.entry_vid = ctk.CTkEntry(vid_box, textvariable=self.var_source_vid, height=38, font=self.fonts["body"], fg_color=self.colors["accent_bg"], border_width=0, text_color=self.colors["text_p"], placeholder_text="新建模式必填")
        self.entry_vid.grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(vid_box, text="浏览", width=70, height=38, fg_color=self.colors["border"], hover_color=self.colors["border_hover"], text_color=self.colors["text_h"], font=self.fonts["body"], command=self.browse_source_video).grid(row=0, column=1, padx=(10, 0))

        add_row(1, "标题")
        self.var_title = tk.StringVar()
        self.entry_title = ctk.CTkEntry(form_card, textvariable=self.var_title, height=42, font=self.fonts["h2"], fg_color=self.colors["accent_bg"], border_width=0, text_color=self.colors["text_h"], placeholder_text="输入视频标题...")
        self.entry_title.grid(row=1, column=1, sticky="ew", padx=30, pady=(25, 5))

        add_row(2, "简介")
        self.text_desc = ctk.CTkTextbox(form_card, font=self.fonts["body"], fg_color=self.colors["accent_bg"], border_width=0, corner_radius=6, text_color=self.colors["text_p"])
        self.text_desc.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=30, pady=(5, 30))

        # 侧边栏
        sidebar_card = ctk.CTkFrame(self.frame_work, fg_color=self.colors["bg_card"], corner_radius=10, border_width=1, border_color=self.colors["border"])
        sidebar_card.grid(row=1, column=1, sticky="nsew")
        sidebar_card.grid_columnconfigure(0, weight=1)
        sidebar_card.grid_rowconfigure(1, weight=1)

        sb_head = ctk.CTkFrame(sidebar_card, height=50, fg_color="transparent")
        sb_head.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        ctk.CTkLabel(sb_head, text="信息卡片", font=self.fonts["h2"], text_color=self.colors["text_h"]).pack(side="left")
        ctk.CTkButton(sb_head, text="+ 添加", width=60, height=28, font=self.fonts["small"], fg_color="transparent", border_width=1, border_color=self.colors["primary"], text_color=self.colors["primary"], hover_color=self.colors["accent_bg"], command=self.add_sidebar_card_ui).pack(side="right")

        self.scroll_frame = ctk.CTkScrollableFrame(sidebar_card, fg_color="transparent", scrollbar_button_color=self.colors["border"], scrollbar_button_hover_color=self.colors["border_hover"])
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 20))

        # 底部栏
        bottom_bar = ctk.CTkFrame(self.frame_work, height=70, fg_color="transparent")
        bottom_bar.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(20, 0))
        
        self.btn_reset = ctk.CTkButton(bottom_bar, text="取消 / 新建", width=140, height=44, font=self.fonts["body"], fg_color="transparent", border_width=1, border_color=self.colors["border"], text_color=self.colors["text_sub"], hover_color=self.colors["accent_bg"], command=self.reset_to_new_mode)
        self.btn_reset.pack(side="left")
        
        self.btn_action = ctk.CTkButton(bottom_bar, text="发布视频", height=48, font=ctk.CTkFont(family="Microsoft YaHei UI", size=16, weight="bold"), corner_radius=24, fg_color=self.colors["primary"], hover_color=self.colors["primary_hov"], text_color="#FFFFFF", command=self.process_submission)
        self.btn_action.pack(side="right", fill="x", expand=True, padx=(25, 0))

        self.toggle_inputs("disabled")

    # ================= 4. 设置页 =================
    def setup_settings_ui(self):
        self.frame_settings.grid_columnconfigure(0, weight=1)
        container = ctk.CTkFrame(self.frame_settings, fg_color=self.colors["bg_card"], corner_radius=10, border_width=1, border_color=self.colors["border"])
        container.pack(fill="both", expand=True)
        
        inner = ctk.CTkFrame(container, fg_color="transparent")
        inner.pack(fill="x", padx=60, pady=60)
        inner.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(inner, text="环境配置", font=self.fonts["h1"], text_color=self.colors["text_h"]).grid(row=0, column=0, sticky="w", pady=(0, 30))

        def add_row(idx, txt, var, cmd=None):
            ctk.CTkLabel(inner, text=txt, font=self.fonts["body"], text_color=self.colors["text_p"]).grid(row=idx, column=0, sticky="w", pady=15, padx=(0, 20))
            ctk.CTkEntry(inner, textvariable=var, height=38, font=self.fonts["body"], fg_color=self.colors["accent_bg"], border_width=0, text_color=self.colors["text_p"]).grid(row=idx, column=1, sticky="ew", pady=15)
            if cmd: ctk.CTkButton(inner, text="浏览", width=80, height=38, fg_color=self.colors["border"], hover_color=self.colors["border_hover"], text_color=self.colors["text_h"], font=self.fonts["body"], command=cmd).grid(row=idx, column=2, padx=(15, 0))

        add_row(1, "默认作者", self.var_author)
        add_row(2, "列表文件路径", self.var_path_list, self.browse_videolist)
        add_row(3, "EV.js 输出目录", self.var_path_ev, self.browse_ev_path)
        add_row(4, "视频存储目录", self.var_path_vid, self.browse_video_output_path)
        add_row(5, "Web URL 前缀", self.var_web_prefix)

        ctk.CTkLabel(inner, text="外观模式", font=self.fonts["body"], text_color=self.colors["text_p"]).grid(row=6, column=0, sticky="w", pady=15)
        
        # 修复1：外观切换器美化
        theme_seg = ctk.CTkSegmentedButton(inner, values=["System", "Light", "Dark"], variable=self.var_theme, command=lambda m: ctk.set_appearance_mode(m), 
                                           font=self.fonts["body"], height=34,
                                           # 关键颜色调整
                                           unselected_color=self.colors["seg_unselected"], 
                                           unselected_hover_color=self.colors["border"],
                                           text_color=self.colors["seg_text"], 
                                           selected_color=self.colors["primary"], 
                                           selected_hover_color=self.colors["primary_hov"])
        theme_seg.grid(row=6, column=1, sticky="ew", pady=15)

        ctk.CTkButton(inner, text="保存设置", height=44, width=160, font=self.fonts["h2"], fg_color=self.colors["primary"], hover_color=self.colors["primary_hov"], text_color="#FFFFFF", command=self.save_current_config).grid(row=8, column=1, sticky="e", pady=40)

    # ================= 5. 业务逻辑 (保持不变) =================
    def toggle_inputs(self, state, is_editing=False):
        w_state = "normal" if state == "normal" else "disabled"
        self.entry_title.configure(state=w_state)
        self.text_desc.configure(state=w_state)
        self.btn_action.configure(state=w_state)
        vid_state = "disabled" if (is_editing or state == "disabled") else "normal"
        self.entry_vid.configure(state=vid_state)
        
        if state == "normal": self.text_desc.configure(fg_color=self.colors["input_bg"], border_width=1, border_color=self.colors["border"])
        else: self.text_desc.configure(fg_color=self.colors["accent_bg"], border_width=0)

    def add_sidebar_card_ui(self, title="", content=""):
        card = ctk.CTkFrame(self.scroll_frame, fg_color=self.colors["input_bg"], border_width=1, border_color=self.colors["border"], corner_radius=6)
        card.pack(fill="x", pady=6, padx=2)
        card.grid_columnconfigure(0, weight=1)
        
        head = ctk.CTkFrame(card, fg_color="transparent", height=30)
        head.grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 4))
        head.grid_columnconfigure(0, weight=1)
        
        t_entry = ctk.CTkEntry(head, placeholder_text="标题", font=self.fonts["h2"], height=28, fg_color="transparent", border_width=0, text_color=self.colors["text_h"])
        t_entry.grid(row=0, column=0, sticky="ew")
        t_entry.insert(0, title)
        
        ctk.CTkButton(head, text="✕", width=28, height=28, fg_color="transparent", hover_color=self.colors["accent_bg"], text_color=self.colors["danger"], font=("Arial", 14), command=card.destroy).grid(row=0, column=1)
        ctk.CTkFrame(card, height=1, fg_color=self.colors["accent_bg"]).grid(row=1, column=0, sticky="ew", padx=10, pady=2)
        
        c_text = ctk.CTkTextbox(card, height=60, font=self.fonts["small"], fg_color="transparent", border_width=0, text_color=self.colors["text_p"])
        c_text.grid(row=2, column=0, sticky="ew", padx=6, pady=(0, 8))
        c_text.insert("1.0", content)

    def get_sidebar_data(self):
        data = []
        for w in self.scroll_frame.winfo_children():
            try:
                title = w.winfo_children()[0].winfo_children()[0].get().strip()
                content = w.winfo_children()[2].get("1.0", "end-1c").strip()
                if title or content: data.append({"title": title, "content": content})
            except: pass
        return data

    def load_and_parse_videolist(self):
        path = self.var_path_list.get()
        if not path or not os.path.exists(path): return messagebox.showerror("错误", "文件不存在")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                m = re.search(r'const\s+videoList\s*=\s*(\[[\s\S]*?\]);?', f.read(), re.MULTILINE)
                if not m: raise ValueError("格式错误")
                self.video_list_data = json.loads(re.sub(r',\s*([\]}])', r'\1', m.group(1).strip()))
            self.edit_selector.configure(values=[f"{i['id']} - {i['title'].replace(i['id'], '').strip()}" for i in self.video_list_data])
            self.edit_selector.set("")
            self.reset_to_new_mode()
            messagebox.showinfo("完成", f"已加载 {len(self.video_list_data)} 条记录")
        except Exception as e: messagebox.showerror("失败", str(e))

    def load_ev_for_editing(self):
        sel = self.edit_selector.get()
        if not sel or "请先" in sel: return
        info = next((i for i in self.video_list_data if i['id'] == sel.split(' - ')[0]), None)
        if not info: return
        path = os.path.join(self.var_path_ev.get() or os.path.dirname(self.var_path_list.get()), os.path.basename(info['data_file']))
        if not os.path.exists(path): return messagebox.showerror("错误", "文件未找到")
        try:
            with open(path, 'r', encoding='utf-8') as f: content = f.read()
            def get_val(k): 
                m = re.search(rf'{k}\s*:\s*"(.*?)"', content, re.DOTALL)
                return m.group(1).replace("\\n", "\n") if m else ""
            sb_m = re.search(r'sidebarCards\s*:\s*(\[[\s\S]*?\])', content)
            cards = json.loads(re.sub(r',\s*([\]}])', r'\1', sb_m.group(1))) if sb_m else []
            self.switch_mode(True, info, path, get_val, cards)
        except Exception as e: messagebox.showerror("错误", str(e))

    def switch_mode(self, is_edit, info=None, path=None, getter=None, cards=[]):
        self.edit_mode = is_edit
        self.clear_form()
        if is_edit:
            self.editing_ev_info = {**info, 'full_path': path}
            self.var_title.set(getter('title').replace(info['id'], '').strip())
            self.text_desc.insert("1.0", getter('description'))
            self.var_author.set(getter('author'))
            for c in cards: self.add_sidebar_card_ui(c.get('title',''), c.get('content',''))
            self.status_label.configure(text=f"正在编辑 {info['id']}", text_color="#F59E0B")
            self.btn_action.configure(text="保存修改", fg_color="#F59E0B", hover_color="#D97706")
            self.toggle_inputs("normal", True)
        else:
            self.editing_ev_info = {}
            self.next_ev_number = len(self.video_list_data) + 1
            self.status_label.configure(text=f"新建模式 (EV{self.next_ev_number})", text_color=self.colors["primary"][0] if ctk.get_appearance_mode()=="Light" else self.colors["primary"][1])
            self.btn_action.configure(text="发布视频", fg_color=self.colors["primary"], hover_color=self.colors["primary_hov"])
            self.toggle_inputs("normal", False)

    def reset_to_new_mode(self):
        self.edit_selector.set("")
        self.switch_mode(False)

    def clear_form(self):
        self.var_title.set("")
        self.var_source_vid.set("")
        self.text_desc.delete("1.0", "end")
        for w in self.scroll_frame.winfo_children(): w.destroy()

    def process_submission(self):
        if self.edit_mode: self.save_edited()
        else: self.generate_new()

    def save_edited(self):
        if not self.var_title.get(): return
        with open(self.editing_ev_info['full_path'], 'r', encoding='utf-8') as f:
            src = re.search(r'videoSrc\s*:\s*"(.*?)"', f.read()).group(1)
        desc = self.text_desc.get("1.0", "end-1c").strip().replace("\n", "\\n")
        content = self.gen_js(self.var_title.get().strip(), self.editing_ev_info['id'], self.editing_ev_info['date'], self.var_author.get(), src, desc, self.get_sidebar_data())
        try:
            with open(self.editing_ev_info['full_path'], 'w', encoding='utf-8') as f: f.write(content)
            for i in self.video_list_data:
                if i['id'] == self.editing_ev_info['id']:
                    i['title'] = f"{i['id']} {self.var_title.get().strip()}"
                    i['author'] = self.var_author.get()
            self.write_list_file()
            messagebox.showinfo("成功", "保存完成")
            self.load_and_parse_videolist()
        except Exception as e: messagebox.showerror("错误", str(e))

    def generate_new(self):
        t = self.var_title.get().strip()
        src = self.var_source_vid.get()
        if not t or not src: return messagebox.showwarning("提示", "信息不全")
        nid = f"EV{self.next_ev_number}"
        fname = f"{nid}{os.path.splitext(src)[1]}"
        try: shutil.move(src, os.path.join(self.var_path_vid.get(), fname))
        except Exception as e: return messagebox.showerror("错误", str(e))
        today = datetime.now().strftime("%Y-%m-%d")
        desc = self.text_desc.get("1.0", "end-1c").strip().replace("\n", "\\n")
        content = self.gen_js(t, nid, today, self.var_author.get(), f"/{self.var_web_prefix.get().strip('/')}/{fname}", desc, self.get_sidebar_data())
        try:
            with open(os.path.join(self.var_path_ev.get(), f"{nid}.js"), 'w', encoding='utf-8') as f: f.write(content)
            self.video_list_data.append({"id": nid, "title": f"{nid} {t}", "author": self.var_author.get(), "date": today, "data_file": f"js/{nid}.js"})
            self.write_list_file()
            messagebox.showinfo("成功", "发布完成")
            self.load_and_parse_videolist()
        except Exception as e: messagebox.showerror("错误", str(e))

    def gen_js(self, t, i, d, a, s, desc, c):
        return f"/** Generated */\nconst config = {{\n    title: \"{t}\",\n    id: \"{i}\",\n    date: \"{d}\",\n    author: \"{a}\",\n    videoSrc: \"{s}\",\n    poster: \"\", \n    description: \"{desc}\",\n    sidebarCards: {json.dumps(c, indent=4, ensure_ascii=False)}\n}};"

    def write_list_file(self):
        with open(self.var_path_list.get(), 'w', encoding='utf-8') as f:
            f.write(f"const videoList = {json.dumps(self.video_list_data, indent=4, ensure_ascii=False)};")

    def save_current_config(self):
        save_config(self.var_author.get(), self.var_path_list.get(), self.var_path_ev.get(), self.var_path_vid.get(), self.var_web_prefix.get(), self.var_theme.get())
        messagebox.showinfo("提示", "已保存")

    def browse_videolist(self):
        p = filedialog.askopenfilename(filetypes=(("JS", "*.js"),))
        if p: self.var_path_list.set(p); self.var_path_ev.set(os.path.dirname(p)) if not self.var_path_ev.get() else None
    def browse_ev_path(self):
        p = filedialog.askdirectory()
        if p: self.var_path_ev.set(p)
    def browse_video_output_path(self):
        p = filedialog.askdirectory()
        if p: self.var_path_vid.set(p)
    def browse_source_video(self):
        p = filedialog.askopenfilename(filetypes=(("Video", "*.mp4 *.mov *.mkv"),))
        if p: self.var_source_vid.set(p)
    def on_closing(self):
        self.save_current_config(); self.destroy()

if __name__ == "__main__":
    app = VideoApp()
    app.mainloop()