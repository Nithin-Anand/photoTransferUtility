import os
import shutil
from tqdm import tqdm
import sys


# TODO:
# List valid drives

# Temporary Test Folder
SD_CARD_FOLDER = 'G:\\DCIM\\101_FUJI\\'



def copy_files(drive: str, path: str, folder: str, ext: str, src_folder: str, mv: bool):
    """Copies file with ext to new, labelled folder

    Moves files to the specified path, which is created in 
    an OS-appropriate way from the constituent parts. Files are 
    moved to a new folder with the extension appended.

    Args:
        drive: 
            The Windows drive letter
        path:
            The folder prefix
        folder:
            The folder name, for example the occasion 
            that the photos are from
        ext:
            The file's extension - typically JPG or RW2
        src_folder:
            Fully-qualified folder path to the source 
            files  
    """
    mixed_photos = os.listdir(src_folder)

    full_extension = '.' + ext
    desired_files = [photo for photo in mixed_photos if photo.endswith(full_extension)]

    dst_folder = folder + '_' + ext.lower()

    parent_path_string = os.path.normpath('{letter}://{path}/{parent}'.format(letter=drive, path=path, parent=folder))
    if not os.path.exists(parent_path_string):
        os.makedirs(parent_path_string)


    path_string = os.path.normpath('{letter}://{path}/{parent}/{folder}'.format(letter=drive, path=path, parent=folder, folder=dst_folder))

    if len(desired_files) == 0:
        print(f"No files found for extension: {ext}")
        return None 

    if not os.path.exists(path_string):
        os.makedirs(path_string)
    

    for file in tqdm(desired_files, colour='green', ):
        if mv:
            shutil.move(os.path.join(src_folder,file), os.path.join(path_string,file))
        else:
            shutil.copy(os.path.join(src_folder,file), os.path.join(path_string,file))

drive_letter = input('Enter the desired drive letter: ')

base_path = input('Enter desired path: ')

dst_folder = input('Enter the folder name you want: ')

move_without_copy = input('If you want to move the files, please enter \'mv\' exactly: ')

if move_without_copy == 'mv':
    move_without_copy = True
else:
    move_without_copy = False


copy_files("F", "", dst_folder, 'JPG', SD_CARD_FOLDER, move_without_copy)
copy_files(drive_letter, base_path, dst_folder, 'RAF', SD_CARD_FOLDER, move_without_copy)
copy_files(drive_letter, base_path, dst_folder, 'MP4', SD_CARD_FOLDER, move_without_copy)
