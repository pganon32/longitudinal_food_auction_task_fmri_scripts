#!/bin/bash
#SBATCH --account=def-account
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=5000M
#SBATCH --time=0-00:5           # time (DD-HH:MM) ~10min/participant
#SBATCH --job-name="BIDS convert"


# Create a directory for SLURM output and error files in $SCRATCH
scratch_dir="$SCRATCH/slurm_logs"
mkdir -p "$scratch_dir"

# Specify output and error file locations
#SBATCH --output="$scratch_dir/%x_%j.out"
#SBATCH --error="$scratch_dir/%x_%j.err"

# Array for all subject IDs : 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,19,20,21,24,25
#This script were writting to use on Alliance Canada.
#This script convert all DICOM files from data/sourcedata/* to nifti or json with dcm2niix, reorient nifti in RPI and rename files to fit with BIDS format.

# To run locally for a test, uncomment the following line
# SLURM_ARRAY_TASK_ID=1

module load dcm2niix

# Use SUBJECT_NAME passed by sbatch
if [ -z "$SUBJECT_NAME" ]; then
  echo "SUBJECT_NAME is not set. Exiting script."
  exit 1
fi

name="$SUBJECT_NAME"


input_dir=~/projects/def-account/share/projectname/data
output_dir=~/projects/def-account/share/projectname/data2

if [ ! -d "$input_dir/sourcedata/$name/DICOM" ]; then
  echo "$name"
  echo "Source directory does not exist. Exiting script."
  exit 1
fi

for file in $input_dir/sourcedata/$name/DICOM/*/; do
#for file in $dir/sourcedata/SUBJ005/DICOM/*/; do

  #name=$(echo $file| cut  -d'/' -f 10) #find the subject id
  ses=$(echo $file| cut  -d'/' -f 12) #find the session number
   if [[ ${ses} = 'BL' ]]; then
    session=1
  elif [[ ${ses} = '4M' ]]; then
    session=2
  elif [[ ${ses} = '12M' ]]; then
    session=3
  elif [[ ${ses} = '24M' ]]; then
    session=4
  elif [[ ${ses} = '60M' ]]; then
    session=5
  else
    session=x
  fi
  echo "Processing subject: $name"
  echo "Session: $ses"

# Check if the directory exists
  if [ ! -d "$output_dir/sub-${name}/ses-${session}" ]; then
    mkdir -p $output_dir/sub-${name}/ses-${session}/{anat,func,fmap}
  fi



  #mkdir $dir/sub-${name}/ses-${session}/{anat,func,fmap} -p
# Debugging: Print the pattern being checked
echo "DEBUG: Checking for files with pattern: $output_dir/sub-${name}/ses-${session}/sub-*${name}*.nii.gz"

# Check if NIfTI files already exist
if find "$output_dir/sub-${name}/ses-${session}" -maxdepth 1 -type f -name "sub-*${name}*.nii.gz" | grep -q .; then
  echo "NIfTI files already exist for subject $name, session $session. Skipping conversion."
else
  echo "No existing NIfTI files found. Starting conversion for subject $name, session $session."
  dcm2niix -o "$output_dir/sub-${name}/ses-${session}" -b y -m y -z y -p y -s y -f sub-%i_%t_%p "$input_dir/sourcedata/${name}/DICOM/${ses}/"
fi

done

  #./dcm2niix -o $dir/sub-${name}/ses-${session} -b y -m y -z y -p y -s y -f sub-%i_%t_%p $dir/sourcedata/${name}/DICOM/${ses}/

  #anat
  # Check if the FOV file exists
#  if ls $dir/sub-${name}/ses-${session}/*T1W_3D_TFE_FOV*.nii.gz 1> /dev/null 2>&1; then
    # Use the FOV file if it exists
   # input_file=$(ls $dir/sub-${name}/ses-${session}/*T1W_3D_TFE_FOV*.nii.gz)
 #   json_file=$(ls $dir/sub-${name}/ses-${session}/*T1W_3D_TFE_FOV*.json)
 # else
    # Otherwise, use the TFE file
  #  input_file=$(ls $dir/sub-${name}/ses-${session}/*T1W_3D_TFE*.nii.gz)
  #  json_file=$(ls $dir/sub-${name}/ses-${session}/*T1W_3D_TFE*.json)
