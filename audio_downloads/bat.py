import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from pydub import AudioSegment

class MP3toWAVConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 to WAV Converter")
        self.root.geometry("600x400")

        self.input_paths = []
        self.output_dir = ""

        self.create_widgets()

    def create_widgets(self):
        # Input Frame
        input_frame = tk.LabelFrame(self.root, text="Input MP3 Files/Folder", padx=10, pady=10)
        input_frame.pack(pady=10, padx=10, fill="x")

        self.input_label = tk.Label(input_frame, text="No files or folder selected.", wraplength=500, justify="left")
        self.input_label.pack(side="left", fill="x", expand=True)

        input_button_frame = tk.Frame(input_frame)
        input_button_frame.pack(side="right")

        select_files_button = tk.Button(input_button_frame, text="Select Files", command=self.select_input_files)
        select_files_button.pack(pady=5)

        select_folder_button = tk.Button(input_button_frame, text="Select Folder", command=self.select_input_folder)
        select_folder_button.pack(pady=5)

        # Output Frame
        output_frame = tk.LabelFrame(self.root, text="Output WAV Folder", padx=10, pady=10)
        output_frame.pack(pady=10, padx=10, fill="x")

        self.output_label = tk.Label(output_frame, text="No output folder selected.", wraplength=500, justify="left")
        self.output_label.pack(side="left", fill="x", expand=True)

        select_output_button = tk.Button(output_frame, text="Select Folder", command=self.select_output_folder)
        select_output_button.pack(side="right")

        # Convert Button
        self.convert_button = tk.Button(self.root, text="Convert to WAV", command=self.convert_files, state="disabled")
        self.convert_button.pack(pady=20)

        # Progress Bar
        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=500, mode="determinate")
        self.progress_bar.pack(pady=10)

        self.status_label = tk.Label(self.root, text="")
        self.status_label.pack(pady=5)

    def select_input_files(self):
        files = filedialog.askopenfilenames(
            title="Select MP3 Files",
            filetypes=(("MP3 files", "*.mp3"), ("All files", "*.*"))
        )
        if files:
            self.input_paths = list(files)
            self.input_label.config(text="\n".join(self.input_paths))
            self.check_can_convert()

    def select_input_folder(self):
        folder = filedialog.askdirectory(title="Select Folder Containing MP3 Files")
        if folder:
            self.input_paths = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(".mp3")]
            if self.input_paths:
                self.input_label.config(text=f"Selected folder: {folder}\n({len(self.input_paths)} MP3 files found)")
            else:
                self.input_label.config(text=f"Selected folder: {folder}\n(No MP3 files found)")
            self.check_can_convert()

    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder for WAV Files")
        if folder:
            self.output_dir = folder
            self.output_label.config(text=self.output_dir)
            self.check_can_convert()

    def check_can_convert(self):
        if self.input_paths and self.output_dir:
            self.convert_button.config(state="normal")
        else:
            self.convert_button.config(state="disabled")

    def convert_files(self):
        if not self.input_paths or not self.output_dir:
            messagebox.showerror("Error", "Please select input files/folder and an output folder.")
            return

        self.convert_button.config(state="disabled")
        self.progress_bar["value"] = 0
        self.progress_bar["maximum"] = len(self.input_paths)
        self.status_label.config(text="Starting conversion...")
        self.root.update_idletasks()

        converted_count = 0
        for i, mp3_path in enumerate(self.input_paths):
            try:
                self.status_label.config(text=f"Converting: {os.path.basename(mp3_path)} ({i+1}/{len(self.input_paths)})")
                self.root.update_idletasks()

                audio = AudioSegment.from_mp3(mp3_path)
                wav_filename = os.path.splitext(os.path.basename(mp3_path))[0] + ".wav"
                wav_path = os.path.join(self.output_dir, wav_filename)
                audio.export(wav_path, format="wav")
                converted_count += 1
            except Exception as e:
                messagebox.showerror("Conversion Error", f"Failed to convert {os.path.basename(mp3_path)}: {e}")
            finally:
                self.progress_bar["value"] = i + 1
                self.root.update_idletasks()

        self.status_label.config(text=f"Conversion complete! Converted {converted_count} of {len(self.input_paths)} files.")
        messagebox.showinfo("Conversion Complete", f"Successfully converted {converted_count} files to WAV.")
        self.convert_button.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = MP3toWAVConverter(root)
    root.mainloop()
