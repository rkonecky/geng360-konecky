"""
Data Collection GUI for Arduino Serial Data

This GUI allows you to collect data from an Arduino connected via USB and save it as a CSV file.

Key Features:
- Select your Arduino's COM/serial port from the dropdown
- Set the data collection time and sampling period
- View incoming serial data in real-time
- Save the collected data as a CSV file for analysis

Usage:
1. Connect your Arduino via USB
2. Select the correct serial port
3. Configure collection parameters
4. Click "Start Collection" to begin recording data
5. Save your data when collection is complete

Run this file by pushing the triangular play button in the top right of the file. A separate window will appear. 
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import serial
import serial.tools.list_ports
import time
import csv
import threading
import os
from datetime import datetime
import string

class SerialDataCollector:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Collection GUI")
        self.root.geometry("750x550")
        
        # Variables
        self.is_collecting = False
        self.data_list = []
        self.ser = None
        self.display_line_count = 0  # Track lines in display
        self.max_display_lines = 1000  # Maximum lines to show
        
        self.setup_gui()
        
        # Initialize serial ports after GUI is completely ready
        self.root.after(100, self.refresh_serial_ports)
    
    def calculate_samples(self, event=None):
        """Calculate number of samples based on collection time and sampling period"""
        try:
            collection_time = float(self.collection_time_var.get())
            sampling_period = float(self.sampling_period_var.get())
            
            # Calculate samples: time(s) * 1000(ms/s) / period(ms)
            num_samples = int(collection_time * 1000 / sampling_period)
            self.calculated_samples_var.set(str(num_samples))
            
        except ValueError:
            # If invalid input, show placeholder
            self.calculated_samples_var.set("---")
        
    def setup_gui(self):
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)  # Data display row
        
        # === CONNECTION SETTINGS SECTION ===
        conn_frame = ttk.LabelFrame(main_frame, text="Connection Settings", padding="10")
        conn_frame.grid(row=0, column=0, sticky="nwe", padx=(0,10), pady=(0,15))
        conn_frame.columnconfigure(1, weight=1)
        
        # Serial Port row
        ttk.Label(conn_frame, text="Serial Port:").grid(row=0, column=0, sticky=tk.W, pady=(0,8))
        
        port_frame = ttk.Frame(conn_frame)
        port_frame.grid(row=0, column=1, columnspan=2, sticky="we", pady=(0,8))
        port_frame.columnconfigure(0, weight=1)
        
        self.serial_port_var = tk.StringVar()
        self.serial_port_combo = ttk.Combobox(port_frame, textvariable=self.serial_port_var, state="readonly")
        self.serial_port_combo.grid(row=0, column=0, sticky="we", padx=(0,5))
        
        self.refresh_button = ttk.Button(port_frame, text="↻", command=self.refresh_serial_ports, width=3)
        self.refresh_button.grid(row=0, column=1)
        
        # Baud Rate row
        ttk.Label(conn_frame, text="Baud Rate:").grid(row=1, column=0, sticky=tk.W)
        self.baud_rate_var = tk.StringVar(value="115200")
        baud_rates = ["9600", "19200", "38400", "57600", "115200"]
        self.baud_rate_combo = ttk.Combobox(conn_frame, textvariable=self.baud_rate_var, values=baud_rates, state="readonly", width=15)
        self.baud_rate_combo.grid(row=1, column=1, sticky=tk.W)
        
        # === COLLECTION SETTINGS SECTION ===
        coll_frame = ttk.LabelFrame(main_frame, text="Collection Settings", padding="10")
        coll_frame.grid(row=0, column=1, sticky="nwe", pady=(0,15))
        coll_frame.columnconfigure(1, weight=1)
        coll_frame.columnconfigure(3, weight=1)
        
        # Time and Period row
        ttk.Label(coll_frame, text="Time (s):").grid(row=0, column=0, sticky=tk.W, padx=(0,5), pady=(0,8))
        self.collection_time_var = tk.StringVar(value="5")
        self.collection_time_entry = ttk.Entry(coll_frame, textvariable=self.collection_time_var, width=8)
        self.collection_time_entry.grid(row=0, column=1, sticky=tk.W, padx=(0,15), pady=(0,8))
        self.collection_time_entry.bind('<KeyRelease>', self.calculate_samples)
        
        ttk.Label(coll_frame, text="Period (ms):").grid(row=0, column=2, sticky=tk.W, padx=(0,5), pady=(0,8))
        self.sampling_period_var = tk.StringVar(value="4")
        self.sampling_period_entry = ttk.Entry(coll_frame, textvariable=self.sampling_period_var, width=8)
        self.sampling_period_entry.grid(row=0, column=3, sticky=tk.W, pady=(0,8))
        self.sampling_period_entry.bind('<KeyRelease>', self.calculate_samples)
        
        # Samples and Filename row
        ttk.Label(coll_frame, text="Samples:").grid(row=1, column=0, sticky=tk.W, padx=(0,5))
        self.calculated_samples_var = tk.StringVar(value="1250")
        samples_label = ttk.Label(coll_frame, textvariable=self.calculated_samples_var, relief=tk.SUNKEN, width=8)
        samples_label.grid(row=1, column=1, sticky=tk.W, padx=(0,15))
        
        ttk.Label(coll_frame, text="Filename:").grid(row=1, column=2, sticky=tk.W, padx=(0,5))
        self.filename_var = tk.StringVar(value="data.csv")
        self.filename_entry = ttk.Entry(coll_frame, textvariable=self.filename_var, width=18)
        self.filename_entry.grid(row=1, column=3, sticky="we")
        
        # === CONTROL BUTTONS ===
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=15)
        
        self.start_button = ttk.Button(button_frame, text="Start Collection", command=self.start_collection)
        self.start_button.pack(side=tk.LEFT, padx=(0,15))
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_collection, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)
        
        # === PROGRESS SECTION ===
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=2, column=0, columnspan=2, sticky="we", pady=(0,10))
        progress_frame.columnconfigure(1, weight=1)
        
        ttk.Label(progress_frame, text="Progress:").grid(row=0, column=0, sticky=tk.W, padx=(0,10))
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.grid(row=0, column=1, sticky="we", padx=(0,10))
        
        self.progress_label = ttk.Label(progress_frame, text="0/0")
        self.progress_label.grid(row=0, column=2)
        
        # === DATA DISPLAY ===
        data_frame = ttk.LabelFrame(main_frame, text="Data", padding="5")
        data_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(0,10))
        data_frame.columnconfigure(0, weight=1)
        data_frame.rowconfigure(0, weight=1)
        
        self.data_text = tk.Text(data_frame, wrap=tk.WORD, height=12, font=("Consolas", 9))
        scrollbar = ttk.Scrollbar(data_frame, orient=tk.VERTICAL, command=self.data_text.yview)
        self.data_text.configure(yscrollcommand=scrollbar.set)
        
        self.data_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # === STATUS BAR ===
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, columnspan=2, sticky="we", pady=(5,0))
        
        # Initialize calculated samples 
        self.calculate_samples()
    
    def refresh_serial_ports(self):
        """Scan for available serial ports and update the dropdown with detailed info"""
        try:
            ports = serial.tools.list_ports.comports()
            # Show both device and description (e.g., COM3 - USB-SERIAL CH340)
            port_list = [f"{port.device} - {port.description}" for port in ports]
            self._port_device_map = {f"{port.device} - {port.description}": port.device for port in ports}

            self.serial_port_combo['values'] = port_list

            # Set default selection
            if port_list:
                # Try to find a USB serial port first
                usb_ports = [p for p in port_list if 'usb' in p.lower() or 'serial' in p.lower() or 'ch340' in p.lower()]
                if usb_ports:
                    self.serial_port_var.set(usb_ports[0])
                else:
                    self.serial_port_var.set(port_list[0])
                self.status_var.set(f"Found {len(port_list)} serial port(s)")
            else:
                self.serial_port_var.set("")
                self.status_var.set("No serial ports found")
        except Exception as e:
            self.status_var.set(f"Error scanning ports: {str(e)}")

    def start_collection(self):
        try:
            # Get values from GUI
            # Map the selected combo string to the device name
            selected_port = self.serial_port_var.get()
            serial_port = self._port_device_map.get(selected_port, selected_port)
            baud_rate = int(self.baud_rate_var.get())
            
            # Calculate number of samples from time and period
            collection_time = float(self.collection_time_var.get())
            sampling_period = float(self.sampling_period_var.get())
            target_samples = int(collection_time * 1000 / sampling_period)
            num_samples = target_samples + 1  # Add 1 for header row
            
            if target_samples <= 0:
                messagebox.showerror("Input Error", "Number of samples must be greater than 0")
                return
                
            # Reset data
            self.data_list = []
            self.data_text.delete(1.0, tk.END)
            self.display_line_count = 0  # Reset display counter
            self.progress.config(maximum=target_samples, value=0)  # Use target_samples for display
            self.progress_label.config(text=f"0/{target_samples}")
            
            # Set collection flag
            self.is_collecting = True
            
            # Update GUI state
            self.status_var.set("Starting connection...")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            # Start collection in separate thread (pass both values)
            collection_thread = threading.Thread(target=self.collect_data, 
                                                args=(serial_port, baud_rate, num_samples, sampling_period, target_samples))
            collection_thread.daemon = True
            collection_thread.start()
            
        except ValueError as e:
            messagebox.showerror("Input Error", "Please check your numeric inputs")
            self.status_var.set("Error: Invalid input")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start collection: {str(e)}")
            self.status_var.set("Error starting collection")
    
    def collect_data(self, serial_port, baud_rate, num_samples, sampling_period, target_samples):
        """Serial collection logic with connection and data timeout error handling"""
        try:
            self.root.after(0, lambda: self.status_var.set("Establishing connection..."))
            try:
                self.ser = serial.Serial(serial_port, baud_rate, timeout=1)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Serial Error", f"Could not open serial port: {str(e)}"))
                self.root.after(0, lambda: self.status_var.set(f"Error: Could not open serial port"))
                self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
                return

            self.root.after(0, lambda: self.status_var.set("Connection established. Waiting for data..."))

            # Data timeout logic: wait up to 5 seconds for first data
            data_timeout = 5  # seconds
            start_time = time.monotonic()
            first_line = None
            while time.monotonic() - start_time < data_timeout and self.is_collecting:
                if self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8', errors='replace').strip()
                    if line:
                        first_line = line
                        break
                time.sleep(0.01)
            if not first_line:
                self.ser.close()
                self.ser = None
                self.root.after(0, lambda: messagebox.showerror("No Data", "Error, no incoming data, check port or Arduino code"))
                self.root.after(0, lambda: self.status_var.set("Error: No incoming data from device"))
                self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
                return

            # Got first line, proceed as normal
            self.data_list.append(first_line)
            self.root.after(0, lambda: self.status_var.set("Connection established. Collecting data..."))
            self.root.after(0, lambda: self.update_progress(1, target_samples))
            self.root.after(0, lambda: self.display_new_data(first_line))

            sampling_period_sec = sampling_period / 1000.0
            last_sample_time = time.time()

            while len(self.data_list) < num_samples and self.is_collecting:
                current_time = time.time()
                if current_time - last_sample_time >= sampling_period_sec:
                    if self.ser.in_waiting > 0:
                        line = self.ser.readline().decode('utf-8', errors='replace').strip()
                        if line:
                            self.data_list.append(line)
                            last_sample_time = current_time
                            current_count = min(len(self.data_list), target_samples)
                            self.root.after(0, lambda: self.update_progress(current_count, target_samples))
                            self.root.after(0, lambda: self.display_new_data(line))
                time.sleep(0.001)

            self.ser.close()
            self.ser = None

            if len(self.data_list) >= num_samples:
                self.root.after(0, lambda: self.collection_complete(target_samples))
            else:
                self.root.after(0, lambda: self.collection_stopped(target_samples))

        except Exception as e:
            if self.ser:
                self.ser.close()
                self.ser = None
            self.root.after(0, lambda: messagebox.showerror("Serial Error", f"Error: {str(e)}"))
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
    
    def update_progress(self, current, total):
        """Update progress bar and label"""
        self.progress.config(value=current)
        self.progress_label.config(text=f"{current}/{total}")
    
    def display_new_data(self, line):
        """Add new data line to the text display with rolling window"""
        # Add new line to display
        self.data_text.insert(tk.END, line + "\n")
        self.display_line_count += 1
        
        # If we exceed max lines, remove the oldest line
        if self.display_line_count > self.max_display_lines:
            self.data_text.delete("1.0", "2.0")  # Remove first line
            self.display_line_count = self.max_display_lines  # Keep count accurate
        
        # Auto-scroll to bottom to show newest data
        self.data_text.see(tk.END)
    
    def stop_collection(self):
        """Stop collection and save whatever data we have"""
        self.is_collecting = False  # This will cause the collection loop to exit
    
    def collection_complete(self, target_samples):
        # Called when collection finishes naturally
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.save_data_automatically()
        self.status_var.set(f"Collection complete - saved {target_samples} samples + header")
        
    def collection_stopped(self, target_samples):
        """Called when collection was stopped early - save partial data"""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.save_data_automatically()
        # Calculate actual data samples (total - 1 for header, but don't go negative)
        data_samples = max(0, len(self.data_list) - 1)
        self.status_var.set(f"Collection stopped - saved {data_samples} samples + header")
        
    def is_garbled(self, line):
        """Return True if the line is likely garbled (mostly non-printable characters)."""
        if not line:
            return True
        printable = set(string.printable)
        ratio = sum(1 for c in line if c in printable) / len(line)
        return ratio < 0.7
    
    def save_data_automatically(self):
        if not self.data_list:
            self.status_var.set("No data to save")
            return
        
        filename = self.filename_var.get()
        
        # Check if file exists and auto-rename if needed
        if os.path.exists(filename):
            # Split filename and extension
            name, ext = os.path.splitext(filename)
            # Create timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            # Create new filename with timestamp
            filename = f"{name}_{timestamp}{ext}"
        
        try:
            # Remove garbled first line if present
            data_to_save = self.data_list[:]
            if data_to_save and self.is_garbled(data_to_save[0]):
                data_to_save = data_to_save[1:]
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                for item in data_to_save:
                    writer.writerow(item.split(','))
            self.status_var.set(f"Data saved to {filename}")
        except Exception as e:
            self.status_var.set(f"Error saving data: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialDataCollector(root)
    root.mainloop()