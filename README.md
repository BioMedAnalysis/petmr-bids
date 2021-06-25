scripts for converting MRI and PET(listmode data) to BIDS format using HeuDiConv.

Useful materials:
* Tutorial about how to use HeuDiConv can be find here: <br>
http://reproducibility.stanford.edu/bids-tutorial-series-part-2a/

* PET ListMode Specification (PEP - not final): <br>
https://bids-specification.readthedocs.io/en/bep-009/04-modality-specific-files/09-positron-emission-tomography.html

* BIDS specs github: <br>
https://github.com/bids-standard/bids-specification

* BIDS online validator: <br>
https://bids-standard.github.io/bids-validator/

* BIDS specitification Python tool, pybids: <br>
https://github.com/bids-standard/pybids

* Heudiconv source code: <br>
https://github.com/nipy/heudiconv


N.B. heudiconv in docker container will be used.


## Usage
1. customized heudiconv.py file
-> follow each of the steps

2. use the existing heudiconv.py
-> follow the steps: 1, 2 and 5


## Instructions (MRI):
### 1. Download Dicom files
N.B. Make sure all the required scans are present.


### 2. Organize the data in the following strucutre:

<pre> 
sub-*/
  sess-*/
    1/
      DICOM/
        dicom files
    2/
      DICOM/
        dicom files
    ...
</pre>

or omit the session level if it is not necessary:
<pre> 
sub-*/
  1/
    DICOM/
      dicom files
  2/
    DICOM/
      dicom files
  ...
</pre>

### 3. Initlized the convertion
3.1 Create a new directory, e.g. 'nifti' in the working directory.

3.2 Run the initialized heudiconv command: <br>

`docker run --rm -ti -v ${PWD}:/base nipy/heudiconv:latest -d /base/sub-{subject}/ses-{session}/*/DICOM/*.dcm -o /base/nifti/ -f convertall -s <subject-IDs> -ss <session-IDs> -c none --overwrite`


examples: <br>
Run the initialized heudiconv command, if session is included: <br>
`docker run --rm -ti -v ${PWD}:/base nipy/heudiconv:latest -d /base/sub-{subject}/ses-{session}/*/DICOM/*.dcm -o /base/nifti/ -f convertall -s 02 05 -ss 001 -c none --overwrite` <br>

if session is omitted, run the following command to initialize: <br>
`docker run --rm -ti -v ${PWD}:/base nipy/heudiconv:latest -d /base/sub-{subject}/*/DICOM/*.dcm -o /base/nifti/ -f convertall -s 02 05 -ss 001 -c none --overwrite`

### 4. prepare heudiconv.py script

4.1 After running the init step (step 3 above), there will be template heudiconv.py file in: <br>

`nifti/.heudiconv/<sub-id>/info/`

4.2 modify the heudiconv.py according to the dataset.

An example can be seen below:

<pre>
import os


def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    return template, outtype, annotation_classes


def infotodict(seqinfo):

    t1w = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_run-00{item:01d}_T1w')
    fmap_mag = create_key('sub-{subject}/{session}/fmap/sub-{subject}_{session}_magnitude')
    fmap_phase = create_key('sub-{subject}/{session}/fmap/sub-{subject}_{session}_phasediff')
    dixon = create_key('sub-{subject}/{session}/dixon/sub-{subject}_{session}_run-00{item:01d}_dixon')
    ute = create_key('sub-{subject}/{session}/ute/sub-{subject}_{session}_run-00{item:01d}_ute')
    fmri_full = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-fullchecker_run-00{item:01d}_bold')
    fmri_half = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-halfchecker_run-00{item:01d}_bold')
    fmri_rest = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-rest_run-00{item:01d}_bold')

    info = {t1w:[], fmap_mag:[], fmap_phase:[], dixon:[], ute:[], fmri_full:[], fmri_half:[], fmri_rest:[]}
    #info = {t1w:[], fmap_mag:[], fmap_phase:[], dixon:[], ute:[], fmri_full:[]}
    last_run = len(seqinfo)

    for s in seqinfo:
        """
        The namedtuple `s` contains the following fields:

        * total_files_till_now
        * example_dcm_file
        * series_id
        * dcm_dir_name
        * unspecified2
        * unspecified3
        * dim1
        * dim2
        * dim3
        * dim4
        * TR
        * TE
        * protocol_name
        * is_motion_corrected
        * is_derived
        * patient_id
        * study_description
        * referring_physician_name
        * series_description
        * image_type
        """
        if ('t1_mprage_sag 1 iso' in s.protocol_name):
            info[t1w].append(s.series_id)
        
        if (s.dim1 == 64) and (s.dim3 == 88) and 'gre_field_mapping' in s.protocol_name:
            info[fmap_mag] = [s.series_id]

        if (s.dim1 == 64) and (s.dim3 == 44) and 'gre_field_mapping' in s.protocol_name:
            info[fmap_phase] = [s.series_id]

        if 'Head_MRAC_PET DIXON' in s.protocol_name:
            info[dixon].append(s.series_id)

        if 'Head_MRAC PET UTE' in s.protocol_name:
            info[ute].append(s.series_id)

        if 'Full_checker_ep2d_task_bold' in s.protocol_name:
            info[fmri_full].append(s.series_id)

        if 'Half_checker_ep2d_task_bold' in s.protocol_name:
            info[fmri_half].append(s.series_id)

        if 'Rest_ep2d_task_bold' in s.protocol_name:
            info[fmri_rest].append(s.series_id)

    return info

