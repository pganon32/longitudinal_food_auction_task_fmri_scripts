#!/usr/bin/env python
# coding: utf-8

# # Module Loading

# In[58]:


# Module Load

import sys
import nibabel as nib
import numpy as np
from nilearn import plotting as plot
from nilearn.image.image import mean_img
import pandas as pd
from nilearn.image import load_img, new_img_like
from nilearn import image as img
from nilearn.plotting import plot_design_matrix
import os
from nilearn.glm.first_level import FirstLevelModel
from nilearn.plotting import plot_stat_map
from nilearn.glm import threshold_stats_img
from nilearn.reporting import get_clusters_table
from nilearn.plotting import plot_contrast_matrix
from nilearn.masking import intersect_masks
from nilearn.glm.contrasts import compute_fixed_effects
from nilearn.reporting import make_glm_report
from nilearn.glm.second_level import SecondLevelModel
from nilearn.image import math_img
from nilearn.datasets import fetch_neurovault_ids
from nilearn import datasets
from nilearn.image import smooth_img
from scipy.stats import ttest_ind
from scipy.ndimage import binary_dilation, label
import nibabel as nib
from nilearn.image import get_data
from nilearn.plotting import plot_roi
from nilearn.datasets import load_mni152_template
from nilearn.image import resample_to_img
import ssl




# # Set Path

# In[59]:


project_dir = "/home/pagag24/projects/def-amichaud/share/GutBrain"
data_dir = f"{project_dir}/data2"
derivatives_dir = f"{project_dir}/derivatives2/fmriprep"
results_dir = f"{project_dir}/BIDS_results2"


# # Load ROI Masks and participants.tsv

# In[60]:


# Set variables

# Set variables

do_plot = True
verbose = True
sessions = ["1","2","3","4"]  # Example sessions



# In[61]:


# Define paths to the specified masks
mask_paths = [
    f"{results_dir}/ROIs/cluster_vmPFC_L_merged.nii.gz",
    f"{results_dir}/ROIs/cluster_dlPFC_R_merged.nii.gz",
    f"{results_dir}/ROIs/cluster_VS_L.nii.gz",
    f"{results_dir}/ROIs/cluster_VS_R.nii.gz",
]

# Load masks using nibabel
masks = [nib.load(mask_path) for mask_path in mask_paths]





# In[62]:


# Load participants.tsv file
participants_path = f"{data_dir}/participants.tsv"
participants_df = pd.read_csv(participants_path, sep='\t')

# Print confirmation and display the first few rows
if verbose:
    print(f"Loaded participants.tsv with {len(participants_df)} entries.")
    print(participants_df.head())


# In[63]:


# Get all subject IDs dynamically
subject_dirs = [d for d in os.listdir(results_dir) if d.startswith("sub-")]

# Define suffixes and contrast labels
suffixes = ["ssib_v1"]  # Example suffixes
contrast_labels = [
    #"view_Hi_Sweet_Hi_Salt_Lo_Lo_vs_view_cross",
    #"mod_view_Hi_Sweet_Hi_Salt_Lo_Lo_vs_view_cross",
  #  "mod_view_Hi_Salt_vs_Lo_Lo"
   # "mod_view_Hi_Sweet_vs_Lo_Lo"
   "Hi_vs_Lo"
]  # Example contrast labels

# Define suffixes and contrast labels
#suffixes = ["ssib_v2_simple"]  # Example suffixes
#contrast_labels = [
#    "mod_view_vs_view_cross"
#]  # Example contrast labels


# Loop through subjects, sessions, suffixes, and contrast labels
for subject_dir in subject_dirs:
    subject_id = subject_dir.split("-")[1]  # Extract subject ID
    if verbose:
        print(f"Processing subject: {subject_id}")

    for ses_id in sessions:
        for suffix in suffixes:
            for contrast_label in contrast_labels:
                if verbose:
                    print(f"Session: {ses_id}, Suffix: {suffix}, Contrast: {contrast_label}")
                # Add your processing logic here
                # Generate z-map file path
                zmap_path = f"{results_dir}/sub-{subject_id}/ses-{ses_id}/func/sub-{subject_id}_ses-{ses_id}_run-combined_zmap_{suffix}_{contrast_label}.nii.gz"
                if verbose:
                    print(f"Generated z-map path: {zmap_path}")

                # Check if the file exists before loading
                if not os.path.exists(zmap_path):
                    if verbose:
                        print(f"File not found: {zmap_path}. Skipping this z-map.")
                    continue

                # Load the z-map file
                try:
                    zmap_img = load_img(zmap_path)
                except FileNotFoundError as e:
                    if verbose:
                        print(f"File not found: {zmap_path}. Skipping this z-map.")
                    continue

                # Loop through masks and process them
                for i, mask in enumerate(masks):
                    if verbose:
                        print(f"Processing Mask {i+1}: {mask_paths[i]}")

                    # Resample mask to match z-map's shape with updated parameters
                    resampled_mask = resample_to_img(
                        mask, 
                        zmap_img, 
                        interpolation='nearest', 
                        copy_header=True,  # Copy the header of the input image
                        force_resample=True  # Force resampling even if shapes match
                    )

                    # Extract resampled mask data
                    mask_data = resampled_mask.get_fdata()

                    # Extract z-map data
                    zmap_data = zmap_img.get_fdata()

                    # Perform element-wise multiplication
                    masked_zmap_data = zmap_data * mask_data

                    # Create a new nibabel image with the masked data
                    masked_zmap_img = nib.Nifti1Image(masked_zmap_data, affine=zmap_img.affine, header=zmap_img.header)

                    mask_name = mask_paths[i].split("cluster_")[1].split(".nii.gz")[0]


                    if verbose:
                        print(f"Masked z-map created for Mask {i+1}: {mask_name}.")

                    # Save the masked z-map image
                    masked_zmap_path = f"{results_dir}/sub-{subject_id}/ses-{ses_id}/func/sub-{subject_id}_ses-{ses_id}_run-combined_masked_zmap_{suffix}_{contrast_label}_mask_{mask_name}.nii.gz"
                    masked_zmap_img.to_filename(masked_zmap_path)

                    # Extract the data from the masked z-map image
                    masked_zmap_data = masked_zmap_img.get_fdata()

                    # Filter out zero values
                    non_zero_voxels = masked_zmap_data[masked_zmap_data != 0]

                    # Compute the mean of non-zero voxels
                    if non_zero_voxels.size > 0:
                        mean_value = np.nanmean(non_zero_voxels)  # Use np.nanmean to handle potential NaN values
                    else:
                        mean_value = np.nan  # If no non-zero voxels exist, return NaN

                    # Print the mean value if verbose
                    if verbose:
                        print(f"Mean value of masked z-map for Mask {i+1}: {mean_value}")

                    # Construct the column label dynamically
                    column_label = f"Z_ROI_{suffix}_{contrast_label}_mask_{mask_name}"

                    # Check if the column exists, if not, create it
                    if column_label not in participants_df.columns:
                        participants_df[column_label] = np.nan

                    # Find the row matching the current subject ID and session
                    row_index = participants_df[(participants_df['Subject id'] == subject_id) & (participants_df['Session'] == ses_id)].index

                    # Store the mean value in the appropriate row and column
                    if len(row_index) > 0:
                        participants_df.at[row_index[0], column_label] = mean_value

# Save the updated participants_df back to participants.tsv
participants_df.to_csv(participants_path, sep='\t', index=False)

if verbose:
    print(f"Updated participants.tsv saved to {participants_path}.")





# In[ ]:




