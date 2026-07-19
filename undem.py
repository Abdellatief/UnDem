import sys
import os
import json
from tkinter import Tk, StringVar, Label, Button, Entry, Text, filedialog, messagebox, ttk, Frame, BOTH, LEFT, RIGHT, TOP, BOTTOM, X, Y, END

class UnDemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UnDem — The Future Vision")
        self.root.geometry("950x680")
        self.root.configure(bg="#07090e") # الخلفية الكربونية الزرقاء المتوافقة مع الشعار
        
        # الإعدادات الافتراضية لويندوز الإعدادات
        self.config_file = "undem_config.json"
        self.settings = self.load_settings()
        self.current_lang = self.settings.get("language", "EN")

        # المتغيرات البرمجية لتخزين البيانات والمسارات المضافة
        self.video_files = []
        self.output_dir_var = StringVar()
        
        # النصوص المحدثة بالكامل لتعبر عن فصل وفك الفيديوهات والمشاهد
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
        # تنظيف النافذة وإعادة بنائها فوراً باللغة الجديدة
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_ui()
        self.update_file_list_display()

    # ---- دالات التحكم بالأزرار والأوامر الخلفية ----
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
            self.file_list.insert(END, f" 🎥  {os.path.basename(path)}  —  ({path})\n")
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
        
        # جاري العمل وتحديث شريط التقدم (الـ Backend الفعلي يوضع هنا)
        self.status_var.set(ln["status_processing"])
        self.progress['value'] = 15
        self.root.update_idletasks()
        
        # محاكاة اكتمال النبضة البرمجية بنجاح
        self.progress['value'] = 100
        self.status_var.set(ln["status_done"])
        messagebox.showinfo("UnDem", ln["status_done"])

    def setup_ui(self):
        ln = self.languages[self.current_lang]
        align = RIGHT if self.current_lang == "AR" else LEFT
        
        # ستايل التنسيق والتقدم المتناسق مع ألوان الموقع المتوهجة
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TProgressbar", thickness=8, troughcolor="#0e121a", background="#00ffd1") # توهج سياني متطابق مع الألوان الجديدة
        
        # ---- الهيدر العلوي ----
        header = Frame(self.root, bg="#0e121a", height=70)
        header.pack(fill=X, side=TOP)
        header.pack_propagate(False)
        
        title_lbl = Label(header, text=ln["title"], fg="#f4f6fa", bg="#0e121a", font=("Segoe UI", 14, "bold"))
        title_lbl.pack(side=align, padx=20, pady=18)
        
        # لوحة تبديل اللغات داخل الهيدر
        lang_frame = Frame(header, bg="#0e121a")
        lang_frame.pack(side=RIGHT if align == LEFT else LEFT, padx=20, pady=18)
        
        Label(lang_frame, text=ln["lang_lbl"], fg="#7e879a", bg="#0e121a", font=("Segoe UI", 10)).pack(side=LEFT, padx=5)
        
        btn_en = Button(lang_frame, text="English", command=lambda: self.switch_language("EN"), bg="#1c2436", fg="#f4f6fa", activebackground="#008be5", activeforeground="#ffffff", relief="flat", font=("Segoe UI", 9, "bold" if self.current_lang=="EN" else "normal"), padx=8)
        btn_en.pack(side=LEFT, padx=3)
        
        btn_ar = Button(lang_frame, text="العربية", command=lambda: self.switch_language("AR"), bg="#1c2436", fg="#f4f6fa", activebackground="#008be5", activeforeground="#ffffff", relief="flat", font=("Segoe UI", 9, "bold" if self.current_lang=="AR" else "normal"), padx=8)
        btn_ar.pack(side=LEFT, padx=3)

        # ---- الجسم الأساسي للبرنامج ----
        body = Frame(self.root, bg="#07090e")
        body.pack(fill=BOTH, expand=True, padx=20, pady=15)
        
        # القسم الأيسر/الأيمن: الملفات والمجلدات
        left_frame = Frame(body, bg="#07090e")
        left_frame.pack(side=align, fill=BOTH, expand=True, padx=10)
        
        Label(left_frame, text=ln["input_lbl"], fg="#f4f6fa", bg="#07090e", font=("Segoe UI", 11, "bold")).pack(anchor="w" if align==LEFT else "e", pady=5)
        
        # قائمة ملفات الفيديو المستوردة
        self.file_list = Text(left_frame, height=12, bg="#0e121a", fg="#c5cbd8", bd=0, highlightthickness=1, highlightbackground="#1c2436", font=("Segoe UI", 10), state="disabled")
        self.file_list.pack(fill=X, pady=5)
        
        btn_box = Frame(left_frame, bg="#07090e")
        btn_box.pack(fill=X, pady=5)
        
        # ربط دالات الإضافة والمسح بالتطبيق
        Button(btn_box, text=ln["btn_add"], command=self.add_videos, bg="#008be5", fg="#FFFFFF", activebackground="#00ffd1", relief="flat", font=("Segoe UI", 10, "bold"), width=18).pack(side=align, padx=2)
        Button(btn_box, text=ln["btn_clear"], command=self.clear_video_list, bg="#1c2436", fg="#EF4444", activebackground="#141a26", relief="flat", font=("Segoe UI", 10), width=12).pack(side=align, padx=2)
        
        # مجلدات المخرجات
        Label(left_frame, text=ln["output_lbl"], fg="#f4f6fa", bg="#07090e", font=("Segoe UI", 11, "bold")).pack(anchor="w" if align==LEFT else "e", pady=15)
        out_box = Frame(left_frame, bg="#07090e")
        out_box.pack(fill=X)
        
        Entry(out_box, textvariable=self.output_dir_var, bg="#0e121a", fg="#FFFFFF", bd=0, highlightthickness=1, highlightbackground="#1c2436", font=("Segoe UI", 10)).pack(side=align, fill=X, expand=True, ipady=5, padx=2)
        Button(out_box, text=ln["btn_browse"], command=self.browse_output_directory, bg="#1c2436", fg="#FFFFFF", activebackground="#008be5", relief="flat", font=("Segoe UI", 9)).pack(side=align, padx=2)
        
        # القسم الآخر: التسميات والقواعد
        right_frame = Frame(body, bg="#0e121a", bd=0, highlightthickness=1, highlightbackground="#1c2436")
        right_frame.pack(side=RIGHT if align==LEFT else LEFT, fill=BOTH, expand=True, padx=10, ipady=10)
        
        Label(right_frame, text=ln["naming_lbl"], fg="#f4f6fa", bg="#0e121a", font=("Segoe UI", 11, "bold")).pack(pady=10, padx=15, anchor="w" if align==LEFT else "e")
        
        # حقول التسمية التلقائية الافتراضية للمشاهد
        for i in range(1, 4):
            t_frame = Frame(right_frame, bg="#0e121a")
            t_frame.pack(fill=X, padx=15, pady=4)
            Label(t_frame, text=f"{ln['track_prefix']} {i}:", fg="#7e879a", bg="#0e121a", font=("Segoe UI", 10)).pack(side=align, padx=5)
            Entry(t_frame, bg="#07090e", fg="#FFFFFF", bd=0, highlightthickness=1, highlightbackground="#1c2436", width=25).pack(side=RIGHT if align==LEFT else LEFT, ipady=4)
            
        Button(right_frame, text=ln["btn_add_track"], bg="#1c2436", fg="#c5cbd8", activebackground="#07090e", relief="flat", font=("Segoe UI", 9)).pack(fill=X, padx=15, pady=15)

        # ---- الفوتر السفلي (التقدم والتشغيل) ----
        footer = Frame(self.root, bg="#0e121a", height=80)
        footer.pack(fill=X, side=BOTTOM)
        
        self.progress = ttk.Progressbar(footer, orient="horizontal", mode="determinate", style="TProgressbar")
        self.progress.pack(fill=X, side=TOP)
        self.progress['value'] = 0
        
        status_lbl = Label(footer, textvariable=self.status_var, fg="#7e879a", bg="#0e121a", font=("Segoe UI", 10))
        status_lbl.pack(side=align, padx=20, pady=18)
        
        # ربط زر التشغيل ببدء معالجة وفصل الفيديوهات والمشاهد يدوياً وتحديث الألوان
        Button(footer, text=ln["btn_start"], command=self.start_splitting_process, bg="#008be5", fg="#FFFFFF", activebackground="#00ffd1", activeforeground="#07090e", relief="flat", font=("Segoe UI", 11, "bold"), padx=25).pack(side=RIGHT if align==LEFT else LEFT, padx=20, pady=14)

if __name__ == "__main__":
    root = Tk()
    
    try:
        if hasattr(sys, '_MEIPASS'):
            icon_path = os.path.join(sys._MEIPASS, "logo.ico")
        else:
            icon_path = "logo.ico"
            
        root.iconbitmap(icon_path)
    except Exception as e:
        print("تنبيه الأيقونة:", e)
        
    app = UnDemApp(root)
    root.mainloop()
