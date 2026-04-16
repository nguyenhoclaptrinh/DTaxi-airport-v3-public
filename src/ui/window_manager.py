import customtkinter as ctk

class WindowManager:
    """
    Quản lý giao diện người dùng (Logs, Controls) bằng CustomTkinter.
    """
    def __init__(self, on_next, on_prev, on_reset, on_stop, on_scenario_change):
        self.root = ctk.CTk()
        self.root.title("DTaxi - AeroMACS Controller")
        self.root.geometry("400x744")
        
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
            values=["(Đang quét kịch bản...)"],
            command=self.on_scenario_change
        )
        self.scenario_selector.pack(pady=10)

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
        """Thêm một dòng tin nhắn vào log board với màu sắc phân biệt."""
        self.log_box.configure(state="normal")
        
        # Xác định tag màu dựa trên sender
        tag_name = "system"
        if sender in ["ATC", "KSV", "ATC/Ground"]:
            tag_name = "atc"
        elif sender == "SYSTEM":
            tag_name = "system"
        elif sender and sender != "?": # Mặc định là Pilot
            tag_name = "pilot"

        header = f"[{sender}]"
        if target and target != "?":
            header = f"[{sender} -> {target}]"
            
        full_msg = f"{header}: {text}\n\n"
        
        # Chèn văn bản kèm theo tag màu đã định nghĩa
        self.log_box.insert("end", full_msg, tag_name)
        self.log_box.see("end") # Tự động cuộn xuống cuối
        
        self.log_box.configure(state="disabled")

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
        self.log_box.configure(state="normal")
        
        # Tìm dấu xuống dòng kép (ngăn cách các message) từ cuối ngược lên
        # end-1c: trước ký tự newline cuối cùng
        # end-3c: bỏ qua cụm \n\n ở cuối message hiện tại để tìm cụm \n\n của message trước đó
        idx = self.log_box._textbox.search("\n\n", "end-3c", "1.0", backwards=True)
        
        if idx:
            # Nếu tìm thấy, xóa từ sau dấu \n\n đó đến hết
            self.log_box.delete(f"{idx} + 2 chars", "end")
        else:
            # Nếu không tìm thấy (chỉ có 1 log), xóa sạch
            self.log_box.delete("1.0", "end")
            
        self.log_box.configure(state="disabled")

    def clear_log(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    def run_step(self):
        """Cập nhật vòng lặp Tkinter."""
        self.root.update()
