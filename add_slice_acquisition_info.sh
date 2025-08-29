#!/bin/bash

# Define the directory containing the BIDS dataset 
bids_dir="$HOME/projects/def-account/share/projectname/data2"

# Define the SliceTiming field with 59.78260 ms increments for exactly 45 points
slice_timing=$(awk 'BEGIN { for (i = 0; i < 45; i++) printf "%.8f,", i * 0.05978260; printf "\n" }' | sed 's/,$//')

# Traverse the BIDS directory

find "$bids_dir" -type f -name "*bold.json" | while read -r json_file; do
    # Debug: Print the current JSON file being processed
    echo "Processing: $json_file"

    # Extract the PhaseEncodingAxis from the JSON file
    phase_encoding_axis=$(jq -r '.PhaseEncodingAxis // empty' "$json_file")

    # Determine PhaseEncodingDirection based on PhaseEncodingAxis
    case "$phase_encoding_axis" in
        "i") phase_encoding_direction="j" ;;
        "j") phase_encoding_direction="j" ;;
        "k") phase_encoding_direction="k" ;;
        *) 
            echo "Warning: Invalid or missing PhaseEncodingAxis in $json_file. Skipping."
            continue
            ;;
    esac

    # Check if EstimatedTotalReadoutTime exists and rename it to TotalReadoutTime
    if jq -e '.EstimatedTotalReadoutTime? // empty' "$json_file" > /dev/null; then
        temp_file=$(mktemp)
        jq '.TotalReadoutTime = .EstimatedTotalReadoutTime | del(.EstimatedTotalReadoutTime)' "$json_file" > "$temp_file" && mv "$temp_file" "$json_file"
        if [[ $? -eq 0 ]]; then
            echo "Renamed EstimatedTotalReadoutTime to TotalReadoutTime in: $json_file"
        else
            echo "Failed to rename EstimatedTotalReadoutTime in: $json_file"
        fi
    fi

    # Extract participant and session information from the path
    participant=$(echo "$json_file" | grep -oP "sub-[^/]+" || echo "Unknown participant")
    session=$(echo "$json_file" | grep -oP "ses-[^/]+" || echo "Unknown session")

    # Debug: Print participant and session information
    echo "Participant: $participant, Session: $session"

    # Load the JSON file and add the new fields
    temp_file=$(mktemp)
    jq --argjson sliceTiming "[$slice_timing]" \
       --arg PhaseEncodingDirection "$phase_encoding_direction" \
       '.SliceTiming = $sliceTiming | .PhaseEncodingDirection = $PhaseEncodingDirection' \
       "$json_file" > "$temp_file" && mv "$temp_file" "$json_file"

    # Check if jq succeeded
    if [[ $? -eq 0 ]]; then
        echo "Updated: $json_file"
    else
        echo "Failed to update: $json_file"
    fi

    # Make sure t1s and fmap .jsons don't have SliceTiming and SliceEncodingDirection
    if [[ "$json_file" != *"bold"* ]]; then
        jq 'del(.SliceTiming, .PhaseEncodingDirection)' "$json_file" > "$temp_file" && mv "$temp_file" "$json_file"
        if [[ $? -eq 0 ]]; then
            echo "Removed SliceTiming and PhaseEncodingDirection from: $json_file"
        else
            echo "Failed to remove SliceTiming and PhaseEncodingDirection from: $json_file"
        fi
    fi

    # Check if PhaseEncodingDirection exists and has a value
    if jq -e '.PhaseEncodingDirection? // empty' "$json_file" > /dev/null; then
        # Remove PhaseEncodingAxis if PhaseEncodingDirection exists and has a value
        jq 'del(.PhaseEncodingAxis)' "$json_file" > "$temp_file" && mv "$temp_file" "$json_file"
        if [[ $? -eq 0 ]]; then
            echo "Removed PhaseEncodingAxis from: $json_file"
        else
            echo "Failed to remove PhaseEncodingAxis from: $json_file"
        fi
    fi

done

echo "All JSON files updated successfully."
