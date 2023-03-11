import os 
import pandas as pd
import shutil
import logging
import zipfile
from os import listdir
from os.path import isfile, join, isdir
import argparse
"""
This py file is modified the code from Angel and does following things: 
1) Select assigned students name from the xlsx file
2) Select assigned students files from "submissions" and save into "selected_submissions"
3) Unzip students zip files in "selected_submissions"
4) Find the directory of the student folder which contain .py files and save to "target_dirs_found.txt"

Hope this helps you save some time! 
"""
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def modify_name(name):
    name_list = name.lower().split()

    if len(name_list) == 3:
        new_name = name_list[1] + name_list[-1] + name_list[0]
        logger.warning(f"If this name is missing, it's possible that coursework have different name order {name_list}")
    elif len(name_list) == 2:
        new_name = name_list[-1] + name_list[0]
    else:
        new_name = "".join(name_list[::])
        logger.warning(f"If this name is missing, it's possible that coursework have different name order {name_list}")

    new_name = new_name.replace("-", "")
    return new_name

def get_log_dir(directory):
    return directory.splits()

class Single_Out(): 
    def __init__(self,  grader_name, excel_filename="HW2 grade sec1.xlsx",
                 src_path="submissions", out_path="selected_submissions"):
        self.excel_filename = excel_filename
        self.src_path = src_path
        self.out_path = out_path
        self.grader_name = grader_name

        self.my_student_prefixes = self.get_my_students()
        self.output_file_names()
        self.unzip_files(src_path=self.out_path, dst_path=self.out_path)


    def get_my_students(self): 
        excel_df = pd.read_excel(self.excel_filename)
        excel_df = excel_df[excel_df["Grader"] == self.grader_name]
        full_names = list(excel_df["Name"])
        logger.info(f"Ideal number of files to capture: {len(full_names)}")
        return [modify_name(name) for name in full_names]
    
    def check_starts_with(self, filename): 
        for prefix in self.my_student_prefixes: 
            if filename.startswith(prefix): 
                return True
        return False

    def create_dir(self, directory):
        if not os.path.isdir(directory):
            os.makedirs(directory)
            logger.info(f"created folder : {directory}")
        else:
            logger.info(f"{directory} folder already exists.")

    def output_file_names(self):
        target_files = []
        directory = os.fsencode(self.src_path)
        cnt = 0
        self.create_dir(self.out_path)

        for i, file in enumerate(os.listdir(directory)):
            filename = os.fsdecode(file)
            if self.check_starts_with(filename):
                src = os.path.join(self.src_path, filename)
                dst = os.path.join(self.out_path, filename)
                target_files.append(dst)
                shutil.copyfile(src, dst)
                cnt += 1

        target_files = sorted(target_files)
        with open("target_files_found.txt", 'w') as f:
            f.write('\n'.join(target_files) + '\n')
        logger.info(f"num of files found: {cnt}")

    def unzip_files(self, src_path, dst_path):
        zip_files = [f for f in listdir(src_path) if isfile(join(src_path, f)) if f.endswith(".zip")]

        target_folders = []
        # unzip files
        for zip_file in zip_files:
            logger.info(f"unzip {zip_file}")
            with zipfile.ZipFile(os.path.join(src_path, zip_file), 'r') as zip_ref:
                folder_name = os.path.join(dst_path, zip_file.split(".zip")[0])
                zip_ref.extractall(folder_name)
                target_folders.append(folder_name)

        logger.info(f"unzip {len(zip_files)} zip files")
        target_folders = sorted(target_folders)

        target_dirs = []
        # find the folder with .py files
        for target_folder in target_folders:
            py_files = [f for f in listdir(target_folder) if isfile(join(target_folder, f)) and f.endswith(".py")]
            # if py files not exist in current dir, go to the subdir
            if len(py_files) == 0:
                subfolders = [f for f in listdir(target_folder) if isdir(join(target_folder, f)) and "MACOSX" not in f]
                assert len(subfolders) == 1, "incorrect directory"
                target_folder = join(target_folder, subfolders[0])
            target_dirs.append(target_folder)

        target_dirs_fname = "target_dirs_found.txt"
        with open(target_dirs_fname, 'w') as f:
            f.write('\n'.join(target_dirs) + '\n')
        logger.info(f"Unzipped folder dirs are saved to {target_dirs_fname}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--grader_name", type=str, required=True)
    parser.add_argument("--excel_name", type=str, default="HW2 grade sec1.xlsx")
    parser.add_argument("--submissions_dir", type=str, default="submissions")
    parser.add_argument("--selected_submissions_dir", type=str, default="selected_submissions")
    args = parser.parse_args()

    single_out = Single_Out(args.grader_name, excel_filename=args.excel_name,
                            src_path=args.submissions_dir, out_path=args.selected_submissions_dir)
