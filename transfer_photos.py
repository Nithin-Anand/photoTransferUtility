import os
import shutil
from tqdm import tqdm
import tkinter as tk
from tkinter import filedialog, messagebox

class FileCopyMoveUtility:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("File Copy/Move Utility")

        self.src_folder = tk.StringVar()
        self.dst_folder = tk.StringVar()
        self.move_without_copy = tk.BooleanVar()
        self.dry_run = tk.BooleanVar()

        self.create_widgets()

    def create_widgets(self):
        src_folder_frame = tk.Frame(self.window)
        src_folder_frame.pack(pady=10)
        tk.Label(src_folder_frame, text="Source Folder:").pack(side=tk.LEFT)
        tk.Entry(src_folder_frame, width=50, textvariable=self.src_folder).pack(side=tk.LEFT)
        tk.Button(src_folder_frame, text="Browse", command=self.browse_src_folder).pack(side=tk.LEFT, padx=5)

        dst_folder_frame = tk.Frame(self.window)
        dst_folder_frame.pack(pady=5)
        tk.Label(dst_folder_frame, text="Destination Folder:").pack(side=tk.LEFT)
        tk.Entry(dst_folder_frame, width=50, textvariable=self.dst_folder).pack(side=tk.LEFT)
        tk.Button(dst_folder_frame, text="Browse", command=self.browse_dst_folder).pack(side=tk.LEFT, padx=5)

        tk.Checkbutton(self.window, text="Move Files (instead of Copy)", variable=self.move_without_copy).pack(pady=5)
        tk.Checkbutton(self.window, text="Dry Run (No actual copy/move)", variable=self.dry_run).pack(pady=5)
        tk.Button(self.window, text="Start Copy/Move", command=self.start_copy).pack(pady=10)

    def browse_src_folder(self):
        folder_path = filedialog.askdirectory()
        self.src_folder.set(folder_path)

    def browse_dst_folder(self):
        folder_path = filedialog.askdirectory()
        self.dst_folder.set(folder_path)

    def copy_files(self, src_folder, dst_folder, ext, mv, dry_run):
        mixed_photos = os.listdir(src_folder)
        full_extension = f".{ext}"
        desired_files = [photo for photo in mixed_photos if photo.endswith(full_extension)]
        dst_subfolder = f"{os.path.basename(dst_folder)}_{ext.lower()}"
        dst_path = os.path.join(dst_folder, dst_subfolder)

        if not dry_run and not os.path.exists(dst_folder):
            os.makedirs(dst_folder)

        if not desired_files:
            print(f"No files found for extension: {ext}")
            return

        if not dry_run and not os.path.exists(dst_path):
            os.makedirs(dst_path)

        for file in tqdm(desired_files, colour='green'):
            src_file = os.path.join(src_folder, file)
            dst_file = os.path.join(dst_path, file)
            if dry_run:
                print(f"[Dry Run] {'Moving' if mv else 'Copying'}: {src_file} -> {dst_file}")
            else:
                if mv:
                    shutil.move(src_file, dst_file)
                else:
                    shutil.copy(src_file, dst_file)

    def start_copy(self):
        src_folder = self.src_folder.get()
        dst_folder = self.dst_folder.get()
        move_without_copy = self.move_without_copy.get()
        dry_run = self.dry_run.get()

        if not src_folder or not dst_folder:
            messagebox.showwarning("Warning", "Please fill in all required fields.")
            return

        extensions = ["JPG", "RAF", "DNG", "MP4"]

        for ext in extensions:
            self.copy_files(src_folder, dst_folder, ext, move_without_copy, dry_run)

        if dry_run:
            messagebox.showinfo("Dry Run", "Dry run completed. No files were copied/moved.")
        else:
            messagebox.showinfo("Success", "File copy/move operation completed.")

        self.window.quit()  # Close the window after completion

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = FileCopyMoveUtility()
    app.run()