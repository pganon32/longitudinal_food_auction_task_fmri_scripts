# Gut Brain fmri Scripts

This repository contains various scripts to compute participant and session level mean z-scored BOLD signal per ROI from fmri BDM food auction task files. 

## Important : this script might not be easily transferable to another dataset, code written searches for specifc filename or directory pattern, especially within source data. Further patches will fix this. 

## These scripts were made to be used on alliance canada clusters

## Source Data format

sourcedata structure:
Has to be within /data folder
Has to have this structure:
  /data/sourcedata/{participant-id}/DICOM/{BL,4M,12M,24M}
relevant sourcedata events have to have this header structure:

Picture/Stimulus/Start Time/Bid Start Time/Bid Duration/Price

## Conversion from dicom to nifty : 

run raw_dcm_to_nii_v_1.1.sh
adjust participant labelprefix if needed, if uniform participant labeling, no need for adjustment. 

Li X, Morgan PS, Ashburner J, Smith J, Rorden C. (2016) The first step for neuroimaging data analysis: DICOM to NIfTI conversion. J Neurosci Methods. 264:47-56.

## Properly name and move files into bids format and adjust the Bo and fieldmaps names based on acquisition time

run rename_BIDS_mv.sh

## add intended for and slice acquisition fields in the .json files

### Those steps are necessary due to the Philips Scanner DICOM header not passing all the required info. Discussion with your Philips MR specialist might be required to properly adjust those scripts for your acquisition parameters. 

run add_int_for_fmap.sh
run slice_info_json.sh

## Quality Control

the mriqc image has to be installed beforehand using this command
apptainer build mriqc-24.0.2.sif docker://nipreps/mriqc:24.0.2
run batch_mriqc.sh
which uses
mriqc_v2.sh
Then run 
mriqc_group.sh

Build and use a run level exclusion text file that has this structure and save it as an exlucsion list file. THis will be a required input in first level modeling scripts. 
The format is a single column with the following structure for a given excluded run. 

sub-{1,2,3,etc.}_ses-{1,2,3,etc.}_task-BDM_run-{1,2,3 etc.}_bold

Esteban O, Birman D, Schaer M, Koyejo OO, Poldrack RA, Gorgolewski KJ (2017) MRIQC: Advancing the automatic prediction of image quality in MRI from unseen sites. PLoS ONE 12(9): e0184661. doi:10.1371/journal.pone.0184661. 

## pre-processing

Run fmriprep using the following scripts:
batch_fmripre.sh
v4_fmriprep.sh 
adjust options and time and hardware requirements accordingly. 

Esteban O, Markiewicz CJ, Blair RW, Moodie CA, Isik AI, Erramuzpe A, Kent JD, Goncalves M, DuPre E, Snyder M, Oya H, Ghosh SS, Wright J, Durnez J, Poldrack RA, Gorgolewski KJ. fMRIPrep: a robust preprocessing pipeline for functional MRI. Nat Meth. 2018; doi:10.1038/s41592-018-0235-4

## create and re-organise events into BIDS format for easier design matrices creation in Nilearn later

run the following:
create_evs.py

## Create design matrices

The following script creates a design matrix from the previously created events: 

dm_ssib_v2.py

Read the script carefully and adjust the matrix suffix and columns to remove according to the desired design matrix.

Abraham A, Pedregosa F, Eickenberg M, Gervais P, Mueller A, Kossaifi J, Gramfort A, Thirion B and Varoquaux G (2014) Machine learning for neuroimaging with scikit-learn. Front. Neuroinform. 8:14. doi: 10.3389/fninf.2014.00014

## First level model

Read, adjust and run the following script to get contrast z-map per subject and session:

first_level_glm_combined_runs.py

## Compute masks from a meta-analysis ALE map

Read, adjust and run the following script. In our case, the BDM auction task meta-analysis ALE map from Newton-Fenner et al. 2023 was used. 

create_brain_masks.ipynb

Newton-Fenner A, Hewitt D, Henderson J, Roberts H, Mari T, Gu Y, Gorelkina O, Giesbrecht T, Fallon N, Roberts C, Stancak A. Economic value in the Brain: A meta-analysis of willingness-to-pay using the Becker-DeGroot-Marschak auction. PLoS One. 2023 Jul 10;18(7):e0286969. doi: 10.1371/journal.pone.0286969. PMID: 37428744; PMCID: PMC10332630.

## Compute ROI mean z-score per participant and session

Read adjust and run the following script:

compute_ROI_z-score_allcan.py

This script assumes that a BIDS compliant participant.tsv file is available in the data folder. 

## Run ROI analysis in a linear mixed model, plot results per session

For built matrices and contrast to study, read, adjust and run the following script, that gives FDR corrected linear mixed model result for longitudinal analysis of ROI mean z-score BOLD signal. 

LMM_ROIs_v2.ipynb












