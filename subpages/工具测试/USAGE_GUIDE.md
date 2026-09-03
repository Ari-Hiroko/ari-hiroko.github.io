# Flet MIDI 播放器 使用指南

## 📋 概述

为您提供了三个版本的MIDI播放器，从简单到完整：

| 版本 | 文件名 | 特点 | 用途 |
|------|-------|------|------|
| **简化版** | `midiplayer_simple.py` | 最小功能集 | 快速开发、学习Flet |
| **标准版** | `midiplayer.py` | 完整功能 | 日常使用 |
| **增强版** | `midiplayer_v2.py` | 高级UI、快捷键 | 专业使用 |

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 使用pip安装所有依赖
pip install -r requirements.txt

# 或手动安装
pip install flet mido pygame music21
```

### 2. 运行播放器

选择要运行的版本：

```bash
# 简化版（推荐初学者）
python midiplayer_simple.py

# 标准版
python midiplayer.py

# 增强版（功能最全）
python midiplayer_v2.py
```

### 3. 使用步骤

1. 点击 **"打开MIDI文件"** 按钮
2. 选择一个 `.mid` 或 `.midi` 文件
3. 点击 **播放** ▶️ 开始播放
4. 观看琴键和琴卷的实时可视化

---

## 💡 版本详细对比

### 简化版 (midiplayer_simple.py)

**特点：**
- 代码量最少（<200行）
- 最少依赖
- 基础播放控制：播放/暂停/停止
- 时间进度条
- 当前音符显示

**快捷键：** 无

**界面：**
```
┌─ 简易MIDI播放器 ───────────────┐
│ [打开] [▶] [⏸] [⏹] [文件名]   │
├─ [════════════] 00:00/03:20 ────┤
│ 音符: 无                        │
│                                 │
└─────────────────────────────────┘
```

**使用场景：**
- 学习Flet框架
- 快速原型开发
- 嵌入其他应用

---

### 标准版 (midiplayer.py)

**特点：**
- 完整的MIDI解析
- 琴键可视化
- 琴卷可视化
- 音符信息显示
- 文件加载和解析

**快捷键：** 无

**界面：**
```
┌─────────────────────────────────┐
│ [打开] [▶] [⏸] [⏹]  文件名    │
├─ [════════════] 00:00 / 03:20 ──┤
│ ┌──── 琴键可视化 ──────────────┐│
│ │░░░░░░░░░░░░░░░░░░░░░░░░░░░░││
│ └──────────────────────────────┘│
│ ┌──── 琴卷可视化 ──────────────┐│
│ │          (音符矩形)          ││
│ └──────────────────────────────┘│
│ 当前音符: C4, E4, G4           │
└─────────────────────────────────┘
```

**使用场景：**
- 学习MIDI结构
- 开发MIDI分析工具
- 教学演示

---

### 增强版 (midiplayer_v2.py)

**特点：**
- 美观的暗色主题
- 完整的快捷键支持
- 音量控制
- 快进/快退功能
- 统计信息显示
- 改进的UI布局
- 响应式设计

**快捷键：**
- `Space`: 播放/暂停
- `Backspace`: 停止
- `←`: 后退5秒
- `→`: 前进5秒
- `Ctrl+O`: 打开文件

**界面：** 现代化设计，包含所有高级功能

**使用场景：**
- 日常MIDI播放
- 作曲/编排时的参考播放
- 专业演示

---

## 🎵 MIDI 文件获取

### 获取免费MIDI文件的网站

1. **MuseScore** (musescore.com)
   - 大量古典音乐MIDI
   - 需要注册账户

2. **MIDIWorld** (midiworld.com)
   - 各个风格的MIDI文件
   - 完全免费

3. **FreeMIDI** (freemidi.org)
   - 搜索功能强大
   - 多个风格分类

4. **Classical Archives** (classicalarchives.com)
   - 古典音乐MIDI
   - 高质量

### 创建测试MIDI文件

使用MuseScore、Finale或其他DAW创建简单的MIDI文件进行测试。

---

## 🔧 功能说明

### 琴键显示 (Piano Keyboard Visualization)

显示88键钢琴的完整键盘，当前活跃的琴键用红色高亮。

```
示例：A4和C#5正在播放时
┌─┐┌─┐┌─┐┌─┐┌─┐┌─┐┌─┐┌─┐
│ ││█││ ││ ││ ││ ││ ││ │  ← 黑键（A#4正在播放）
└─┘└─┘└─┘└─┘└─┘└─┘└─┘└─┘
┌───┐┌───┐┌───┐┌───┐┌───┐
│███││   ││   ││   ││   │  ← 白键（C5、E5）
└───┘└───┘└───┘└───┘└───┘
  A4   B4   C5   D5   E5
