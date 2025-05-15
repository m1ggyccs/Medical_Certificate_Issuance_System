import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import logging
from datetime import datetime
from predefined_cases import SIMULATION_SCENARIOS
from simulation import run_simulation, ClinicConfig
import ttkthemes
import threading
import queue
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Configure logging
logging.basicConfig(
    filename='medical_certificate.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

SURVEY_ASSUMPTIONS = {
    'operating_hours': '8:30 AM - 5:00 PM (510 min)',
    'nurses': 3,
    'doctors': 1,
    'clinic_staff': 1,
    'director': 1,
    'peak_hours': '10:00-11:30 AM, 1:30-5:00 PM',
    'nurse_inquiry': 5,
    'simple_case': 3,
    'complex_case': 10,
    'finalization': 2,
    'it_input': 2,
    'avg_wait_time': 5,  # Example survey value for comparison
    'success_rate': 90,  # Example survey value for comparison
}

class ModernFrame(ttk.Frame):
    """A custom frame with modern styling"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure(style='Modern.TFrame')

class StatCard(ttk.Frame):
    """A modern statistics card widget"""
    def __init__(self, parent, title, value, icon="📊"):
        super().__init__(parent, style='Card.TFrame')
        
        # Card layout
        self.title = ttk.Label(self, text=title, style='CardTitle.TLabel')
        self.title.pack(anchor='w', padx=15, pady=(15,5))
        
        self.value = ttk.Label(self, text=str(value), style='CardValue.TLabel')
        self.value.pack(anchor='w', padx=15, pady=(0,15))
        
        self.icon = ttk.Label(self, text=icon, style='CardIcon.TLabel')
        self.icon.place(relx=0.85, rely=0.5, anchor='center')
        
    def update_value(self, value):
        self.value.config(text=str(value))

class EventItem(ttk.Frame):
    """A modern event list item"""
    def __init__(self, parent, title, description, time, category):
        super().__init__(parent, style='ListItem.TFrame')
        
        # Icon based on category
        icons = {
            'NURSE': '👨‍⚕️',
            'DOCTOR': '👩‍⚕️',
            'SYSTEM': '⚙️',
            'PATIENT': '🏥'
        }
        icon = icons.get(category, '📋')
        
        # Layout
        self.icon = ttk.Label(self, text=icon, style='EventIcon.TLabel')
        self.icon.pack(side='left', padx=(15,10), pady=10)
        
        info_frame = ttk.Frame(self)
        info_frame.pack(side='left', fill='x', expand=True, pady=10)
        
        ttk.Label(info_frame, text=title, style='EventTitle.TLabel').pack(anchor='w')
        if description:
            ttk.Label(info_frame, text=description, style='EventDesc.TLabel').pack(anchor='w')
        
        ttk.Label(self, text=time, style='EventTime.TLabel').pack(side='right', padx=15)

    def configure_styles(self):
        # Color scheme
        colors = {
            'primary': '#6C5CE7',      # Purple
            'secondary': '#A8A5E6',    # Light Purple
            'success': '#00B894',      # Green
            'warning': '#FDCB6E',      # Yellow
            'danger': '#FF7675',       # Red
            'background': '#F8F9FA',   # Light Gray
            'surface': '#FFFFFF',      # White
            'text': '#2D3436'          # Dark Gray
        }
        
        # Configure styles
        self.style = ttk.Style()
        
        # Frame styles
        self.style.configure('Card.TFrame', background=colors['background'])
        self.style.configure('ListItem.TFrame', background=colors['background'])
        self.style.configure('Sidebar.TFrame', background=colors['surface'])
        self.style.configure('Tab.TFrame', background=colors['background'])
        
        # Label styles
        self.style.configure('CardTitle.TLabel',
                           font=('Segoe UI', 12),
                           foreground=colors['text'],
                           background=colors['background'])
        self.style.configure('CardValue.TLabel',
                           font=('Segoe UI', 24, 'bold'),
                           foreground=colors['primary'],
                           background=colors['background'])
        self.style.configure('CardIcon.TLabel',
                           font=('Segoe UI', 24),
                           foreground=colors['secondary'],
                           background=colors['background'])
        self.style.configure('EventTitle.TLabel',
                           font=('Segoe UI', 11, 'bold'),
                           foreground=colors['text'],
                           background=colors['background'])
        self.style.configure('EventDesc.TLabel',
                           font=('Segoe UI', 10),
                           foreground=colors['secondary'],
                           background=colors['background'])
        self.style.configure('EventTime.TLabel',
                           font=('Segoe UI', 10),
                           foreground=colors['secondary'],
                           background=colors['background'])
        self.style.configure('EventIcon.TLabel',
                           font=('Segoe UI', 16),
                           foreground=colors['primary'],
                           background=colors['background'])
        
        # Tab styles
        self.style.configure('TNotebook.Tab', padding=[12, 8], font=('Segoe UI', 10))
        self.style.map('TNotebook.Tab',
                      background=[('selected', colors['surface'])],
                      foreground=[('selected', colors['primary'])])

class MedicalCertificateSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Medical Certificate Issuance Support System")
        self.root.geometry("1200x800")
        
        # Event queue for real-time updates
        self.event_queue = queue.Queue()
        self.is_simulating = False
        
        # Apply modern theme
        self.style = ttkthemes.ThemedStyle(self.root)
        self.style.set_theme("arc")
        
        # Configure custom styles
        self.configure_styles()
        
        # Create main layout
        self.create_main_layout()
        
        # Start queue processing
        self.process_queue()

        # Initialize statistics
        self.current_patients = 0
        self.total_certificates = 0
        self.avg_waiting_time = 0.0
        self.success_rate = 0.0

    def configure_styles(self):
        # Color scheme
        colors = {
            'primary': '#6C5CE7',      # Purple
            'secondary': '#A8A5E6',    # Light Purple
            'success': '#00B894',      # Green
            'warning': '#FDCB6E',      # Yellow
            'danger': '#FF7675',       # Red
            'background': '#F8F9FA',   # Light Gray
            'surface': '#FFFFFF',      # White
            'text': '#2D3436'          # Dark Gray
        }
        
        # Configure styles
        self.style = ttk.Style()
        
        # Frame styles
        self.style.configure('Card.TFrame', background=colors['background'])
        self.style.configure('ListItem.TFrame', background=colors['background'])
        self.style.configure('Sidebar.TFrame', background=colors['surface'])
        self.style.configure('Tab.TFrame', background=colors['background'])
        
        # Label styles
        self.style.configure('CardTitle.TLabel',
                           font=('Segoe UI', 12),
                           foreground=colors['text'],
                           background=colors['background'])
        self.style.configure('CardValue.TLabel',
                           font=('Segoe UI', 24, 'bold'),
                           foreground=colors['primary'],
                           background=colors['background'])
        self.style.configure('CardIcon.TLabel',
                           font=('Segoe UI', 24),
                           foreground=colors['secondary'],
                           background=colors['background'])
        self.style.configure('EventTitle.TLabel',
                           font=('Segoe UI', 11, 'bold'),
                           foreground=colors['text'],
                           background=colors['background'])
        self.style.configure('EventDesc.TLabel',
                           font=('Segoe UI', 10),
                           foreground=colors['secondary'],
                           background=colors['background'])
        self.style.configure('EventTime.TLabel',
                           font=('Segoe UI', 10),
                           foreground=colors['secondary'],
                           background=colors['background'])
        self.style.configure('EventIcon.TLabel',
                           font=('Segoe UI', 16),
                           foreground=colors['primary'],
                           background=colors['background'])
        
        # Button styles
        self.style.configure('Action.TButton',
                           font=('Segoe UI', 11),
                           background=colors['primary'],
                           foreground='#000000')
        # Navigation button style
        self.style.configure('Nav.TButton', font=('Segoe UI', 12, 'bold'), padding=10)

    def create_main_layout(self):
        # Main container with padding
        self.main_container = ttk.Frame(self.root, padding="20")
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Sidebar (only title and navigation buttons)
        self.sidebar = ttk.Frame(self.main_container, style='Sidebar.TFrame', width=220)
        self.sidebar.pack(side='left', fill='y', padx=(0, 20))
        self.create_sidebar()

        # Main content area
        self.content = ttk.Frame(self.main_container)
        self.content.pack(side='left', fill='both', expand=True)

        # Top row: stat cards
        stats_frame = ttk.Frame(self.content)
        stats_frame.pack(fill='x', pady=(0, 10))
        self.stat_cards = {
            'current_patients': StatCard(stats_frame, "Current Patients", "0", "👥"),
            'waiting_time': StatCard(stats_frame, "Avg. Waiting Time", "0.0 min", "⏱️"),
            'certificates': StatCard(stats_frame, "Certificates", "0", "📄"),
            'success_rate': StatCard(stats_frame, "Success Rate", "0.0%", "📊")
        }
        for i, card in enumerate(self.stat_cards.values()):
            card.grid(row=0, column=i, padx=5, sticky='nsew')
        stats_frame.grid_columnconfigure((0,1,2,3), weight=1)

        # Simulation controls row (below stat cards)
        self.sim_controls_frame = ttk.Frame(self.content)
        self.sim_controls_frame.pack(fill='x', pady=(0, 10))
        self.create_simulation_controls(self.sim_controls_frame)

        # Main area for tab content
        self.tab_content_frame = ttk.Frame(self.content)
        self.tab_content_frame.pack(fill='both', expand=True)

        # Create all tab frames but only show one at a time
        self.tabs = {
            'events': self.create_events_tab(self.tab_content_frame),
            'statistics': self.create_statistics_tab(self.tab_content_frame),
            'graphs': self.create_graphs_tab(self.tab_content_frame)
        }
        self.show_tab('events')

    def create_sidebar(self):
        # Sidebar title
        profile_frame = ttk.Frame(self.sidebar)
        profile_frame.pack(fill='x', pady=(0, 30))
        ttk.Label(profile_frame, text="MCIS System", font=('Segoe UI', 18, 'bold')).pack(anchor='center')

        # Navigation buttons
        nav_frame = ttk.Frame(self.sidebar)
        nav_frame.pack(fill='x', pady=(0, 10))
        ttk.Button(nav_frame, text="Real-time Events", command=lambda: self.show_tab('events'), style='Nav.TButton').pack(fill='x', pady=8)
        ttk.Button(nav_frame, text="Statistics", command=lambda: self.show_tab('statistics'), style='Nav.TButton').pack(fill='x', pady=8)
        ttk.Button(nav_frame, text="Graphs", command=lambda: self.show_tab('graphs'), style='Nav.TButton').pack(fill='x', pady=8)

    def create_simulation_controls(self, parent):
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill='x')
        # Resource inputs (horizontal)
        ttk.Label(controls_frame, text="Number of Doctors:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.doctors_var = tk.StringVar(value="2")
        ttk.Entry(controls_frame, textvariable=self.doctors_var, width=5).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(controls_frame, text="Number of Nurses:").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.nurses_var = tk.StringVar(value="3")
        ttk.Entry(controls_frame, textvariable=self.nurses_var, width=5).grid(row=0, column=3, padx=5, pady=5)
        ttk.Label(controls_frame, text="Duration (hours):").grid(row=0, column=4, padx=5, pady=5, sticky='e')
        self.duration_var = tk.StringVar(value="8")
        ttk.Entry(controls_frame, textvariable=self.duration_var, width=5).grid(row=0, column=5, padx=5, pady=5)
        # New agent-based timing controls
        ttk.Label(controls_frame, text="Nurse Inquiry (min):").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.nurse_inquiry_var = tk.StringVar(value="5")
        ttk.Entry(controls_frame, textvariable=self.nurse_inquiry_var, width=5).grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(controls_frame, text="Simple Case (min):").grid(row=1, column=2, padx=5, pady=5, sticky='e')
        self.simple_case_var = tk.StringVar(value="3")
        ttk.Entry(controls_frame, textvariable=self.simple_case_var, width=5).grid(row=1, column=3, padx=5, pady=5)
        ttk.Label(controls_frame, text="Complex Case (min):").grid(row=1, column=4, padx=5, pady=5, sticky='e')
        self.complex_case_var = tk.StringVar(value="10")
        ttk.Entry(controls_frame, textvariable=self.complex_case_var, width=5).grid(row=1, column=5, padx=5, pady=5)
        ttk.Label(controls_frame, text="Finalization (min):").grid(row=1, column=6, padx=5, pady=5, sticky='e')
        self.finalization_var = tk.StringVar(value="2")
        ttk.Entry(controls_frame, textvariable=self.finalization_var, width=5).grid(row=1, column=7, padx=5, pady=5)
        # Control buttons
        ttk.Button(controls_frame, text="Start Simulation", command=self.run_simulation, style='Action.TButton').grid(row=2, column=6, padx=10, pady=5)
        ttk.Button(controls_frame, text="Reset", command=self.reset_statistics).grid(row=2, column=7, padx=5, pady=5)
        controls_frame.grid_columnconfigure((1,3,5,7), weight=0)
        controls_frame.grid_columnconfigure((0,2,4,6), weight=0)

    def create_events_tab(self, parent):
        frame = ttk.Frame(parent)
        # Events list with scrollbar
        self.events_canvas = tk.Canvas(frame, background='#F8F9FA', highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.events_canvas.yview)
        self.events_list = ttk.Frame(self.events_canvas, style='Tab.TFrame')
        self.events_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.events_canvas.pack(side="left", fill="both", expand=True)
        self.events_canvas.create_window((0, 0), window=self.events_list, anchor="nw")
        self.events_list.bind("<Configure>", self._on_frame_configure)
        self.events_canvas.bind('<Configure>', self._on_canvas_configure)
        return frame

    def create_statistics_tab(self, parent):
        frame = ttk.Frame(parent)
        self.create_statistics_sections_in_tab(frame)
        return frame

    def create_graphs_tab(self, parent):
        frame = ttk.Frame(parent)
        self.graph_canvas = None
        self.graph_frame = ttk.Frame(frame)
        self.graph_frame.pack(fill='both', expand=True)
        return frame

    def show_tab(self, tab_name):
        for name, frame in self.tabs.items():
            frame.pack_forget()
        self.tabs[tab_name].pack(fill='both', expand=True)

    def create_statistics_sections_in_tab(self, parent):
        # Main statistics text
        self.stats_text = scrolledtext.ScrolledText(parent, height=15, width=70)
        self.stats_text.pack(fill='both', expand=True, pady=(0, 10))
        self.stats_text.config(state=tk.DISABLED)
        # Case complexity frame
        complexity_frame = ttk.LabelFrame(parent, text="Case Complexity", padding=10)
        complexity_frame.pack(fill='x', pady=5)
        self.complexity_labels = {
            'simple': ttk.Label(complexity_frame, text="Simple Cases: 0"),
            'complex': ttk.Label(complexity_frame, text="Complex Cases: 0")
        }
        self.complexity_labels['simple'].pack(side='left', padx=10)
        self.complexity_labels['complex'].pack(side='left', padx=10)
        # Peak hours frame
        peak_frame = ttk.LabelFrame(parent, text="Visit Timing", padding=10)
        peak_frame.pack(fill='x', pady=5)
        self.peak_labels = {
            'peak': ttk.Label(peak_frame, text="Peak Hours: 0"),
            'off_peak': ttk.Label(peak_frame, text="Off-Peak: 0")
        }
        self.peak_labels['peak'].pack(side='left', padx=10)
        self.peak_labels['off_peak'].pack(side='left', padx=10)

    def _on_frame_configure(self, event=None):
        """Reset the scroll region to encompass the inner frame"""
        self.events_canvas.configure(scrollregion=self.events_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """When the canvas is resized, resize the inner frame to match"""
        width = event.width
        self.events_canvas.itemconfig(self.events_canvas.find_withtag('all')[0], width=width)

    def handle_simulation_event(self, event_type, data):
        """Handle events from the simulation."""
        try:
            if event_type == "student":
                # Create detailed event description
                description = (
                    f"Status: {data.get('action', 'unknown')}\n"
                    f"Excuse Letter: {'Yes' if data.get('has_excuse_letter') else 'No'}\n"
                    f"Valid ID: {'Yes' if data.get('has_valid_id') else 'No'}"
                )
                self.add_event(
                    f"Student {data['id']}", 
                    description,
                    datetime.now().strftime("%H:%M:%S"),
                    "PATIENT"
                )
                
            elif event_type == "stats":
                self._update_stat_cards(data)
                
            elif event_type == "completion":
                description = (
                    f"Status: {data.get('status', 'unknown')}\n"
                    f"Reason: {data.get('reason', 'N/A')}\n"
                    f"Wait Time: {data.get('wait_time', 0):.1f} min"
                )
                self.add_event(
                    f"Student {data['id']} Completed",
                    description,
                    datetime.now().strftime("%H:%M:%S"),
                    "SYSTEM"
                )
                
        except Exception as e:
            logging.error(f"Error handling simulation event: {str(e)}")
            self.add_event(
                "System Error",
                str(e),
                datetime.now().strftime("%H:%M:%S"),
                "SYSTEM"
            )

    def _update_stat_cards(self, data):
        """Safely update statistics cards with new data"""
        try:
            # Update current patients
            if 'Patients in System' in data:
                self.stat_cards['current_patients'].update_value(str(data['Patients in System']))
            
            # Update waiting time
            if 'Average Wait' in data:
                wait_mins = f"{data['Average Wait']:.1f}"
                self.stat_cards['waiting_time'].update_value(f"{wait_mins} min")
            
            # Update certificates
            if 'Certificates Issued' in data:
                self.stat_cards['certificates'].update_value(str(data['Certificates Issued']))
            
            # Update success rate
            if 'Success Rate' in data:
                self.stat_cards['success_rate'].update_value(f"{data['Success Rate']:.1f}%")
        except Exception as e:
            logging.error(f"Error updating statistics cards: {str(e)}")

    def process_queue(self):
        """Process events from the queue and update the GUI."""
        try:
            while True:
                event_type, data = self.event_queue.get_nowait()
                
                if event_type == "log":
                    self.add_event(
                        data['message'],
                        time=data['timestamp'],
                        category=data.get('category', 'SYSTEM')
                    )
                elif event_type == "stats":
                    for card_name, value in data.items():
                        if card_name in self.stat_cards:
                            self.stat_cards[card_name].update_value(value)
                elif event_type == "status":
                    self.add_event("Status Update", data, category="SYSTEM")
                
        except queue.Empty:
            pass
        finally:
            # Schedule the next queue check
            self.root.after(100, self.process_queue)

    def run_simulation(self):
        """Run the simulation with real-time updates."""
        try:
            if self.is_simulating:
                messagebox.showwarning("Warning", "Simulation is already running")
                return

            self.is_simulating = True
            num_doctors = int(self.doctors_var.get())
            num_nurses = int(self.nurses_var.get())
            duration = float(self.duration_var.get())
            nurse_inquiry = int(self.nurse_inquiry_var.get())
            simple_case = int(self.simple_case_var.get())
            complex_case = int(self.complex_case_var.get())
            finalization = int(self.finalization_var.get())

            # Clear previous events
            for widget in self.events_list.winfo_children():
                widget.destroy()

            # Reset statistics
            for card in self.stat_cards.values():
                card.update_value("0")

            # Add initial event
            self.add_event("Starting Simulation", 
                          f"Doctors: {num_doctors}, Nurses: {num_nurses}, Duration: {duration}h",
                          category="SYSTEM")

            # Start simulation in a separate thread
            self.sim_thread = threading.Thread(
                target=self._run_simulation_thread,
                args=(duration, num_doctors, num_nurses, nurse_inquiry, simple_case, complex_case, finalization)
            )
            self.sim_thread.daemon = True
            self.sim_thread.start()

        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numbers for resources and duration.")
        except Exception as e:
            messagebox.showerror("Error", f"Simulation error: {str(e)}")

    def _run_simulation_thread(self, duration, num_doctors, num_nurses, nurse_inquiry, simple_case, complex_case, finalization):
        """Run the simulation in a separate thread."""
        try:
            # Create a custom ClinicConfig for agent-based simulation
            custom_config = ClinicConfig(
                OPENING_TIME="08:30",
                CLOSING_TIME="17:00",
                MAX_NURSES=num_nurses,
                MAX_DOCTORS=num_doctors,
                MAX_STAFF=1,
                NURSE_PROCESS_TIME=nurse_inquiry,
                DOCTOR_PROCESS_TIME=complex_case,
                STAFF_PROCESS_TIME=finalization
            )
            # Run the simulation with the custom config
            results = run_simulation(
                duration_hours=duration,
                num_doctors=num_doctors,
                num_nurses=num_nurses,
                event_callback=self.handle_simulation_event
            )
            # Update final results
            self.root.after(0, self.show_simulation_results, results)
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", f"Simulation error: {str(e)}")
        finally:
            self.is_simulating = False
            self.event_queue.put(("status", "Completed"))

    def show_simulation_results(self, results):
        """Display final simulation results."""
        try:
            if 'error' in results:
                messagebox.showerror("Simulation Error", results['error'])
                return

            # Run survey-based simulation for comparison
            survey_results = self.run_survey_simulation()

            # Update statistics text
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete(1.0, tk.END)

            # User simulation block
            self.stats_text.insert(tk.END, "Agent-Based Simulation\n=======================\n")
            self.stats_text.insert(tk.END, f"Total Patients: {results.get('total_patients', 0)}\n")
            self.stats_text.insert(tk.END, f"Patients Seen: {results.get('patients_seen', 0)}\n")
            self.stats_text.insert(tk.END, f"Certificates Issued: {results.get('certificates_issued', 0)}\n")
            self.stats_text.insert(tk.END, f"Average Wait Time: {results.get('average_wait_time', 0):.2f} minutes\n")
            self.stats_text.insert(tk.END, f"Certificate Success Rate: {results.get('certificate_issuance_rate', 0):.1f}%\n")
            self.stats_text.insert(tk.END, f"Cases: {results.get('simple_cases', 0)}\n")
            self.stats_text.insert(tk.END, f"Visits: {results.get('off_peak_visits', 0)}\n")
            self.stats_text.insert(tk.END, "\n")

            # Survey simulation block
            self.stats_text.insert(tk.END, "Survey-Based Simulation\n=======================\n")
            self.stats_text.insert(tk.END, f"Total Patients: {survey_results.get('total_patients', 0)}\n")
            self.stats_text.insert(tk.END, f"Patients Seen: {survey_results.get('patients_seen', 0)}\n")
            self.stats_text.insert(tk.END, f"Certificates Issued: {survey_results.get('certificates_issued', 0)}\n")
            self.stats_text.insert(tk.END, f"Average Wait Time: {survey_results.get('average_wait_time', 0):.2f} minutes\n")
            self.stats_text.insert(tk.END, f"Certificate Success Rate: {survey_results.get('certificate_issuance_rate', 0):.1f}%\n")
            self.stats_text.insert(tk.END, f"Cases: {survey_results.get('simple_cases', 0)}\n")
            self.stats_text.insert(tk.END, f"Visits: {survey_results.get('off_peak_visits', 0)}\n")
            self.stats_text.insert(tk.END, "\n")

            # Add comparison to survey assumptions (for reference)
            self.stats_text.insert(tk.END, "--- Survey Assumptions Reference ---\n")
            self.stats_text.insert(tk.END, f"Operating Hours: {SURVEY_ASSUMPTIONS['operating_hours']}\n")
            self.stats_text.insert(tk.END, f"Nurses: {SURVEY_ASSUMPTIONS['nurses']}\n")
            self.stats_text.insert(tk.END, f"Doctors: {SURVEY_ASSUMPTIONS['doctors']}\n")
            self.stats_text.insert(tk.END, f"Nurse Inquiry: {SURVEY_ASSUMPTIONS['nurse_inquiry']} min\nSimple Case: {SURVEY_ASSUMPTIONS['simple_case']} min\nComplex Case: {SURVEY_ASSUMPTIONS['complex_case']} min\nFinalization: {SURVEY_ASSUMPTIONS['finalization']} min\nIT Input: {SURVEY_ASSUMPTIONS['it_input']} min\n")
            self.stats_text.config(state=tk.DISABLED)

            # Update complexity labels
            self.complexity_labels['simple'].config(
                text=f"Cases: {results.get('simple_cases', 0)}"
            )
            if 'complex' in self.complexity_labels:
                self.complexity_labels['complex'].pack_forget()

            # Update peak hour labels
            self.peak_labels['peak'].config(
                text=f"Peak Hours: 0"
            )
            self.peak_labels['off_peak'].config(
                text=f"Visits: {results.get('off_peak_visits', 0)}"
            )

            # Update graph tab with comparison
            self.update_graphs_tab(results, survey_results)

            # Add completion event
            self.add_event(
                "Simulation Complete", 
                f"Processed {results.get('total_patients', 0)} patients",
                category="SYSTEM"
            )
        except Exception as e:
            logging.error(f"Error showing simulation results: {str(e)}")
            messagebox.showerror("Error", f"Failed to display simulation results: {str(e)}")

    def run_survey_simulation(self):
        # Use survey-based parameters
        survey_config = ClinicConfig(
            OPENING_TIME="08:30",
            CLOSING_TIME="17:00",
            MAX_NURSES=3,
            MAX_DOCTORS=1,
            MAX_STAFF=1,
            NURSE_PROCESS_TIME=5,   # Nurse Inquiry
            DOCTOR_PROCESS_TIME=10, # Complex Case
            STAFF_PROCESS_TIME=2    # Certificate Finalization
        )
        # Duration: 510 minutes = 8.5 hours
        return run_simulation(duration_hours=8.5, num_doctors=1, num_nurses=3, event_callback=None)

    def update_graphs_tab(self, results, survey_results=None):
        # Remove previous graph if exists
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        # Prepare data for comparison
        sim_total_patients = results.get('total_patients', 0)
        sim_cert_issued = results.get('certificates_issued', 0)
        sim_wait = results.get('average_wait_time', 0)
        sim_rate = results.get('certificate_issuance_rate', 0)
        if survey_results:
            survey_total_patients = survey_results.get('total_patients', 0)
            survey_cert_issued = survey_results.get('certificates_issued', 0)
            survey_wait = survey_results.get('average_wait_time', 0)
            survey_rate = survey_results.get('certificate_issuance_rate', 0)
        else:
            survey_total_patients = SURVEY_ASSUMPTIONS.get('total_patients', 0)
            survey_cert_issued = SURVEY_ASSUMPTIONS.get('certificates_issued', 0)
            survey_wait = SURVEY_ASSUMPTIONS['avg_wait_time']
            survey_rate = SURVEY_ASSUMPTIONS['success_rate']
        labels = ['Total Patients', 'Certificates Issued', 'Avg. Wait Time (min)', 'Success Rate (%)']
        sim_values = [sim_total_patients, sim_cert_issued, sim_wait, sim_rate]
        survey_values = [survey_total_patients, survey_cert_issued, survey_wait, survey_rate]
        x = range(len(labels))
        fig, ax = plt.subplots(figsize=(7,4))
        ax.bar([i-0.2 for i in x], sim_values, width=0.4, label='Agent-Based', color='#6C5CE7')
        ax.bar([i+0.2 for i in x], survey_values, width=0.4, label='Survey-Based', color='#00B894')
        ax.set_xticks(list(x))
        ax.set_xticklabels(labels)
        ax.legend()
        ax.set_title('Agent-Based vs Survey-Based Simulation Comparison')
        fig.tight_layout()
        self.graph_canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.graph_canvas.draw()
        self.graph_canvas.get_tk_widget().pack(fill='both', expand=True)

    def reset_statistics(self):
        """Reset all statistics and clear events."""
        try:
            # Clear events list
            for widget in self.events_list.winfo_children():
                widget.destroy()
            
            # Reset stat cards
            for card in self.stat_cards.values():
                card.update_value("0")
            
            # Clear statistics text
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.config(state=tk.DISABLED)
            
            # Add reset event
            self.add_event("Statistics Reset", "All statistics have been cleared", category="SYSTEM")
        except Exception as e:
            logging.error(f"Error resetting statistics: {str(e)}")
            messagebox.showerror("Error", f"Failed to reset statistics: {str(e)}")

    def add_event(self, title, description="", time=None, category="SYSTEM"):
        """Add a new event to the events list."""
        try:
            if time is None:
                time = datetime.now().strftime("%H:%M:%S")
            
            # Create new event item
            event = EventItem(self.events_list, title, description, time, category)
            event.pack(fill='x', pady=1)
            
            # Auto-scroll to bottom
            self.events_canvas.yview_moveto(1.0)
            
        except Exception as e:
            logging.error(f"Error adding event: {str(e)}")
            # Try to add error event without fancy formatting
            try:
                ttk.Label(self.events_list, text=f"Error: {str(e)}").pack(fill='x')
            except:
                pass
        finally:
            # Always update scroll region
            try:
                self._on_frame_configure()
            except Exception as e:
                logging.error(f"Error updating scroll region: {str(e)}")

    def update_statistics(self, stats):
        """Update the statistics display with new values."""
        if 'current_patients' in stats:
            self.stats_values[0].config(text=str(stats['current_patients']))
        if 'avg_waiting_time' in stats:
            formatted_time = f"{stats['avg_waiting_time']:.1f} min"
            self.stats_values[1].config(text=formatted_time)
        if 'certificates' in stats:
            self.stats_values[2].config(text=str(stats['certificates']))
        if 'success_rate' in stats:
            formatted_rate = f"{stats['success_rate']:.1f}%"
            self.stats_values[3].config(text=formatted_rate)

if __name__ == "__main__":
    root = tk.Tk()
    app = MedicalCertificateSystem(root)
    root.mainloop() 