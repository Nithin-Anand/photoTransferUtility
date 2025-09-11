import os
import tkinter as tk
from tkinter import filedialog, messagebox


class ImageFileCleaner:

    def init(self):
        self.window = tk.Tk()
        self.window.title("Image File Cleaner")
        self.folder_path = tk.StringVar()
        self.dry_run = tk.BooleanVar()
        self.clean_raf = tk.BooleanVar(value=True)
        self.clean_dng = tk.BooleanVar(value=True)

        self.create_widgets()


    def create_widgets(self):
        folder_frame = tk.Frame(self.window)
        folder_frame.pack(pady=10)

        tk.Label(folder_frame, text="JPG Folder:").pack(side=tk.LEFT)
        tk.Entry(folder_frame, width=50,
                textvariable=self.folder_path).pack(side=tk.LEFT)
        tk.Button(folder_frame, text="Browse",
                command=self.browse_folder).pack(side=tk.LEFT, padx=5)

        options_frame = tk.Frame(self.window)
        options_frame.pack(pady=5)

        tk.Checkbutton(options_frame, text="Clean RAF Files",
                    variable=self.clean_raf).pack(side=tk.LEFT)
        tk.Checkbutton(options_frame, text="Clean DNG Files",
                    variable=self.clean_dng).pack(side=tk.LEFT, padx=10)

        tk.Checkbutton(self.window, text="Dry Run", variable=self.dry_run).pack()
        tk.Button(self.window, text="Clean Image Files",
                command=self.clean_image_files).pack(pady=10)


    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)


    def clean_image_files(self):
        jpg_folder = self.folder_path.get()

        if not jpg_folder:
            messagebox.showwarning("Warning", "Please select a JPG folder.")
            return

        jpg_files = set(os.listdir(jpg_folder))

        if self.clean_raf.get():
            self.clean_files(jpg_folder, jpg_files, "_raf", ".RAF")

        if self.clean_dng.get():
            self.clean_files(jpg_folder, jpg_files, "_dng", ".DNG")

        self.window.quit()


    def clean_files(self, jpg_folder, jpg_files, folder_suffix, file_extension):
        image_folder = jpg_folder.replace("_jpg", folder_suffix)

        if not os.path.exists(image_folder):
            messagebox.showwarning(
                "Warning", f"Corresponding {folder_suffix.upper()} folder not found: {image_folder}")
            return

        image_files = set(os.listdir(image_folder))

        files_to_delete = sorted([file for file in image_files if file.replace(
            file_extension, ".JPG") not in jpg_files])

        if self.dry_run.get():
            messagebox.showinfo(
                "Dry Run", f"Files that would be deleted from {folder_suffix.upper()} folder:\n" + "\n".join(files_to_delete))
        else:
            for file in files_to_delete:
                file_path = os.path.join(image_folder, file)
                os.remove(file_path)
                print(f"Deleted: {file_path}")

            messagebox.showinfo(
                "Cleaning Completed", f"{folder_suffix.upper()} files cleaned successfully.")


    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    cleaner = ImageFileCleaner()
    cleaner.run()
