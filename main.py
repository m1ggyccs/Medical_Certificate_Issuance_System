import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import logging
from datetime import datetime
from predefined_cases import SIMULATION_SCENARIOS
from simulation import run_simulation
import ttkthemes
import threading
import queue

# Configure logging
logging.basicConfig(
    filename='medical_certificate.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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
        self.style.configure('Card.TFrame', background=colors['surface'])
        self.style.configure('ListItem.TFrame', background=colors['surface'])
        self.style.configure('Sidebar.TFrame', background=colors['surface'])
        self.style.configure('Tab.TFrame', background=colors['background'])
        
        # Label styles
        self.style.configure('CardTitle.TLabel',
                           font=('Segoe UI', 12),
                           foreground=colors['text'])
        self.style.configure('CardValue.TLabel',
                           font=('Segoe UI', 24, 'bold'),
                           foreground=colors['primary'])
        self.style.configure('CardIcon.TLabel',
                           font=('Segoe UI', 24),
                           foreground=colors['secondary'])
        self.style.configure('EventTitle.TLabel',
                           font=('Segoe UI', 11, 'bold'),
                           foreground=colors['text'])
        self.style.configure('EventDesc.TLabel',
                           font=('Segoe UI', 10),
                           foreground=colors['secondary'])
        self.style.configure('EventTime.TLabel',
                           font=('Segoe UI', 10),
                           foreground=colors['secondary'])
        self.style.configure('EventIcon.TLabel',
                           font=('Segoe UI', 16),
                           foreground=colors['primary'])
        
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
        self.style.configure('Card.TFrame', background=colors['surface'])
        self.style.configure('ListItem.TFrame', background=colors['surface'])
        self.style.configure('Sidebar.TFrame', background=colors['surface'])
        
        # Label styles
        self.style.configure('CardTitle.TLabel',
                           font=('Segoe UI', 12),
                           foreground=colors['text'])
        self.style.configure('CardValue.TLabel',
                           font=('Segoe UI', 24, 'bold'),
                           foreground=colors['primary'])
        self.style.configure('CardIcon.TLabel',
                           font=('Segoe UI', 24),
                           foreground=colors['secondary'])
        self.style.configure('EventTitle.TLabel',
                           font=('Segoe UI', 11, 'bold'),
                           foreground=colors['text'])
        self.style.configure('EventDesc.TLabel',
                           font=('Segoe UI', 10),
                           foreground=colors['secondary'])
        self.style.configure('EventTime.TLabel',
                           font=('Segoe UI', 10),
                           foreground=colors['secondary'])
        self.style.configure('EventIcon.TLabel',
                           font=('Segoe UI', 16),
                           foreground=colors['primary'])
        
        # Button styles
        self.style.configure('Action.TButton',
                           font=('Segoe UI', 11),
                           background=colors['primary'],
                           foreground=colors['surface'])

    def create_main_layout(self):
        # Main container with padding
        self.main_container = ttk.Frame(self.root, padding="20")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left sidebar (30% width)
        self.sidebar = ttk.Frame(self.main_container, style='Sidebar.TFrame')
        self.sidebar.pack(side='left', fill='y', padx=(0,20))
        
        # Create sidebar content
        self.create_sidebar()
        
        # Main content area (70% width)
        self.content = ttk.Frame(self.main_container)
        self.content.pack(side='left', fill='both', expand=True)
        
        # Create main content
        self.create_dashboard()

    def create_sidebar(self):
        # Profile section
        profile_frame = ttk.Frame(self.sidebar)
        profile_frame.pack(fill='x', pady=(0,20))
        
        ttk.Label(profile_frame, text="Medical Certificate", 
                 font=('Segoe UI', 18, 'bold')).pack(anchor='w')
        ttk.Label(profile_frame, text="Simulation Dashboard",
                 font=('Segoe UI', 12)).pack(anchor='w')
        
        # Simulation controls
        controls_frame = ttk.LabelFrame(self.sidebar, text="Simulation Controls", padding=10)
        controls_frame.pack(fill='x', pady=(0,20))
        
        # Resource inputs
        ttk.Label(controls_frame, text="Number of Doctors:").pack(anchor='w', pady=(0,5))
        self.doctors_var = tk.StringVar(value="2")
        ttk.Entry(controls_frame, textvariable=self.doctors_var).pack(fill='x', pady=(0,10))
        
        ttk.Label(controls_frame, text="Number of Nurses:").pack(anchor='w', pady=(0,5))
        self.nurses_var = tk.StringVar(value="3")
        ttk.Entry(controls_frame, textvariable=self.nurses_var).pack(fill='x', pady=(0,10))
        
        ttk.Label(controls_frame, text="Duration (hours):").pack(anchor='w', pady=(0,5))
        self.duration_var = tk.StringVar(value="8")
        ttk.Entry(controls_frame, textvariable=self.duration_var).pack(fill='x', pady=(0,10))
        
        # Control buttons
        ttk.Button(controls_frame, text="Start Simulation", 
                  command=self.run_simulation, style='Action.TButton').pack(fill='x', pady=(10,5))
        ttk.Button(controls_frame, text="Reset", 
                  command=self.reset_statistics).pack(fill='x')

    def create_dashboard(self):
        # Statistics cards row
        stats_frame = ttk.Frame(self.content)
        stats_frame.pack(fill='x', pady=(0,20))
        
        # Create stat cards
        self.stat_cards = {
            'current_patients': StatCard(stats_frame, "Current Patients", "0", "👥"),
            'waiting_time': StatCard(stats_frame, "Avg. Waiting Time", "0.0 min", "⏱️"),
            'certificates': StatCard(stats_frame, "Certificates", "0", "📄"),
            'success_rate': StatCard(stats_frame, "Success Rate", "0.0%", "📊")
        }
        
        # Layout stat cards in grid
        for i, card in enumerate(self.stat_cards.values()):
            card.grid(row=0, column=i, padx=5, sticky='nsew')
        stats_frame.grid_columnconfigure((0,1,2,3), weight=1)
        
        # Create tabs container
        self.notebook = ttk.Notebook(self.content)
        self.notebook.pack(fill='both', expand=True)
        
        # Real-time events tab
        self.events_frame = ttk.Frame(self.notebook, style='Tab.TFrame', padding=10)
        self.notebook.add(self.events_frame, text="Real-time Events")
        
        # Events list with scrollbar
        self.events_canvas = tk.Canvas(self.events_frame, background='#F8F9FA', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.events_frame, orient="vertical", command=self.events_canvas.yview)
        self.events_list = ttk.Frame(self.events_frame, style='Tab.TFrame')
        
        self.events_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrolling list
        scrollbar.pack(side="right", fill="y")
        self.events_canvas.pack(side="left", fill="both", expand=True)
        self.events_canvas.create_window((0, 0), window=self.events_list, anchor="nw")
        
        # Configure canvas scrolling
        self.events_list.bind("<Configure>", self._on_frame_configure)
        self.events_canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Statistics tab
        self.stats_frame = ttk.Frame(self.notebook, style='Tab.TFrame', padding=10)
        self.notebook.add(self.stats_frame, text="Statistics")
        
        # Create statistics sections
        self.create_statistics_sections()

    def create_statistics_sections(self):
        """Create detailed statistics sections"""
        # Main statistics text
        self.stats_text = scrolledtext.ScrolledText(self.stats_frame, height=15, width=70)
        self.stats_text.pack(fill='both', expand=True, pady=(0, 10))
        self.stats_text.config(state=tk.DISABLED)
        
        # Case complexity frame
        complexity_frame = ttk.LabelFrame(self.stats_frame, text="Case Complexity", padding=10)
        complexity_frame.pack(fill='x', pady=5)
        
        self.complexity_labels = {
            'simple': ttk.Label(complexity_frame, text="Simple Cases: 0"),
            'complex': ttk.Label(complexity_frame, text="Complex Cases: 0")
        }
        self.complexity_labels['simple'].pack(side='left', padx=10)
        self.complexity_labels['complex'].pack(side='left', padx=10)
        
        # Peak hours frame
        peak_frame = ttk.LabelFrame(self.stats_frame, text="Visit Timing", padding=10)
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
            duration = int(self.duration_var.get())
            
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
                args=(duration, num_doctors, num_nurses)
            )
            self.sim_thread.daemon = True
            self.sim_thread.start()
            
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numbers for resources and duration.")
        except Exception as e:
            messagebox.showerror("Error", f"Simulation error: {str(e)}")

    def _run_simulation_thread(self, duration, num_doctors, num_nurses):
        """Run the simulation in a separate thread."""
        try:
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

            # Update statistics text
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete(1.0, tk.END)
            
            # Format and display results
            self.stats_text.insert(tk.END, f"""Simulation Results Summary
            
Total Statistics:
----------------
Total Patients: {results.get('total_patients', 0)}
Patients Seen: {results.get('patients_seen', 0)}
Certificates Issued: {results.get('certificates_issued', 0)}
Average Wait Time: {results.get('average_wait_time', 0):.2f} minutes
Certificate Success Rate: {results.get('certificate_issuance_rate', 0):.1f}%

Resource Utilization:
-------------------
Doctors: {results.get('num_doctors', 0)}
Nurses: {results.get('num_nurses', 0)}

Case Distribution:
----------------
Simple Cases: {results.get('simple_cases', 0)}
Complex Cases: {results.get('complex_cases', 0)}
Peak Hour Visits: {results.get('peak_hour_visits', 0)}
Off-Peak Visits: {results.get('off_peak_visits', 0)}

Decision Statistics:
-----------------
Nurse Decisions:
- Referred to Emergency: {results.get('nurse_decisions', {}).get('refer', 0)}
- Treated in Clinic: {results.get('nurse_decisions', {}).get('treat', 0)}

Doctor Decisions:
- Certificates Issued: {results.get('doctor_decisions', {}).get('issue', 0)}
- Certificates Denied: {results.get('doctor_decisions', {}).get('deny', 0)}
""")
            self.stats_text.config(state=tk.DISABLED)
            
            # Update complexity labels
            self.complexity_labels['simple'].config(
                text=f"Simple Cases: {results.get('simple_cases', 0)}"
            )
            self.complexity_labels['complex'].config(
                text=f"Complex Cases: {results.get('complex_cases', 0)}"
            )
            
            # Update peak hour labels
            self.peak_labels['peak'].config(
                text=f"Peak Hours: {results.get('peak_hour_visits', 0)}"
            )
            self.peak_labels['off_peak'].config(
                text=f"Off-Peak: {results.get('off_peak_visits', 0)}"
            )
            
            # Add completion event
            self.add_event(
                "Simulation Complete", 
                f"Processed {results.get('total_patients', 0)} patients",
                category="SYSTEM"
            )
        except Exception as e:
            logging.error(f"Error showing simulation results: {str(e)}")
            messagebox.showerror("Error", f"Failed to display simulation results: {str(e)}")

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