#  fi

# Reorient the NIfTI file
#fslreorient2std $input_file $dir/sub-${name}/ses-${session}/anat/sub-${name}_ses-${session}_T1w.nii.gz 2>&1

# Move the JSON file
#mv $json_file $dir/sub-${name}/ses-${session}/anat/sub-${name}_ses-${session}_T1w.json

 # fslreorient2std $dir/sub-${name}/ses-${session}/*T1W_3D_TFE*.nii.gz $dir/sub-${name}/ses-${session}/anat/sub-${name}_ses-${session}_T1w.nii.gz 2>&1
  # mv $dir/sub-${name}/ses-${session}/*T1W_3D_TFE*.json $dir/sub-${name}/ses-${session}/anat/sub-${name}_ses-${session}_T1w.json


  #func
#  fslreorient2std  $dir/sub-${name}/ses-${session}/*FOOD1*.nii.gz $dir/sub-${name}/ses-${session}/func/sub-${name}_ses-${session}_task-BDM_run-1_bold.nii.gz 2>&1
#  fslreorient2std  $dir/sub-${name}/ses-${session}/*FOOD2*.nii.gz $dir/sub-${name}/ses-${session}/func/sub-${name}_ses-${session}_task-BDM_run-2_bold.nii.gz 2>&1
#  fslreorient2std  $dir/sub-${name}/ses-${session}/*FOOD3*.nii.gz $dir/sub-${name}/ses-${session}/func/sub-${name}_ses-${session}_task-BDM_run-3_bold.nii.gz 2>&1
#   mv $dir/sub-${name}/ses-${session}/*FOOD1*.json $dir/sub-${name}/ses-${session}/func/sub-${name}_ses-${session}_task-BDM_run-1_bold.json
#   mv $dir/sub-${name}/ses-${session}/*FOOD2*.json $dir/sub-${name}/ses-${session}/func/sub-${name}_ses-${session}_task-BDM_run-2_bold.json
#   mv $dir/sub-${name}/ses-${session}/*FOOD3*.json $dir/sub-${name}/ses-${session}/func/sub-${name}_ses-${session}_task-BDM_run-3_bold.json
#   sed -i '$s/}/,\n"TaskName":"BDM"}/' $dir/sub-${name}/ses-${session}/func/sub-${name}_ses-${session}_task-BDM_run*.json

 # fslreorient2std $dir/sub-${name}/ses-${session}/*FOOD1.nii.gz $dir/sub-${name}/ses-${session}/func/sub-${name}_ses-${session}_task-BDM_run-1_bold.nii.gz
  #fslreorient2std $dir/sub-${name}/ses-${session}/*FOOD2.nii.gz $dir/sub-${name}/ses-${session}/func/sub-${name}_ses-${session}_task-BDM_run-2_bold.nii.gz
 # fslreorient2std $dir/sub-${name}/ses-${session}/*FOOD3.nii.gz $dir/sub-${name}/ses-${session}/func/sub-${name}_ses-${session}_task-BDM_run-3_bold.nii.gz
 #  mv $dir/sub-${name}/ses-${session}/*FOOD1.json $dir/sub-${name}/ses-${session}/func/sub-${name}_ses-${session}_task-BDM_run-1_bold.json
 #  mv $dir/sub-${name}/ses-${session}/*FOOD2.json $dir/sub-${name}/ses-${session}/func/sub-${name}_ses-${session}_task-BDM_run-2_bold.json
 #  mv $dir/sub-${name}/ses-${session}/*FOOD3.json $dir/sub-${name}/ses-${session}/func/sub-${name}_ses-${session}_task-BDM_run-3_bold.json
 #  sed -i '$s/}/,\n"TaskName":"BDM"}/' $dir/sub-${name}/ses-${session}/func/sub-${name}_ses-${session}_task-BDM_run*.json


  #fmap
