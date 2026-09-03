import flet as ft
from pathlib import Path
import mido
import threading
import time
from typing import cast
import asyncio
import mido
import threading
import time

class SimpleMidiPlayer:
    def __init__(self):
        self.midi_file = None
        self.notes = []
        self.playback_events = [] 
        self.playing = False
        self.paused = False
        self.current_time = 0
        self.total_time = 0
        self.active_notes = set()
        self.volume = 1.0  # 🆕 全局音量属性
        self._seek_request = False  
        
        self.port = None
        self._init_midi_port()

    def _init_midi_port(self):
        try:
            self.port = mido.open_output()  # type: ignore
            print(f"成功连接音频合成器: {self.port.name}")
        except Exception as e:
            print(f"无法打开系统音频合成器: {e}")

    def load(self, path: str) -> bool:
        try:
            self.midi_file = mido.MidiFile(path)
            self._parse_midi()
            return True
        except Exception as e:
            print(f"加载失败: {e}")
            return False
            
    def _parse_midi(self):
        self.notes = []
        self.playback_events = []
        if not self.midi_file: return
        
        current_time = 0
        note_times = {} 
        
        for msg in self.midi_file:
            current_time += msg.time
            
            if not msg.is_meta:
                self.playback_events.append((current_time, msg))
                
            if msg.type == 'note_on' and msg.velocity > 0:
                note_times[(msg.channel, msg.note)] = current_time
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                key = (msg.channel, msg.note)
                if key in note_times:
                    start = note_times[key]
                    self.notes.append({
                        'note': msg.note,
                        'start': start,
                        'duration': current_time - start,
                    })
                    del note_times[key]
                    
        self.total_time = current_time

    def play(self):
        if self.playing: return
        self.playing = True
        self.paused = False
        threading.Thread(target=self._play_loop, daemon=True).start()

    def _play_loop(self):
        start_real_time = time.time() - self.current_time
        event_idx = 0
        
        while event_idx < len(self.playback_events) and self.playback_events[event_idx][0] < self.current_time:
            msg = self.playback_events[event_idx][1]
            if msg.type in ('program_change', 'control_change'):
                if self.port: self.port.send(msg)
            event_idx += 1

        active = set()

        while self.playing:
            if self._seek_request:
                start_real_time = time.time() - self.current_time
                event_idx = 0
                active.clear()
                
                while event_idx < len(self.playback_events) and self.playback_events[event_idx][0] < self.current_time:
                    msg = self.playback_events[event_idx][1]
                    if msg.type in ('program_change', 'control_change'):
                        if self.port: self.port.send(msg)
                    event_idx += 1
                    
                self._seek_request = False 

            if not self.paused:
                self.current_time = time.time() - start_real_time
                
                while event_idx < len(self.playback_events) and self.playback_events[event_idx][0] <= self.current_time:
                    msg = self.playback_events[event_idx][1]
                    if self.port:
                        if msg.type in ('note_on', 'note_off'):
                            scaled_vel = int(msg.velocity * self.volume)
                            self.port.send(msg.copy(velocity=scaled_vel))
                        else:
                            self.port.send(msg)
                    
                    # 动态更新 UI 活跃音符
                    if msg.type == 'note_on' and msg.velocity > 0:
                        active.add(msg.note)
                    elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                        active.discard(msg.note)
                        
                    # 🔧 修复项：游标推进必须在这个位置，不能在 if 分支里面！
                    event_idx += 1
                
                self.active_notes = active
                
                if self.current_time >= self.total_time:
                    self.playing = False
                    self.current_time = 0
                    self._stop_all_notes()
                    break
                    
            time.sleep(0.01)

    def _stop_all_notes(self):
        if self.port:
            for channel in range(16):
                self.port.send(mido.Message('control_change', channel=channel, control=120, value=0))
                self.port.send(mido.Message('control_change', channel=channel, control=123, value=0))
        self.active_notes.clear()

    def pause(self):
        self.paused = True
        self._stop_all_notes()

    def stop(self):
        self.playing = False
        self.paused = False
        self.current_time = 0
        self._stop_all_notes()

    def seek(self, time_sec: float):
        self._stop_all_notes()
        self.current_time = max(0, min(time_sec, self.total_time))
        self._seek_request = True  
        
    def __del__(self):
        if self.port:
            self._stop_all_notes()
            self.port.close()

    def set_volume(self, vol: float):
        self.volume = max(0.0, min(1.0, vol))
        
