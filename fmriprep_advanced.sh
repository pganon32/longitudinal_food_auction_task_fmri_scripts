#!/bin/bash

#SBATCH --time=12:00:00
#SBATCH --ntasks-per-node=16
#SBATCH --cpus-per-task=1
#SBATCH --job-name=fmriprep
#SBATCH --account=def-account
#SBATCH --mem=32000

# Optionally, uncomment and set for testing:
export SUBJECT_NAME=067

# Check if SUBJECT_NAME is provided
if [ -z "$SUBJECT_NAME" ]; then
  echo "Error: SUBJECT_NAME environment variable is not set."
  exit 1
fi

# Load modules
module load StdEnv/2023
module load apptainer fmriprep

# Use SUBJECT_NAME directly (provided via sbatch --export=SUBJECT_NAME=...)
subj="$SUBJECT_NAME"

# Specify hardware
nthreads=16  # Match the number of CPUs allocated
mem=32 # GB
omp_nthreads=8  # Maximum threads per process

# Convert virtual memory from GB to MB
mem_mb=$((mem*1000 - 500)) # Slight buffer

# File pathing
input_dir=${HOME}/projects/def-account/share/projectname/data2
output_dir=${HOME}/projects/def-account/share/projectname/derivatives3/fmriprep
work_dir=${SLURM_TMPDIR}
license_dir=${HOME}/projects/def-account/share/projectname/fs_license

# Export paths - use Beluga-style paths
export APPTAINERENV_TEMPLATEFLOW_HOME=/tmp/templateflow
export APPTAINER_BIND=${input_dir}:/data,${output_dir}:/out,${license_dir}:/license,${work_dir}:/work,${HOME}/projects/def-account/share/templateflow:/tmp/templateflow

# Run fmriprep
fmriprep /data /out participant \
 --skip_bids_validation \
 --work-dir /work \
 --participant-label ${subj} \
 --fs-license-file /license/license.txt \
 --nthreads ${nthreads} \
 --omp-nthreads ${omp_nthreads} \
 --mem_mb ${mem_mb} \
 --output-spaces MNI152NLin2009cAsym \
 --use-syn-sdc \
 --ignore fieldmaps \
 --notrack
