#!/bin/bash
# This script will segment the images in the current directory

MRA_ROOT=$(dirname $(readlink -f "$0"))/..

# Show each command and exit on errors
IMGDIR=${IMGDIR:-$MRA_ROOT/images}
OUTDIR=${OUTDIR:-$MRA_ROOT/output}
DEBUG=${DEBUG:-False}

# Make sure parallel is installed
if ! which parallel > /dev/null; then
    echo "Please install GNU parallel, e.g. 'sudo apt-get install parallel'"
    exit 1
fi

# Find all images in the image directory and segment them in parallel
find "${IMGDIR}" -iname '*.jpg' |\
  awk -F '/' '{print $(NF-1)"/"$NF}' |\
  parallel  mra seg -i "${IMGDIR}"/{} -o "${OUTDIR}"/{} --debug=${DEBUG}

# Count the positive and negative examples and report accuracy
# TODO this assumes that the output images are in `pos` and `neg` folders
npos=$(find "${OUTDIR}/pos" -iname '*.jpg' | wc -l | xargs)
nneg=$(find "${OUTDIR}/neg" -iname '*.jpg' | wc -l | xargs)
npos_gt=$(find "${IMGDIR}/pos" -iname '*.jpg' | wc -l | xargs)
nneg_gt=$(find "${IMGDIR}/neg" -iname '*.jpg' | wc -l | xargs)

echo "Found rover segments in ${npos}/${npos_gt} positive examples"
echo "Incorrectly found rover segments in ${nneg}/${nneg_gt} negative examples"
echo "Total Accuracy: $(echo "scale=2; 100*(${npos} + ${nneg_gt} - ${nneg})/(${npos_gt}+${nneg_gt})" | bc)%"
