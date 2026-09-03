import flet as ft
import os
from pathlib import Path
import mido
import threading
import time
from dataclasses import dataclass
from typing import List, Optional

# pygame是可选依赖
try:
    import pygame
    pygame.mixer.init()
except:
    pygame = None

# MIDI音符到琴键位置的映射 (C0到B8)
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
WHITE_KEYS = [0, 2, 4, 5, 7, 9, 11]  # C, D, E, F, G, A, B在12音中的位置
BLACK_KEYS = [1, 3, 6, 8, 10]  # C#, D#, F#, G#, A#

@dataclass
class MidiNote:
    """MIDI音符数据"""
    note: int  # MIDI音符号 (0-127)
    velocity: int  # 力度 (0-127)
    start_time: float  # 开始时间
    duration: float  # 持续时间
    
    def get_note_name(self) -> str:
        """获取音符名称"""
        octave = (self.note // 12) - 1
        note_name = NOTE_NAMES[self.note % 12]
        return f"{note_name}{octave}"


class MidiPlayer:
    """MIDI播放器核心类"""
    
    def __init__(self):
        self.current_file: Optional[str] = None
        self.midi_data: Optional[mido.MidiFile] = None
        self.notes: List[MidiNote] = []
        self.is_playing = False
        self.is_paused = False
        self.current_time = 0
        self.total_time = 0
        self.playback_thread = None
        self.active_notes: set = set()
        self.on_time_changed = None
        self.on_notes_changed = None
        
        # 初始化pygame mixer用于MIDI播放
        try:
            pygame.mixer.init()
        except:
            pass
    
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
            current_time = 0
            note_on_map = {}  # 记录未关闭的音符
            
            for msg in track:
                current_time += msg.time
                
                if msg.type == 'note_on' and msg.velocity > 0:
                    note_on_map[msg.note] = (current_time, msg.velocity)
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    if msg.note in note_on_map:
                        start_time, velocity = note_on_map[msg.note]
                        duration = current_time - start_time
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
        microseconds_per_beat = 500000  # 默认120 BPM
        total_ticks = 0
        
        for track in self.midi_data.tracks:
            current_ticks = 0
            for msg in track:
                current_ticks += msg.time
                total_ticks = max(total_ticks, current_ticks)
                if msg.type == 'set_tempo':
                    microseconds_per_beat = msg.tempo
        
        return (total_ticks * microseconds_per_beat) / (ticks_per_beat * 1000000)
    
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
            
            time.sleep(0.01)
    
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
    
    def seek(self, time: float) -> None:
        """跳转到指定时间"""
        self.current_time = max(0, min(time, self.total_time))


class KeyboardVisualizer:
    """钢琴键盘可视化器 - 简化版"""
    
    def __init__(self):
        self.active_notes = set()
    
    def build(self):
        """构建控件"""
        note_display = ft.Text(
            value="无活跃音符",
            size=14,
            color=ft.colors.BLUE_300,
            selectable=True
        )
        self.note_display = note_display
        
        return ft.Container(
            content=note_display,
            padding=10,
            bgcolor=ft.colors.GREY_900,
            border=ft.border.all(1, ft.colors.GREY_700)
        )
    
    def update_active_notes(self, notes: set) -> None:
        """更新活动音符"""
        self.active_notes = notes
        if hasattr(self, 'note_display'):
            if notes:
                note_names = sorted([f"Note {n}" for n in notes])
                self.note_display.value = f"活跃琴键: {', '.join(note_names[:10])}"
            else:
                self.note_display.value = "无活跃音符"


class PianoRoll:
    """琴卷可视化器 - 简化版"""
    
    def __init__(self, player):
        self.player = player
        self.scale_x = 50
        self.scale_y = 2
        self.scroll_x = 0
    
    def build(self):
        """构建控件"""
        info_text = ft.Text(
            value=f"琴卷: {len(self.player.notes)} 个音符",
            size=12,
            color=ft.colors.BLUE_300
        )
        self.info_text = info_text
        
        return ft.Container(
            content=info_text,
            padding=10,
            bgcolor=ft.colors.GREY_900,
            border=ft.border.all(1, ft.colors.GREY_700)
        )


class MidiPlayerApp:
    """MIDI播放器应用主类"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Flet MIDI 播放器"
        
        self.player = MidiPlayer()
        self.player.on_time_changed = lambda t: self.update_time_display(t)
        self.player.on_notes_changed = lambda n: self.update_visualizers(n)
        
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """设置用户界面"""
        # 顶部控制栏
        file_picker = ft.FilePicker()
        file_picker.on_result = self.on_file_selected
        self.page.overlay.append(file_picker)
        
        control_buttons = ft.Row(
            controls=[
                ft.ElevatedButton(
                    "打开MIDI文件",
                    icon=ft.icons.FOLDER_OPEN,
                    on_click=lambda e: file_picker.pick_files(allowed_extensions=["mid", "midi"])
                ),
                ft.IconButton(
                    ft.icons.PLAY_ARROW,
                    icon_size=30,
                    on_click=self.play
                ),
                ft.IconButton(
                    ft.icons.PAUSE,
                    icon_size=30,
                    on_click=self.pause
                ),
                ft.IconButton(
                    ft.icons.STOP,
                    icon_size=30,
                    on_click=self.stop
                ),
                ft.Text("", expand=True),
                ft.Text("文件: 未加载", size=12, weight="bold", expand=False),
            ],
            spacing=10,
            padding=ft.padding.symmetric(horizontal=10, vertical=5)
        )
        
        self.file_text = control_buttons.controls[-1]
        
        # 进度条和时间显示
        self.progress_slider = ft.Slider(
            min=0,
            max=100,
            value=0,
            on_change=self.on_progress_changed,
            expand=True
        )
        
        self.time_display = ft.Text("00:00 / 00:00", size=12)
        
        progress_row = ft.Row(
            controls=[
                self.progress_slider,
                self.time_display
            ],
            spacing=10,
            padding=ft.padding.symmetric(horizontal=10, vertical=5)
        )
        
        # 琴键可视化
        self.keyboard = KeyboardVisualizer()
        keyboard_container = self.keyboard.build()
        
        # 琴卷可视化
        self.piano_roll = ft.Container(
            content=ft.Text("打开MIDI文件以显示琴卷", size=14, color=ft.colors.GREY_700),
            height=200,
            bgcolor=ft.colors.GREY_900,
            padding=10,
            border=ft.border.all(1, ft.colors.GREY_700)
        )
        
        # 音符信息显示
        self.note_info = ft.Text(
            "当前音符: 无",
            size=12,
            color=ft.colors.BLUE_300,
            selectable=True
        )
        
        # 主布局
        self.page.add(
            ft.Column(
                controls=[
                    control_buttons,
                    progress_row,
                    ft.Divider(height=1),
                    ft.Text("琴键可视化", size=14, weight="bold"),
                    keyboard_container,
                    ft.Divider(height=1),
                    ft.Text("琴卷可视化", size=14, weight="bold"),
                    self.piano_roll,
                    ft.Divider(height=1),
                    self.note_info,
                ],
                spacing=5,
                padding=10,
                expand=True,
                scroll=ft.ScrollMode.AUTO
            )
        )
    
    def on_file_selected(self, e) -> None:
        """文件选择回调"""
        if e.files:
            file_path = e.files[0].path
            if self.player.load_midi(file_path):
                file_name = Path(file_path).name
                self.file_text.value = f"文件: {file_name}"
                self.progress_slider.max = self.player.total_time or 100
                
                # 更新琴卷
                piano_roll_visual = PianoRoll(self.player)
                self.piano_roll.content = piano_roll_visual.build()
                
                self.page.snack_bar = ft.SnackBar(
                    ft.Text(f"已加载: {file_name}")
                )
                self.page.snack_bar.open = True
                self.page.update()
            else:
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("加载MIDI文件失败")
                )
                self.page.snack_bar.open = True
                self.page.update()
    
    def play(self, e) -> None:
        """播放"""
        if self.player.current_file:
            if self.player.is_paused:
                self.player.resume()
            else:
                self.player.play()
    
    def pause(self, e) -> None:
        """暂停"""
        self.player.pause()
    
    def stop(self, e) -> None:
        """停止"""
        self.player.stop()
        self.progress_slider.value = 0
        self.page.update()
    
    def on_progress_changed(self, e) -> None:
        """进度条改变回调"""
        if self.player.midi_data and not self.player.is_playing:
            self.player.seek(e.control.value)
            self.update_time_display(e.control.value)
    
    def update_time_display(self, current_time: float) -> None:
        """更新时间显示"""
        def format_time(seconds: float) -> str:
            mins = int(seconds) // 60
            secs = int(seconds) % 60
            return f"{mins:02d}:{secs:02d}"
        
        if self.player.total_time > 0:
            self.time_display.value = f"{format_time(current_time)} / {format_time(self.player.total_time)}"
            self.progress_slider.value = current_time
        
        self.page.update()
    
    def update_visualizers(self, active_notes: set) -> None:
        """更新可视化"""
        note_names = [MidiNote(note=n, velocity=100, start_time=0, duration=0).get_note_name() for n in sorted(active_notes)]
        self.note_info.value = f"当前音符: {', '.join(note_names) if note_names else '无'}"
        
        # 更新琴键
        if hasattr(self, 'keyboard'):
            self.keyboard.update_active_notes(active_notes)
        
        self.page.update()


def main(page: ft.Page) -> None:
    """应用入口"""
    app = MidiPlayerApp(page)


if __name__ == "__main__":
    ft.run(main)
