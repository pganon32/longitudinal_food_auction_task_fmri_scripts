# Module Load

import nibabel as nib
import numpy as np
import pandas as pd
import os
import gc
import time
import resource
from nilearn.image import load_img, math_img
from nilearn.glm.first_level import FirstLevelModel
from nilearn.masking import intersect_masks
from nilearn.glm.contrasts import compute_fixed_effects


# Set Path

project_dir = "/home/pagag24/projects/def-amichaud/share/GutBrain"
data_dir = f"{project_dir}/data2"
derivatives_dir = f"{project_dir}/derivatives2/fmriprep"
results_dir = f"{project_dir}/BIDS_results2"
tsnr_fd_outliers_path = f"{derivatives_dir}/tsnr_fd_outliers.txt"

# project_dir = "/home/gagpat01/Documents/GutBrain"
# data_dir = f"{project_dir}/data5"
# derivatives_dir = f"{project_dir}/derivatives4/fmriprep"
# results_dir = f"{project_dir}/BIDS_results"
# tsnr_fd_outliers_path = f"{derivatives_dir}/tsnr_fd_outliers.txt"


# Set variables

hrf_model = "glover"
drift_model = "cosine"
t_r = 2.75
do_plot = False
verbose = True
sessions = ["1","x","2","3","4"]  # Example sessions
run_indexes = [0, 1, 2]  # Run indices for list arguments
# Define variables for contrast conditions
#contrast_pos = ["mod_view_Hi_Sweet","mod_view_Hi_Salt"]  # List of positive contrast conditions
contrast_pos = ["mod_view_Hi_Salt", "mod_view_Hi_Sweet"]  # List of positive contrast conditions
contrast_neg = ["mod_view_Lo_Lo"]  # Empty negative contrast condition
# Choose what DM to use by modifying suffix below:
suffix = "ssib_v1"
# Generate the contrast label using clean column names
contrast_label = "Hi_vs_Lo"
if verbose:
    print(f"Contrast label: {contrast_label}")




# Load the tsnr_fd_outliers.txt file as a one-column DataFrame
tsnr_fd_outliers_df = pd.read_csv(tsnr_fd_outliers_path, header=None, names=["Outliers"])
if verbose:
    print(f"Loaded tsnr_fd_outliers.txt with {len(tsnr_fd_outliers_df)} entries.")
    # Display the first 50 rows of the tsnr_fd_outliers_df DataFrame
    print(tsnr_fd_outliers_df.head(50))

# Get all subject IDs dynamically
subject_dirs = [d for d in os.listdir(derivatives_dir) if d.startswith("sub-")]

# Initialize memory monitoring
start_time = time.time()

