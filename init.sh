docker run --rm -ti -v ${PWD}:/base nipy/heudiconv:latest -d /base/sub-{subject}/ses-{session}/*/DICOM/*.dcm -o /base/nifti/ -f convertall -s 02 05 06 07 08 10 12 13 14 16 -ss 001 -c none --overwrite
