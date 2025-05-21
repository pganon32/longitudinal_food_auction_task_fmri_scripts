# Module Load

import os
import glob
import pandas as pd
from nilearn.glm.second_level import SecondLevelModel
from nilearn.image import load_img
from nilearn.plotting import plot_stat_map
from nilearn.reporting import make_glm_report
from nilearn.glm.second_level import make_second_level_design_matrix
from nilearn.reporting import get_clusters_table
from atlasreader import create_output
import numpy as np
from datetime import datetime



print("Debug: Modules loaded.")

# Set Path
project_dir = "/home/pagag24/projects/def-amichaud/share/GutBrain"
results_dir = f"{project_dir}/BIDS_results"
print(f"Debug: project_dir={project_dir}")
print(f"Debug: results_dir={results_dir}")

# Choose what DM to use by modifying suffix below:
suffix = "simple_valuation"
contrast_label = "mod_view_against_0"
print(f"Debug: suffix={suffix}, contrast_label={contrast_label}")

# Find all z-maps for this contrast
zmap_pattern = f"{results_dir}/sub-*/ses-*/func/sub-*_ses-*_run-combined_zmap_{suffix}_{contrast_label}.nii.gz"
print(f"Debug: zmap_pattern={zmap_pattern}")
zmap_files = sorted(glob.glob(zmap_pattern))
print(f"Debug: Found {len(zmap_files)} zmap_files: {zmap_files}")

# Extract subject and session info for design matrix
subjects = []
sessions = []
for zmap in zmap_files:
    basename = os.path.basename(zmap)
    parts = basename.split('_')
    sub = [p for p in parts if p.startswith('sub-')][0].replace('sub-', '')
    ses = [p for p in parts if p.startswith('ses-')][0].replace('ses-', '')
    # Cut first 3 characters and convert to int
    sub_num = int(sub[3:])
    subjects.append(sub_num)
    sessions.append(ses)
    print(f"Debug: zmap={zmap}, sub={sub_num}, ses={ses}")

# Prepare subject labels DataFrame (no session, one row per z-map)
subjects_label = [str(s) for s in subjects]  # list of str

# Build design matrix: one row per z-map, intercept only

design_matrix = pd.DataFrame({'intercept': np.ones(len(zmap_files))})
print(f"Debug: design_matrix shape={design_matrix.shape}")
print(f"Debug: design_matrix head:\n{design_matrix.head()}")

# Optionally, load a custom design matrix:
# design_matrix = pd.read_csv('path/to/your/design_matrix.csv')

