#projectcode

import os
import json
import hashlib
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import tkinter.font as tkfont
from datetime import datetime, timedelta
import calendar

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Study Planner Login")
        self.root.geometry("320x220")
        self.root.configure(bg="#f0f0f0")
        self.users_file = "users.json"
      

        self.users = self.load_users()
        self.create_login_widgets()

    def create_login_widgets(self):
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(expand=True, padx=20, pady=20)

        tk.Label(frame, text="Username:", bg="#f0f0f0").grid(row=0, column=0, pady=5, sticky="w")
        self.username = tk.Entry(frame)
        self.username.grid(row=0, column=1, pady=5)

        tk.Label(frame, text="Password:", bg="#f0f0f0").grid(row=1, column=0, pady=5, sticky="w")
        self.password = tk.Entry(frame, show="*")
        self.password.grid(row=1, column=1, pady=5)

        login_btn = tk.Button(frame, text="Login", command=self.login, bg="#4a90e2", fg="white")
        login_btn.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

        register_btn = tk.Button(frame, text="Register", command=self.show_register, bg="#4caf50", fg="white")
        register_btn.grid(row=3, column=0, columnspan=2, sticky="ew")

    def load_users(self):
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                  return {}
        return {}

    def save_users(self):
        try:
            with open(self.users_file, "w", encoding="utf-8") as f:
                json.dump(self.users, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save users: {e}")

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self):
        username = self.username.get().strip()
        password_hash = self.hash_password(self.password.get())

        if not username:
            messagebox.showwarning("Login", "Please enter a username.")
            return

        if username in self.users and self.users[username] == password_hash:
            messagebox.showinfo("Login", f"Welcome, {username}!")
            self.root.withdraw()
            app_root = tk.Toplevel(self.root)
            StudyPlanner(app_root, username, self.root)
        else:
            messagebox.showerror("Login", "Invalid username or password.")

    def show_register(self):
        register_window = tk.Toplevel(self.root)
        register_window.title("Register")
        register_window.geometry("320x200")
        register_window.configure(bg="#f0f0f0")

        frame = tk.Frame(register_window, bg="#f0f0f0")
        frame.pack(expand=True, padx=20, pady=20)

        tk.Label(frame, text="Username:", bg="#f0f0f0").grid(row=0, column=0, pady=5, sticky="w")
        new_username = tk.Entry(frame)
        new_username.grid(row=0, column=1, pady=5)

        tk.Label(frame, text="Password:", bg="#f0f0f0").grid(row=1, column=0, pady=5, sticky="w")
        new_password = tk.Entry(frame, show="*")
        new_password.grid(row=1, column=1, pady=5)

        def register():
            u = new_username.get().strip()
            p = new_password.get()
            if not u or not p:
                messagebox.showwarning("Register", "Please enter username and password.")
                return
            if len(p) < 6:
                messagebox.showwarning("Register", "Password must be atleast 6 characters Long!")
                return
            if len(p) > 16:
                messagebox.showwarning("Register", "Password must not exceed 16 characters!")
            if u in self.users:
                messagebox.showerror("Register", "Username already exists.")
                return
            self.users[u] = self.hash_password(p)
            self.save_users()
            messagebox.showinfo("Register", "Registration successful!")
            register_window.destroy()

        register_btn = tk.Button(frame, text="Register", command=register, bg="#4caf50", fg="white")
        register_btn.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")


class StudyPlanner:
    def __init__(self, root, username, login_root):
        self.root = root
        self.username = username
        self.login_root = login_root
        self.root.title(f"Study Planner - {self.username}")
        self.root.geometry("1200x800")

        # Data storage
        self.tasks = []
        self.filtered_task_indices = []
        self.search_var = tk.StringVar()
        self.subjects = ("GEN 001", "GEN 002", "MAT 152", "ITE 260", "ITE 366")
        self.themes ={
            "Default": {"bg": "#f0f0f0", "accent": "#4a90e2", "text": "#333333"},
            "Dark": {"bg": "#2d2d2d", "accent": "#64b5f6", "text": "#b6b6b6"},
            "Red": {"bg": "#f37676", "accent": "#aa1212", "text": "#830e18"},
            "Green": {"bg": "#e8f5e8", "accent": "#4caf50", "text": "#2e7d32"},
            "Yellow": {"bg": "#faf2d0", "accent": "#f7e973", "text": "#838b07"},
            "Blue": {"bg": "#cedfff", "accent": "#2ba2e7", "text": "#1361a1"},
            "Purple": {"bg": "#f3e5f5", "accent": "#9c27b0", "text": "#4a148c"},
            "Pink": {"bg": "#ffc4f0", "accent": "#ff75c3", "text": "#8c146c"},
            

        }
        self.current_theme = "Default"
        self.sticky_notes = []
        self.data_file = f"data_{self.username}.json"
