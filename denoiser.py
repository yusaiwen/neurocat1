#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Seven Yu
# @Date: May 8, 2022
# @Function: Denoising 4D fMRI BOLD file
# Copyright:
#    Made by Seven Yu with ♥ 
#    yusaiwen@mail.bnu.edu.cn,
#    State Key Laboratory of Cognitive Neuroscience and Learning,
#    Beijing Normal University,
#    No.19 Xinjiekouwai Street, Haidian District,
#    Beijing, China, 100875

VERSION = '0.1.0'
NAME = 'fMRI Denoiser'
ACCOUNT = 'Denoise fMRI NIFTI file following fMRIPREP'
COMMAND_NAME = 'denoiser'
MEME = "💦"



# load basic packages
from rich.color import Color
from rich.text import Text
from rich.console import Console

#import rich_click as click
import click

from os.path import exists as ope
from os.path import abspath as opa
from os.path import join as opj
import os
import sys

import logging
from rich.logging import RichHandler

from bids import BIDSLayout

import warnings
with warnings.catch_warnings():
    # silent nilearn.image
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    from nilearn import image as nimg
from nilearn.interfaces.fmriprep import load_confounds as load_confounds
from nilearn.image import clean_img as denoiser

import numpy as np

# self
from util import RC
from util.alert import *

class NoSuchPath(Exception):
    '''
    An self-made exception: No such path
    '''
    pass

def yaml2dic(yml_file):
    import yaml 

    with open(yml_file,'r', encoding='UTF-8') as f:
        return yaml.load(f, Loader=yaml.Loader)


def k2n(keys):
    # keys to numpys
    return np.array(list(keys))

def get_task(layout):
    return layout.get_task()
def get_run(layout):
    return layout.get_run()
def get_subjects(layout):
    from natsort import natsorted as ns
    return ns(layout.get_subjects())
def get_TR(layout):
    return layout.get_tr()

def get_bids_meta(layout, info):
    switcher = {
        'sub_list': get_subjects(layout),
        'task': get_task(layout),
        'run': get_run(layout),
        'TR': get_TR(layout)
    }
    return switcher.get(info)
    

def get_fmri(sub, layout, task, run, log):        
    fmri_file = layout.get(
        scope='derivatives',
        subject=sub,
        task=task,
        run=run,
        space='MNI152NLin2009cAsym',
        return_type='file',
        extension='nii.gz',
        suffix='bold'
    )
    if len(fmri_file) != 1:
        try:
            raise ValueError
        except:
            error_account = 'Multiple fMRI file or none fMRI file was found (／‵Д′)／~ ╧╧'
            log_red_error(log, error_account)
            sys.exit(1)
    return fmri_file[0]

def get_mask(sub, layout, task, run, log):
    mask_file = layout.get(
        scope='derivatives',
        subject=sub,
        task=task,
        run=run,
        space='MNI152NLin2009cAsym',
        return_type='file',
        extension='nii.gz',
        suffix='mask'
    )
    if len(mask_file) != 1:
        try:
            raise ValueError
        except:
            error_account = 'Multiple fMRI mask file or none fMRI mask file was found (／‵Д′)／~ ╧╧'
            log_red_error(log, error_account)
            sys.exit(1)
    return mask_file[0]

def get_confounds(fmri_file, confounds):
    with warnings.catch_warnings():
    # silent nilearn.image
        warnings.filterwarnings("ignore", category=UserWarning)

        stra = confounds.get('strategy')
        stra_keys = k2n(stra.keys())
        stra_index = np.where(k2n(stra.values()) == True)
        strategy = list(stra_keys[stra_index])

        return load_confounds(
            # this strategy contains 36 parameters
            # to be updated!
            img_files=fmri_file,
            strategy=strategy,
            motion=confounds.get('motion'),
            wm_csf=confounds.get('wm_csf'),
            global_signal=confounds.get('global_signal')
        )