for subject_dir in subject_dirs:
    subject_id = subject_dir.split("-")[1]  # Extract subject ID
    if verbose:
        print(f"Processing subject: {subject_id}")


    for ses_id in sessions:
        try:
  
            # Initialize lists for available runs
            available_runs = []

            # Check availability of fMRI images, masks, and design matrices for each run
            for run in run_indexes:
                fmri_path = f"{derivatives_dir}/sub-{subject_id}/ses-{ses_id}/func/sub-{subject_id}_ses-{ses_id}_task-BDM_run-{run+1}_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz"
                mask_path = f"{derivatives_dir}/sub-{subject_id}/ses-{ses_id}/func/sub-{subject_id}_ses-{ses_id}_task-BDM_run-{run+1}_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz"
                dm_path = f"{results_dir}/sub-{subject_id}/ses-{ses_id}/func/sub-{subject_id}_ses-{ses_id}_run-{run+1}_dm_{suffix}.csv"

                if os.path.exists(fmri_path) and os.path.exists(mask_path) and os.path.exists(dm_path):
                    available_runs.append({
                        "fmri_path": fmri_path,
                        "mask_path": mask_path,
                        "dm_path": dm_path
                    })
                else:
                    if verbose:
                        print(f"Skipping run {run+1} due to missing files.")

            # Ensure there are available runs
            if not available_runs:
                print(f"No valid runs found for subject {subject_id}, session {ses_id}.")
                continue

            # Load fMRI images, masks, and design matrices for available runs
            fmri_imgs = [load_img(run["fmri_path"]) for run in available_runs]
            mask_imgs = [load_img(run["mask_path"]) for run in available_runs]
            design_matrices = [pd.read_csv(run["dm_path"]) for run in available_runs]

            # Compute the intersection of all run masks
            intersected_mask = intersect_masks(mask_imgs, threshold=0.33, connected=True)
            if verbose:
                print("Intersected mask computed.")

            # Fit GLMs for available runs
            fmri_glms = []
            for idx, (fmri_img, mask_img, dm) in enumerate(zip(fmri_imgs, mask_imgs, design_matrices)):
                fmri_glm = FirstLevelModel(
                    t_r=t_r,
                    slice_time_ref=0.5,
                    smoothing_fwhm=8,
                    signal_scaling=(0, 1),
                    verbose=1,
                    mask_img=mask_img,
                    subject_label=subject_id,
                )
                fmri_glm.fit(fmri_img, design_matrices=dm)
                fmri_glms.append(fmri_glm)
                if verbose:
                    print(f"fMRI GLM fitted for run-{idx+1}.")

                # Initialize a list to store contrast vectors for each run
            contrast_vectors = []

            # Loop through each run's design matrix
            for dm in design_matrices:
                pos_indices = [i for i, col in enumerate(dm.columns) if col in contrast_pos]
                neg_indices = [i for i, col in enumerate(dm.columns) if col in contrast_neg]

                # Initialize contrast vector with zeros for this run's design matrix
                contrast = np.zeros(len(dm.columns))

                # Set positive and negative indices with normalized weights
                if len(pos_indices) > 0:
                    pos_weight = 1.0 / len(pos_indices)
                    for idx in pos_indices:
                        contrast[idx] = pos_weight
                
                if len(neg_indices) > 0:
                    neg_weight = -1.0 / len(neg_indices)
                    for idx in neg_indices:
                        contrast[idx] = neg_weight

                # Append to list
                contrast_vectors.append(contrast)

                if verbose:
                    print(f"Contrast vector: {contrast}")


            # Compute summary statistics for each run dynamically
            summary_statistics = []
            # Extract degrees of freedom from each fitted GLM
            dofs = []

            for idx, contrast_vector in enumerate(contrast_vectors):
                try:
                    summary_stat = fmri_glms[idx].compute_contrast(
                        contrast_vector,
                        output_type="all",
                    )
                    summary_statistics.append(summary_stat)
                    # Extract degrees of freedom from the fitted GLM
                    dof = fmri_glms[idx].design_matrices_[0].shape[0] - fmri_glms[idx].design_matrices_[0].shape[1]
                    dofs.append(dof)
                    if verbose:
                        print(f"Summary statistics for run {idx + 1}: {summary_stat}")
                        print(f"Degrees of freedom for run {idx + 1}: {dof}")
                except Exception as e:
                    print(f"Error computing summary statistics for run {idx + 1}: {e}")

            if verbose:
                print(f"Collected summary statistics for {len(summary_statistics)} runs.")
                print(f"Degrees of freedom: {dofs}")

            # Compute fixed effects if sufficient data is available
            if len(summary_statistics) > 0:
                # Prepare contrast and variance images for all runs
                contrast_imgs = [stat["effect_size"] for stat in summary_statistics]
                variance_imgs = [stat["effect_variance"] for stat in summary_statistics]
                if verbose:
                    print("Preparing contrast and variance images for all runs.")
                    print(f"Contrast images: {contrast_imgs}")
                    print(f"Variance images: {variance_imgs}")
                
                fixed_fx_contrast, fixed_fx_variance, fixed_fx_stat = compute_fixed_effects(
                    contrast_imgs,
                    variance_imgs,
                    intersected_mask,
                    dofs=dofs,  # Pass the actual DOFs
                )
                if verbose:
                    print("Fixed effects computed.")
                    print(f"Fixed effects contrast image: {fixed_fx_contrast}")
                    print(f"Fixed effects variance image: {fixed_fx_variance}")
                    print(f"Fixed effects stat image: {fixed_fx_stat}")
            else:
                print(f"No valid runs found for subject {subject_id}, session {ses_id}.")
                continue

            def squeeze_nii(img):
                data = img.get_fdata()
                squeezed_data = np.squeeze(data)

                # Fix: make a copy of the header and update the shape
                new_header = img.header.copy()
                new_header.set_data_shape(squeezed_data.shape)

                return nib.Nifti1Image(squeezed_data, img.affine, new_header)

            # Use this instead of squeeze_img
            fixed_fx_contrast = squeeze_nii(fixed_fx_contrast)
            fixed_fx_variance = squeeze_nii(fixed_fx_variance)

            # After you have fixed_fx_contrast and fixed_fx_variance:
            z_map = math_img("con / np.sqrt(var)", con=fixed_fx_contrast, var=fixed_fx_variance)
            if verbose:
                print("z map computed.")

            # Commenting out the save part
            zmap_path = f"{results_dir}/sub-{subject_id}/ses-{ses_id}/func/sub-{subject_id}_ses-{ses_id}_run-combined_zmap_{suffix}_{contrast_label}.nii.gz"
            if verbose:
                print(f"Saving z-map to: {zmap_path}")
            z_map.to_filename(zmap_path)
            if verbose:
                print("z-map saved.")
            
            # AGGRESSIVE memory cleanup with explicit nulling and multiple gc calls
            pre_cleanup_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024  # Convert to MB
            
            if verbose:
                print(f"  Starting cleanup from {pre_cleanup_memory:.1f}MB memory...")
            
            # Delete GLM objects first - they hold the most memory
            glm_objects_memory = 0
            for i, glm in enumerate(fmri_glms):
                pre_del = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
                glm = None
                post_del = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
                if verbose and abs(post_del - pre_del) > 50:  # Only report significant changes (50MB)
                    print(f"    Deleted GLM {i+1}: {post_del - pre_del:+.1f}MB")
                glm_objects_memory += (pre_del - post_del)
            fmri_glms = None
            
            # Explicitly delete and null all large objects
            z_map = None
            fixed_fx_contrast = None
            fixed_fx_variance = None
            fixed_fx_stat = None
            intersected_mask = None
            
            # Delete image data
            for img in fmri_imgs:
                img = None
            fmri_imgs = None
            
            for img in mask_imgs:
                img = None
            mask_imgs = None
            
            # Delete other data structures
            design_matrices = None
            summary_statistics = None
            contrast_vectors = None
            contrast_imgs = None
            variance_imgs = None
            
            # Multiple garbage collection calls
            gc.collect()
            gc.collect()
            gc.collect()
            
            post_cleanup_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
            if verbose:
                print(f"  Memory after cleanup: {post_cleanup_memory:.1f}MB (reduced by {pre_cleanup_memory - post_cleanup_memory:.1f}MB)")

        except Exception as e:
            print(f"Error processing subject {subject_id}, session {ses_id}: {e}")
            # Force cleanup on error with explicit nulling
            locals_to_clear = ['z_map', 'fixed_fx_contrast', 'fixed_fx_variance', 'intersected_mask', 
                             'fmri_glms', 'fmri_imgs', 'mask_imgs', 'design_matrices', 
                             'summary_statistics', 'contrast_vectors', 'contrast_imgs', 'variance_imgs']
            for var_name in locals_to_clear:
                if var_name in locals():
                    locals()[var_name] = None
            gc.collect()
            gc.collect()

end_time = time.time()
processing_time = end_time - start_time

final_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
if verbose:
    print(f"Total processing time: {processing_time:.2f} seconds")
    print(f"Final memory usage: {final_memory:.1f}MB")

