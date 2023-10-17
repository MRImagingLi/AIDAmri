"""
Created on 27/10/2020

@author: Leon Scharwächter
AG Neuroimaging and Neuroengineering of Experimental Stroke
Department of Neurology, University Hospital Cologne

This script automates the conversion from the raw bruker data format to the NIfTI
format for the whole dataset using 1_PV2NIfTiConverter/pv_conv2Nifti.py. The raw
data needs to be in the following structure: projectfolder/days/subjects/data/.
For this script to work, the groupMapping.csv needs to be adjusted, where the group
name of every subject's folder in the raw data structure needs to be specified.
This script computes the conversion either for all data in the raw project folder
or for certain days and/or groups specified through the optionalx
arguments -d and -g . During the processing a new folder called proc_data is being
created in the same directory where the raw data folder is located.

Example:
python conv2Nifti_auto.py -f /Volumes/Desktop/MRI/raw_data -d Baseline P1 P7 P14
"""

import os
import csv
import json
import pandas as pd
import nibabel as nii
import glob as glob
from pathlib import Path
import numpy as np
import re

def create_slice_timings(method_file, out_file):
    with open(method_file, "r") as infile:
        lines = infile.readlines()
        interleaved = False
        repetition_time = None
        slicepack_delay = None
        slice_order = []
        n_slices = 0
        reverse = False
        
        for idx, line in enumerate(lines):
            if "RepetitionTime=" in line:
                repetition_time = int(float(line.split("=")[1]))
                repetition_time = int(repetition_time)
            if "PackDel=" in line:
                slicepack_delay = int(float(line.split("=")[1]))
            if "ObjOrderScheme=" in line:
                slice_order = line.split("=")[1]
            if slice_order == 'Sequential':
                interleaved = False
            else:
                interleaved = True
            if "ObjOrderList=" in line:    
                n_slices = re.findall(r'\d+', line)
                if len(n_slices) == 1:
                    n_slices = int(n_slices[0])
                if lines[idx+1]:
                    slice_order = [int(float(s)) for s in re.findall(r'\d+', lines[idx+1])]
                    if slice_order[0] > slice_order[-1]:
                        reverse = True

        slice_timings = calculate_slice_timings(n_slices, repetition_time, slicepack_delay, slice_order, reverse)

        # adjust slice order to start at 1
        slice_order = [x+1 for x in slice_order]
           
        #save metadata
        mri_meta_data = {}
        mri_meta_data["RepetitionTime"] = repetition_time
        mri_meta_data["ObjOrderList"] = slice_order
        mri_meta_data["n_slices"] = n_slices
        mri_meta_data["costum_timings"] = slice_timings

        with open(out_file, "r") as outfile:
            content = json.load(outfile)
            #update brkraw content with own slice timings
            content.update(mri_meta_data)
            with open(out_file, "w") as outfile:
                json.dump(content, outfile)
                 