```

### 琴卷显示 (Piano Roll Visualization)

展示所有音符在时间-频率坐标上的分布：

```
纵轴：音符高度（从低到高）
横轴：时间（从左到右）

B8 ┤
   ├─ ┌──────┐
C4 ├─ │██████│
   ├─ └──────┘
C0 ├─
   └─┴─────────────────── 时间
     0  1  2  3  4  5秒

蓝色矩形宽度 = 音符持续时间
```

### 时间显示格式

`MM:SS.MS / MM:SS.MS` (当前时间 / 总时间)

例如: `01:23.45 / 03:20.00`

---

## 📊 MIDI 分析功能

所有版本都能展示：

1. **元数据**
   - 文件名
   - 总时长
   - 音符总数

2. **音符统计**
   - 当前播放的音符
   - 音符名称（例如 C4, E4, G4）
   - MIDI音符号（0-127）

3. **时间信息**
   - 当前播放位置
   - 总文件长度
   - 进度百分比

---

## 🎮 扩展功能建议

### 可以添加的功能

1. **真实音频输出**
   ```python
   # 使用fluidsynth生成音频
   import fluidsynth
   fs = fluidsynth.Synth()
   fs.noteon(0, note, velocity)
   fs.noteoff(0, note)
   ```

2. **MIDI录制**
   ```python
   # 记录用户输入的MIDI
   def record_midi(self):
       # 在播放时记录键盘输入
       pass
   ```

3. **节拍器**
   ```python
   # 添加节拍指示器
   bpm = self.extract_bpm()  # 从MIDI提取BPM
   ```

4. **MIDI编辑**
   ```python
   # 允许编辑音符参数
   def edit_note(self, note_index, new_velocity):
       self.notes[note_index].velocity = new_velocity
   ```

5. **导出功能**
   ```python
   # 导出琴卷为图像
   def export_piano_roll(self, output_path):
       # 使用matplotlib生成图表
       pass
   ```

---

## 🐛 常见问题排查

### Q: 打开MIDI文件后没有显示琴键
**A:** 
- 检查MIDI文件是否有效
- 尝试用另一个MIDI播放器打开该文件
- 确认MIDI包含note_on消息

### Q: 进度条不能拖动
**A:**
- 这是增强版中的设计，只能在停止时拖动
- 在简化版中始终可以拖动

### Q: 播放没有声音
**A:**
- 当前版本是**MIDI读取器**而非音乐播放器
- 它读取和显示MIDI数据，但不生成音频
- 要获得音频输出，需要集成音频合成库

### Q: 速度播放很慢
**A:**
- 关闭其他应用
- 检查MIDI文件大小（>10MB时可能缓慢）
- 尝试使用简化版

---

## 📝 代码示例：集成到自己的项目

### 使用播放器类

```python
from midiplayer import MidiPlayer

# 创建播放器
player = MidiPlayer()

# 加载MIDI文件
if player.load_midi("song.mid"):
    # 注册回调
    player.on_time_changed = lambda t: print(f"时间: {t}")
    player.on_notes_changed = lambda n: print(f"活跃音符: {n}")
    
    # 播放
    player.play()
    
    # 暂停
    player.pause()
    
    # 停止
    player.stop()
    
    # 跳转
    player.seek(30)  # 跳到30秒
```

### 自定义UI

```python
import flet as ft
from midiplayer import MidiPlayer, PianoRollVisual

def main(page: ft.Page):
    player = MidiPlayer()
    piano_roll = PianoRollVisual(player)
    
    # 添加你的自定义UI
    page.add(piano_roll)

ft.app(target=main)
```

---

## 📚 相关资源

- [Flet文档](https://flet.dev/)
- [Mido文档](https://mido.readthedocs.io/)
- [MIDI规范](https://www.midi.org/)
- [Music21文档](https://web.mit.edu/music21/)

---

## ✅ 检查清单

运行MIDI播放器前：

- [ ] Python 3.7+ 已安装
- [ ] 依赖已安装 (`pip install -r requirements.txt`)
- [ ] 有MIDI文件可用
- [ ] Flet应用能正常启动

---

## 🤝 支持和反馈

如遇到问题：
1. 检查MIDI文件格式是否正确
2. 尝试不同的MIDI文件
3. 参考本指南的故障排查部分
4. 查看代码注释了解实现细节

---

**最后更新**: 2026年2月22日  
**版本**: 2.0
