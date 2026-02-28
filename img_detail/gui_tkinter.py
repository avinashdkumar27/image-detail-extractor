import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import json
import os
from metadata_extractor import MetadataExtractor

class MetadataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Detail Extractor - Intelligence Tool")
        self.root.geometry("900x700")
        self.root.configure(bg="#1e1e1e")
        
        self.filepath = None
        self.extractor = None
        self.metadata = None
        self.raw_exif_visible = False
        
        self.setup_ui()
        
    def setup_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#1e1e1e")
        style.configure("TLabel", background="#1e1e1e", foreground="#ffffff", font=("Segoe UI", 10))
        style.configure("TButton", background="#333333", foreground="#ffffff", font=("Segoe UI", 10, "bold"), padding=5)
        style.map("TButton", background=[("active", "#555555")])
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#4DA8DA")
        
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(top_frame, text="Image Metadata Intelligence", style="Header.TLabel").pack(side=tk.LEFT)
        ttk.Button(top_frame, text="Upload Image", command=self.upload_image).pack(side=tk.RIGHT, padx=5)
        
        self.paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        left_panel = ttk.Frame(self.paned_window)
        self.paned_window.add(left_panel, weight=1)
        
        self.img_label = ttk.Label(left_panel, text="No Image Selected", anchor="center")
        self.img_label.pack(fill=tk.BOTH, expand=True, pady=10)
        
        action_frame = ttk.Frame(left_panel)
        action_frame.pack(fill=tk.X, pady=10)
        
        self.btn_export = ttk.Button(action_frame, text="Export JSON", command=self.export_json, state=tk.DISABLED)
        self.btn_export.pack(fill=tk.X, pady=2)
        
        self.btn_strip = ttk.Button(action_frame, text="Strip Metadata", command=self.strip_metadata, state=tk.DISABLED)
        self.btn_strip.pack(fill=tk.X, pady=2)
        
        self.btn_toggle_exif = ttk.Button(action_frame, text="Show Raw EXIF", command=self.toggle_raw_exif, state=tk.DISABLED)
        self.btn_toggle_exif.pack(fill=tk.X, pady=2)
        
        right_panel = ttk.Frame(self.paned_window)
        self.paned_window.add(right_panel, weight=2)
        
        self.text_area = tk.Text(right_panel, bg="#2d2d2d", fg="#ffffff", font=("Consolas", 10), wrap=tk.WORD, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(right_panel, command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=scrollbar.set)
        
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def upload_image(self):
        filetypes = (
            ("Image files", "*.jpg *.jpeg *.png *.tiff *.webp"),
            ("All files", "*.*")
        )
        self.filepath = filedialog.askopenfilename(title="Select an image", filetypes=filetypes)
        if self.filepath:
            self.load_image()
            self.extract_data()

    def load_image(self):
        try:
            img = Image.open(self.filepath)
            img.thumbnail((300, 300))
            self.photo = ImageTk.PhotoImage(img)
            self.img_label.configure(image=self.photo, text="")
        except Exception as e:
            self.img_label.configure(text=f"Error loading preview: {str(e)}", image="")

    def extract_data(self):
        self.extractor = MetadataExtractor(self.filepath)
        self.metadata = self.extractor.extract_all()
        
        self.btn_export.config(state=tk.NORMAL)
        self.btn_strip.config(state=tk.NORMAL)
        self.btn_toggle_exif.config(state=tk.NORMAL)
        self.raw_exif_visible = False
        self.btn_toggle_exif.config(text="Show Raw EXIF")
        
        self.display_metadata()

    def display_metadata(self):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        
        if not self.metadata:
            self.text_area.insert(tk.END, "No metadata available.")
            self.text_area.config(state=tk.DISABLED)
            return
            
        def insert_bold(text):
            self.text_area.insert(tk.END, text + "\n", "bold")
            
        self.text_area.tag_configure("bold", font=("Consolas", 11, "bold"), foreground="#4DA8DA")
        self.text_area.tag_configure("alert", font=("Consolas", 10, "bold"), foreground="#ff4c4c")
        
        insert_bold("=== BASIC INFORMATION ===")
        if "Error" in self.metadata["Basic Info"]:
            self.text_area.insert(tk.END, self.metadata["Basic Info"]["Error"] + "\n\n")
        else:
            for k, v in self.metadata["Basic Info"].items():
                self.text_area.insert(tk.END, f"{k:25}: {v}\n")
        
        self.text_area.insert(tk.END, "\n")
        insert_bold("=== SECURITY & FORENSIC ===")
        for k, v in self.metadata["Security / Forensic Info"].items():
            self.text_area.insert(tk.END, f"{k:25}: {v}\n")
        
        self.text_area.insert(tk.END, "\n")
        insert_bold("=== EXIF & PRIVACY ===")
        exif_info = self.metadata.get("EXIF Info", {})
        if "Error" in exif_info:
            self.text_area.insert(tk.END, exif_info["Error"] + "\n")
        else:
            cam = exif_info.get("Camera Info", {})
            self.text_area.insert(tk.END, f"{'Camera Make':25}: {cam.get('Make', 'N/A')}\n")
            self.text_area.insert(tk.END, f"{'Camera Model':25}: {cam.get('Model', 'N/A')}\n")
            
            highlights = exif_info.get("Highlights", {})
            if highlights:
                self.text_area.insert(tk.END, "\n--- Shooting Parameters ---\n")
                for k, v in highlights.items():
                    self.text_area.insert(tk.END, f"{k:25}: {v}\n")
            
            self.text_area.insert(tk.END, "\n--- Editing & Privacy ---\n")
            sus = exif_info.get("Likely Manipulated", False)
            self.text_area.insert(tk.END, f"{'Software':25}: {exif_info.get('Software', 'N/A')}\n")
            if sus:
                self.text_area.insert(tk.END, f"⚠️ WARNING: Image may be edited/manipulated!\n", "alert")
            
            risk = exif_info.get("Privacy Risk (GPS Data Found)", False)
            self.text_area.insert(tk.END, f"{'GPS Coordinates':25}: {exif_info.get('GPS Coordinates', 'N/A')}\n")
            if risk:
                self.text_area.insert(tk.END, f"🚨 PRIVACY RISK: GPS location embedded!\n", "alert")
                
        if self.raw_exif_visible and "Raw EXIF" in exif_info:
            self.text_area.insert(tk.END, "\n")
            insert_bold("=== RAW EXIF DUMP ===")
            for k, v in exif_info["Raw EXIF"].items():
                self.text_area.insert(tk.END, f"{k}: {v}\n")

        self.text_area.config(state=tk.DISABLED)

    def toggle_raw_exif(self):
        self.raw_exif_visible = not self.raw_exif_visible
        if self.raw_exif_visible:
            self.btn_toggle_exif.config(text="Hide Raw EXIF")
        else:
            self.btn_toggle_exif.config(text="Show Raw EXIF")
        self.display_metadata()

    def export_json(self):
        if not self.metadata:
            return
            
        save_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile=f"{os.path.splitext(os.path.basename(self.filepath))[0]}_metadata.json"
        )
        if save_path:
            try:
                with open(save_path, "w") as f:
                    json.dump(self.metadata, f, indent=4)
                messagebox.showinfo("Success", f"Metadata exported to {save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")

    def strip_metadata(self):
        if not self.extractor:
            return
            
        save_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")],
            initialfile=f"{os.path.splitext(os.path.basename(self.filepath))[0]}_stripped.jpg"
        )
        
        if save_path:
            success, msg = self.extractor.strip_metadata(save_path)
            if success:
                messagebox.showinfo("Success", msg)
            else:
                messagebox.showerror("Error", msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = MetadataApp(root)
    root.mainloop()
