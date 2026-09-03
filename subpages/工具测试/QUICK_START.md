# 🎹 Flet MIDI 播放器 - 快速开始

## 📦 文件清单

已为您创建的文件：

```
工具测试/
├── midiplayer.py              ← 标准版（完整功能）
├── midiplayer_v2.py           ← 增强版（最新功能，推荐）
├── midiplayer_simple.py       ← 简化版（快速上手）
├── midi_player_config.json    ← 配置文件示例
├── MIDI_PLAYER_README.md      ← 功能文档
├── USAGE_GUIDE.md             ← 详细使用指南
└── QUICK_START.md             ← 本文件
```

---

## ⚡ 5分钟快速开始

### 1️⃣ 安装依赖 (30秒)

打开PowerShell/命令行，运行：

```bash
pip install flet mido pygame
```

### 2️⃣ 运行应用 (10秒)

用以下命令选择版本启动：

```bash
# 💡 推荐：功能最全，UI最美观
python midiplayer_v2.py

# 标准版（完整功能）
python midiplayer.py

# 简化版（学习Flet）
python midiplayer_simple.py
```

### 3️⃣ 打开MIDI文件 (1分钟)

- 点击 **"打开MIDI文件"** 按钮
- 选择电脑上的 `.mid` 或 `.midi` 文件
- 看到琴键和琴卷实时显示 ✨

### 4️⃣ 播放控制 (剩余时间)

| 按钮 | 快捷键 | 功能 |
|------|--------|------|
| ▶️ | Space | 播放/恢复 |
| ⏸️ | Space | 暂停 |
| ⏹️ | Backspace | 停止 |
| ◀ | ← | 后退5秒 |
| ▶ | → | 前进5秒 |

---

## 🎯 三个版本选择

### 你想要的是...

**"我想快速体验"** → 使用 `midiplayer_v2.py`
- ✅ 现代暗色UI
- ✅ 完整快捷键
- ✅ 音量控制
- ✅ 所有功能

**"我想学习Flet编程"** → 使用 `midiplayer_simple.py`
- ✅ 代码最简洁（<200行）
- ✅ 易于理解和修改
- ✅ 完美的学习教材

**"我想深入理解MIDI"** → 使用 `midiplayer.py`
- ✅ 详细的代码注释
- ✅ 完整的类结构
- ✅ 易于二次开发

---

## 🎵 获取测试MIDI文件

### 方法1：下载免费MIDI

推荐网站：
- https://www.midiworld.com/ - 各类风格MIDI
- https://musescore.com/ - 古典音乐MIDI
- https://freemidi.org/ - 免费MIDI库

### 方法2：用Windows自带文件

Windows通常有示例MIDI文件：
```
C:\Windows\Media\*.mid
```

### 方法3：创建简单MIDI用于测试

用MuseScore或任何音乐软件创建简单的MIDI文件。

---

## 🖥️ 系统要求

| 项目 | 要求 |
|------|------|
| Python | 3.7+ |
| 操作系统 | Windows/Mac/Linux |
| 内存 | 200MB+ |
| MIDI文件大小 | <100MB |

---

## 🎨 界面预览

```
┌─ 🎹 MIDI 播放器 v2.0 ────────────────────────┐
│                                               │
│ [📁] [▶] [⏸] [⏹] [◀] [▶] 🔊[---] song.mid  │
│                                               │
│ ═════════════════════════  01:23.45/3:20.00 │
│                                               │
│ ┌────────┐  ┌────────────────────────────┐  │
│ │ 琴键   │  │          琴卷              │  │
│ │░▓░▓░▓░░│  │  ■■■■    ■■■             │  │
│ │█ █ █ █ │  │    ■■        ■■■         │  │
│ └────────┘  │      ■■■          ■■■    │  │
│            └────────────────────────────┘  │
│                                               │
│ 当前音符: C4, E4, G4                        │
│ 文件信息: 312 音符 | 3:20.00                │
│                                               │
└───────────────────────────────────────────────┘
```

