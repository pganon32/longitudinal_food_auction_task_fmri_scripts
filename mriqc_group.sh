#!/bin/bash
#SBATCH --job-name=MRIQC
#SBATCH --output=MRIQC_%j_.out
#SBATCH --error=MRIQC_%j_.err
#SBATCH --time=00:30:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=60G

echo "Loading the necessary module..."
module load apptainer/1.3.5

# Define paths
input_dir=/home/pagag24/projects/def-amichaud/share/GutBrain/data2
output_dir=/home/pagag24/projects/def-amichaud/share/GutBrain/derivatives/mriqc
CONTAINER_IMAGE=/home/pagag24/myimages/mriqc-24.0.2.sif

# Echo all of the directories
echo "Input directory: $input_dir"
echo "Output directory: $output_dir"
echo "Container image: $CONTAINER_IMAGE"

mkdir $SLURM_TMPDIR/HZ_tmp
apptainer run -C -W $SLURM_TMPDIR \
     --writable-tmpfs \
     -B /home/pagag24/projects/def-amichaud/share/GutBrain:/GutBrain \
     -B $SLURM_TMPDIR \
     -B $SLURM_TMPDIR/HZ_tmp:/tmp \
     $CONTAINER_IMAGE \
     /GutBrain/data2 /GutBrain/derivatives/mriqc group \
     --work-dir $SLURM_TMPDIR/HZ_tmp \
     --n_procs 4  \
     --mem_gb 55 \
     --no-sub \
     --bids-database-wipe

echo "MRIQC processing complete."