# Daily motivational quotes
        self.quotes = [
            ("The secret of getting ahead is getting started.", "Mark Twain"),
            ("Don't watch the clock; do what it does. Keep going.", "Sam Levenson"),
            ("Success is not final, failure is not fatal: it is the courage to continue that counts.", "Winston Churchill"),
            ("It always seems impossible until it's done.", "Nelson Mandela"),
            ("Start where you are. Use what you have. Do what you can.", "Arthur Ashe"),
            ("The future depends on what you do today.", "Mahatma Gandhi"),
            ("Do something today that your future self will thank you for.", "Unknown"),
            ("Small progress is still progress.", "Unknown"),
            ("One step at a time is good walking.", "Chinese Proverb"),
            ("You don't have to be great to start, but you have to start to be great.", "Zig Ziglar")
        ]
        self.quote_index = None

        # Load data
        self.load_data()

        # Store widget references for theme updates
        self.themed_widgets = []

        # Create main interface
        self.create_widgets()
        self.update_calendar()
        self.check_reminders()

        # Apply theme after widgets are created
        self.apply_theme()

        # Save data on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.themed_widgets.append(self.main_frame)

        self.title_label = tk.Label(self.main_frame, text=f"Study Planner: {self.username}",
                                    font=("Arial", 20, "bold"))
        self.title_label.pack(pady=(0, 20))
        self.themed_widgets.append(self.title_label)

        top_frame = tk.Frame(self.main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        self.themed_widgets.append(top_frame)

        self.create_control_buttons(top_frame)

        content_frame = tk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        self.themed_widgets.append(content_frame)

        left_frame = tk.Frame(content_frame, width=400)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        left_frame.pack_propagate(False)
        self.themed_widgets.append(left_frame)

        self.create_task_panel(left_frame)

        right_frame = tk.Frame(content_frame, width=400)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        right_frame.pack_propagate(False)
        self.themed_widgets.append(right_frame)

        self.create_calendar_panel(right_frame)

    def create_control_buttons(self, parent):
        theme_label = tk.Label(parent, text="Theme:")
        theme_label.pack(side=tk.LEFT, padx=(0, 5))
        self.themed_widgets.append(theme_label)

        self.theme_var = tk.StringVar(value=self.current_theme)
        theme_combo = ttk.Combobox(parent, textvariable=self.theme_var, values=list(self.themes.keys()),
                                  state="readonly", width=10)
        theme_combo.pack(side=tk.LEFT, padx=(0, 20))
        theme_combo.bind('<<ComboboxSelected>>', self.change_theme)

        self.subjects_btn = tk.Button(parent, text="Manage Subjects", command=self.manage_subjects,
                                     fg="white", font=("Arial", 10, "bold"))
        self.subjects_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.themed_widgets.append(self.subjects_btn)

        self.reminders_btn = tk.Button(parent, text="View Reminders", command=self.view_reminders,
                                      fg="white", font=("Arial", 10, "bold"))
        self.reminders_btn.pack(side=tk.LEFT)
        self.themed_widgets.append(self.reminders_btn)

    def create_task_panel(self, parent):
        self.task_frame = tk.LabelFrame(parent, text="Task Management", font=("Arial", 14, "bold"))
        self.task_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.themed_widgets.append(self.task_frame)

        form_frame = tk.Frame(self.task_frame)
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        self.themed_widgets.append(form_frame)

        labels_data = [
            ("Type:", 0), ("Subject:", 1), ("Title:", 2),
            ("Date (YYYY-MM-DD):", 3), ("Time (HH:MM):", 4), ("Priority:", 5)
        ]
        
        self.form_labels = []
        for text, row in labels_data:
            lbl = tk.Label(form_frame, text=text)
            lbl.grid(row=row, column=0, sticky="w", pady=2)
            self.form_labels.append(lbl)
            self.themed_widgets.append(lbl)
#task type
        self.task_type_var = tk.StringVar(value="Assignment")
        task_type_combo = ttk.Combobox(form_frame, textvariable=self.task_type_var,
                                      values=["Assignment", "Exam", "Class", "Study Session"], width=15)
        task_type_combo.grid(row=0, column=1, pady=2, sticky="ew")
#subject
        self.subject_var = tk.StringVar()
        self.subject_combo = ttk.Combobox(form_frame, textvariable=self.subject_var,
                                         values=self.subjects, width=15)
        self.subject_combo.grid(row=1, column=1, pady=2, sticky="ew")
#title
        self.title_entry = tk.Entry(form_frame, width=18)
        self.title_entry.grid(row=2, column=1, pady=2, sticky="ew")
#time
        self.date_entry = tk.Entry(form_frame, width=18)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=3, column=1, pady=2, sticky="ew")

        self.time_entry = tk.Entry(form_frame, width=18)
        self.time_entry.insert(0, "09:00")
        self.time_entry.grid(row=4, column=1, pady=2, sticky="ew")
        # AM / PM selector (ante meridiem / post meridiem)
        self.am_pm_var = tk.StringVar(value="AM")
        ampm_combo = ttk.Combobox(form_frame, textvariable=self.am_pm_var,
                                  values=["AM", "PM"], width=5, state="readonly")
        ampm_combo.grid(row=4, column=2, padx=(5,0), pady=2)