def main(page: ft.Page):
    """主应用"""
    page.title = "简易MIDI播放器"
    player = SimpleMidiPlayer()
    
    # UI控件
    filename = ft.Text("未加载", size=12)
    time_text = ft.Text("00:00/00:00", size=12)
    notes_text = ft.Text("音符: 无", size=12, color="blue")
    notes_list = ft.Column(height=150, expand=True, scroll=ft.ScrollMode.AUTO)
    
    async def open_file_dialog(e):
        result = await ft.FilePicker().pick_files()
        if result:
            path = result[0].path
            load_file(path, player)
            
    def update_ui():
        mins = int(player.current_time) // 60
        secs = int(player.current_time) % 60
        total_mins = int(player.total_time) // 60
        total_secs = int(player.total_time) % 60
        time_text.value = f"{mins:02d}:{secs:02d}/{total_mins:02d}:{total_secs:02d}"
        
        # 强制限制进度条 value 不得超过 max
        if player.total_time > 0:
            safe_value = min(float(player.current_time), float(player.total_time))
            slider.value = safe_value
            
        if player.active_notes:
            notes_text.value = f"音符: {', '.join(map(str, sorted(player.active_notes)))}"
        else:
            notes_text.value = "音符: 无"
        page.update()
    
    def load_file(path, p):
        if path:
            if p.load(path):
                filename.value = f"文件: {Path(path).name}"
                if p.total_time > 0:
                    time_text.value = f"00:00/{int(p.total_time)//60:02d}:{int(p.total_time)%60:02d}"
                    slider.max = float(p.total_time)
                    slider.value = 0.0
                else:
                    time_text.value = "00:00/00:00"
                    slider.max = 100.0
                    slider.value = 0.0
                update_ui()  
            else:
                filename.value = "加载失败"
            page.update()

    def seek(e, p):
        if p.total_time > 0:
            # 提取 float 并加入容错，规避 Pylance 警告
            val = float(e.control.value or 0.0)
            p.seek(val)
            update_ui()

    # 找回之前丢失的播放控制函数
    async def play_click(e):
        if not player.playing:
            player.play()
            while player.playing:
                update_ui()
                await asyncio.sleep(0.1)
            update_ui()

    def pause_click(e):
        player.pause()
        update_ui()

    def stop_click(e):
        player.stop()
        update_ui()

    slider = ft.Slider(min=0, max=100, value=0, expand=True, on_change_end=lambda e: seek(e, player))
    
    # 音量滑块（加入 float 和 or 0 容错处理，消除 "None" 报错）
    vol_slider = ft.Slider(
        min=0, max=100, value=100, width=150,
        label="{value}%",
        on_change=lambda e: player.set_volume(float(e.control.value or 0) / 100.0)
    )
    
    main_controls = cast(list[ft.Control], [
        ft.Text("🎹 简易MIDI播放器", size=20, weight=ft.FontWeight.BOLD),
        ft.Row(cast(list[ft.Control], [
            ft.Button("打开", on_click=open_file_dialog),
            ft.IconButton(icon=ft.Icons.PLAY_ARROW, on_click=play_click),
            ft.IconButton(icon=ft.Icons.PAUSE, on_click=pause_click),
            ft.IconButton(icon=ft.Icons.STOP, on_click=stop_click),
            filename,
        ])),
        ft.Row(cast(list[ft.Control], [
            ft.Icon(ft.Icons.VOLUME_UP), vol_slider
        ])),
        ft.Row(cast(list[ft.Control], [slider, time_text])),
        notes_text,
        ft.Divider(),
        ft.Text("音符信息:", weight=ft.FontWeight.BOLD),
        notes_list,
    ])
    
    # 布局
    page.add(
        ft.Container(
            content=ft.Column(main_controls, expand=True),
            padding=10
        )
    )
    
    page.window.width = 800
    page.window.height = 400

if __name__ == "__main__":
    ft.run(main)