import sys
import os
import json
import subprocess
from tkinter import Tk, StringVar, Label, Button, Entry, Text, filedialog, messagebox, ttk, Frame, BOTH, LEFT, RIGHT, TOP, BOTTOM, X, Y, END

class UnDemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UnDem — The Future Vision")
        self.root.geometry("950x680")
        self.root.configure(bg="#07090e")
        
        self.config_file = "undem_config.json"
        self.settings = self.load_settings()
        self.current_lang = self.settings.get("language", "EN")

        self.video_files = []
        self.output_dir_var = StringVar()
        self.scene_entries = [] # قائمة لحفظ الـ Entries البرمجية لاستخراج نصوص المربعات
        
        self.languages = {
            "EN": {
                "title": "UnDem: Multi-Scene Video Splitter & Extractor",
                "subtitle": "The Future Vision - Professional Splitting Tool",
                "input_lbl": "1. Input Video Files",
                "output_lbl": "2. Output Directory",
                "naming_lbl": "3. Video Naming Rules (e.g., OBS)",
                "btn_add": " Add Videos",
                "btn_clear": " Clear List",
                "btn_browse": "Choose Folder",
                "btn_start": "Start Splitting Now",
                "btn_add_track": " Add Custom Video Name",
                "status_ready": "Ready to work...",
                "status_processing": "Processing videos... Please wait.",
                "status_done": "Splitting completed successfully! 🎉",
                "settings_title": "Control Panel",
                "lang_lbl": "App Language:",
                "theme_lbl": "Interface Theme: Dark Premium",
                "track_prefix": "Video Scene",
                "msg_select_video": "Please add at least one video file first.",
                "msg_select_output": "Please select an output directory."
            },
            "AR": {
                "title": "أنديم: فصل الكاميرات والمشاهد بسهولة",
                "subtitle": "UnDem: The Future Vision — أداة احترافية",
                "input_lbl": "1. ملفات الفيديو المدخلة",
                "output_lbl": "2. مكان فك المشاهد (Output)",
                "naming_lbl": "3. قاعدة تسمية الفيديوهات المستخرجة (مثل OBS)",
                "btn_add": " إضافة فيديوهات يدوياً",
                "btn_clear": " مسح القائمة",
                "btn_browse": "اختيار مجلد",
                "btn_start": "ابدأ فصل المشاهد الآن",
                "btn_add_track": " إضافة اسم فيديو مخصص",
                "status_ready": "...جاهز لبدء العمل",
                "status_processing": "...جاري معالجة وفصل الفيديوهات الآن، يرجى الانتظار",
                "status_done": "تم فصل الكاميرات والمشاهد بنجاح! 🎉",
                "settings_title": "لوحة التحكم",
                "lang_lbl": "لغة التطبيق:",
                "theme_lbl": "المظهر: داكن احترافي",
                "track_prefix": "مشهد فيديو",
                "msg_select_video": "يرجى إضافة ملف فيديو واحد على الأقل أولاً.",
                "msg_select_output": "يرجى تحديد مجلد إخراج لحفظ الفيديوهات المستخرجة."
            }
        }
        
        self.status_var = StringVar()
        self.status_var.set(self.languages[self.current_lang]["status_ready"])
        self.setup_ui()

    def get_bin_path(self, bin_name):
        """دالة ذكية للحصول على مسار FFmpeg المدمج أو من النظام مباشرة"""
        if hasattr(sys, '_MEIPASS'):
            ext = ".exe" if os.name == 'nt' else ""
            embedded_path = os.path.join(sys._MEIPASS, bin_name + ext)
            if os.path.exists(embedded_path):
                return embedded_path
        return bin_name

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
            self.file_list.insert(END, f" 🎥   {os.path.basename(path)}  —  ({path})\n")
        self.file_list.config(state="disabled")

    def browse_output_directory(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)

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
        ffprobe_bin = self.get_bin_path("ffprobe")
        
        try:
            total_files = len(self.video_files)
            creation_flag = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            
            for file_index, video_path in enumerate(self.video_files):
                base_name = os.path.splitext(os.path.basename(video_path))[0]
                
                # 1. جلب قنوات الفيديو باستخدام ffprobe
                v_probe = [ffprobe_bin, '-v', 'error', '-select_streams', 'v', '-show_entries', 'stream=index', '-of', 'csv=p=0', video_path]
                res_v = subprocess.run(v_probe, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=creation_flag)
                v_streams = [x for x in res_v.stdout.strip().split('\n') if x]
                
                # 2. جلب قنوات الصوت باستخدام ffprobe
                a_probe = [ffprobe_bin, '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index', '-of', 'csv=p=0', video_path]
                res_a = subprocess.run(a_probe, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=creation_flag)
                a_streams = [x for x in res_a.stdout.strip().split('\n') if x]
                
                # 3. معالجة وتفريع مسارات الفيديو كـ (.mkv) متل الـ Bat تماماً
                for idx, stream in enumerate(v_streams):
                    custom_name = ""
                    if idx < len(self.scene_entries):
                        custom_name = self.scene_entries[idx].get().strip()
                    
                    if not custom_name:
                        custom_name = f"Video_{idx}"
                        
                    v_out_dir = os.path.join(output_dir, f"Video_{idx}")
                    os.makedirs(v_out_dir, exist_ok=True)
                    
                    # حفظ الملف وحذف الرموز الغريبة من الاسم
                    out_file = os.path.join(v_out_dir, f"{custom_name}_{base_name}.mkv")
                    cmd = [ffmpeg_bin, '-y', '-i', video_path, '-map', f'0:v:{idx}', '-c', 'copy', out_file]
                    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=creation_flag)
                
                # 4. معالجة وتفريع مسارات الصوت كـ (.wav) وموجة احترافية 24بت
                for idx, stream in enumerate(a_streams):
                    custom_name = f"Audio_{idx}"
                    a_out_dir = os.path.join(output_dir, f"Audio_{idx}")
                    os.makedirs(a_out_dir, exist_ok=True)
                    
                    out_file = os.path.join(a_out_dir, f"{custom_name}_{base_name}.wav")
                    cmd = [ffmpeg_bin, '-y', '-i', video_path, '-map', f'0:a:{idx}', '-c:a', 'pcm_s24le', out_file]
                    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=creation_flag)
                
                # معالجة التدفق لشريط الرفع
                self.progress['value'] = 5 + int((file_index + 1) / total_files * 95)
                self.root.update_idletasks()
            
            self.progress['value'] = 100
            self.status_var.set(ln["status_done"])
            messagebox.showinfo("UnDem", ln["status_done"])
            
        except Exception as e:
            self.progress['value'] = 0
            self.status_var.set("Error!")
            messagebox.showerror("UnDem Error", f"Error during execution:\n{str(e)}")

    def setup_ui(self):
        ln = self.languages[self.current_lang]
        align = RIGHT if self.current_lang == "AR" else LEFT
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TProgressbar", thickness=8, troughcolor="#0e121a", background="#00ffd1")
        
        header = Frame(self.root, bg="#0e121a", height=70)
        header.pack(fill=X, side=TOP)
        header.pack_propagate(False)
        
        title_lbl = Label(header, text=ln["title"], fg="#f4f6fa", bg="#0e121a", font=("Segoe UI", 14, "bold"))
        title_lbl.pack(side=align, padx=20, pady=18)
        
        lang_frame = Frame(header, bg="#0e121a")
        lang_frame.pack(side=RIGHT if align == LEFT else LEFT, padx=20, pady=18)
        
        Label(lang_frame, text=ln["lang_lbl"], fg="#7e879a", bg="#0e121a", font=("Segoe UI", 10)).pack(side=LEFT, padx=5)
        
        btn_en = Button(lang_frame, text="English", command=lambda: self.switch_language("EN"), bg="#1c2436", fg="#f4f6fa", relief="flat", font=("Segoe UI", 9, "bold" if self.current_lang=="EN" else "normal"), padx=8)
        btn_en.pack(side=LEFT, padx=3)
        
        btn_ar = Button(lang_frame, text="العربية", command=lambda: self.switch_language("AR"), bg="#1c2436", fg="#f4f6fa", relief="flat", font=("Segoe UI", 9, "bold" if self.current_lang=="AR" else "normal"), padx=8)
        btn_ar.pack(side=LEFT, padx=3)

        body = Frame(self.root, bg="#07090e")
        body.pack(fill=BOTH, expand=True, padx=20, pady=15)
        
        left_frame = Frame(body, bg="#07090e")
        left_frame.pack(side=align, fill=BOTH, expand=True, padx=10)
        
        Label(left_frame, text=ln["input_lbl"], fg="#f4f6fa", bg="#07090e", font=("Segoe UI", 11, "bold")).pack(anchor="w" if align==LEFT else "e", pady=5)
        
        self.file_list = Text(left_frame, height=12, bg="#0e121a", fg="#c5cbd8", bd=0, highlightthickness=1, highlightbackground="#1c2436", font=("Segoe UI", 10), state="disabled")
        self.file_list.pack(fill=X, pady=5)
        
        btn_box = Frame(left_frame, bg="#07090e")
        btn_box.pack(fill=X, pady=5)
        
        Button(btn_box, text=ln["btn_add"], command=self.add_videos, bg="#008be5", fg="#FFFFFF", relief="flat", font=("Segoe UI", 10, "bold"), width=18).pack(side=align, padx=2)
        Button(btn_box, text=ln["btn_clear"], command=self.clear_video_list, bg="#1c2436", fg="#EF4444", relief="flat", font=("Segoe UI", 10), width=12).pack(side=align, padx=2)
        
        Label(left_frame, text=ln["output_lbl"], fg="#f4f6fa", bg="#07090e", font=("Segoe UI", 11, "bold")).pack(anchor="w" if align==LEFT else "e", pady=15)
        out_box = Frame(left_frame, bg="#07090e")
        out_box.pack(fill=X)
        
        Entry(out_box, textvariable=self.output_dir_var, bg="#0e121a", fg="#FFFFFF", bd=0, highlightthickness=1, highlightbackground="#1c2436", font=("Segoe UI", 10)).pack(side=align, fill=X, expand=True, ipady=5, padx=2)
        Button(out_box, text=ln["btn_browse"], command=self.browse_output_directory, bg="#1c2436", fg="#FFFFFF", relief="flat", font=("Segoe UI", 9)).pack(side=align, padx=2)
        
        right_frame = Frame(body, bg="#0e121a", bd=0, highlightthickness=1, highlightbackground="#1c2436")
        right_frame.pack(side=RIGHT if align==LEFT else LEFT, fill=BOTH, expand=True, padx=10, ipady=10)
        
        Label(right_frame, text=ln["naming_lbl"], fg="#f4f6fa", bg="#0e121a", font=("Segoe UI", 11, "bold")).pack(pady=10, padx=15, anchor="w" if align==LEFT else "e")
        
        self.scene_entries.clear()
        for i in range(1, 4):
            t_frame = Frame(right_frame, bg="#0e121a")
            t_frame.pack(fill=X, padx=15, pady=4)
            Label(t_frame, text=f"{ln['track_prefix']} {i}:", fg="#7e879a", bg="#0e121a", font=("Segoe UI", 10)).pack(side=align, padx=5)
            
            ent = Entry(t_frame, bg="#07090e", fg="#FFFFFF", bd=0, highlightthickness=1, highlightbackground="#1c2436", width=25)
            ent.pack(side=RIGHT if align==LEFT else LEFT, ipady=4)
            self.scene_entries.append(ent)
            
        Button(right_frame, text=ln["btn_add_track"], bg="#1c2436", fg="#c5cbd8", relief="flat", font=("Segoe UI", 9)).pack(fill=X, padx=15, pady=15)

        footer = Frame(self.root, bg="#0e121a", height=80)
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
