# fMRI Analysis Scripts

## Project Overview

This repository contains scripts and workflows for preprocessing, organizing, and analyzing participant and session-level mean z-scored BOLD signals per ROI from fMRI BDM food auction task files. The pipeline is tailored for data acquired on Philips scanners and designed for use on Alliance Canada clusters.

> **Note:** The scripts may require adaptation for other datasets or environments due to hard-coded filename and directory patterns. Future patches may improve portability.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Data Structure](#data-structure)
- [Workflow](#workflow)
  - [1. DICOM to NIfTI Conversion](#1-dicom-to-nifti-conversion)
  - [2. Organize Data in BIDS Format](#2-organize-data-in-bids-format)
  - [3. Add Metadata Fields](#3-add-metadata-fields)
  - [4. Quality Control](#4-quality-control)
  - [5. Preprocessing](#5-preprocessing)
  - [6. Event File Creation](#6-event-file-creation)
  - [7. Design Matrix Construction](#7-design-matrix-construction)
  - [8. First-Level Modeling](#8-first-level-modeling)
  - [9. ROI Mask Generation](#9-roi-mask-generation)
  - [10. ROI Z-Score Calculation](#10-roi-z-score-calculation)
  - [11. ROI Statistical Analysis](#11-roi-statistical-analysis)
- [Troubleshooting](#troubleshooting)
- [References](#references)
- [Contributing and Citation](#contributing-and-citation)
- [License](#license)

---

## Prerequisites

- **Cluster access:** Alliance Canada clusters recommended
- **Software:** 
  - Bash
  - Python 3.x
  - Apptainer/Singularity
  - fMRIPrep
  - MRIQC
  - Nilearn
  - scikit-learn
- **Container images:** See [Quality Control](#quality-control) for MRIQC
- **Data:** Philips scanner DICOMs, structured as below

---

## Data Structure

```
/data/
└── sourcedata/
    └── {participant-id}/
        └── DICOM/
            └── {BL,4M,12M,24M}/
```

**Event files must have columns:**  
`Picture | Stimulus | Start Time | Bid Start Time | Bid Duration | Price`

---

## Workflow

### 1. DICOM to NIfTI Conversion

```bash
bash convert_dicom_to_nifti.sh
# Adjust participant label prefix if needed
```

Reference:  
Li X et al. (2016), J Neurosci Methods.

---

### 2. Organize Data in BIDS Format

```bash
bash organize_BIDS_structure.sh
# Adjust Bo and fieldmaps names based on acquisition time
```

Reference:  
Gorgolewski, K.J. et al. (2016), Scientific Data.

---

### 3. Add Metadata Fields

```bash
bash add_intended_for_fmap.sh
bash add_slice_acquisition_info.sh
# Add "IntendedFor" and slice acquisition info to .json files
```
*Philips DICOM headers may lack info; consult with MR specialist as needed.*

---

### 4. Quality Control

Build MRIQC image:
```bash
apptainer build mriqc-24.0.2.sif docker://nipreps/mriqc:24.0.2
```

Run:
```bash
bash run_mriqc_batch.sh
bash mriqc_group_summary.sh
```


### 5. Preprocessing

Run fMRIPrep:
```bash
bash run_fmriprep_batch.sh
bash fmriprep_advanced.sh
# Adjust options, time, hardware requirements as needed
```

*Requires exclusion list file from QC process:*
```
sub-{ID}_ses-{ID}_task-BDM_run-{ID}_bold
```

Reference:  
Esteban O et al. (2017), PLoS ONE.

---

Reference:  
Esteban O et al. (2019), Nat Methods.

---

### 6. Event File Creation

```bash
python events_to_bids.py
```

---

### 7. Design Matrix Construction

```bash
python build_design_matrix.py
# Adjust suffix and columns as needed
```

Reference:  
Abraham A et al. (2014), Front Neuroinform.

---

### 8. First-Level Modeling

```bash
python run_first_level_glm.py
# Adjust contrast and settings as needed
```

---

### 9. ROI Mask Generation

```bash
jupyter notebook make_roi_masks.ipynb
# Use meta-analysis ALE map as needed
```

Reference:  
Newton-Fenner et al. (2023).

---

### 10. ROI Z-Score Calculation

```bash
python compute_roi_zscores.py
# Requires BIDS-compliant participant.tsv in /data
```

---

### 11. ROI Statistical Analysis

```bash
jupyter notebook roi_lmm_analysis.ipynb
# FDR-corrected linear mixed model analysis of longitudinal ROI z-score BOLD signals
```

---

## Troubleshooting

- **Directory or filename errors:** Ensure strict compliance with required folder structure and naming conventions.
- **Missing DICOM header info:** Consult with MR specialist, especially for Philips scanners.
- **MRIQC/fMRIPrep container fails:** Check container build versions and cluster compatibility.
- **Script errors:** Read script comments for adjustable parameters.

---

## References

- Gorgolewski, K.J., Auer, T., Calhoun, V.D., Craddock, R.C., Das, S., Duff, E.P., Flandin, G., Ghosh, S.S., Glatard, T., Halchenko, Y.O., Handwerker, D.A., Hanke, M., Keator, D., Li, X., Michael, Z., Maumet, C., Nichols, B.N., Nichols, T.E., Pellman, J., Poline, J.-B., Rokem, A., Schaefer, G., Sochat, V., Triplett, W., Turner, J.A., Varoquaux, G., Poldrack, R.A. (2016). The brain imaging data structure, a format for organizing and describing outputs of neuroimaging experiments. Scientific Data, 3 (160044). doi:10.1038/sdata.2016.44
- Li X, Morgan PS, Ashburner J, Smith J, Rorden C. (2016) J Neurosci Methods. 264:47-56.
- Esteban O et al. (2017) PLoS ONE 12(9): e0184661.
- Esteban O et al. (2019) Nat Methods 16, 111–116.
- Abraham A et al. (2014) Front Neuroinform. 8:14.
- Newton-Fenner A et al. (2023) [Economic value in the Brain: A meta-analysis...](https://doi.org/10.1177/20438087231160434)

---

## Contributing and Citation

Contributions welcome! Please open issues or pull requests.

If you use these scripts, please cite the relevant references above.

---


