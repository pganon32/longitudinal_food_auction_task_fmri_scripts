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
contrast_label = "bid_against_0"
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

# Fit second-level model
second_level_model = SecondLevelModel()
print("Debug: SecondLevelModel instantiated.")
second_level_model = second_level_model.fit(zmap_files, design_matrix=design_matrix)
print("Debug: SecondLevelModel fitted.")


# Compute contrast (one-sample t-test on intercept)
z_map = second_level_model.compute_contrast('intercept', output_type='z_score')
print("Debug: z_map computed.")

# Save and plot
second_level_zmap_path = f"{results_dir}/second_level_zmap_{suffix}_{contrast_label}.nii.gz"
z_map.to_filename(second_level_zmap_path)
print(f"Second-level z-map saved to: {second_level_zmap_path}")

# Plot and save mosaic
plot_path = f"{results_dir}/second_level_zmap_{suffix}_{contrast_label}_mosaic.png"
display = plot_stat_map(z_map, display_mode="mosaic", title=f"Second-level Z-map: {contrast_label}")
display.savefig(plot_path)
display.close()
print(f"Second-level z-map mosaic saved to: {plot_path}")

# Generate and save HTML report
report = make_glm_report(
    second_level_model,
    contrasts='intercept',
    title=f"Second-level GLM: {contrast_label}",
    threshold=3.09,
    alpha=0.001,
    cluster_threshold=0,
    height_control='fpr',
    min_distance=8.0,
    plot_type='slice',
    report_dims=(1600, 800)
)
report_path = f"{results_dir}/second_level_report_{suffix}_{contrast_label}.html"
report.save_as_html(report_path)
print(f"Second-level GLM report saved to: {report_path}")

# Set your statistical threshold (should match your report threshold)
stat_threshold = 3.09

# Get cluster table from your z_map
cluster_table = get_clusters_table(
    stat_img=z_map,
    stat_threshold=stat_threshold,
    cluster_threshold=0,  # or set a minimum cluster size in voxels
    two_sided=False,
    min_distance=8.0
)

print(cluster_table)
# Save to CSV if desired
cluster_table_path = f"{results_dir}/second_level_clusters_{suffix}_{contrast_label}.csv"
cluster_table.to_csv(cluster_table_path, index=False)
print(f"Cluster table saved to: {cluster_table_path}")


print("Running atlasreader.create_output to generate labeled cluster tables and figures...")
print(f"  Input z-map: {second_level_zmap_path}")
print(f"  Output directory: {results_dir}")
print(f"  Voxel threshold: {stat_threshold}")
print(f"  Atlas: default")
print(f"  Cluster extent: 0")
print(f"  Direction: pos")
print(f"  Min distance: 8.0")

# Create a unique output directory for atlasreader results
today_str = datetime.now().strftime("%Y%m%d")
atlasreader_outdir = os.path.join(
    results_dir,
    f"{today_str}_{suffix}_{contrast_label}_atlasreader"
)
os.makedirs(atlasreader_outdir, exist_ok=True)
print(f"Atlasreader output directory created: {atlasreader_outdir}")

# This will create labeled cluster tables and figures in the output_dir
create_output(
    z_map,  # or str path to your z-map file
    cluster_extent=0,  # or set a minimum cluster size in voxels
    voxel_thresh=stat_threshold,  # your z threshold
    direction='pos',  # or 'both' if you want both tails
    outdir=atlasreader_outdir,
    atlas='default',  # or 'harvard_oxford', 'aal', etc.
    min_distance=8.0
)

print("atlasreader.create_output finished. Check the output directory for labeled cluster tables and figures.")