---

## 🚀 常用操作

### 播放一个MIDI文件

1. 启动程序
2. 点击📁 打开MIDI
3. 选择文件
4. 点击▶️ 播放
5. 使用◀️/▶️ 控制播放位置

### 使用键盘快捷键

| 快捷键 | 功能 |
|--------|------|
| `Space` | 切换播放/暂停 |
| `←` | 快退5秒 |
| `→` | 快进5秒 |
| `Backspace` | 停止 |

### 拖动进度条

直接拖动进度条可以跳到任意位置（停止时有效）

---

## ❓ 快速问题解答

**Q: 怎样更改UI语言？**  
A: 编辑配置文件 `midi_player_config.json` 中的 `language` 字段

**Q: 网络很慢，安装不了依赖？**  
A: 换个镜像源：
```bash
pip install -i https://pypi.tsinghua.edu.cn/simple flet mido
```

**Q: 打开MIDI文件后没有声音？**  
A: 这是正常的！这个应用显示MIDI数据而不播放音频。如需音频输出，可扩展集成音频库。

**Q: 想打包成exe怎么办？**  
A: 使用PyInstaller：
```bash
pip install pyinstaller
pyinstaller --onefile midiplayer_v2.py
```

**Q: 能编辑MIDI文件吗？**  
A: 当前版本只能读取和播放。可手动调整代码添加编辑功能。

---

## 📖 进阶使用

### 集成到其他项目

```python
from midiplayer import MidiPlayer

player = MidiPlayer()
player.load_midi("my_song.mid")
player.on_time_changed = my_custom_callback
player.play()
```

### 自定义UI

编辑 `midiplayer_v2.py` 中的 `setup_ui()` 方法

### 修改可视化效果

调整这些参数：
```python
WHITE_KEY_WIDTH = 30        # 琴键宽度
BLACK_KEY_HEIGHT = 110      # 黑键高度
pixels_per_second = 50      # 琴卷时间轴缩放
```

---

## 🔧 技术栈

- **框架**: Flet (跨平台UI)
- **MIDI**: mido (MIDI文件读取)
- **音频**: pygame (可选)
- **可视化**: Flet Canvas (绘图)

---

## 📞 需要帮助？

### 见错误提示？

1. 检查MIDI文件是否有损坏
2. 尝试用另一个MIDI播放器打开
3. 查看 `USAGE_GUIDE.md` 的故障排查部分

### 想要新功能？

- 编辑源代码添加功能
- 参考 `MIDI_PLAYER_README.md` 的"高级功能建议"
- 使用注释的代码作为参考

### 想学习代码？

- 从 `midiplayer_simple.py` 开始
- 阅读代码注释
- 在 `midiplayer_v2.py` 中看完整实现

---

## 📋 下一步

选择一个版本运行后：

1. ✅ 加载一个MIDI文件
2. ✅ 尝试所有播放控制
3. ✅ 观察琴键和琴卷的变化
4. ✅ 阅读源代码理解实现
5. ✅ 根据需要进行定制

---

## 🎓 学习资源

- **Flet官方文档**: https://flet.dev/docs
- **Mido文档**: https://mido.readthedocs.io/
- **MIDI规范**: https://www.midi.org/specifications

---

## ✨ 功能亮点

🎹 **88键钢琴显示** - 实时高亮活跃琴键  
📊 **琴卷可视化** - 看到所有音符的时间分布  
⚡ **实时播放** - 流畅的播放和跳转  
🎨 **现代UI** - 暗色主题，专业外观  
⌨️ **快捷键支持** - 键盘快速控制  
📈 **统计信息** - 显示音符数等信息  

---

## 🎉 开始享受吧！

```
python midiplayer_v2.py
```

祝您使用愉快！🎶

---

**最后更新**: 2026年2月22日
