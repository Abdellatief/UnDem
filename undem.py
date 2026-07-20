import sys
import os
import json
import subprocess
import re
import urllib.request
import zipfile
import shutil
import threading
from tkinter import Tk, StringVar, Label, Button, Entry, Text, filedialog, messagebox, ttk, Frame, BOTH, LEFT, RIGHT, TOP, BOTTOM, X, Y, END, Toplevel

class UnDemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UnDem — The Future Vision")
        self.root.geometry("650x580")
        self.root.configure(bg="#07090e")
        
        self.config_file = "undem_config.json"
        
        # اللغات المدعومة بالكامل في النظام
        self.languages = {
            "EN": {
                "title": "UnDem: Multi-Scene Video Splitter & Extractor",
                "input_lbl": "1. Input Video Files",
                "output_lbl": "2. Output Directory",
                "btn_add": " Add Videos",
                "btn_clear": " Clear List",
                "btn_browse": "Choose Folder",
                "btn_start": "Start Splitting Now",
                "status_ready": "Ready to work...",
                "status_processing": "Processing videos... Please wait.",
                "status_done": "Splitting completed successfully! 🎉",
                "lang_lbl": "Language:",
                "msg_select_video": "Please add at least one video file first.",
                "msg_select_output": "Please select an output directory.",
                "dl_title": "Downloading Components",
                "dl_msg": "Downloading FFmpeg component to run the application for the first time...\nPlease wait, the file is compressed and lightweight.",
                "dl_fail": "Failed to download FFmpeg automatically:\n"
            },
            "AR": {
                "title": "أنديم: فصل الكاميرات والمشاهد بسهولة",
                "input_lbl": "1. ملفات الفيديو المدخلة",
                "output_lbl": "2. مجلد حفظ المشاهد المستخرجة (Output)",
                "btn_add": " إضافة فيديوهات",
                "btn_clear": " مسح القائمة",
                "btn_browse": "اختيار مجلد",
                "btn_start": "ابدأ فصل المشاهد الآن",
                "status_ready": "...جاهز لبدء العمل",
                "status_processing": "...جاري معالجة وفصل الفيديوهات الآن، يرجى الانتظار",
                "status_done": "تم فصل الكاميرات والمشاهد بنجاح! 🎉",
                "lang_lbl": "اللغة:",
                "msg_select_video": "يرجى إضافة ملف فيديو واحد على الأقل أولاً.",
                "msg_select_output": "يرجى تحديد مجلد إخراج لحفظ الفيديوهات المستخرجة.",
                "dl_title": "تحميل المكونات الإضافية",
                "dl_msg": "جاري تحميل مكون FFmpeg لتشغيل البرنامج لأول مرة...\nيرجى الانتظار، حجم الملف صغير ومضغوط.",
                "dl_fail": "فشل تحميل FFmpeg تلقائياً:\n"
            }
        }

        # فحص وجود إعدادات سابقة (لتحديد أول تشغيل)
        if not os.path.exists(self.config_file):
            self.current_lang = "EN" # افتراضي مؤقت لحين الاختيار
            self.show_language_selector_first_time()
        else:
            self.settings = self.load_settings()
            self.current_lang = self.settings.get("language", "EN")
            self.initialize_app()

    def show_language_selector_first_time(self):
        """نافذة تظهر للمستخدم عند أول تشغيل لاختيار اللغة المفضلة للبرنامج"""
        lang_win = Toplevel(self.root)
        lang_win.title("UnDem — Welcome")
        lang_win.geometry("380x180")
        lang_win.configure(bg="#0e121a")
        lang_win.resizable(False, False)
        
        # تجعل النافذة تركز في منتصف الشاشة فوق النافذة الرئيسية وتمنع الضغط خلفها
        lang_win.transient(self.root)
        lang_win.grab_set()
        
        # لضمان غلق البرنامج بالكامل لو قفل النافذة دي بدون اختيار
        def on_close():
            lang_win.destroy()
            self.root.quit()
            sys.exit()
        lang_win.protocol("WM_DELETE_WINDOW", on_close)

        lbl = Label(lang_win, text="Welcome! Please choose your preferred language\nمرحباً بك! يرجى اختيار لغة البرنامج المفضلة", 
                    fg="#f4f6fa", bg="#0e121a", font=("Segoe UI", 10, "bold"), justify="center")
        lbl.pack(pady=25)

        btn_frame = Frame(lang_win, bg="#0e121a")
        btn_frame.pack(pady=5)

        def select_lang(lang):
            self.current_lang = lang
            self.save_settings()
            lang_win.destroy()
            self.initialize_app()

        Button(btn_frame, text="English (EN)", command=lambda: select_lang("EN"), bg="#008be5", fg="#FFFFFF", relief="flat", font=("Segoe UI", 10, "bold"), width=14, padx=5, pady=5).pack(side=LEFT, padx=10)
        Button(btn_frame, text="العربية (AR)", command=lambda: select_lang("AR"), bg="#1c2436", fg="#00ffd1", relief="flat", font=("Segoe UI", 10, "bold"), width=14, padx=5, pady=5).pack(side=RIGHT, padx=10)

        # توسيط النافذة برمجياً
        lang_win.update_idletasks()
        x = (lang_win.winfo_screenwidth() // 2) - (lang_win.winfo_width() // 2)
        y = (lang_win.winfo_screenheight() // 2) - (lang_win.winfo_height() // 2)
        lang_win.geometry(f"+{x}+{y}")

    def initialize_app(self):
        """بدء تشغيل واجهة البرنامج والتحقق الذكي من المكونات"""
        self.video_files = []
        self.output_dir_var = StringVar()
        self.status_var = StringVar()
        self.status_var.set(self.languages[self.current_lang]["status_ready"])
        
        self.setup_ui()
        
        # فحص المكونات التلقائي بعد ظهور الواجهة بـ 100 ملي ثانية
        self.root.after(100, self.check_and_download_ffmpeg)

    def get_bin_path(self, bin_name):
        ext = ".exe" if os.name == 'nt' else ""
        target_name = bin_name + ext
        
        if hasattr(sys, '_MEIPASS'):
            local_path = os.path.join(os.path.dirname(sys.executable), target_name)
        else:
            local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), target_name)
            
        if os.path.exists(local_path):
            return local_path
        return shutil.which(bin_name) if shutil.which(bin_name) else local_path

    def check_and_download_ffmpeg(self):
        ffmpeg_path = self.get_bin_path("ffmpeg")
        if os.path.exists(ffmpeg_path) or shutil.which("ffmpeg"):
            return

        ln = self.languages[self.current_lang]
        download_win = Toplevel(self.root)
        download_win.title(ln["dl_title"])
        download_win.geometry("420x180")
        download_win.configure(bg="#0e121a")
        download_win.resizable(False, False)
        download_win.transient(self.root)
        download_win.grab_set()
        
        # منع إغلاق نافذة التحميل يدوياً لحماية ملفات النظام من العطب
        download_win.protocol("WM_DELETE_WINDOW", lambda: None)
        
        lbl = Label(download_win, text=ln["dl_msg"], fg="#f4f6fa", bg="#0e121a", font=("Segoe UI", 10), justify="center")
        lbl.pack(pady=15)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("DL.TProgressbar", thickness=12, troughcolor="#07090e", background="#00ffd1")
        
        progress = ttk.Progressbar(download_win, orient="horizontal", length=340, mode="determinate", style="DL.TProgressbar")
        progress.pack(pady=5)
        
        lbl_percent = Label(download_win, text="0%", fg="#00ffd1", bg="#0e121a", font=("Segoe UI", 10, "bold"))
        lbl_percent.pack(pady=2)
        
        def download_task():
            try:
                if os.name == 'nt':
                    url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
                else:
                    url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-osx64-gpl.zip"
                
                if hasattr(sys, '_MEIPASS'):
                    base_dir = os.path.dirname(sys.executable)
                else:
                    base_dir = os.path.dirname(os.path.abspath(__file__))
                    
                zip_tmp = os.path.join(base_dir, "ffmpeg_tmp.zip")
                extract_dir = os.path.join(base_dir, "ffmpeg_extracted")
                
                def reporthook(blocknum, blocksize, totalsize):
                    read_so_far = blocknum * blocksize
                    if totalsize > 0:
                        percent = int((read_so_far * 100) / totalsize)
                        if percent > 100: percent = 100
                        progress['value'] = percent
                        lbl_percent.config(text=f"{percent}%")
                        download_win.update_idletasks()
                
                urllib.request.urlretrieve(url, zip_tmp, reporthook)
                
                with zipfile.ZipFile(zip_tmp, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                target_bin = "ffmpeg.exe" if os.name == 'nt' else "ffmpeg"
                out_bin_path = os.path.join(base_dir, target_bin)
                
                if os.path.exists(out_bin_path):
                    os.remove(out_bin_path)
                    
                file_found = False
                for root_dir, _, files in os.walk(extract_dir):
                    if target_bin in files:
                        shutil.move(os.path.join(root_dir, target_bin), out_bin_path)
                        if os.name != 'nt':
                            os.chmod(out_bin_path, 0o755)
                        file_found = True
                        break
                
                shutil.rmtree(extract_dir, ignore_errors=True)
                if os.path.exists(zip_tmp):
                    os.remove(zip_tmp)
                
                if not file_found:
                    raise Exception("FFmpeg binary missing inside zip package.")
                
                # إغلاق النافذة تلقائياً لبدء العمل الآمن مباشرة دون مقاطعة المستخدم
                download_win.destroy()
            except Exception as e:
                messagebox.showerror("UnDem Error", f"{ln['dl_fail']}{str(e)}", parent=download_win)
                download_win.destroy()

        threading.Thread(target=download_task, daemon=True).start()
        self.root.wait_window(download_win)

    def load_settings(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"language": "EN"}

    def save_settings(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump({"language": self.current_lang}, f)

    def switch_language(self, lang):
        if self.current_lang == lang:
            return
        self.current_lang = lang
        self.save_settings()
        self.status_var.set(self.languages[self.current_lang]["status_ready"])
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_ui()
        self.update_file_list_display()

    def add_videos(self):
        files = filedialog.askopenfilenames(
            title="Select Video Files",
            filetypes=[("Video Files", "*.mp4 *.mkv *.avi *.mov *.m4v")]
        )
        if files:
            for file in files:
                if file not in self.video_files:
                    self.video_files.append(file)
            self.update_file_list_display()

    def clear_video_list(self):
        self.video_files.clear()
        self.update_file_list_display()

    def update_file_list_display(self):
        self.file_list.config(state="normal")
        self.file_list.delete("1.0", END)
        for path in self.video_files:
            self.file_list.insert(END, f" 🎥    {os.path.basename(path)}  —  ({path})\n")
        self.file_list.config(state="disabled")

    def browse_output_directory(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)

    def get_stream_counts(self, ffmpeg_bin, video_path, creation_flag):
        cmd = [ffmpeg_bin, '-i', video_path]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore', creationflags=creation_flag)
        output = res.stderr
        video_matches = re.findall(r'Stream #\d+:\d+.*Video:', output)
        audio_matches = re.findall(r'Stream #\d+:\d+.*Audio:', output)
        return len(video_matches), len(audio_matches)

    def start_splitting_process(self):
        ln = self.languages[self.current_lang]
        if not self.video_files:
            messagebox.showwarning("UnDem", ln["msg_select_video"])
            return
        if not self.output_dir_var.get():
            messagebox.showwarning("UnDem", ln["msg_select_output"])
            return
        
        self.status_var.set(ln["status_processing"])
        self.progress['value'] = 5
        self.root.update_idletasks()
        
        output_dir = self.output_dir_var.get()
        ffmpeg_bin = self.get_bin_path("ffmpeg")
        
        if not os.path.exists(ffmpeg_bin):
            self.progress['value'] = 0
            self.status_var.set("Error!")
            messagebox.showerror("UnDem Error", "FFmpeg component is missing. Please restart the app.")
            return

        def worker_task():
            try:
                total_files = len(self.video_files)
                creation_flag = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                
                for file_index, video_path in enumerate(self.video_files):
                    base_name = os.path.splitext(os.path.basename(video_path))[0]
                    v_count, a_count = self.get_stream_counts(ffmpeg_bin, video_path, creation_flag)
                    
                    if v_count == 0 and a_count == 0:
                        raise Exception("Could not retrieve system streams. Check file parameters.")
                    
                    for idx in range(v_count):
                        folder_name = f"Video_{idx}"
                        v_out_dir = os.path.join(output_dir, folder_name)
                        os.makedirs(v_out_dir, exist_ok=True)
                        out_file = os.path.join(v_out_dir, f"{folder_name}_{base_name}.mkv")
                        cmd = [ffmpeg_bin, '-y', '-i', video_path, '-map', f'0:v:{idx}', '-c', 'copy', out_file]
                        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=creation_flag)
                    
                    for idx in range(a_count):
                        folder_name = f"Audio_{idx}"
                        a_out_dir = os.path.join(output_dir, folder_name)
                        os.makedirs(a_out_dir, exist_ok=True)
                        out_file = os.path.join(a_out_dir, f"{folder_name}_{base_name}.wav")
                        cmd = [ffmpeg_bin, '-y', '-i', video_path, '-map', f'0:a:{idx}', '-c:a', 'pcm_s24le', out_file]
                        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=creation_flag)
                    
                    percent = 5 + int((file_index + 1) / total_files * 95)
                    self.root.after(0, lambda p=percent: self.progress.configure(value=p))
                
                self.root.after(0, lambda: self.progress.configure(value=100))
                self.root.after(0, lambda: self.status_var.set(ln["status_done"]))
                self.root.after(0, lambda: messagebox.showinfo("UnDem", ln["status_done"]))
                
            except Exception as e:
                self.root.after(0, lambda: self.progress.configure(value=0))
                self.root.after(0, lambda: self.status_var.set("Error!"))
                self.root.after(0, lambda err=str(e): messagebox.showerror("UnDem Error", f"Execution stopped:\n{err}"))

        threading.Thread(target=worker_task, daemon=True).start()

    def setup_ui(self):
        ln = self.languages[self.current_lang]
        align = RIGHT if self.current_lang == "AR" else LEFT
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TProgressbar", thickness=8, troughcolor="#0e121a", background="#00ffd1")
        
        header = Frame(self.root, bg="#0e121a", height=65)
        header.pack(fill=X, side=TOP)
        header.pack_propagate(False)
        
        title_lbl = Label(header, text=ln["title"], fg="#f4f6fa", bg="#0e121a", font=("Segoe UI", 12, "bold"))
        title_lbl.pack(side=align, padx=20, pady=18)
        
        lang_frame = Frame(header, bg="#0e121a")
        lang_frame.pack(side=RIGHT if align == LEFT else LEFT, padx=20, pady=18)
        
        Label(lang_frame, text=ln["lang_lbl"], fg="#7e879a", bg="#0e121a", font=("Segoe UI", 10)).pack(side=LEFT, padx=5)
        
        btn_en = Button(lang_frame, text="EN", command=lambda: self.switch_language("EN"), bg="#1c2436", fg="#f4f6fa", relief="flat", font=("Segoe UI", 9, "bold" if self.current_lang=="EN" else "normal"), padx=6)
        btn_en.pack(side=LEFT, padx=2)
        
        btn_ar = Button(lang_frame, text="AR", command=lambda: self.switch_language("AR"), bg="#1c2436", fg="#f4f6fa", relief="flat", font=("Segoe UI", 9, "bold" if self.current_lang=="AR" else "normal"), padx=6)
        btn_ar.pack(side=LEFT, padx=2)

        body = Frame(self.root, bg="#07090e")
        body.pack(fill=BOTH, expand=True, padx=20, pady=15)
        
        Label(body, text=ln["input_lbl"], fg="#f4f6fa", bg="#07090e", font=("Segoe UI", 11, "bold")).pack(anchor="w" if align==LEFT else "e", pady=5)
        
        self.file_list = Text(body, height=12, bg="#0e121a", fg="#c5cbd8", bd=0, highlightthickness=1, highlightbackground="#1c2436", font=("Segoe UI", 10), state="disabled")
        self.file_list.pack(fill=X, pady=5)
        
        btn_box = Frame(body, bg="#07090e")
        btn_box.pack(fill=X, pady=5)
        
        Button(btn_box, text=ln["btn_add"], command=self.add_videos, bg="#008be5", fg="#FFFFFF", relief="flat", font=("Segoe UI", 10, "bold"), width=15).pack(side=align, padx=2)
        Button(btn_box, text=ln["btn_clear"], command=self.clear_video_list, bg="#1c2436", fg="#EF4444", relief="flat", font=("Segoe UI", 10), width=12).pack(side=align, padx=2)
        
        Label(body, text=ln["output_lbl"], fg="#f4f6fa", bg="#07090e", font=("Segoe UI", 11, "bold")).pack(anchor="w" if align==LEFT else "e", pady=15)
        out_box = Frame(body, bg="#07090e")
        out_box.pack(fill=X)
        
        Entry(out_box, textvariable=self.output_dir_var, bg="#0e121a", fg="#FFFFFF", bd=0, highlightthickness=1, highlightbackground="#1c2436", font=("Segoe UI", 10)).pack(side=align, fill=X, expand=True, ipady=5, padx=2)
        Button(out_box, text=ln["btn_browse"], command=self.browse_output_directory, bg="#1c2436", fg="#FFFFFF", relief="flat", font=("Segoe UI", 9)).pack(side=align, padx=2)

        footer = Frame(self.root, bg="#0e121a", height=75)
        footer.pack(fill=X, side=BOTTOM)
        
        self.progress = ttk.Progressbar(footer, orient="horizontal", mode="determinate", style="TProgressbar")
        self.progress.pack(fill=X, side=TOP)
        self.progress['value'] = 0
        
        status_lbl = Label(footer, textvariable=self.status_var, fg="#7e879a", bg="#0e121a", font=("Segoe UI", 10))
        status_lbl.pack(side=align, padx=20, pady=18)
        
        Button(footer, text=ln["btn_start"], command=self.start_splitting_process, bg="#008be5", fg="#FFFFFF", relief="flat", font=("Segoe UI", 11, "bold"), padx=25).pack(side=RIGHT if align==LEFT else LEFT, padx=20, pady=14)

if __name__ == "__main__":
    root = Tk()
    try:
        if hasattr(sys, '_MEIPASS'):
            icon_path = os.path.join(sys._MEIPASS, "logo.ico")
        else:
            icon_path = "logo.ico"
        root.iconbitmap(icon_path)
    except Exception as e:
        print("Icon alert:", e)
        
    app = UnDemApp(root)
    root.mainloop()
