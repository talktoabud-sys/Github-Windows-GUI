#!/usr/bin/env python3
"""
Windows GUI application to digest folders using Gitingest.
Forces UTF-8 encoding globally to avoid cp1252 errors.
"""

import sys
import os

# CRITICAL: Set UTF-8 mode BEFORE any other imports
# This must be the very first thing
os.environ['PYTHONUTF8'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Set locale to UTF-8
import locale
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except:
        pass

from io import StringIO

# Redirect stdout and stderr to prevent logging errors in windowed mode
sys.stdout = StringIO()
sys.stderr = StringIO()

os.environ['LOG_LEVEL'] = 'CRITICAL'
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

# Monkey-patch locale.getpreferredencoding to always return UTF-8
original_getpreferredencoding = locale.getpreferredencoding
def patched_getpreferredencoding(do_setlocale=True):
    return 'utf-8'
locale.getpreferredencoding = patched_getpreferredencoding

# Now import everything else
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import threading
from pathlib import Path


def run_ingest(folder_path, output_file, status_text, progress_bar, window):
    """Run the ingestion with UTF-8 enforcement."""
    try:
        # Patch gitingest's encoding detection before importing
        import gitingest.utils.file_utils as file_utils
        
        # Override _get_preferred_encodings to return UTF-8 first
        original_get_encodings = file_utils._get_preferred_encodings
        def utf8_first_encodings():
            return ['utf-8', 'utf-8-sig', 'latin-1']
        file_utils._get_preferred_encodings = utf8_first_encodings
        
        from gitingest import ingest
        
        status_text.insert(tk.END, f"Processing: {folder_path}\n")
        status_text.insert(tk.END, f"Output: {output_file}\n\n")
        status_text.see(tk.END)
        window.update()
        
        # Run ingestion
        summary, tree, content = ingest(
            source=str(folder_path),
            output=str(output_file)
        )
        
        # Update status
        status_text.insert(tk.END, "="*60 + "\n")
        status_text.insert(tk.END, "SUMMARY\n")
        status_text.insert(tk.END, "="*60 + "\n")
        status_text.insert(tk.END, summary + "\n\n")
        status_text.insert(tk.END, "✓ Digest completed successfully!\n")
        status_text.insert(tk.END, f"✓ Saved to: {output_file}\n")
        status_text.see(tk.END)
        
        progress_bar.stop()
        progress_bar['mode'] = 'determinate'
        progress_bar['value'] = 100
        
        messagebox.showinfo("Success", f"Digest created successfully!\n\nSaved to:\n{output_file}")
        
    except Exception as e:
        progress_bar.stop()
        error_msg = str(e)
        status_text.insert(tk.END, f"\n❌ Error: {error_msg}\n")
        status_text.see(tk.END)
        messagebox.showerror("Error", f"Failed to create digest:\n\n{error_msg}")


class DigestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gitingest Folder Digester")
        self.root.geometry("700x550")
        self.root.resizable(True, True)
        
        # Variables
        self.folder_path = tk.StringVar()
        self.output_path = tk.StringVar(value="digest.txt")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Title
        title_frame = tk.Frame(self.root, bg="#2c3e50", pady=15)
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            title_frame,
            text="📁 Gitingest Folder Digester",
            font=("Arial", 16, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Convert any folder into a prompt-friendly text digest",
            font=("Arial", 9),
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        subtitle_label.pack()
        
        # Main content frame
        content_frame = tk.Frame(self.root, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Folder selection
        folder_frame = tk.LabelFrame(content_frame, text="Select Folder to Digest", padx=10, pady=10)
        folder_frame.pack(fill=tk.X, pady=(0, 10))
        
        folder_entry = tk.Entry(folder_frame, textvariable=self.folder_path, width=50)
        folder_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
        browse_btn = tk.Button(
            folder_frame,
            text="Browse...",
            command=self.browse_folder,
            bg="#3498db",
            fg="white",
            padx=15
        )
        browse_btn.pack(side=tk.LEFT)
        
        # Output file selection
        output_frame = tk.LabelFrame(content_frame, text="Output File", padx=10, pady=10)
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        output_entry = tk.Entry(output_frame, textvariable=self.output_path, width=50)
        output_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
        save_btn = tk.Button(
            output_frame,
            text="Save As...",
            command=self.browse_output,
            bg="#3498db",
            fg="white",
            padx=15
        )
        save_btn.pack(side=tk.LEFT)
        
        # Process button
        self.process_btn = tk.Button(
            content_frame,
            text="🚀 Create Digest",
            command=self.process_folder,
            bg="#27ae60",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10
        )
        self.process_btn.pack(pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            content_frame,
            mode='indeterminate',
            length=300
        )
        self.progress.pack(pady=(0, 10))
        
        # Status text area
        status_frame = tk.LabelFrame(content_frame, text="Status", padx=10, pady=10)
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_text = scrolledtext.ScrolledText(
            status_frame,
            height=10,
            wrap=tk.WORD,
            font=("Consolas", 9)
        )
        self.status_text.pack(fill=tk.BOTH, expand=True)
        self.status_text.insert(tk.END, "Ready to process a folder.\n\n")
        self.status_text.insert(tk.END, "Instructions:\n")
        self.status_text.insert(tk.END, "1. Click 'Browse...' to select a folder\n")
        self.status_text.insert(tk.END, "2. Choose output file location (optional)\n")
        self.status_text.insert(tk.END, "3. Click 'Create Digest' to start\n")
    
    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Folder to Digest")
        if folder:
            self.folder_path.set(folder)
            folder_name = Path(folder).name
            default_output = str(Path(folder).parent / f"{folder_name}_digest.txt")
            self.output_path.set(default_output)
    
    def browse_output(self):
        file = filedialog.asksaveasfilename(
            title="Save Digest As",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file:
            self.output_path.set(file)
    
    def process_folder(self):
        folder = self.folder_path.get()
        output = self.output_path.get()
        
        if not folder:
            messagebox.showwarning("No Folder", "Please select a folder to digest.")
            return
        
        if not Path(folder).exists():
            messagebox.showerror("Invalid Folder", "The selected folder does not exist.")
            return
        
        if not output:
            messagebox.showwarning("No Output", "Please specify an output file.")
            return
        
        self.status_text.delete(1.0, tk.END)
        self.progress['mode'] = 'indeterminate'
        self.progress['value'] = 0
        self.progress.start(10)
        self.process_btn.config(state=tk.DISABLED)
        
        thread = threading.Thread(
            target=lambda: self._process_wrapper(folder, output)
        )
        thread.daemon = True
        thread.start()
    
    def _process_wrapper(self, folder, output):
        """Wrapper to re-enable button after processing."""
        try:
            run_ingest(folder, output, self.status_text, self.progress, self.root)
        finally:
            self.process_btn.config(state=tk.NORMAL)


def main():
    root = tk.Tk()
    app = DigestApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()