#priority
        self.priority_var = tk.StringVar(value="Medium")
        priority_combo = ttk.Combobox(form_frame, textvariable=self.priority_var,
                                     values=["Low", "Medium", "High"], width=15)
        priority_combo.grid(row=5, column=1, pady=2, sticky="ew")
        
        form_frame.columnconfigure(1, weight=1)

        btn_frame = tk.Frame(self.task_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        self.themed_widgets.append(btn_frame)

        self.add_btn = tk.Button(btn_frame, text="Add Task", command=self.add_task,
                                fg="white", font=("Arial", 10, "bold"))
        self.add_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.themed_widgets.append(self.add_btn)
        self.edit_btn = tk.Button(btn_frame, text="Edit Selected", command=self.edit_task,
                                 bg="#ff9800", fg="white", font=("Arial", 10, "bold"))
        self.edit_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.delete_btn = tk.Button(btn_frame, text="Delete Selected", command=self.delete_task,
                                   bg="#f44336", fg="white", font=("Arial", 10, "bold"))
        self.delete_btn.pack(side=tk.LEFT)
        
#search bar
        self.search_entry = tk.Entry(btn_frame, textvariable=self.search_var, text="Search", width=35)
        self.search_entry.pack(side=tk.RIGHT, padx=(5,0))

        #Bind live filtering
        self.search_var.trace_add("write", lambda *args: self.update_task_list())
        self.search_entry.bind("<KeyRelease>", lambda e: self.update_task_list())
        
#frame
        list_frame = tk.Frame(self.task_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.themed_widgets.append(list_frame)
        
        # Use a Treeview with columns to organize tasks into Priority, Date, Time, Type, zSubject, Title
        self.task_tree = ttk.Treeview(list_frame, columns=("Priority", "Date", "Time", "Type", "Subject", "Title"),
                                      show="headings", selectmode="browse", height=15)
        self.task_tree.heading("Priority", text="Priority")
        self.task_tree.heading("Date", text="Date")
        self.task_tree.heading("Time", text="Time")
        self.task_tree.heading("Type", text="Type")
        self.task_tree.heading("Subject", text="Subject")
        self.task_tree.heading("Title", text="Title")
        self.task_tree.column("Priority", width=75, anchor="center")
        self.task_tree.column("Date", width=90, anchor="center")
        self.task_tree.column("Time", width=90, anchor="center")
        self.task_tree.column("Type", width=120, anchor="center")
        self.task_tree.column("Subject", width=120, anchor="center")
        self.task_tree.column("Title", width=260, anchor="w")
        # Create a font for completed tasks with strikethrough
        # (Removed automatic "done" styling and detection — tasks are shown without auto-complete styling)
      
        # Single scrollbar for the Treeview
        tree_scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=tree_scrollbar.set)
        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind selection/double-click events
        self.task_tree.bind("<<TreeviewSelect>>", lambda e: None)  # placeholder if needed later
        self.task_tree.bind("<Double-1>", lambda e: self.edit_task())
         
        self.update_task_list()
        
# calendar
        self.task_tree.bind("<Double-1>", lambda e: self.edit_task())
         
        self.update_task_list()

    def create_calendar_panel(self, parent):
        # Top container to hold calendar (left) and daily quote (right)
        top_container = tk.Frame(parent)
        top_container.pack(fill=tk.X, pady=(0, 10))
        self.themed_widgets.append(top_container)

        # Calendar frame (left)
        self.cal_frame = tk.LabelFrame(top_container, text="Calendar View", font=("Arial", 14, "bold"))
        self.cal_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.themed_widgets.append(self.cal_frame)

        nav_frame = tk.Frame(self.cal_frame)
        nav_frame.pack(fill=tk.X, padx=10, pady=5)
        self.themed_widgets.append(nav_frame)

        self.current_date = datetime.now()

        self.prev_btn = tk.Button(nav_frame, text="<<", command=self.prev_month, fg="white")
        self.prev_btn.pack(side=tk.LEFT)
        self.themed_widgets.append(self.prev_btn)

        self.month_label = tk.Label(nav_frame, text="", font=("Arial", 12, "bold"))
        self.month_label.pack(side=tk.LEFT, expand=True)
        self.themed_widgets.append(self.month_label)

        self.next_btn = tk.Button(nav_frame, text=">>", command=self.next_month, fg="white")
        self.next_btn.pack(side=tk.RIGHT)
        self.themed_widgets.append(self.next_btn)

        self.calendar_frame = tk.Frame(self.cal_frame)
        self.calendar_frame.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)
        self.themed_widgets.append(self.calendar_frame)

        # Quotes frame (right) - shows a daily motivational quote
        quotes_frame = tk.LabelFrame(top_container, text="Daily Quote", font=("Arial", 14, "bold"))
        quotes_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10,0), pady=0)
        self.themed_widgets.append(quotes_frame)

        self.quote_text_var = tk.StringVar(value="")
        self.quote_author_var = tk.StringVar(value="")

        # Ensure the quote labels use theme colors so they're visible
        theme = self.themes.get(self.current_theme, {"bg": "#f0f0f0", "text": "#333333"})
        self.quote_label = tk.Label(quotes_frame, textvariable=self.quote_text_var,
                        font=("Arial", 12), wraplength=320, justify="center",
                        bg=theme["bg"], fg=theme["text"])
        self.quote_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10,4))
        self.themed_widgets.append(self.quote_label)

        self.quote_author_label = tk.Label(quotes_frame, textvariable=self.quote_author_var,
                          font=("Arial", 10, "italic"), justify="center",
                          bg=theme["bg"], fg=theme["text"])
        self.quote_author_label.pack(padx=10, pady=(0,10))
        self.themed_widgets.append(self.quote_author_label)