</pre>

### 5. run conversion
5.1 Copy the heudiconv.py file to 
`nifti/code/`

5.2 Start conversion

``docker run --rm -ti -v ${PWD}:/base nipy/heudiconv:latest -d /base/sub-{subject}/ses-{session}/*/DICOM/*.dcm -o /base/nifti/ -f /base/nifti/code/heuristic.py -s <subject-IDs> -ss <session-IDs> -c dcm2niix -b --overwrite``

example (with session): <br>
`docker run --rm -ti -v ${PWD}:/base nipy/heudiconv:latest -d /base/sub-{subject}/ses-{session}/*/DICOM/*.dcm -o /base/nifti/ -f /base/nifti/code/heuristic.py -s 02 05 06 07 08 10 12 13 14 16 -ss 001 -c dcm2niix -b --overwrite`

example (without session): <br>
`docker run --rm -ti -v ${PWD}:/base nipy/heudiconv:latest -d /base/sub-{subject}/ses-{session}/*/DICOM/*.dcm -o /base/nifti/ -f /base/nifti/code/heuristic.py -s 02 05 06 07 08 10 12 13 14 16 -c dcm2niix -b --overwrite`


### 6. validate
There are several ways can be used to validate a dataset is BIDS valid. The online and commandline validation are recommended.

6.1 online validation
You can upload the directory to the online validation link:
http://bids-standard.github.io/bids-validator/

6.2 commandline with docker (recommended)

`docker run -ti --rm -v ${PWD}:/data:ro bids/validator /data`

where the ${PWD} is the current directory, so change the directory to the path (where the bids dataset resides) before launching the validation.


### 7. deface structual images

Option 1 (recommended):

tool: pydeface

link: https://github.com/poldracklab/pydeface

* run defacing using pydeface: `pydeface <input file>`
* Options: 
  * --cost : cost function (default: mutualinfo)
  * --applyto : for some scans that is not easy to be defaced, using --applyto can solve the issue
  * e.g. `pydeface <input file 1> --cost leastsq --applyto <input file 2> <input file 3>`

Option 2: 

tool: https://surfer.nmr.mgh.harvard.edu/fswiki/mri_deface

* make the mri_deface executable: `chmod +x mri_deface`
* run `./mri_deface <input> talairach_mixed_with_skull.gca face.gca <output>`

### 8. upload to OpenNeuro from command line
the tool used is the openneuro-cli nodejs package

the installation instrument of cli tool: https://www.npmjs.com/package/openneuro-cli

8.1. generate API key
To authenticate with the openneuro server, a API key need to be generated from the OpenNeuro web page.
https://openneuro.org/keygen

8.2. openneuro login

* run
`openneuro login` 
from command line to setup the authentication information.

* `Choose an OpenNeuro instance to use. **https://openneuro.org/**`

* paste the api key in the command line (input is hidden)

8.3 upload dataset
run 
`openneuro upload <dataset directory>`

8.4 update dataset
To resume an interrupted upload or add files to an existing dataset:

`openneuro upload --dataset <accession number> <dataset directory>`

to ignore the warning in BIDS

`openneuro upload -i --dataset <accession number> <dataset directory>`

where <accession_number> is a unique dataset identifier that can be found in the URL. For example accession number for https://openneuro.org/datasets/ds001555 is ds001555.

