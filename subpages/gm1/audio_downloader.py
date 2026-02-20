import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import threading
import urllib3

# Suppress the InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AudioDownloader(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("音频下载器")
        self.geometry("600x450") # Increased height to accommodate new elements

        # URL input
        self.url_label = ttk.Label(self, text="网页URL:")
        self.url_label.pack(pady=5)
        self.url_entry = ttk.Entry(self, width=80)
        self.url_entry.insert(0, "https://kcwiki.org/wiki/大鲸")
        self.url_entry.pack(pady=5)

        # Local File input
        self.file_label = ttk.Label(self, text="或选择本地HTML文件:")
        self.file_label.pack(pady=5)
        self.file_path_entry = ttk.Entry(self, width=80)
        self.file_path_entry.pack(pady=5)
        self.browse_button = ttk.Button(self, text="浏览...", command=self.browse_file)
        self.browse_button.pack(pady=5)

        # Download button
        self.download_button = ttk.Button(self, text="下载音频", command=self.start_download_thread)
        self.download_button.pack(pady=10)

        # Status text area
        self.status_text = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=70, height=15)
        self.status_text.pack(pady=10)

    def log(self, message):
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.update_idletasks()

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="选择HTML文件",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")])
        if file_path:
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, file_path)

    def start_download_thread(self):
        self.download_button.config(state=tk.DISABLED)
        self.log("开始下载...")
        thread = threading.Thread(target=self.download_audio)
        thread.start()

    def download_audio(self):
        url = self.url_entry.get()
        local_file_path = self.file_path_entry.get()

        html_content = ""
        base_url_for_join = url # Use the URL entry as base for urljoin if local file is used

        if local_file_path:
            self.log(f"正在从本地文件读取: {local_file_path}")
            try:
                with open(local_file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                # If reading from local file, use the URL entry as the base for resolving relative paths
                # This assumes the local file is a saved version of the URL.
                if not base_url_for_join:
                    self.log("警告: 未提供URL，相对路径可能无法正确解析。")
            except Exception as e:
                self.log(f"错误: 无法读取本地文件。 {e}")
                self.download_button.config(state=tk.NORMAL)
                return
        else:
            if not url:
                self.log("错误: URL和本地文件路径都不能为空。")
                self.download_button.config(state=tk.NORMAL)
                return

            self.log("注意: 正在跳过SSL证书验证。")
            try:
                response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, verify=False)
                response.raise_for_status()
                html_content = response.text
            except requests.exceptions.RequestException as e:
                self.log(f"错误: 无法获取网页内容。 {e}")
                self.download_button.config(state=tk.NORMAL)
                return

        soup = BeautifulSoup(html_content, 'html.parser')
        # Find <a> tags that have a 'data-filesrc' attribute
        audio_links = soup.find_all('a', attrs={'data-filesrc': True})

        if not audio_links:
            self.log("未找到任何音频文件链接。")
            self.download_button.config(state=tk.NORMAL)
            return

        download_dir = "audio_downloads"
        os.makedirs(download_dir, exist_ok=True)
        self.log(f"文件将保存到 '{download_dir}' 文件夹。")
        self.log(f"找到 {len(audio_links)} 个音频文件链接。")

        for link_tag in audio_links:
            audio_url = link_tag['data-filesrc']
            
            # Skip if URL is empty or invalid
            if not audio_url or not audio_url.startswith(('http', 'https')):
                self.log(f"跳过无效的URL: {audio_url}")
                continue

            file_name = os.path.basename(audio_url)
            # Ensure there's a filename
            if not file_name:
                file_name = "unknown_audio.mp3" # Default if no filename can be extracted

            save_path = os.path.join(download_dir, file_name)

            try:
                self.log(f"正在下载: {file_name}")
                audio_response = requests.get(audio_url, stream=True, verify=False)
                audio_response.raise_for_status()

                with open(save_path, 'wb') as f:
                    for chunk in audio_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                self.log(f"下载完成: {file_name}")

            except requests.exceptions.RequestException as e:
                self.log(f"下载失败: {file_name}。错误: {e}")

        self.log("\n所有下载任务已完成。")
        self.download_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    app = AudioDownloader()
    app.mainloop()
