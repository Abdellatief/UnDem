import sys
import os
import json
from tkinter import Tk, StringVar, Label, Button, Entry, Text, filedialog, messagebox, ttk, Frame, BOTH, LEFT, RIGHT, TOP, BOTTOM, X, Y, END

class UnDemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UnDem — The Future Vision")
        self.root.geometry("900x650")
        self.root.configure(bg="#121214")
        
        # الإعدادات الافتراضية للوحة التحكم
        self.config_file = "undem_config.json"
        self.settings = self.load_settings()
        
        # النصوص للغات
        self.languages = {
            "EN": {
                "title": "UnDem: Multi-Scene Video Splitter & Extractor",
                "subtitle": "The Future Vision - Professional Splitting Tool",
                "input_lbl": "1. Input Video Files",
                "output_lbl": "2. Output Directory",
                "naming_lbl": "3. Track Naming Rules (e.g., OBS)",
                "btn_add": " Add Videos",
                "btn_clear": " Clear List",
                "btn_browse": "Choose Folder",
                "btn_start": "Start Splitting Now",
                "btn_add_track": " Add Custom Track Name",
                "status_ready": "Ready to work...",
                "settings_title": "Control Panel",
                "lang_lbl": "App Language:",
                "theme_lbl": "Interface Theme: Dark Premium",
                "track_prefix": "Video Track"
            },
            "AR": {
                "title": "أنديم: فصل الكاميرات والمشاهد بسهولة",
                "subtitle": "UnDem: The Future Vision — أداة احترافية",
                "input_lbl": "1. ملفات الفيديو المدخلة",
                "output_lbl": "2. مكان فك المشاهد (Output)",
                "naming_lbl": "3. قاعدة تسمية الفيديوهات (مثل OBS)",
                "btn_add": " إضافة فيديوهات يدوياً",
                "btn_clear": " مسح القائمة",
                "btn_browse": "اختيار مجلد",
                "btn_start": "ابدأ فصل المشاهد الآن",
                "btn_add_track": " إضافة تراك إضافي في التسمية",
                "status_ready": "...جاهز لبدء العمل",
                "settings_title": "لوحة التحكم",
                "lang_lbl": "لغة التطبيق:",
                "theme_lbl": "المظهر: داكن احترافي",
                "track_prefix": "تراك فيديو"
            }
        }
        
        self.current_lang = self.settings.get("language", "EN")
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
        self.current_lang = lang
        self.save_settings()
        # إعادة بناء الواجهة لتطبيق اللغة فوراً
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_ui()

    def setup_ui(self):
        ln = self.languages[self.current_lang]
        align = RIGHT if self.current_lang == "AR" else LEFT
        
        # ستايل التنسيق العام (Premium Dark UI)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TProgressbar", thickness=8, troughcolor="#1A1A1E", background="#6366F1")
        
        # ---- الهيدر العلوي ----
        header = Frame(self.root, bg="#1E1E24", height=70)
        header.pack(fill=X, side=TOP)
        header.pack_propagate(False)
        
        title_lbl = Label(header, text=ln["title"], fg="#FFFFFF", bg="#1E1E24", font=("Segoe UI", 14, "bold"))
        title_lbl.pack(side=align, padx=20, pady=10)
        
        # لوحة التحكم في اللغات داخل الهيدر
        lang_frame = Frame(header, bg="#1E1E24")
        lang_frame.pack(side=RIGHT if align == LEFT else LEFT, padx=20, pady=15)
        
        Label(lang_frame, text=ln["lang_lbl"], fg="#A1A1AA", bg="#1E1E24", font=("Segoe UI", 9)).pack(side=LEFT, padx=5)
        btn_en = Button(lang_frame, text="English", command=lambda: self.switch_language("EN"), bg="#27272A", fg="#FFFFFF", relief="flat", font=("Segoe UI", 8))
        btn_en.pack(side=LEFT, padx=2)
        btn_ar = Button(lang_frame, text="العربية", command=lambda: self.switch_language("AR"), bg="#27272A", fg="#FFFFFF", relief="flat", font=("Segoe UI", 8))
        btn_ar.pack(side=LEFT, padx=2)

        # ---- الجسم الأساسي للبرنامج ----
        body = Frame(self.root, bg="#121214")
        body.pack(fill=BOTH, expand=True, padx=20, pady=15)
        
        # القسم الأيسر/الأيمن: الملفات والمجلدات
        left_frame = Frame(body, bg="#121214")
        left_frame.pack(side=align, fill=BOTH, expand=True, padx=10)
        
        Label(left_frame, text=ln["input_lbl"], fg="#F4F4F5", bg="#121214", font=("Segoe UI", 11, "bold")).pack(anchor="w" if align==LEFT else "e", pady=5)
        
        # قائمة الملفات بشكل مودرن
        self.file_list = Text(left_frame, height=12, bg="#1E1E24", fg="#E4E4E7", bd=0, highlightthickness=1, highlightbackground="#27272A", font=("Segoe UI", 10))
        self.file_list.pack(fill=X, pady=5)
        
        btn_box = Frame(left_frame, bg="#121214")
        btn_box.pack(fill=X, pady=5)
        Button(btn_box, text=ln["btn_add"], bg="#4F46E5", fg="#FFFFFF", relief="flat", font=("Segoe UI", 10, "bold"), width=15).pack(side=align, padx=2)
        Button(btn_box, text=ln["btn_clear"], bg="#27272A", fg="#EF4444", relief="flat", font=("Segoe UI", 10), width=12).pack(side=align, padx=2)
        
        # المخرجات
        Label(left_frame, text=ln["output_lbl"], fg="#F4F4F5", bg="#121214", font=("Segoe UI", 11, "bold")).pack(anchor="w" if align==LEFT else "e", pady=15)
        out_box = Frame(left_frame, bg="#121214")
        out_box.pack(fill=X)
        Entry(out_box, bg="#1E1E24", fg="#FFFFFF", bd=0, highlightthickness=1, highlightbackground="#27272A", font=("Segoe UI", 10)).pack(side=align, fill=X, expand=True, ipady=4, padx=2)
        Button(out_box, text=ln["btn_browse"], bg="#27272A", fg="#FFFFFF", relief="flat", font=("Segoe UI", 9)).pack(side=align, padx=2)
        
        # القسم الآخر: التسميات والقواعد
        right_frame = Frame(body, bg="#1E1E24", bd=0, highlightthickness=1, highlightbackground="#27272A")
        right_frame.pack(side=RIGHT if align==LEFT else LEFT, fill=BOTH, expand=True, padx=10, ipady=10)
        
        Label(right_frame, text=ln["naming_lbl"], fg="#F4F4F5", bg="#1E1E24", font=("Segoe UI", 11, "bold")).pack(pady=10, padx=15, anchor="w" if align==LEFT else "e")
        
        # حقول التسمية التلقائية الافتراضية
        for i in range(1, 4):
            t_frame = Frame(right_frame, bg="#1E1E24")
            t_frame.pack(fill=X, padx=15, pady=4)
            Label(t_frame, text=f"{ln['track_prefix']} {i}:", fg="#A1A1AA", bg="#1E1E24", font=("Segoe UI", 10)).pack(side=align, padx=5)
            Entry(t_frame, bg="#121214", fg="#FFFFFF", bd=0, highlightthickness=1, highlightbackground="#27272A", width=25).pack(side=RIGHT if align==LEFT else LEFT, ipady=3)
            
        Button(right_frame, text=ln["btn_add_track"], bg="#27272A", fg="#A1A1AA", relief="flat", font=("Segoe UI", 9)).pack(fill=X, padx=15, pady=15)

        # ---- الفوتر السفلي (التقدم والتشغيل) ----
        footer = Frame(self.root, bg="#1E1E24", height=80)
        footer.pack(fill=X, side=BOTTOM)
        
        self.progress = ttk.Progressbar(footer, orient="horizontal", mode="determinate", style="TProgressbar")
        self.progress.pack(fill=X, side=TOP)
        self.progress['value'] = 35  # تجربة للشكل فقط
        
        status_lbl = Label(footer, text=ln["status_ready"], fg="#A1A1AA", bg="#1E1E24", font=("Segoe UI", 10))
        status_lbl.pack(side=align, padx=20, pady=15)
        
        Button(footer, text=ln["btn_start"], bg="#6366F1", fg="#FFFFFF", relief="flat", font=("Segoe UI", 11, "bold"), padx=20).pack(side=RIGHT if align==LEFT else LEFT, padx=20, pady=12)

if __name__ == "__main__":
    root = Tk()
    app = UnDemApp(root)
    root.mainloop()
