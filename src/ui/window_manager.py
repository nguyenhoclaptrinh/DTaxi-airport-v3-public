import customtkinter as ctk

class WindowManager:
    """
    Quản lý giao diện người dùng (Logs, Controls) bằng CustomTkinter.
    """
    def __init__(
            self, 
            on_next, 
            on_prev, 
            on_reset, 
            on_stop, 
            on_scenario_change, 
            on_auto_play=None,
            on_speed_change=None
    ):
        self.root = ctk.CTk()
        self.root.title("DTaxi - D-TAXI Controller")
        self.root.geometry("400x744")
        
        # Callbacks
        self.on_next = on_next
        self.on_prev = on_prev
        self.on_reset = on_reset
        self.on_stop = on_stop
        self.on_scenario_change = on_scenario_change
        self.on_auto_play = on_auto_play
        self.on_speed_change = on_speed_change
        self.log_entries = []
        
        self._setup_ui()

    def _setup_ui(self):
        # 1. Tiêu đề & Chọn kịch bản
        self.label_title = ctk.CTkLabel(self.root, text="D-TAXI LOG", font=("Roboto", 20, "bold"))
        self.label_title.pack(pady=(20, 5))

        # Thong so RCP/Latency
        self.comm_label = ctk.CTkLabel(self.root, text="Comm: RCP 240 | Latency <= 15ms", font=("Arial", 10, "italic"), text_color="gray")
        self.comm_label.pack(pady=(0, 5))

        self.scenario_selector = ctk.CTkOptionMenu(
            self.root, 
            values=["(Đang quét kịch bản...)"],
            command=self.on_scenario_change
        )
        self.scenario_selector.pack(pady=10)
        
        # Checkbox Auto Play
        self.auto_play_var = ctk.BooleanVar(value=False)
        self.check_auto_play = ctk.CTkCheckBox(
            self.root, 
            text="AUTO PLAY / LOOP MODE", 
            variable=self.auto_play_var,
            command=self._handle_auto_play_toggle
        )
        self.check_auto_play.pack(pady=5)

        # 1.1 Slider Speed
        self.speed_label = ctk.CTkLabel(self.root, text="Simulation Speed: 1.0x", font=("Arial", 12))
        self.speed_label.pack(pady=(10, 0))
        
        self.speed_slider = ctk.CTkSlider(
            self.root, 
            from_=0.5, 
            to=32.0, 
            number_of_steps=63, # 0.5, 1.0, 1.5 ... 32.0
            command=self._handle_speed_slider
        )
        self.speed_slider.set(1.0)
        self.speed_slider.pack(pady=5)

        # 2. Khung Log (Scrollable)
        self.log_box = ctk.CTkTextbox(self.root, width=360, height=400, font=("Consolas", 12))
        self.log_box.pack(padx=20, pady=10)
        self.log_box.configure(state="disabled") # Chỉ đọc

        # Cấu hình màu sắc (Tags) - Tông màu đậm dành cho nền sáng
        # Vì CTkTextbox bọc ngoài tkinter.Text, ta truy cập thông qua _textbox
        self.log_box._textbox.tag_configure("pilot", foreground="#1E8449") # Dark Green
        self.log_box._textbox.tag_configure("atc", foreground="#21618C")   # Dark Blue
        self.log_box._textbox.tag_configure("system", foreground="#566573")# Dark Gray

        # 3. Khung điều khiển (Buttons)
        self.control_frame = ctk.CTkFrame(self.root)
        self.control_frame.pack(pady=20, fill="x", padx=20)

        self.btn_prev = ctk.CTkButton(self.control_frame, text="PREV", width=80, command=self.on_prev)
        self.btn_prev.pack(side="left", padx=10, expand=True)

        self.btn_stop = ctk.CTkButton(self.control_frame, text="PAUSE", width=80, fg_color="#C0392B", hover_color="#922B21", command=self.on_stop)
        self.btn_stop.pack(side="left", padx=10, expand=True)

        self.btn_next = ctk.CTkButton(self.control_frame, text="NEXT", width=120, fg_color="green", hover_color="darkgreen", command=self.on_next)
        self.btn_next.pack(side="left", padx=10, expand=True)

        self.btn_reset = ctk.CTkButton(self.root, text="RESET SCENARIO", fg_color="gray", command=self.on_reset)
        self.btn_reset.pack(pady=10)

        # 4. Status Bar
        self.status_label = ctk.CTkLabel(self.root, text="Ready", font=("Roboto", 10))
        self.status_label.pack(side="bottom", pady=5)

    def _get_log_tag(self, sender):
        """Xac dinh tag mau theo nguoi gui."""
        if sender in ["ATC", "KSV", "ATC/Ground"]:
            return "atc"
        if sender == "SYSTEM":
            return "system"
        if sender and sender != "?":
            return "pilot"
        return "system"

    def _append_log_entry(self, entry):
        """Chen mot log entry da co vao textbox."""
        self.log_box.configure(state="normal")
        
        sender = entry.get("sender")
        target = entry.get("target")
        text = entry.get("text", "")
        tag_name = self._get_log_tag(sender)

        header = f"[{sender}]"
        if target and target != "?":
            header = f"[{sender} -> {target}]"
            
        full_msg = f"{header}: {text}\n\n"
        
        # Chèn văn bản kèm theo tag màu đã định nghĩa
        self.log_box.insert("end", full_msg, tag_name)
        self.log_box.see("end") # Tự động cuộn xuống cuối
        
        self.log_box.configure(state="disabled")

    def _render_log_entries(self):
        """Ve lai textbox tu danh sach log_entries."""
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")
        for entry in self.log_entries:
            self._append_log_entry(entry)

    def add_log(self, sender, text, target=None):
        """Thêm một dòng tin nhắn vào log board với màu sắc phân biệt."""
        entry = {"sender": sender, "text": text, "target": target}
        self.log_entries.append(entry)
        self._append_log_entry(entry)

    def set_stop_state(self, paused: bool):
        """Cap nhat trang thai nut Pause/Resume."""
        if paused:
            self.btn_stop.configure(text="RESUME", fg_color="#2980B9", hover_color="#2471A3")
        else:
            self.btn_stop.configure(text="PAUSE", fg_color="#C0392B", hover_color="#922B21")

    def set_status(self, text):
        self.status_label.configure(text=text)

    def set_scenario_list(self, files: list[str], current: str = None):
        """Cập nhật danh sách kịch bản vào Dropdown."""
        if not files:
            self.scenario_selector.configure(values=["(Không tìm thấy kịch bản)"], state="disabled")
            return
            
        self.scenario_selector.configure(values=files, state="normal")
        if current and current in files:
            self.scenario_selector.set(current)
        else:
            self.scenario_selector.set(files[0])

    def remove_last_log(self):
        """Xóa block log cuối cùng khi người dùng nhấn PREV."""
        if self.log_entries:
            self.log_entries.pop()
        self._render_log_entries()

    def clear_log(self):
        self.log_entries = []
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    def get_log_entries(self):
        """Tra ve ban copy log de snapshot PREV."""
        return [dict(entry) for entry in self.log_entries]

    def set_log_entries(self, entries):
        """Khoi phuc log tu snapshot."""
        self.log_entries = [dict(entry) for entry in entries]
        self._render_log_entries()

    def _handle_auto_play_toggle(self):
        """Callback khi toggle checkbox AUTO PLAY."""
        if self.on_auto_play:
            self.on_auto_play(self.auto_play_var.get())

    def _handle_speed_slider(self, value):
        """Callback khi kéo thanh trượt tốc độ."""
        text = f"Simulation Speed: {value:.1f}x"
        self.speed_label.configure(text=text)
        if self.on_speed_change:
            self.on_speed_change(value)

    def run_step(self):
        """Cập nhật vòng lặp Tkinter."""
        self.root.update()
