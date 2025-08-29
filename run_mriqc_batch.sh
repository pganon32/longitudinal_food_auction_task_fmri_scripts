#!/bin/bash
# filepath: /home/username/Documents/projectname/scripts/submit_jobs.sh

# Define the input directory containing sourcedata
input_dir=~/projects/def-account/share/projectname/data2/

# Loop through each directory in sourcedata
for subject_dir in "$input_dir"/*; do
  if [ -d "$subject_dir" ]; then
    # Extract the subject name from the directory path
    subject_name=$(basename "$subject_dir")
    
    # Submit the sbatch job for the subject
    echo "Submitting job for subject: $subject_name"
    sbatch --export=SUBJECT_NAME="$subject_name" $HOME/projects/def-account/share/projectname/scripts/scripts_mriqc/mriqc_single_run.sh
  fi
done