# Optional: allow user to view a different quote for the day
        btns = tk.Frame(quotes_frame)
        btns.pack(pady=(0,10))
        self.themed_widgets.append(btns)
        self.new_quote_btn = tk.Button(btns, text="Another Quote", command=self._cycle_quote)
        self.new_quote_btn.pack(side=tk.LEFT, padx=5)
        self.themed_widgets.append(self.new_quote_btn)

# Quick notes (below calendar area)
        notes_frame = tk.LabelFrame(parent, text="Quick Notes", font=("Arial", 14, "bold"))
        notes_frame.pack(fill=tk.BOTH, expand=True)
        self.themed_widgets.append(notes_frame)

        note_input_frame = tk.Frame(notes_frame)
        note_input_frame.pack(fill=tk.X, padx=10, pady=5)
        self.themed_widgets.append(note_input_frame)

        self.note_entry = tk.Entry(note_input_frame, font=("Arial", 10))
        self.note_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.note_entry.bind('<Return>', lambda e: self.add_note())

        self.add_note_btn = tk.Button(note_input_frame, text="Add", command=self.add_note, fg="white")
        self.add_note_btn.pack(side=tk.RIGHT, padx=(5, 0))
        self.themed_widgets.append(self.add_note_btn)

        note_btn_frame = tk.Frame(notes_frame)
        note_btn_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        self.themed_widgets.append(note_btn_frame)

        self.delete_note_btn = tk.Button(note_btn_frame, text="Delete Selected", command=self.delete_note, 
                                        bg="#f44336", fg="white", font=("Arial", 9))
        self.delete_note_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_notes_btn = tk.Button(note_btn_frame, text="Clear All", command=self.clear_all_notes, 
                                        bg="#ff5722", fg="white", font=("Arial", 9))
        self.clear_notes_btn.pack(side=tk.LEFT)
        self.themed_widgets.append(self.clear_notes_btn)

        notes_display_frame = tk.Frame(notes_frame)
        notes_display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.themed_widgets.append(notes_display_frame)

        # Use a Treeview for notes with columns: Date, Time, Note
        self.notes_tree = ttk.Treeview(notes_display_frame, columns=("Date", "Time", "Note"),
                           show="headings", height=6)
        self.notes_tree.heading("Date", text="Date")
        self.notes_tree.heading("Time", text="Time")
        self.notes_tree.heading("Note", text="Note")
        self.notes_tree.column("Date", width=100, anchor="center")
        self.notes_tree.column("Time", width=80, anchor="center")
        self.notes_tree.column("Note", width=320, anchor="w")

        notes_scrollbar = tk.Scrollbar(notes_display_frame, orient=tk.VERTICAL,
                          command=self.notes_tree.yview)
        self.notes_tree.configure(yscrollcommand=notes_scrollbar.set)
        self.notes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        notes_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.themed_widgets.append(self.notes_tree)

        # set initial quote
        self.update_daily_quote()

    def update_calendar(self):
        # Update month label
        self.month_label.config(text=self.current_date.strftime("%B %Y"))
        
        # Clear existing calendar
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        
        # Get calendar for current month
        cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)
        
        # Day headers
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        theme = self.themes[self.current_theme]
        
        for col, day in enumerate(days):
            lbl = tk.Label(self.calendar_frame, text=day, font=("Arial", 10, "bold"),
                          bg=theme["bg"], fg=theme["accent"], width=5)
            lbl.grid(row=0, column=col, padx=2, pady=2)
        
        # Calendar dates
        today = datetime.now()
        for row_num, week in enumerate(cal, start=1):
            for col_num, day in enumerate(week):
                if day == 0:
                    # Empty cell
                    lbl = tk.Label(self.calendar_frame, text="", width=5, height=2,
                                  bg=theme["bg"])
                else:
                    # Check if this is today
                    is_today = (day == today.day and 
                               self.current_date.month == today.month and 
                               self.current_date.year == today.year)
                    
                    # Check if there are tasks on this day
                    date_str = f"{self.current_date.year}-{self.current_date.month:02d}-{day:02d}"
                    has_task = any(t.get("datetime", "").startswith(date_str) for t in self.tasks)
                    
                    bg_color = theme["accent"] if is_today else theme["bg"]
                    fg_color = "white" if is_today else theme["text"]
                    
                    font_weight = "bold" if (is_today or has_task) else "normal"
                    
                    lbl = tk.Label(self.calendar_frame, text=str(day), 
                                  font=("Arial", 9, font_weight),
                                  bg=bg_color, fg=fg_color, width=5, height=2,
                                  relief="solid" if has_task else "flat",
                                  borderwidth=1 if has_task else 0)
                
                lbl.grid(row=row_num, column=col_num, padx=1, pady=1, sticky="nsew")

    def add_task(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("Add Task", "Please enter a title.")
            return
        try:
            date_text = self.date_entry.get().strip()
            time_text = self.time_entry.get().strip()
            # Expect time_text as HH:MM in 12-hour format plus AM/PM selector
            parts = time_text.split(":")
            if len(parts) != 2:
                raise ValueError("Invalid time")
            hour = int(parts[0])
            minute = int(parts[1])
            ampm = (self.am_pm_var.get() or "AM").upper()
            # Convert 12-hour -> 24-hour
            if ampm == "AM" and hour == 12:
                hour = 0
            elif ampm == "PM" and hour < 12:
                hour += 12
            dt = datetime.strptime(f"{date_text} {hour:02d}:{minute:02d}", "%Y-%m-%d %H:%M")
        except Exception:
            messagebox.showwarning("Add Task", "Invalid date/time format.")
            return
        task = {
            "type": self.task_type_var.get(),
            "subject": self.subject_var.get(),
            "title": title,
            "datetime": dt.isoformat(),
            "priority": self.priority_var.get()
        }
        self.tasks.append(task)
        self.save_data()
        self.update_task_list()
        self.update_calendar()
        self.clear_task_form()

    def edit_task(self):
        sel = self.task_tree.selection()
        if not sel:
            messagebox.showwarning("Edit Task", "Select a task to edit.")
            return
        # iid is set to the actual tasks index in update_task_list
        actual_idx = int(sel[0])
        task = self.tasks[actual_idx]
        new_title = simpledialog.askstring("Edit Task", "Title:", initialvalue=task["title"], parent=self.root)
        
        if new_title:
            task["title"] = new_title
            self.save_data()
            self.update_task_list()

    def delete_task(self):
        sel = self.task_listbox.curselection()
        if not sel:
            messagebox.showwarning("Delete Task", "Select a task to delete.")
            return
        idx = sel[0]
        actual_idx = self.filtered_task_indices[idx] if self.filtered_task_indices else idx
        if messagebox.askyesno("Delete Task", "Delete selected task?"):
            self.tasks.pop(actual_idx)
            self.save_data()
            self.update_task_list()
            self.update_calendar()

    def clear_task_form(self):
        self.title_entry.delete(0, tk.END)
        self.subject_var.set("")
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, "09:00")
        self.priority_var.set("Medium")
        if hasattr(self, "am_pm_var"):
            self.am_pm_var.set("AM")

    def _format_time_entry(self, event=None):
        """Format time entry to auto-insert ':' after two digits (HH:MM)."""
        try:
            s = self.time_entry.get()
        except Exception:
            return
        # Keep only digits
        digits = ''.join(ch for ch in s if ch.isdigit())
        if not digits:
            new = ""
        elif len(digits) <= 2:
            new = digits
        else:
            new = digits[:2] + ":" + digits[2:4]
        # limit to 5 characters (HH:MM)
        new = new[:5]
        if new != s:
            # update entry without triggering recursion (we're on KeyRelease/FocusOut)
            self.time_entry.delete(0, tk.END)
            self.time_entry.insert(0, new)
            # place cursor at end for simplicity
            try:
                self.time_entry.icursor(len(new))
            except Exception:
                pass

    def update_task_list(self):
        query = self.search_var.get().strip().lower() if hasattr(self, "search_var") else ""
