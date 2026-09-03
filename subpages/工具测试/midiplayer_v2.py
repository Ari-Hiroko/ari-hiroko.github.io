"""
Flet MIDI 播放器 - 改进版本
支持实时琴键显示、琴卷可视化和高级播放控制
"""

import flet as ft
import os
from pathlib import Path
import mido
import threading
import time
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple
import math

# MIDI音符到琴键位置的映射
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
WHITE_KEYS = [0, 2, 4, 5, 7, 9, 11]  # 白键在12个音符中的位置
BLACK_KEYS = [1, 3, 6, 8, 10]  # 黑键在12个音符中的位置
WHITE_KEY_WIDTH = 30
BLACK_KEY_WIDTH = 20
WHITE_KEY_HEIGHT = 180
BLACK_KEY_HEIGHT = 110


@dataclass
class MidiNote:
    """MIDI音符数据"""
    note: int  # MIDI音符号 (0-127)
    velocity: int  # 力度 (0-127)
    start_time: float  # 开始时间（秒）
    duration: float  # 持续时间（秒）
    
    def get_note_name(self) -> str:
        """获取音符名称"""
        octave = (self.note // 12) - 1
        note_name = NOTE_NAMES[self.note % 12]
        return f"{note_name}{octave}"
    
    def get_note_class(self) -> int:
        """获取12音中的位置"""
        return self.note % 12


class MidiPlayer:
    """MIDI播放器核心类"""
    
    def __init__(self):
        self.current_file: Optional[str] = None
        self.midi_data: Optional[mido.MidiFile] = None
        self.notes: List[MidiNote] = []
        self.is_playing = False
        self.is_paused = False
        self.current_time = 0.0
        self.total_time = 0.0
        self.playback_thread = None
        self.active_notes: set = set()
        self.on_time_changed = None
        self.on_notes_changed = None
        self.volume = 1.0
    
    def load_midi(self, file_path: str) -> bool:
        """加载MIDI文件"""
        try:
            self.midi_data = mido.MidiFile(file_path)
            self.current_file = file_path
            self.parse_notes()
            self.total_time = self.calculate_duration()
            self.current_time = 0
            return True
        except Exception as e:
            print(f"加载MIDI失败: {e}")
            return False
    
    def parse_notes(self) -> None:
        """解析MIDI文件中的所有音符"""
        self.notes = []
        if not self.midi_data:
            return
        
        for track in self.midi_data.tracks:
            current_time = 0.0
            note_on_map = {}  # 记录未关闭的音符
            tempo = 500000  # 默认120 BPM (微秒/拍)
            ticks_per_beat = self.midi_data.ticks_per_beat
            
            for msg in track:
                # 更新节奏
                if msg.type == 'set_tempo':
                    tempo = msg.tempo
                
                # 转换时间增量为秒
                time_delta = msg.time * tempo / (ticks_per_beat * 1000000)
                current_time += time_delta
                
                if msg.type == 'note_on' and msg.velocity > 0:
                    note_on_map[msg.note] = (current_time, msg.velocity)
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    if msg.note in note_on_map:
                        start_time, velocity = note_on_map[msg.note]
                        duration = current_time - start_time
                        if duration > 0:  # 只记录有效的音符
                            self.notes.append(MidiNote(
                                note=msg.note,
                                velocity=velocity,
                                start_time=start_time,
                                duration=duration
                            ))
                        del note_on_map[msg.note]
    
    def calculate_duration(self) -> float:
        """计算MIDI文件总时长（秒）"""
        if not self.midi_data:
            return 0
        
        ticks_per_beat = self.midi_data.ticks_per_beat
        tempo = 500000  # 默认120 BPM
        total_ticks = 0
        
        for track in self.midi_data.tracks:
            current_ticks = 0
            for msg in track:
                current_ticks += msg.time
                if msg.type == 'set_tempo':
                    tempo = msg.tempo
                total_ticks = max(total_ticks, current_ticks)
        
        return (total_ticks * tempo) / (ticks_per_beat * 1000000)
    
    def get_active_notes(self, time: float) -> set:
        """获取在指定时间点活动的音符"""
        active = set()
        for note in self.notes:
            if note.start_time <= time < note.start_time + note.duration:
                active.add(note.note)
        return active
    
    def play(self) -> None:
        """开始播放"""
        if self.is_playing:
            return
        
        self.is_playing = True
        self.is_paused = False
        self.playback_thread = threading.Thread(target=self._playback_loop, daemon=True)
        self.playback_thread.start()
    
    def _playback_loop(self) -> None:
        """播放循环"""
        start_time = time.time() - self.current_time
        
        while self.is_playing:
            if not self.is_paused:
                self.current_time = time.time() - start_time
                
                if self.current_time >= self.total_time:
                    self.is_playing = False
                    self.current_time = 0
                    break
                
                # 获取当前活动的音符
                new_active_notes = self.get_active_notes(self.current_time)
                if new_active_notes != self.active_notes:
                    self.active_notes = new_active_notes
                    if self.on_notes_changed:
                        self.on_notes_changed(self.active_notes)
                
                # 回调时间更新
                if self.on_time_changed:
                    self.on_time_changed(self.current_time)
            
            time.sleep(0.02)  # 50Hz 更新率
    
    def pause(self) -> None:
        """暂停"""
        self.is_paused = True
    
    def resume(self) -> None:
        """恢复"""
        self.is_paused = False
    
    def stop(self) -> None:
        """停止"""
        self.is_playing = False
        self.current_time = 0
        self.active_notes = set()
    
    def seek(self, time_seconds: float) -> None:
        """跳转到指定时间"""
        self.current_time = max(0, min(time_seconds, self.total_time))


class PianoKeyboardVisual(ft.UserControl):
    """88键钢琴键盘可视化"""
    
    def __init__(self):
        super().__init__()
        self.active_notes: set = set()
    
    def build(self):
        canvas = ft.Canvas(
            width=52 * WHITE_KEY_WIDTH,  # 52 white keys in 88-key piano
            height=WHITE_KEY_HEIGHT + 20,
            bgcolor='#1e1e1e',
        )
        
        self.canvas = canvas
        self._draw_keyboard()
        
        return ft.Container(
            content=canvas,
            expand=True,
        )
    
    def _draw_keyboard(self) -> None:
        """绘制钢琴键盘"""
        # A0 = 21, C8 = 108 (88键钢琴)
        white_key_count = 0
        
        for note in range(21, 109):
            note_class = note % 12
            is_white = note_class in WHITE_KEYS
            
            if is_white:
                x = white_key_count * WHITE_KEY_WIDTH
                color = '#b0453a' if note in self.active_notes else '#ffffff'
                
                # 绘制白键
                self.canvas.rect(
                    x, 0, WHITE_KEY_WIDTH - 1, WHITE_KEY_HEIGHT,
                    paint=ft.Paint(
                        stroke_width=1,
                        stroke_color='#000000',
                        color=color
                    )
                )
                white_key_count += 1
        
        # 绘制黑键
        white_key_count = 0
        for note in range(21, 109):
            note_class = note % 12
            is_black = note_class in BLACK_KEYS
            
            if note_class in WHITE_KEYS:
                white_key_count += 1
            
            if is_black:
                # 计算黑键位置
                white_before = sum(1 for n in range(21, note) if (n % 12) in WHITE_KEYS)
                x = white_before * WHITE_KEY_WIDTH + WHITE_KEY_WIDTH - BLACK_KEY_WIDTH // 2
                color = '#8b0000' if note in self.active_notes else '#000000'
                
                # 绘制黑键
                self.canvas.rect(
                    x, 0, BLACK_KEY_WIDTH, BLACK_KEY_HEIGHT,
                    paint=ft.Paint(color=color)
                )
    
    def update_active_notes(self, notes: set) -> None:
        """更新活动音符"""
        self.active_notes = notes
        # 重新绘制
        self.canvas.clean()
        self._draw_keyboard()


class PianoRollVisual(ft.UserControl):
    """琴卷可视化"""
    
    def __init__(self, player: MidiPlayer):
        super().__init__()
        self.player = player
        self.pixels_per_second = 50
        self.pixels_per_semitone = 2
        self.scroll_pos = 0
    
    def build(self):
        self.canvas = ft.Canvas(
            width=900,
            height=400,
            bgcolor='#0d1117',
        )
        
        self._draw_piano_roll()
        
        return ft.Container(
            content=self.canvas,
            expand=True,
            border=ft.border.all(1, '#30363d')
        )
    
    def _draw_piano_roll(self) -> None:
        """绘制琴卷"""
        if not self.player.notes:
            self.canvas.text(
                x=450, y=200,
                text="未加载MIDI文件",
                text_baseline='middle',
                color='#8b949e'
            )
            return
        
        # 绘制背景网格
        for octave in range(0, 11):
            y = (127 - octave * 12) * self.pixels_per_semitone
            if 0 <= y < 400:
                self.canvas.line(
                    0, y, 900, y,
                    paint=ft.Paint(stroke_width=0.5, color='#30363d')
                )
        
        # 绘制音符
        for note in self.player.notes:
            x = note.start_time * self.pixels_per_second
            y = (127 - note.note) * self.pixels_per_semitone
            width = note.duration * self.pixels_per_second
            height = self.pixels_per_semitone
            
            if 0 <= x < 900 and 0 <= y < 400:
                # 根据力度调整颜色
                brightness = int(100 + (note.velocity / 127) * 50)
                color = f'hsl(200, 70%, {brightness}%)'
                
                self.canvas.rect(
                    x, y, width, height,
                    paint=ft.Paint(color=color)
                )
    
    def update_visualization(self, current_time: float) -> None:
        """更新可视化"""
        self.scroll_pos = current_time * self.pixels_per_second
        # 可选：在这里添加滚动逻辑


def format_time(seconds: float) -> str:
    """格式化时间"""
    if seconds < 0:
        seconds = 0
    mins = int(seconds) // 60
    secs = int(seconds) % 60
    millis = int((seconds % 1) * 100)
    return f"{mins:02d}:{secs:02d}.{millis:02d}"


class MidiPlayerApp:
    """MIDI播放器主应用"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Flet MIDI 播放器 v2.0"
        self.page.window_width = 1400
        self.page.window_height = 900
        self.page.window_min_width = 800
        self.page.window_min_height = 600
        
        self.player = MidiPlayer()
        self.player.on_time_changed = self.on_time_updated
        self.player.on_notes_changed = self.on_notes_updated
        
        self.setup_ui()
        self.setup_keyboard_shortcuts()
    
    def setup_ui(self) -> None:
        """设置用户界面"""
        # 文件选择器
        file_picker = ft.FilePicker(on_result=self.on_file_selected)
        self.page.overlay.append(file_picker)
        
        # 标题栏
        title = ft.Text(
            "🎹 MIDI 播放器",
            size=24,
            weight="bold",
            color="#58a6ff"
        )
        
        # 控制按钮
        self.filename_text = ft.Text("未加载文件", size=12, color="#8b949e", expand=True)
        
        controls_row = ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.icons.FOLDER_OPEN,
                    tooltip="打开MIDI文件 (Ctrl+O)",
                    on_click=lambda e: file_picker.pick_files(allowed_extensions=["mid", "midi"])
                ),
                ft.IconButton(
                    icon=ft.icons.PLAY_ARROW,
                    tooltip="播放 (Space)",
                    on_click=self.play_clicked
                ),
                ft.IconButton(
                    icon=ft.icons.PAUSE,
                    tooltip="暂停 (Space)",
                    on_click=self.pause_clicked
                ),
                ft.IconButton(
                    icon=ft.icons.STOP,
                    tooltip="停止 (Backspace)",
                    on_click=self.stop_clicked
                ),
                ft.VerticalDivider(),
                ft.IconButton(
                    icon=ft.icons.FAST_REWIND,
                    tooltip="后退5秒 (←)",
                    on_click=self.rewind_clicked
                ),
                ft.IconButton(
                    icon=ft.icons.FAST_FORWARD,
                    tooltip="前进5秒 (→)",
                    on_click=self.forward_clicked
                ),
                ft.VerticalDivider(),
                ft.Text("🔊", size=20),
                ft.Slider(
                    min=0, max=1, value=1, width=100,
                    on_change=self.volume_changed,
                    tooltip="音量"
                ),
                self.filename_text,
            ],
            spacing=5,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            padding=ft.padding.symmetric(horizontal=10, vertical=5)
        )
        
        # 进度条
        self.time_slider = ft.Slider(
            min=0, max=100, value=0,
            on_change=self.on_slider_changed,
            expand=True,
            tooltip="进度"
        )
        
        self.time_text = ft.Text("00:00.00 / 00:00.00", size=11, color="#8b949e", width=140)
        
        progress_row = ft.Row(
            controls=[self.time_slider, self.time_text],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            padding=ft.padding.symmetric(horizontal=10, vertical=5)
        )
        
        # 键盘显示
        self.keyboard_visual = PianoKeyboardVisual()
        keyboard_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("琴键", size=12, weight="bold", color="#58a6ff"),
                    self.keyboard_visual,
                ],
                spacing=5
            ),
            expand=True,
            border=ft.border.all(1, '#30363d'),
            padding=10
        )
        
        # 琴卷显示
        self.piano_roll = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("琴卷", size=12, weight="bold", color="#58a6ff"),
                    ft.Text("打开MIDI文件查看琴卷", size=12, color="#8b949e")
                ],
                spacing=5
            ),
            expand=True,
            border=ft.border.all(1, '#30363d'),
            padding=10
        )
        
        # 信息面板
        self.notes_text = ft.Text(
            "当前音符: 无",
            size=12,
            color="#79c0ff",
            selectable=True
        )
        
        self.stats_text = ft.Text(
            "文件信息: 无",
            size=12,
            color="#79c0ff",
            selectable=True
        )
        
        info_panel = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("信息", size=12, weight="bold", color="#58a6ff"),
                    self.notes_text,
                    self.stats_text,
                ],
                spacing=8
            ),
            border=ft.border.all(1, '#30363d'),
            padding=10
        )
        
        # 主布局
        main_column = ft.Column(
            controls=[
                title,
                controls_row,
                progress_row,
                ft.Divider(height=5),
                ft.Row(
                    controls=[
                        ft.Column(
                            controls=[keyboard_container],
                            expand=True
                        ),
                        info_panel
                    ],
                    expand=True,
                    spacing=10
                ),
                ft.Divider(height=5),
                self.piano_roll,
            ],
            spacing=5,
            expand=True,
            padding=10
        )
        
        self.page.add(main_column)
    
    def setup_keyboard_shortcuts(self) -> None:
        """设置键盘快捷键"""
        def on_key(e: ft.KeyboardEvent):
            if e.key == "Space":
                if self.player.is_playing and not self.player.is_paused:
                    self.player.pause()
                elif self.player.is_paused:
                    self.player.resume()
                elif self.player.current_file:
                    self.player.play()
            elif e.key == "Backspace":
                self.player.stop()
            elif e.key == "ArrowLeft":
                self.rewind_clicked(None)
            elif e.key == "ArrowRight":
                self.forward_clicked(None)
            elif e.key.lower() == "o" and e.ctrl:
                # Ctrl+O 打开文件
                pass
        
        self.page.on_keyboard_event = on_key
    
    def on_file_selected(self, e: ft.FilePickerResultEvent) -> None:
        """文件选择回调"""
        if e.files:
            file_path = e.files[0].path
            if self.player.load_midi(file_path):
                file_name = Path(file_path).name
                self.filename_text.value = file_name
                self.time_slider.max = self.player.total_time or 100
                self.time_text.value = f"00:00.00 / {format_time(self.player.total_time)}"
                
                # 更新统计信息
                note_count = len(self.player.notes)
                min_time = min((n.start_time for n in self.player.notes), default=0) if self.player.notes else 0
                max_time = max((n.start_time + n.duration for n in self.player.notes), default=0) if self.player.notes else 0
                
                self.stats_text.value = f"音符数: {note_count} | 时长: {format_time(self.player.total_time)}"
                
                # 更新琴卷
                piano_roll_visual = PianoRollVisual(self.player)
                self.piano_roll.content = ft.Column(
                    controls=[
                        ft.Text("琴卷", size=12, weight="bold", color="#58a6ff"),
                        piano_roll_visual,
                    ],
                    spacing=5,
                    expand=True
                )
                
                self.page.update()
                self.show_snackbar(f"✓ 已加载: {file_name}")
            else:
                self.show_snackbar("✗ 加载MIDI文件失败")
    
    def play_clicked(self, e):
        """播放按钮回调"""
        if self.player.current_file:
            if self.player.is_paused:
                self.player.resume()
            else:
                self.player.play()
    
    def pause_clicked(self, e):
        """暂停按钮回调"""
        self.player.pause()
    
    def stop_clicked(self, e):
        """停止按钮回调"""
        self.player.stop()
        self.on_time_updated(0)
    
    def rewind_clicked(self, e):
        """后退5秒"""
        new_time = max(0, self.player.current_time - 5)
        self.player.seek(new_time)
    
    def forward_clicked(self, e):
        """前进5秒"""
        new_time = min(self.player.total_time, self.player.current_time + 5)
        self.player.seek(new_time)
    
    def volume_changed(self, e):
        """音量改变回调"""
        self.player.volume = e.control.value
    
    def on_slider_changed(self, e):
        """进度条改变回调"""
        if not self.player.is_playing:
            self.player.seek(e.control.value)
    
    def on_time_updated(self, current_time: float) -> None:
        """时间更新回调"""
        self.time_slider.value = current_time
        total_formatted = format_time(self.player.total_time)
        current_formatted = format_time(current_time)
        self.time_text.value = f"{current_formatted} / {total_formatted}"
        self.page.update()
    
    def on_notes_updated(self, active_notes: set) -> None:
        """活跃音符更新回调"""
        if active_notes:
            note_names = sorted([MidiNote(n, 100, 0, 0).get_note_name() for n in active_notes])
            self.notes_text.value = f"当前音符: {' '.join(note_names)}"
        else:
            self.notes_text.value = "当前音符: 无"
        
        # 更新琴键显示
        self.keyboard_visual.update_active_notes(active_notes)
        self.page.update()
    
    def show_snackbar(self, message: str) -> None:
        """显示提示信息"""
        self.page.snack_bar = ft.SnackBar(ft.Text(message))
        self.page.snack_bar.open = True
        self.page.update()


def main(page: ft.Page) -> None:
    """应用入口"""
    page.bgcolor = "#0d1117"
    app = MidiPlayerApp(page)


if __name__ == "__main__":
    ft.app(target=main)
