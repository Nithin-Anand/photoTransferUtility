import os
import shutil
from tqdm import tqdm
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import List

from save_data_handler import SaveDataHandler


class FileCopyMoveUtility:
    def __init__(self, save_data_handler: SaveDataHandler) -> None:

        self.save_data_handler: SaveDataHandler = save_data_handler

        self.window: tk.Tk = tk.Tk()
        self.window.title("File Copy/Move Utility")

        # Tkinter variable types
        self.src_folder: tk.StringVar = tk.StringVar(value=self.save_data_handler.source_path)
        self.dst_folder: tk.StringVar = tk.StringVar(value=self.save_data_handler.destination_path)
        self.move_without_copy: tk.BooleanVar = tk.BooleanVar()
        self.dry_run: tk.BooleanVar = tk.BooleanVar()

        self.create_widgets()

    def create_widgets(self) -> None:
        src_folder_frame: tk.Frame = tk.Frame(self.window)
        src_folder_frame.pack(pady=10)
        tk.Label(src_folder_frame, text="Source Folder:").pack(side=tk.LEFT)
        tk.Entry(src_folder_frame, width=50, textvariable=self.src_folder).pack(side=tk.LEFT)
        tk.Button(src_folder_frame, text="Browse", command=self.browse_src_folder).pack(side=tk.LEFT, padx=5)

        dst_folder_frame: tk.Frame = tk.Frame(self.window)
        dst_folder_frame.pack(pady=5)
        tk.Label(dst_folder_frame, text="Destination Folder:").pack(side=tk.LEFT)
        tk.Entry(dst_folder_frame, width=50, textvariable=self.dst_folder).pack(side=tk.LEFT)
        tk.Button(dst_folder_frame, text="Browse", command=self.browse_dst_folder).pack(side=tk.LEFT, padx=5)

        tk.Checkbutton(self.window, text="Move Files (instead of Copy)", variable=self.move_without_copy).pack(pady=5)
        tk.Checkbutton(self.window, text="Dry Run (No actual copy/move)", variable=self.dry_run).pack(pady=5)
        tk.Button(self.window, text="Start Copy/Move", command=self.start_copy).pack(pady=10)

    def browse_src_folder(self) -> None:
        folder_path: str = filedialog.askdirectory()
        if folder_path:
            self.src_folder.set(folder_path)

    def browse_dst_folder(self) -> None:
        folder_path: str = filedialog.askdirectory()
        if folder_path:
            self.dst_folder.set(folder_path)

    def copy_files(self, src_folder: str, dst_folder: str, ext: str, mv: bool, dry_run: bool) -> None:
        """Copy or move files with a specific extension from src_folder to a subfolder under dst_folder.

        Args:
            src_folder: Source directory path.
            dst_folder: Destination directory path.
            ext: File extension to filter (without leading dot), case-sensitive match.
            mv: If True, move files; otherwise copy.
            dry_run: If True, only print planned actions.
        """
        mixed_photos: List[str] = os.listdir(src_folder)
        full_extension: str = f".{ext.upper()}"
        desired_files: List[str] = [photo for photo in mixed_photos if photo.upper().endswith(full_extension)]
        dst_subfolder: str = f"{os.path.basename(dst_folder)}_{ext.lower()}"
        dst_path: str = os.path.join(dst_folder, dst_subfolder)

        if not dry_run and not os.path.exists(dst_folder):
            os.makedirs(dst_folder)

        if not desired_files:
            print(f"No files found for extension: {ext}")
            return

        if not dry_run and not os.path.exists(dst_path):
            os.makedirs(dst_path)

        for file in tqdm(desired_files, colour='green'):
            src_file: str = os.path.join(src_folder, file)
            dst_file: str = os.path.join(dst_path, file)
            if dry_run:
                print(f"[Dry Run] {'Moving' if mv else 'Copying'}: {src_file} -> {dst_file}")
            else:
                if mv:
                    shutil.move(src_file, dst_file)
                else:
                    shutil.copy(src_file, dst_file)

    def start_copy(self) -> None:
        src_folder: str = self.src_folder.get()
        dst_folder: str = self.dst_folder.get()
        move_without_copy: bool = bool(self.move_without_copy.get())
        dry_run: bool = bool(self.dry_run.get())

        if not src_folder or not dst_folder:
            messagebox.showwarning("Warning", "Please fill in all required fields.")
            return

        extensions: List[str] = ["JPG", "RAF", "DNG", "MP4"]

        for ext in extensions:
            self.copy_files(src_folder, dst_folder, ext, move_without_copy, dry_run)

        if dry_run:
            messagebox.showinfo("Dry Run", "Dry run completed. No files were copied/moved.")
        else:
            messagebox.showinfo("Success", "File copy/move operation completed.")

        # Persist the last used settings
        self.save_data_handler.update_settings(src_folder, dst_folder)

        self.window.quit()  # Close the window after completion

    def run(self) -> None:
        self.window.mainloop()