# Prepare sorted indices by datetime so tasks are shown in chronological order
        sorted_indices = sorted(range(len(self.tasks)),
                                key=lambda i: self.tasks[i].get("datetime", ""))

# Clear both displays
        # Clear treeview and reset filtered indices
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        self.filtered_task_indices = []

        for i in sorted_indices:
            t = self.tasks[i]
            title = t.get("title", "")
            subject = t.get("subject", "")
            ttype = t.get("type", "")
            priority = t.get("priority", "")
            dt = t.get("datetime", "")

            # Format date/time for display
            date_only = ""
            time_only = ""
            dt_str = ""
            if dt:
                # dt is expected to be ISO format
                try:
                    if "T" in dt:
                        date_only, time_part = dt.split("T", 1)
                    else:
                        date_only = dt.split(" ")[0]
                        time_part = dt.split(" ")[1] if len(dt.split()) > 1 else ""
                    time_only = time_part[:5]
                    dt_str = f"{date_only} {time_only}".strip()
                except Exception:
                    dt_str = dt[:16].replace("T", " ")

            # Build searchable text (title, subject, type, priority, date)
            hay = f"{title} {subject} {ttype} {priority} {date_only} {dt_str}".lower()

            if not query or query in hay:
                # Insert into the treeview. Use the real task index as iid so selection maps back.
                values = (priority, date_only, time_only, ttype, subject, title)
                iid = str(i)
                try:
                    self.task_tree.insert("", tk.END, iid=iid, values=values)
                except Exception:
                    self.task_tree.insert("", tk.END, iid=iid, values=values)
                self.filtered_task_indices.append(i)

    def prev_month(self):
        first = self.current_date.replace(day=1)
        prev_month = first - timedelta(days=1)
        self.current_date = prev_month.replace(day=1)
        self.update_calendar()

    def next_month(self):
        year = self.current_date.year + (1 if self.current_date.month == 12 else 0)
        month = (self.current_date.month % 12) + 1
        self.current_date = self.current_date.replace(year=year, month=month, day=1)
        self.update_calendar()



    def add_note(self):
        text = self.note_entry.get().strip()
        if not text:
            return
        # Use 12-hour clock with AM/PM for clarity in the notes view
        timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        self.sticky_notes.append({"text": text, "time": timestamp})
        self.note_entry.delete(0, tk.END)
        self.save_data()
        self.update_notes_display()

    def delete_note(self):
        sel = self.notes_tree.selection()
        if not sel:
            messagebox.showwarning("Delete Note", "Please select a note to delete.")
            return
        # We store the sticky_notes index as the iid when populating
        try:
            actual_idx = int(sel[0])
        except Exception:
            messagebox.showwarning("Delete Note", "Could not determine selected note.")
            return
        if messagebox.askyesno("Delete Note", "Delete selected note?"):
            try:
                self.sticky_notes.pop(actual_idx)
            except Exception:
                messagebox.showerror("Delete Note", "Failed to delete the selected note.")
                return
            self.save_data()
            self.update_notes_display()

    def  clear_all_notes(self):
        if not self.sticky_notes:
            messagebox.showinfo("Clear Notes", "No notes to clear.")
            return
        if messagebox.askyesno("Clear All Notes", "Are you sure you want to delete all notes?"):
            self.sticky_notes.clear()
            self.save_data()
            self.update_notes_display()

    def update_notes_display(self):
        # Repopulate the notes tree. Use the sticky_notes index as iid so selection maps to data.
        for item in self.notes_tree.get_children():
            self.notes_tree.delete(item)
        for idx, n in enumerate(self.sticky_notes):
            ts = n.get('time', '')
            date_part = ''
            time_part = ''
            if ts:
                # Support both old 24-hour format ("YYYY-MM-DD HH:MM") and new
                # 12-hour format ("YYYY-MM-DD HH:MM AM/PM").
                parts = ts.split(' ')
                date_part = parts[0] if len(parts) > 0 else ''
                if len(parts) >= 3:
                    # e.g. ['2025-11-20', '09:15', 'AM'] -> join time and AM/PM
                    time_part = parts[1] + ' ' + parts[2]
                elif len(parts) == 2:
                    # e.g. ['2025-11-20', '09:15']
                    time_part = parts[1]
                else:
                    time_part = ''
            note_text = n.get('text', '')
            # Insert with iid == index so we can map selection back to sticky_notes
            try:
                self.notes_tree.insert('', tk.END, iid=str(idx), values=(date_part, time_part, note_text))
            except Exception:
                # Fallback without iid
                self.notes_tree.insert('', tk.END, values=(date_part, time_part, note_text))

    def manage_subjects(self):
        new = simpledialog.askstring("Manage Subjects", "Add subject:", parent=self.root)
        if new:
            self.subjects.append(new)
            # Update the subject combobox values
            self.subject_combo['values'] = self.subjects
            self.save_data()
            messagebox.showinfo("Subjects", f"Added subject: {new}")

    def view_reminders(self):
        upcoming = []
        now = datetime.now()
        for t in self.tasks:
            try:
                dt = datetime.fromisoformat(t["datetime"])
                if dt >= now:
                    upcoming.append(f"{dt.strftime('%Y-%m-%d %H:%M')} - {t['title']}")
            except Exception:
                continue
        msg = "\n".join(upcoming[:20]) if upcoming else "No upcoming reminders."
        messagebox.showinfo("Reminders", msg)

    def get_daily_quote(self, seed_date=None):
        """Return (quote, author). Deterministic by date so user sees a 'daily' quote."""
        if seed_date is None:
            seed_date = datetime.now().date()
        idx = seed_date.toordinal() % len(self.quotes)
        return self.quotes[idx]

    def update_daily_quote(self, force_new=False):
        """Set displayed quote. If force_new True, cycle to next quote."""
        today = datetime.now().date()
        if force_new:
            # cycle index or initialize
            if self.quote_index is None:
                self.quote_index = today.toordinal() % len(self.quotes)
            self.quote_index = (self.quote_index + 1) % len(self.quotes)
            q, a = self.quotes[self.quote_index]
        else:
            q, a = self.get_daily_quote(today)
            self.quote_index = today.toordinal() % len(self.quotes)
        # Fallback if quotes list is empty or contains empty values
        if not q:
            q = "No quote available."
        # Update author only if available
        if a:
            self.quote_author_var.set(f"— {a}")
        else:
            self.quote_author_var.set("")
        # Use standard double quotes for wide compatibility
        self.quote_text_var.set(f'"{q}"')

    def _cycle_quote(self):
        """Handler for 'Another Quote' button to show a different quote."""
        self.update_daily_quote(force_new=True)

    def check_reminders(self):
        now = datetime.now()
        for t in self.tasks:
            try:
                dt = datetime.fromisoformat(t["datetime"])
                if 0 <= (dt - now).total_seconds() <= 600:
                    messagebox.showinfo("Reminder", f"Upcoming: {t['title']} at {dt.strftime('%Y-%m-%d %H:%M')}")
            except Exception:
                continue
        self.root.after(60000, self.check_reminders)

    def change_theme(self, event=None):
        chosen = self.theme_var.get()
        if chosen in self.themes:
            self.current_theme = chosen
            self.apply_theme()
            self.save_data()

    def apply_theme(self):
        theme = self.themes[self.current_theme]
        bg = theme["bg"]
        accent = theme["accent"]
        text = theme["text"]
        
        # Update root and all themed widgets
        self.root.configure(bg=bg)
        
        for widget in self.themed_widgets:
            try:
                widget.configure(bg=bg)
                if isinstance(widget, tk.Label):
                    if widget == self.title_label or widget == self.month_label:
                        widget.configure(fg=accent)
                    else:
                        widget.configure(fg=text)
                elif isinstance(widget, tk.Button):
                    # Make important action buttons use the accent color so they're visible.
                    # Exclude clear_notes_btn so it keeps its dedicated orange color.
                    if widget in [self.subjects_btn, self.reminders_btn, self.add_btn,
                                  self.prev_btn, self.next_btn, self.add_note_btn,
                                  getattr(self, "delete_note_btn", None)]:
                        widget.configure(bg=accent, fg="white")
                elif isinstance(widget, tk.LabelFrame):
                    widget.configure(fg=text)
            except:
                pass
        # Ensure the "Clear All" button uses a specific orange and remains visible.
        try:
            if hasattr(self, "clear_notes_btn") and self.clear_notes_btn:
                self.clear_notes_btn.configure(bg="#ff9800", fg="white")
        except:
            pass
        
        # Update calendar to reflect theme
        self.update_calendar()

    def save_data(self):
        data = {
            "tasks": self.tasks,
            "subjects": self.subjects,
            "sticky_notes": self.sticky_notes,
            "theme": self.current_theme
        }
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print("Failed to save data:", e)

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.tasks = data.get("tasks", [])
                    self.subjects = data.get("subjects", self.subjects)
                    self.sticky_notes = data.get("sticky_notes", [])
                    self.current_theme = data.get("theme", self.current_theme)
            except Exception:
                pass

    def on_closing(self):
        self.save_data()
        self.root.destroy()
        if self.login_root:
            self.login_root.deiconify()


if __name__ == "__main__":
    login = LoginWindow()
    login.root.mainloop()