#    fslreorient2std   $dir/sub-${name}/ses-${session}/*B0*_fieldmaphz*.nii.gz $dir/sub-${name}/ses-${session}/fmap/sub-${name}_ses-${session}_fieldmap.nii.gz 2>&1
#    fslreorient2std   $dir/sub-${name}/ses-${session}/*B0*_e1*.nii.gz $dir/sub-${name}/ses-${session}/fmap/sub-${name}_ses-${session}_magnitude.nii.gz 2>&1
#    mv $dir/sub-${name}/ses-${session}/*B0*_fieldmaphz*.json $dir/sub-${name}/ses-${session}/fmap/sub-${name}_ses-${session}_fieldmap.json
#    mv $dir/sub-${name}/ses-${session}/*B0*_e1*.json $dir/sub-${name}/ses-${session}/fmap/sub-${name}_ses-${session}_magnitude.json

  #remove nifti
#  rm $dir/sub-${name}/ses-${session}/sub-*



  #temp/MRIConvert-2.1.0/usr/bin/mcverter  \-o projects/def-account/jdaoust/neurocognition/data/sub-${name}/ses-${session} \-f fsl -n projects/def-account/jdaoust/neurocognition/sourcedata/${name}/DICOM/*/*

  #dcm2bids -d projects/def-account/jdaoust/neurocognition/sourcedata/${name}/DICOM/*/* -c -p sub-${name} -s ses-${session} -o projects/def-account/jdaoust/neurocognition/data/

  #dcm2bids -d projects/def-account/jdaoust/neurocognition/data/sourcedata/NCG017/DICOM/BL/* -p NCG017urocognition/scripts/config.json -o projects/def-account/jdaoust/neurocognition/data/

