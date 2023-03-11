#!/bin/bash
# Script to automate mass running of the homework checker.
# Correctness not guaranteed. Verify for yourself if the output is correct.
# This script is partially based on the codes from Sourya Kakarla

# Run it simply by ./mass_checker.sh  | tee mass_checker_output.log

# Outputing folder structure here for clarity using "tree" command
# Files/Directories marked as CRITICAL are input dependencies that are essential for script to work

#hw2 % tree -F -L 1
#./
#├── HW2 grade sec1.xlsx    # CRITICAL, assignments sheet downloaded from google drive
#├── atis3.pcfg             # CRITICAL, data
#├── atis3_test.ptb         # CRITICAL, data
#├── checker_outputs/       # log directory which save all checker results
#├── homework2Checker.py    # CRITICAL, auto grader
#├── mass_checker.sh        # CRITICAL, main script to run mass checker
#├── selected_submissions/  # selected submissions from submissions
#├── single_out.py          # CRITICAL, py file which select student names from xslx, then copy and unzip files
#├── src/                   # copy the target student files into this directory
#├── submissions/           # CRITICAL, downloaded from courseworks
#├── target_dirs_found.txt
#└── target_files_found.txt


#Tested on Mac OS

#Parameters
ta_name="Yukun" #Name of TA based on which filtering is done

submissions_dir="submissions" #directory that contains the submissions
selected_submissions_dir="selected_submissions" #directory that contains the assignments need to be graded

excel_fname="HW2 grade sec1.xlsx" #excel for the grading assignments
checker_program="homework2Checker.py" #checker program
dir_found_fname="target_dirs_found.txt" #file that stores paths of the files found in the submissions for the students found
checker_dir="checker_outputs" #output directory for the checker (logs)
src_dir="src" # src directory to hold the files for the checker

# 1) select assigned students name from the xlsx file
# 2) save selected students files into $selected_submissions_dir
# 3) unzip students zip files in $selected_submissions_dir
# 4) find the directory of the student folder which contain .py files and save to $dir_found_fname
python single_out.py --grader_name $ta_name --excel_name "$excel_fname"  \
  --submissions_dir $submissions_dir  --selected_submissions_dir $selected_submissions_dir


# iterate through all selected students folder
# 5) copy the codes of the target student to $src_dir
# 6) run auto_checker and save results to $checker_dir

# create checker_dir
[[ ! -d $checker_dir ]] && mkdir $checker_dir
export PYTHONPATH="$src_dir:$PYTHONPATH"
while read p; do
  folder_dir="$p"
  if [ -d "$folder_dir" ]
  then
    # copy student files into  src folder
    [[ -d $src_dir ]] && rm -rf $src_dir
    cp -r "$folder_dir" "$src_dir"

    # add __init__.py to the folder into python package
    touch "$src_dir/__init__.py"

    # get the student prefix from the dir as name for the log file
    IFS='/' read -ra splits <<< "$folder_dir"
    log_dir=$checker_dir/"${splits[1]}".log

    # run auto-grader
    python  $checker_program > "$log_dir" 2>&1  #Storing the log
    echo "Save results of $folder_dir to $log_dir"
  else
    echo "$folder_dir not found"
  fi
done < "$dir_found_fname"

echo -e "\n\n######Checker output stored in $checker_dir. Number of logs is $(ls -1 $checker_dir | wc -l). Verify the logs to be sure."
