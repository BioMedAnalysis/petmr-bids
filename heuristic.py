import os


def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    return template, outtype, annotation_classes


def infotodict(seqinfo):
    """Heuristic evaluator for determining which runs belong where

    allowed template fields - follow python string module:

    item: index within category
    subject: participant id
    seqitem: run number during scanning
    subindex: sub index within group
    """

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
