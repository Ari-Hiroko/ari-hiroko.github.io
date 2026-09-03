import pretty_midi
import matplotlib.pyplot as plt
import json
import sys
import os

def process_midi(file_path):
    if not os.path.exists(file_path):
        print(f"错误：找不到文件 '{file_path}'")
        return

    try:
        # 解析 MIDI 文件
        midi_data = pretty_midi.PrettyMIDI(file_path)
    except Exception as e:
        print(f"解析 MIDI 文件时出错: {e}")
        return

    instruments = midi_data.instruments
    if not instruments:
        print("该 MIDI 文件中没有找到任何乐器轨道。")
        return

    # 1. 渲染所有轨道的 MIDI 图形作为预览
    print("正在渲染预览图...")
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 为不同轨道分配不同颜色，方便区分
    colors = plt.cm.get_cmap('tab10', len(instruments))

    valid_tracks = 0
    for i, inst in enumerate(instruments):
        notes = inst.notes
        if not notes:
            continue
        
        valid_tracks += 1
        # 绘制类似钢琴卷帘的水平线 (横轴为时间，纵轴为音高)
        for note in notes:
            ax.hlines(y=note.pitch, xmin=note.start, xmax=note.end, 
                      colors=colors(i), linewidth=2)
        
        # 仅用一个散点作为图例的代理，避免图例重复
        ax.scatter([], [], color=colors(i), label=f"Track {i}: {inst.name} (Notes: {len(notes)})")

    if valid_tracks == 0:
        print("所有轨道都是空的（没有音符）。")
        return

    ax.set_xlabel("Time (Seconds)")
    ax.set_ylabel("Pitch (MIDI Note Number)")
    ax.set_title(f"MIDI Preview: {os.path.basename(file_path)}")
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.tight_layout()
    
    print("请在弹出的窗口中查看预览图。")
    print("【注】请关闭图片窗口后，继续在终端中输入！")
    # 阻塞式显示，用户关闭窗口后才继续执行后面的代码
    plt.show()

    # 2. 选取乐器轨
    print("-" * 30)
    try:
        track_idx = int(input(f"请输入要提取的轨道编号 (0 到 {len(instruments)-1}): "))
        if track_idx < 0 or track_idx >= len(instruments):
            print("输入了无效的轨道编号，程序退出。")
            return
    except ValueError:
        print("格式错误：请输入有效的纯数字。")
        return

    selected_inst = instruments[track_idx]
    if not selected_inst.notes:
        print("警告：你选择的轨道没有任何音符。")
    
    # 3. 提取起始时间并输出结构化文本
    output_data = []
    for note in selected_inst.notes:
        output_data.append({
            "pitch": note.pitch,
            "start_time": round(note.start, 4) # 保留4位小数
        })

    # 按时间顺序排序（通常默认已排序，确保万无一失）
    output_data.sort(key=lambda x: x["start_time"])

    # 转换为 JSON 格式的结构化文本
    output_json = json.dumps(output_data, indent=4)
    
    print("\n" + "="*15 + " 提取结果 " + "="*15)
    print(output_json)
    print("="*40)

    # 自动保存到文件
    out_filename = f"track_{track_idx}_start_times.json"
    with open(out_filename, "w", encoding="utf-8") as f:
        f.write(output_json)
    print(f"\n已将数据成功保存至当前目录下的: {out_filename}")

if __name__ == "__main__":
    # 在此处修改你的 MIDI 文件路径
    midi_file_path = input("请输入你的 MIDI 文件路径 (例如 test.mid): ").strip('"').strip("'")
    process_midi(midi_file_path)