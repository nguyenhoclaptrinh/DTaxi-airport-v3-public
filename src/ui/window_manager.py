import customtkinter as ctk

class WindowManager:
    """
    Quản lý giao diện người dùng (Logs, Controls) bằng CustomTkinter.
    """
    def __init__(self, on_next, on_prev, on_reset, on_stop, on_scenario_change):
        self.root = ctk.CTk()
        self.root.title("DTaxi - AeroMACS Controller")
        self.root.geometry("400x750")
        
        # Callbacks
        self.on_next = on_next
        self.on_prev = on_prev
        self.on_reset = on_reset
        self.on_stop = on_stop
        self.on_scenario_change = on_scenario_change
        
        self._setup_ui()

    def _setup_ui(self):
        # 1. Tiêu đề & Chọn kịch bản
        self.label_title = ctk.CTkLabel(self.root, text="AeroMACS LOG", font=("Roboto", 20, "bold"))
        self.label_title.pack(pady=(20, 5))

        self.scenario_selector = ctk.CTkOptionMenu(
            self.root, 
            values=["Departure Scenario", "Arrival Scenario", "Multi-aircraft Scenario"],
            command=self.on_scenario_change
        )
        self.scenario_selector.pack(pady=10)

        # 2. Khung Log (Scrollable)
        self.log_box = ctk.CTkTextbox(self.root, width=360, height=400, font=("Consolas", 12))
        self.log_box.pack(padx=20, pady=10)
        self.log_box.configure(state="disabled") # Chỉ đọc

        # 3. Khung điều khiển (Buttons)
        self.control_frame = ctk.CTkFrame(self.root)
        self.control_frame.pack(pady=20, fill="x", padx=20)

        self.btn_prev = ctk.CTkButton(self.control_frame, text="PREV", width=80, command=self.on_prev)
        self.btn_prev.pack(side="left", padx=10, expand=True)

        self.btn_stop = ctk.CTkButton(self.control_frame, text="STOP", width=80, fg_color="#C0392B", hover_color="#922B21", command=self.on_stop)
        self.btn_stop.pack(side="left", padx=10, expand=True)

        self.btn_next = ctk.CTkButton(self.control_frame, text="NEXT", width=120, fg_color="green", hover_color="darkgreen", command=self.on_next)
        self.btn_next.pack(side="left", padx=10, expand=True)

        self.btn_reset = ctk.CTkButton(self.root, text="RESET SCENARIO", fg_color="gray", command=self.on_reset)
        self.btn_reset.pack(pady=10)

        # 4. Status Bar
        self.status_label = ctk.CTkLabel(self.root, text="Ready", font=("Roboto", 10))
        self.status_label.pack(side="bottom", pady=5)

    def add_log(self, sender, text, target=None):
        """Thêm một dòng tin nhắn vào log board."""
        self.log_box.configure(state="normal")
        
        tag = f"[{sender}]"
        if target:
            tag = f"[{sender} -> {target}]"
            
        full_msg = f"{tag}: {text}\n\n"
        self.log_box.insert("end", full_msg)
        self.log_box.see("end") # Auto scroll to bottom
        
        self.log_box.configure(state="disabled")

    def set_status(self, text):
        self.status_label.configure(text=text)

    def clear_log(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    def run_step(self):
        """Cập nhật vòng lặp Tkinter."""
        self.root.update()
