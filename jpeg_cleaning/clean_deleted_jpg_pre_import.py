import os
import tkinter as tk
from tkinter import filedialog, messagebox

class RAFFileCleaner:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("RAF File Cleaner")

        self.folder_path = tk.StringVar()
        self.dry_run = tk.BooleanVar()

        self.create_widgets()

    def create_widgets(self):
        folder_frame = tk.Frame(self.window)
        folder_frame.pack(pady=10)

        tk.Label(folder_frame, text="JPG Folder:").pack(side=tk.LEFT)
        tk.Entry(folder_frame, width=50, textvariable=self.folder_path).pack(side=tk.LEFT)
        tk.Button(folder_frame, text="Browse", command=self.browse_folder).pack(side=tk.LEFT, padx=5)

        tk.Checkbutton(self.window, text="Dry Run", variable=self.dry_run).pack()
        tk.Button(self.window, text="Clean RAF Files", command=self.clean_raf_files).pack(pady=10)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)

    def clean_raf_files(self):
        sd_folder = self.folder_path.get()


        all_files = set(os.listdir(sd_folder))        

        files_to_delete = sorted([file for file in all_files if file.replace(".RAF", ".JPG") not in all_files])

        if self.dry_run.get():
            messagebox.showinfo("Dry Run", "Files that would be deleted:\n" + "\n".join(files_to_delete))
        else:
            for file in files_to_delete:
                file_path = os.path.join(sd_folder, file)
                os.remove(file_path)
                print(f"Deleted: {file_path}")

            messagebox.showinfo("Cleaning Completed", "RAF files cleaned successfully.")

        self.window.quit()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    cleaner = RAFFileCleaner()
    cleaner.run()