#fslreorient2std sub-NEUROC-NCG017-KP-BL_20210715103705_WIP_T1W_3D_TFE_201_1.3.46.670589.11.71300.5.0.2120.2021071510390834015.nii sub-001_T1w_reoriented

  #dcm2niix -o ~/projects/def-account/jdaoust/neurocognition/data/data_BIDS/sub-${name}/ses-${session}/ -r y -f %i_%s_%t_%p ~/projects/def-account/jdaoust/neurocognition/data/data_raw/${name}/DICOM/*/*

  #T1w
  #scp ~/projects/def-account/share/dagher6_back_up/raw/${name}/DICOM/mcverter/*T1W*_orient.nii.gz ~/JDaoust_project/data/BIDS/sub-${name::6}/ses-${session}/anat/sub-${name::6}_ses-${session}_T1w.nii.gz
  #mv ~/projects/def-account/jdaoust/neurocognition/data/data_BIDS/sub-${name}/ses-${session}/*T1W*.nii ~/projects/def-account/jdaoust/neurocognition/data/data_BIDS/sub-${name::6}/ses-${session}/anat/sub-${name::6}_ses-${session}_T1w.nii
  #gzip ~/JDaoust_project/data/BIDS/sub-${name::6}/ses-${session}/anat/sub-${name::6}_ses-${session}_T1w.nii
  #mv ~/projects/def-account/jdaoust/neurocognition/data/data_BIDS/sub-${name}/ses-${session}/*T1W*.json ~/projects/def-account/jdaoust/neurocognition/data/data_BIDS/sub-${name}/ses-${session}/anat/sub-${name}_ses-${session}_T1w.json

  #BDM-run1
  #scp ~/projects/def-account/share/dagher6_back_up/raw/${name}/DICOM/mcverter/*FOOD1_orient_cut.nii.gz ~/JDaoust_project/data/BIDS/sub-${name::6}/ses-${session}/func/sub-${name::6}_ses-${session}_task-BDM_run-1_bold.nii.gz
  #scp ~/projects/def-account/share/dagher6_back_up/raw/${name}/DICOM/mcverter/*FOOD1_orient_cut.nii ~/JDaoust_project/data/BIDS/sub-${name::6}/ses-${session}/func/sub-${name::6}_ses-${session}_task-BDM_run-1_bold.nii
  #gzip ~/JDaoust_project/data/BIDS/sub-${name::6}/ses-${session}/func/sub-${name::6}_ses-${session}_task-BDM_run-1_bold.nii
  #mv ~/JDaoust_project/data/BIDS/sub-${name::6}/ses-${session}/*FOOD1*.json ~/JDaoust_project/data/BIDS/sub-${name::6}/ses-${session}/func/sub-${name::6}_ses-${session}_task-BDM_run-1_bold.json

  #BDM-run2
  #scp ~/projects/def-account/share/dagher6_back_up/raw/${name}/DICOM/mcverter/*FOOD2_orient_cut.nii.gz ~/JDaoust_project/data/BIDS/sub-${name::6}/ses-${session}/func/sub-${name::6}_ses-${session}_task-BDM_run-2_bold.nii.gz
  #scp ~/projects/def-account/share/dagher6_back_up/raw/${name}/DICOM/mcverter/*FOOD2_orient_cut.nii ~/JDaoust_project/data/BIDS/sub-${name::6}/ses-${session}/func/sub-${name::6}_ses-${session}_task-BDM_run-2_bold.nii
  #gzip ~/JDaoust_project/data/BIDS/sub-${name::6}/ses-${session}/func/sub-${name::6}_ses-${session}_task-BDM_run-2_bold.nii
  #mv ~/JDaoust_project/data/BIDS/sub-${name::6}/ses-${session}/*FOOD2*.json ~/JDaoust_project/data/BIDS/sub-${name::6}/ses-${session}/func/sub-${name::6}_ses-${session}_task-BDM_run-2_bold.json

  #BDM-run3
  #scp ~/projects/def-account/share/dagher6_back_up/raw/${name}/DICOM/mcverter/*FOOD3_orient_cut.nii.gz ~/JDaoust_project/data/BIDS/sub-${name::6}/ses-${session}/func/sub-${name::6}_ses-${session}_task-BDM_run-3_bold.nii.gz
  #scp ~/projects/def-account/share/dagher6_back_up/raw/${name}/DICOM/mcverter/*FOOD3_orient_cut.nii ~/JDaoust_project/data/BIDS/sub-${name::6}/ses-${session}/func/sub-${name::6}_ses-${session}_task-BDM_run-3_bold.nii
  #gzip ~/JDaoust_project/data/BIDS/sub-${name::6}/ses-${session}/func/sub-${name::6}_ses-${session}_task-BDM_run-3_bold.nii
  #mv ~/JDaoust_project/data/BIDS/sub-${name::6}/ses-${session}/*FOOD3*.json ~/JDaoust_project/data/BIDS/sub-${name::6}/ses-${session}/func/sub-${name::6}_ses-${session}_task-BDM_run-3_bold.json

  #sed -i '$s/}/,\n"TaskName":"BDM"}/' ~/JDaoust_project/data/BIDS/sub-${name::6}/ses-${session}/func/sub-${name::6}_ses-${session}_task-BDM_run*.json
  #jq 'del(.ImageOrientationPatientDICOM)' ~/JDaoust_project/data/BIDS/sub-${name::6}/ses-${session}/func/sub-${name::6}_ses-${session}_task-BDM_run*.json
  #jq 'del(.ImageOrientationPatientDICOM)' ~/JDaoust_project/data/BIDS/sub-${name::6}/ses-${session}/anat/sub-${name::6}_ses-${session}_T1w.json

  #rm ~/JDaoust_project/data/BIDS/sub-${name::6}/ses-${session}/GUT*
  #rm ~/JDaoust_project/data/BIDS/sub-${name::6}/ses-${session}/gut*

  #for run in 1 2 3; do
    # paste ~/projects/def-account/share/dagher6_back_up/EVs/bariatric_${name::6}_session${session}_run${run}_img_onset*.txt ~/projects/def-account/share/dagher6_back_up/EVs/bariatric_${name::6}_session${session}_run${run}_img_duration*.txt ~/projects/def-account/share/dagher6_back_up/EVs/bariatric_${name::6}_session${session}_run${run}_img_bids*.txt > ~/JDaoust_project/data/raw_BIDS/sub-${name::6}/ses-${session}/func/sub-${name::6}_ses-${session}_task-BDM_run-${run}_events.tsv

  #sed -i '1i \onset \tduration \tbids' ~/JDaoust_project/data/raw_BIDS/sub-${name::6}/ses-${session}/func/sub-${name::6}_ses-${session}_task-BDM_run-${run}_events.tsv

  #done
