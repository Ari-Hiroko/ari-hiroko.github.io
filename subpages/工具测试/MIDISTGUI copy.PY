import flet as ft
# 导入 flet_charts 模块并手动标注类型，规避 ModuleType 误报
import flet_charts as fch 
import pretty_midi
import json
import os
import tempfile
import ctypes
import matplotlib
from matplotlib.figure import Figure
from typing import Any, List, Dict

class MidiWorkstationApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "MIDI 轨道解析与提取工作站"
        
        # 窗口设置
        self.page.window.width = 1100
        self.page.window.height = 700
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.window.prevent_close = True
        self.page.window.on_event = self.on_window_event

        # 核心数据声明
        self.midi_data: pretty_midi.PrettyMIDI | None = None
        self.instruments: List[pretty_midi.Instrument] = []
        self.current_output_data: List[Dict[str, float]] | None = None
        self.temp_midi_path: str = os.path.join(tempfile.gettempdir(), "preview_temp.mid")

        self.file_picker = ft.FilePicker()
        self.file_picker.on_result = self.on_file_selected  # type: ignore
        self.save_picker = ft.FilePicker()
        self.save_picker.on_result = self.on_save_selected  # type: ignore
        self.page.overlay.extend([self.file_picker, self.save_picker])

        self.setup_ui()

    def setup_ui(self):
        # --- 左侧 UI ---
        self.btn_browse = ft.Button(
            "📂 加载 MIDI 文件", 
            on_click=self.handle_pick_files # type: ignore
        )
        self.lbl_filepath = ft.Text("未选择文件...", color="#9E9E9E", size=12)
        self.lbl_bpm = ft.Text("BPM: --", size=14)
        
        self.combo_track = ft.Dropdown(
            label="选择轨道", 
            options=[ft.dropdown.Option("0", "空")], 
            disabled=True
        )
        
        self.btn_play = ft.Button(
            "▶ 试听", 
            disabled=True, 
            bgcolor="#388E3C", 
            color="white", 
            on_click=self.play_preview, # type: ignore
            expand=True
        )
        self.btn_stop = ft.Button(
            "⏹ 停止", 
            disabled=True, 
            bgcolor="#D32F2F", 
            color="white", 
            on_click=self.stop_preview # type: ignore
        )
        
        self.btn_extract = ft.Button("⚡ 提取音符", disabled=True, on_click=self.extract_notes) # type: ignore
        self.btn_export = ft.Button(
            "💾 导出 JSON", 
            disabled=True, 
            bgcolor="#795548", 
            color="white", 
            on_click=self.handle_save_file # type: ignore
        )

        # 修复位置参数报错：使用 controls= 关键字参数
        sidebar_controls: List[ft.Control] = [
            ft.Text("MIDI 控制台", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20, color="transparent"),
            self.btn_browse, 
            self.lbl_filepath,
            ft.Container(content=self.lbl_bpm, padding=10, bgcolor="#303030", border_radius=5),
            ft.Divider(height=20, color="transparent"),
            self.combo_track,
            ft.Row(controls=[self.btn_play, self.btn_stop], spacing=10),
            ft.Divider(height=30, color="transparent"),
            self.btn_extract, 
            self.btn_export
        ]

        sidebar = ft.Container(
            width=280, 
            padding=20, 
            bgcolor="#424242",
            content=ft.Column(controls=sidebar_controls)
        )

        # --- 右侧 UI ---
        # 修复位置参数报错：使用 x=, y= 关键字参数
        self.chart_holder = ft.Container(
            content=ft.Text("请加载 MIDI 文件以预览轨道", color="gray"),
            expand=6, 
            padding=10, 
            bgcolor="#2b2b2b", 
            border_radius=10, 
            alignment=ft.Alignment(x=0, y=0)
        )

        self.textbox = ft.TextField(
            multiline=True, 
            read_only=True, 
            expand=4,
            text_size=13, 
            text_style=ft.TextStyle(font_family="Consolas"),
            bgcolor="#424242", 
            border_radius=10
        )

        main_frame = ft.Column(controls=[self.chart_holder, self.textbox], expand=True, spacing=15)
        
        # 整体布局组合
        self.page.add(
            ft.Container(
                content=ft.Row(controls=[sidebar, main_frame], expand=True), 
                padding=15, 
                expand=True
            )
        )

    # --- 异步逻辑 ---
    async def handle_pick_files(self, e: Any):
        await self.file_picker.pick_files(allowed_extensions=["mid", "midi"])

    async def handle_save_file(self, e: Any):
        await self.save_picker.save_file(
            dialog_title="保存 JSON 数据",
            allowed_extensions=["json"],
            file_name="extracted_notes.json"
        )

    async def log(self, message: str):
        prev = self.textbox.value if self.textbox.value else ""
        self.textbox.value = prev + f"\n[System] {message}"
        self.page.update()

    async def on_file_selected(self, e: ft.FilePickerResultEvent):
        if e.files:
            file_path = e.files[0].path
            self.lbl_filepath.value = os.path.basename(file_path)
            await self.load_midi(file_path)

    async def load_midi(self, file_path: str):
        await self.stop_preview(None)
        try:
            self.midi_data = pretty_midi.PrettyMIDI(file_path)
            self.instruments = self.midi_data.instruments
            
            fig = Figure(figsize=(8, 4), dpi=100)
            fig.patch.set_facecolor('#2b2b2b')
            ax = fig.add_subplot(111)
            ax.set_facecolor('#333333')
            ax.tick_params(colors='white')

            cmap = matplotlib.colormaps.get_cmap('tab10')
            for i, inst in enumerate(self.instruments):
                if not inst.notes: continue
                ax.hlines(y=[n.pitch for n in inst.notes], 
                          xmin=[n.start for n in inst.notes], 
                          xmax=[n.end for n in inst.notes], 
                          colors=cmap(i % 10), linewidth=2)
            fig.tight_layout()

            # type: ignore 强制跳过 Pylance 对 MatplotlibChart 的类型识别错误
            self.chart_holder.content = fch.MatplotlibChart(figure=fig, expand=True) # type: ignore
            
            bpm_val = self.midi_data.estimate_tempo()
            self.lbl_bpm.value = f"估算 BPM: {bpm_val:.1f}"
            self.combo_track.options = [
                ft.dropdown.Option(str(i), f"{i}: {inst.name}") 
                for i, inst in enumerate(self.instruments)
            ]
            self.combo_track.value = "0"
            self.combo_track.disabled = False
            self.btn_extract.disabled = self.btn_play.disabled = self.btn_stop.disabled = False
            
            await self.log(f"成功加载: {os.path.basename(file_path)}")
            self.page.update()
        except Exception as ex:
            await self.log(f"错误: {ex}")

    async def play_preview(self, e: Any):
        if self.midi_data is None or self.combo_track.value is None: 
            return
        try:
            idx = int(str(self.combo_track.value))
            temp_midi = pretty_midi.PrettyMIDI()
            temp_midi.instruments.append(self.instruments[idx])
            temp_midi.write(self.temp_midi_path)
            await self.stop_preview(None)
            ctypes.windll.winmm.mciSendStringW(f'open "{self.temp_midi_path}" alias my_midi', None, 0, None)
            ctypes.windll.winmm.mciSendStringW('play my_midi', None, 0, None)
        except Exception: 
            pass

    async def stop_preview(self, e: Any | None):
        ctypes.windll.winmm.mciSendStringW('stop my_midi', None, 0, None)
        ctypes.windll.winmm.mciSendStringW('close my_midi', None, 0, None)

    async def extract_notes(self, e: Any):
        if self.combo_track.value is None: return
        idx = int(str(self.combo_track.value))
        notes = self.instruments[idx].notes
        self.current_output_data = [{"pitch": n.pitch, "start": round(n.start, 4)} for n in notes]
        self.textbox.value = json.dumps(self.current_output_data, indent=4)
        self.btn_export.disabled = False
        self.page.update()

    async def on_save_selected(self, e: ft.FilePickerResultEvent):
        if e.path and self.current_output_data:
            with open(e.path, 'w', encoding='utf-8') as f: 
                json.dump(self.current_output_data, f, indent=4)
            await self.log("导出成功")

    async def on_window_event(self, e: ft.ControlEvent):
        if e.data == "close":
            await self.stop_preview(None)
            if os.path.exists(self.temp_midi_path):
                try: os.remove(self.temp_midi_path)
                except: pass
            await self.page.window.destroy()

async def main(page: ft.Page):
    MidiWorkstationApp(page)

if __name__ == "__main__":
    ft.run(main)