def calculate_slice_timings(n_slices, repetition_time, slicepack_delay, slice_order, reverse=False):
    n_slices_2 = int(n_slices / 2)
    slice_spacing = float(repetition_time - slicepack_delay) / float(n_slices * repetition_time)
    if n_slices % 2 == 1: # odd
        slice_timings = list(range(n_slices_2, -n_slices_2 - 1, -1))
        slice_timings = list(map(float, slice_timings))
    else: # even
        slice_timings = list(range(n_slices_2, -n_slices_2, -1))
        slice_timings = list(map(lambda x: float(x) - 0.5, slice_timings))

    if reverse:
        slice_order.reverse()
    
    slice_timings = list(slice_timings[x] for x in slice_order)

    return list((slice_spacing * x) for x in slice_timings)



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='This script automates the conversion from the raw bruker data format to the NIfTI format using 1_PV2NIfTiConverter/pv_conv2Nifti.py. The raw data needs to be in the following structure: projectfolder/days/subjects/data/. For this script to work, the groupMapping.csv needs to be adjusted, where the group name of every subject''s folder in the raw data structure needs to be specified. This script computes the converison either for all data in the raw project folder or for certain days and/or groups specified through the optional arguments -d and -g. During the processing a new folder called proc_data is being created in the same directory where the raw data folder is located. Example: python conv2Nifti_auto.py -f /Volumes/Desktop/MRI/raw_data -d Baseline P1 P7 P14 P28')
    parser.add_argument('-i', '--input', required=True,
                        help='Path to the parent project folder of the dataset, e.g. raw_data', type=str)
    parser.add_argument('-o', '--output', type=str, required=False, help='Output directory where the results will be saved.')

    ## read out parameters
    args = parser.parse_args()
    pathToRawData = args.input
    if args.output == None:
        output_dir = os.path.join(pathToRawData, "proc_data")
    else:
        output_dir = args.output
    
    # get list of raw data in input folder
    list_of_raw = sorted([d for d in os.listdir(pathToRawData) if os.path.isdir(os.path.join(pathToRawData, d)) \
                              or (os.path.isfile(os.path.join(pathToRawData, d)) and (('zip' in d) or ('PvDataset' in d)))])

    # create list with full paths of raw data
    list_of_paths = []        
    for idx, path in enumerate(list_of_raw):
        full_path = os.path.join(pathToRawData, path)
        list_of_paths.append(full_path)
        
    ## perform bruker to nifti conversion for all files    
    for idx, sub in enumerate(list_of_paths):
        os.system('cd ' + sub)
        os.system('brkraw tonii ' + sub + ' -o ' + sub)
       
    ## rearrange proc data in BIDS-format   
    os.system('brkraw bids_helper ' + pathToRawData + ' ' + "dataset" + ' -j')
    
    # adjust dataset.json template
    with open("dataset" + '.json', 'r') as infile:
        meta_data = json.load(infile)
        meta_data["common"]["RepititionTime"] = ""
        if meta_data["common"]["EchoTime"]:
            del meta_data["common"]["EchoTime"]
            
        with open("dataset" + '.json', 'w') as outfile:
            json.dump(meta_data, outfile)
          
    # convert to bids
    os.system('brkraw bids_convert ' + pathToRawData + ' ' + "dataset" + '.csv ' + '-j ' + "dataset" + '.json ' + ' -o ' + output_dir) 
    
    # delete duplicated files in input folder
    all_files_input_folder = os.listdir(pathToRawData)
    del_file_ext = [".nii", ".bval", ".bvec"]
    
    for file in all_files_input_folder:
        if file not in list_of_raw and file != output_dir and any(ext in file for ext in del_file_ext):
            os.remove(os.path.join(pathToRawData,file)) 
    
    # find MEMS and fmri files 
    mese_scan_ids = []
    fmri_scan_ids = {}
    with open(os.path.abspath("dataset.csv"), 'r') as csvfile:
        df = pd.read_csv(csvfile, delimiter=',')
        for index, row in df.iterrows():
            # save every sub which has MEMS scans
            if row["modality"] == "MESE":
                mese_scan_ids.append(row["SubjID"])
            # save every sub and scanid wich is fmri scan
            if row["DataType"] == "func":
                fmri_scan_ids[row["RawData"]] = {}
                fmri_scan_ids[row["RawData"]]["ScanID"] = row["ScanID"] 
                fmri_scan_ids[row["RawData"]]["SessID"] = row["SessID"]
                fmri_scan_ids[row["RawData"]]["SubjID"] = row["SubjID"]
                
    # iterate over every subject and ses to check if MEMS files are included
    for idx, sub in enumerate(mese_scan_ids):
        mese_scan_path = os.path.join(output_dir, "sub-" + sub)
        sessions = os.listdir(mese_scan_path)
        for ses in sessions:
            anat_data_path = os.path.join(mese_scan_path, ses, "anat", "*MESE.nii*")
            mese_data_paths = glob.glob(anat_data_path, recursive=True)
            
            
            #skip the subject if no MEMS files are found
            if not mese_data_paths:
                continue
            
            # collect data of all individual MEMS files of one subject and session
            img_array_data = {}
            for m_d_p in mese_data_paths:
                # find slice numer in path. e.g.: *echo-10_MESE.nii.gz, extract number 10
                slice_number = int(((Path(m_d_p).name).split('-')[-1]).split('_')[0])
            
                # load nifti image and save the array in a dict while key is the slice number
                data = nii.load(m_d_p)
                affine = data.affine
                img_array = data.get_fdata()
                img_array_data[slice_number] = img_array

            
            # sort imgs into right order 
            sorted_imgs = []
            for key in sorted(img_array_data):
                sorted_imgs.append(img_array_data[key])
              
            # stack all map related niftis
            new_img = np.stack(sorted_imgs, axis=2)
            nii_img = nii.Nifti1Image(new_img, affine)
            
            # save nifti file in anat folder
            img_name = "sub-" + sub + "_" + ses + "_T2w_map.nii.gz"
            nii.save(nii_img, os.path.join(output_dir, "sub-" + sub, ses, "anat", img_name))
            
            
    # iterate over all fmri scans to calculate and save costum slice timings
    for sub, data in fmri_scan_ids.items():
        scanid = str(data["ScanID"])
        sessid = str(data["SessID"])
        subjid = str(data["SubjID"])
        
        # determine method file path
        fmri_scan_method_file = os.path.join(pathToRawData, sub, scanid, "method")
        
        # determine output json file path
        out_file = os.path.join(output_dir, "sub-" + subjid, "ses-" + sessid, "func", "sub-" + subjid + "_ses-" + sessid + "_EPI.json")
        
        # calculate slice timings
        create_slice_timings(fmri_scan_method_file, out_file)
     
    print("\n")
    print("###")
    print("All duplicated files have been deleted")     

    print("\n")
    print("###")
    print("Finished converting raw data into nifti format!")
  


