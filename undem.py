import os
import sys
import json
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# --- الإعدادات الافتراضية لحفظ التسميات والتفضيلات ---
CONFIG_FILE = "undem_config.json"

class UnDemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UnDem - The Future Vision")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        self.selected_videos = []
        self.output_dir = tk.StringVar(value=os.path.expanduser("~"))
        self.track_names = [] # قائمة لحفظ مدخلات أسماء التراكات
        
        # تحميل الإعدادات المحفوظة إن وجدت
        self.load_config()
        
        self.setup_styles()
        self.create_widgets()
        
    def setup_styles(self):
        # تصميم واجهة داكنة احترافية (Dark Theme) تناسب المصممين وصناع المحتوى
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.bg_color = "#1e1e24"
        self.fg_color = "#ffffff"
        self.accent_color = "#4f46e5" # بنفسجي عصري
        self.card_bg = "#2a2a35"
        self.text_muted = "#9ca3af"
        
        self.root.configure(bg=self.bg_color)
        
        self.style.configure(".", background=self.bg_color, foreground=self.fg_color, font=("Segoe UI", 10))
        self.style.configure("TLabel", background=self.bg_color, foreground=self.fg_color)
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground=self.fg_color)
        self.style.configure("Sub.TLabel", font=("Segoe UI", 9), foreground=self.text_muted)
        
        self.style.configure("Card.TFrame", background=self.card_bg, relief="flat")
        self.style.configure("CardLabel.TLabel", background=self.card_bg, foreground=self.fg_color)
        
        # تصميم الأزرار
        self.style.configure("TButton", background="#374151", foreground=self.fg_color, borderwidth=0, padding=6)
        self.style.map("TButton", background=[("active", "#4b5563")])
        
        self.style.configure("Accent.TButton", background=self.accent_color, foreground=self.fg_color, borderwidth=0, padding=8, font=("Segoe UI", 10, "bold"))
        self.style.map("Accent.TButton", background=[("active", "#4338ca")])

    def create_widgets(self):
        # --- الشريط العلوي ---
        top_frame = ttk.Frame(self.root, padding=15)
        top_frame.pack(fill="x")
        
        title_lbl = ttk.Label(top_frame, text="UnDem", style="Header.TLabel")
        title_lbl.pack(anchor="w")
        subtitle_lbl = ttk.Label(top_frame, text="UnDem: The Future Vision - أنديم: فصل الكاميرات والتراكات بسهولة", style="Sub.TLabel")
        subtitle_lbl.pack(anchor="w", pady=(2, 0))
        
        # --- الجسم الرئيسي مقسم لجزئين ---
        main_paned = ttk.Panedwindow(self.root, orient="horizontal")
        main_paned.pack(fill="both", expand=True, padx=15, pady=5)
        
        # الطرف الأيسر: إدخال الفيديوهات والمسار
        left_frame = ttk.Frame(main_paned, padding=5)
        main_paned.add(left_frame, weight=3)
        
        # 1. قسم الفيديوهات
        vid_section = ttk.LabelFrame(left_frame, text=" 1. ملفات الفيديو المدخلة ", padding=10)
        vid_section.pack(fill="both", expand=True, pady=(0, 10))
        
        btn_box = ttk.Frame(vid_section)
        btn_box.pack(fill="x", pady=(0, 5))
        
        add_btn = ttk.Button(btn_box, text="➕ إضافة فيديوهات يدوياً", command=self.browse_videos)
        add_btn.pack(side="left", padx=2)
        clear_btn = ttk.Button(btn_box, text="🗑️ مسح القائمة", command=self.clear_videos)
        clear_btn.pack(side="left", padx=2)
        
        self.vid_listbox = tk.Listbox(vid_section, bg="#111827", fg="#f3f4f6", selectbackground=self.accent_color, borderwidth=0, highlightthickness=0, font=("Segoe UI", 9))
        self.vid_listbox.pack(fill="both", expand=True, side="left")
        
        sb = ttk.Scrollbar(vid_section, orient="vertical", command=self.vid_listbox.yview)
        sb.pack(fill="y", side="right")
        self.vid_listbox.config(yscrollcommand=sb.set)
        
        # 2. قسم مجلد الإخراج
        out_section = ttk.LabelFrame(left_frame, text=" 2. مكان فك التراكات (Output) ", padding=10)
        out_section.pack(fill="x", pady=(0, 5))
        
        out_entry = ttk.Entry(out_section, textvariable=self.output_dir, font=("Segoe UI", 9))
        out_entry.pack(fill="x", side="left", expand=True, padx=(0, 5))
        
        out_btn = ttk.Button(out_section, text="📁 اختيار مجلد", command=self.browse_output)
        out_btn.pack(side="right")
        
        # الطرف الأيمن: تخصيص أسماء التراكات
        right_frame = ttk.Frame(main_paned, padding=5)
        main_paned.add(right_frame, weight=2)
        
        track_section = ttk.LabelFrame(right_frame, text=" 3. قاعدة تسمية التراكات (مثل OBS) ", padding=10)
        track_section.pack(fill="both", expand=True)
        
        tip_lbl = ttk.Label(track_section, text="اكتب لاحقة الاسم لكل تراك تلو الآخر بالترتيب:", style="Sub.TLabel")
        tip_lbl.pack(anchor="w", pady=(0, 8))
        
        # وعاء لعرض خانات التراكات الديناميكية
        self.tracks_scroll_frame = ttk.Frame(track_section)
        self.tracks_scroll_frame.pack(fill="both", expand=True)
        
        self.render_track_inputs()
        
        # زر إضافة خانة تراك جديدة
        add_t_btn = ttk.Button(track_section, text="➕ إضافة تراك إضافي في التسمية", command=self.add_track_field)
        add_t_btn.pack(fill="x", pady=5)
        
        # --- شريط الحالة وزر البدء السفلي ---
        bottom_frame = ttk.Frame(self.root, padding=15)
        bottom_frame.pack(fill="x")
        
        self.progress_bar = ttk.Progressbar(bottom_frame, mode="determinate")
        self.progress_bar.pack(fill="x", pady=(0, 10))
        
        self.status_lbl = ttk.Label(bottom_frame, text="جاهز لبدء العمل...", font=("Segoe UI", 9), style="Sub.TLabel")
        self.status_lbl.pack(side="left")
        
        start_btn = ttk.Button(bottom_frame, text="🎬 ابدأ فك التراكات الآن", style="Accent.TButton", command=self.start_demuxing_thread)
        start_btn.pack(side="right")

    def render_track_inputs(self):
        for widget in self.tracks_scroll_frame.winfo_children():
            widget.destroy()
            
        self.track_entries = []
        for i, name_val in enumerate(self.track_names):
            f = ttk.Frame(self.tracks_scroll_frame, padding=2)
            f.pack(fill="x")
            
            lbl = ttk.Label(f, text=f"تراك فيديو {i+1}: ", width=12)
            lbl.pack(side="left")
            
            ent = ttk.Entry(f)
            ent.insert(0, name_val)
            ent.pack(fill="x", side="left", expand=True, padx=2)
            self.track_entries.append(ent)
            
            if i > 0:
                del_b = ttk.Button(f, text="❌", width=3, command=lambda idx=i: self.remove_track_field(idx))
                del_b.pack(side="right")

    def add_track_field(self):
        self.sync_track_names()
        self.track_names.append(f"Cam_{len(self.track_names)+1}")
        self.render_track_inputs()
        self.save_config()

    def remove_track_field(self, idx):
        self.sync_track_names()
        if 0 <= idx < len(self.track_names):
            self.track_names.pop(idx)
        self.render_track_inputs()
        self.save_config()

    def sync_track_names(self):
        self.track_names = [ent.get().strip() for ent in self.track_entries]

    def browse_videos(self):
        files = filedialog.askopenfilenames(
            title="اختر ملفات الفيديو متعددة التراكات",
            filetypes=[("Video Files", "*.mkv *.mp4 *.avi *.mov"), ("All Files", "*.*")]
        )
        if files:
            for f in files:
                if f not in self.selected_videos:
                    self.selected_videos.append(f)
                    self.vid_listbox.insert(tk.END, os.path.basename(f))

    def clear_videos(self):
        self.selected_videos.clear()
        self.vid_listbox.delete(0, tk.END)

    def browse_output(self):
        dir_path = filedialog.askdirectory(title="اختر مجلد استخراج الفيديوهات")
        if dir_path:
            self.output_dir.set(dir_path)
            self.save_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.track_names = config.get("track_names", ["Original", "Cam_1", "Cam_2"])
                    if "output_dir" in config and os.path.exists(config["output_dir"]):
                        self.output_dir.set(config["output_dir"])
                    return
            except:
                pass
        self.track_names = ["Original", "Cam_1", "Cam_2"]

    def save_config(self):
        self.sync_track_names()
        config = {
            "track_names": self.track_names,
            "output_dir": self.output_dir.get()
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except:
            pass

    def start_demuxing_thread(self):
        self.sync_track_names()
        self.save_config()
        if not self.selected_videos:
            messagebox.showwarning("تنبيه", "من فضلك قم بإضافة ملف فيديو واحد على الأقل أولاً!")
            return
        
        t = threading.Thread(target=self.run_demuxing)
        t.daemon = True
        t.start()

    def run_demuxing(self):
        out_base = self.output_dir.get()
        total_files = len(self.selected_videos)
        
        # إدارة وتحديد مسارات الأدوات لتتوافق مع البناء المدمج (sys._MEIPASS) للويندوز والماك
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        ffmpeg_cmd = os.path.join(base_path, "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")
        ffprobe_cmd = os.path.join(base_path, "ffprobe.exe" if sys.platform == "win32" else "ffprobe")
        
        if not os.path.exists(ffmpeg_cmd): ffmpeg_cmd = "ffmpeg"
        if not os.path.exists(ffprobe_cmd): ffprobe_cmd = "ffprobe"
        
        for idx, video_path in enumerate(self.selected_videos):
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            ext = os.path.splitext(video_path)[1]
            
            self.status_lbl.config(text=f"جاري فحص التراكات لـ: {os.path.basename(video_path)}...")
            self.progress_bar['value'] = (idx / total_files) * 100
            self.root.update_idletasks()
            
            try:
                probe_cmd = [
                    ffprobe_cmd, "-v", "error", "-select_streams", "v",
                    "-show_entries", "stream=index", "-of", "csv=p=0", video_path
                ]
                startupinfo = None
                if sys.platform == "win32":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    
                output = subprocess.check_output(probe_cmd, text=True, startupinfo=startupinfo)
                video_tracks = [line.strip() for line in output.strip().split('\n') if line.strip()]
                num_tracks = len(video_tracks)
            except Exception as e:
                num_tracks = len(self.track_names)
                video_tracks = [str(i) for i in range(num_tracks)]

            if num_tracks == 0:
                continue

            for t_idx, stream_index in enumerate(video_tracks):
                suffix = self.track_names[t_idx] if t_idx < len(self.track_names) else f"Track_{t_idx+1}"
                output_filename = f"{base_name}_{suffix}{ext}"
                full_output_path = os.path.join(out_base, output_filename)
                
                self.status_lbl.config(text=f"جاري استخراج تراك ({suffix}) إلى المجلد المختار...")
                self.root.update_idletasks()
                
                extract_cmd = [
                    ffmpeg_cmd, "-y", "-i", video_path,
                    "-map", f"0:v:{t_idx}", "-map", "0:a?", 
                    "-c", "copy", full_output_path
                ]
                
                try:
                    subprocess.run(extract_cmd, startupinfo=startupinfo, check=True)
                except Exception as e:
                    print(f"خطأ أثناء فك التراك {t_idx}: {e}")

        self.progress_bar['value'] = 100
        self.status_lbl.config(text="🎉 تم فك جميع التراكات وتسميتها بنجاح!")
        messagebox.showinfo("نجاح العملية", "تم الانتهاء من فك وتسمية جميع التراكات بنجاح في المجلد المحدد!")

if __name__ == "__main__":
    root = tk.Tk()
    app = UnDemApp(root)
    root.mainloop()