def denoise_run(sub, layout, task, run, confounds, TR, pass_band, console, log):
    # get two files
    # * 4D fMRI NiFTI file
    # * mask
    # * confounds
    fmri_file = get_fmri(sub, layout, task, run, log)
    mask_file = get_mask(sub, layout, task, run, log)
    confounds = get_confounds(fmri_file, confounds)

    console.log(f"fMRI file: {fmri_file} \nfMRI mask: {mask_file}")

    # drop the dummy scans
    raw_func_img = nimg.load_img(fmri_file)
    func_img = raw_func_img.slicer[:,:,:,4:] # 4th dim is time, d with the first four volumes
    mask_img = nimg.load_img(mask_file)

    # denoising!
    denoised_img = denoiser(
        imgs=func_img,
        confounds=confounds[0].loc[4:], # confounds should be trimed as well
        low_pass=pass_band[0],
        high_pass=pass_band[1],
        t_r=TR,
        mask_img=mask_img
    )
    denoise_tmp_dir = opa('/tmp/denoising')
    denoise_tmp_file = opj(denoise_tmp_dir, 'sub-'+str(sub)+'_task-'+task+'_run-'+str(run)+'_denoised_img.nii.gz')
    denoised_img.to_filename(denoise_tmp_file)

RC.VERSION, RC.NAME, RC.ACCOUNT, RC.COMMAND_NAME, RC.MEME = [VERSION, NAME, ACCOUNT, COMMAND_NAME, MEME]
@click.command(cls=RC.RichCommand)
@click.option('--config', '-c',
              required=True,
              type=str,
              help='General YAML configuration file.'
             )
@click.option('--denoise', '-d',
              required=True,
              type=str,
              help='Denoise YAML configuration file.'
             )
@click.option('--log_level', '-l',
              default='INFO',
              show_default=True,
              metavar='CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET',
              type=click.Choice(['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']),
              help="Logging level."
             )
@click.option("--version", "-v",
              is_flag=True,
              help="Print version and exit."
             )
################ main function ############
def main(config,
         denoise,
         log_level: str = 'INFO',
         version: bool = False
         ):

    console = Console()

    if version:
        """
            print the version and leave
        """
        console.print(f"{VERSION}\n")
        sys.exit(1)

    # configure log package
    logging.basicConfig(
        level=eval(f"logging.{log_level}"),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    log = logging.getLogger("rich")

    # read general configuration file
    ge_config = opa(config)

    if not ope(ge_config):
        # if json file exists ?
        try:
            raise NoSuchPath
        except:
            error_account = 'Can\'t find your general configuration file (／‵Д′)／~ ╧╧'
            log_red_error(log, error_account)
            sys.exit(1)

    bids_dir, layout_dir = list(yaml2dic(ge_config).values())

    # read denoise configuration file
    de_config = opa(denoise)

    if not ope(de_config):
        # if json file exists ?
        try:
            raise NoSuchPath
        except:
            error_account = 'Can\'t find your denoising configuration file (／‵Д′)／~ ╧╧'
            log_red_error(log, error_account)
            sys.exit(1)

    confounder, pass_band, dummy = list(yaml2dic(de_config).values())

    # load pyBIDS
    layout_dir = opj(bids_dir, layout_dir)
    if not ope(layout_dir):
        try:
            raise NoSuchPath
        except:
            error_account = 'Can\'t find your layout path (／‵Д′)／~ ╧╧'
            log_red_error(log, error_account)
            sys.exit(1)
    else:
        console.log(f"Layout directory {layout_dir} found!")

    layout = BIDSLayout.load(layout_dir)

    # Get BIDS meta info
    info_list = ['sub_list', 'task', 'run', 'TR']
    info_dic = {}

    with console.status("[bold green]Get BIDS meta info...", spinner='moon') as status:
        while info_list:
            info = info_list.pop(0)
            info_dic[info] = get_bids_meta(layout, info)
            console.log(f"Fetched {info}: {info_dic.get(info)}!")
    
    # if just one run(run list is empty), run should be [None]
    if not len(info_dic.get('run')):
        info_dic['run'] = [None]

    with console.status("[bold green]Denoising...", spinner='moon') as status:
        #for sub in [1]: 
        for sub in info_dic.get('sub_list'):
            for task in info_dic.get('task'):
                for run in info_dic.get('run'):
                    denoise_run(sub=sub,
                                layout=layout,
                                task=task,
                                run=run,
                                TR = info_dic.get('TR'),
                                pass_band = pass_band,
                                confounds=confounder,
                                console=console,
                                log=log)
            console.log(f"sub {sub} complete")
    cong_account = 'Great! You\'ve done everything without error!  (ﾉ>ω<)ﾉ'
    console.log(cong_account, style='bold yellow')

if __name__ == '__main__':
    main()