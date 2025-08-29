#!/bin/bash
#SBATCH --job-name=MRIQC
#SBATCH --output=MRIQC_%j_.out
#SBATCH --error=MRIQC_%j_.err
#SBATCH --time=02:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=60G

echo "Loading the necessary module..."
module load apptainer/1.3.5

#For testing, uncomment the line below and put in your test participant, if not use run_mriqc_batch.sh
#export SUBJECT_NAME='sub-050'

# Ensure SUBJECT_NAME is provided  
if [ -z "$SUBJECT_NAME" ]; then
  echo "Error: SUBJECT_NAME environment variable is not set."
  exit 1
fi


# Define paths
input_dir=/home/username/projects/def-account/share/projectname/data2
output_dir=/home/username/projects/def-account/share/projectname/derivatives/mriqc
CONTAINER_IMAGE=/home/username/myimages/mriqc-24.0.2.sif

# Echo all of the directories
echo "Input directory: $input_dir"
echo "Output directory: $output_dir"
echo "Container image: $CONTAINER_IMAGE"

mkdir $SLURM_TMPDIR/HZ_tmp
apptainer run -C -W $SLURM_TMPDIR \
     --writable-tmpfs \
     -B /home/username/projects/def-account/share/projectname:/projectname \
     -B $SLURM_TMPDIR \
     -B $SLURM_TMPDIR/HZ_tmp:/tmp \
     $CONTAINER_IMAGE \
     /projectname/data2 /projectname/derivatives/mriqc  participant \
     --participant-label $SUBJECT_NAME \
     --work-dir $SLURM_TMPDIR/HZ_tmp \
     --n_procs 4  \
     --mem_gb 55 \
     --no-sub \
     --bids-database-wipe

echo "MRIQC processing complete."
