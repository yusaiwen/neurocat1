import yaml
from os.path import abspath as opa 
from os.path import exists as ope
from os.path import join as opj
import os
import sys
from shutil import copytree
import rich
import logging
from rich.logging import RichHandler

sys.path.append("..")
from util.alert import *

# configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
log = logging.getLogger("rich")

if os.getuid():
    log_red_error(log, red_error("Why don't give me sudo mode? (／‵Д′)／~ ╧╧"))
    sys.exit(1)

def run():
    yml_file = opa('install.yml')

    with open(yml_file,'r', encoding='UTF-8') as f:
        ins = yaml.load(f, Loader=yaml.Loader)

    dest_dir = ins.get('dest')
    bin_dir = ins.get('bin')

    # make sure to have super power
    try:
        copytree(opa('../../neurocat'), opj(dest_dir, 'neurocat'))
    except FileExistsError:
        log_red_error(log, f"{opj(dest_dir, 'neurocat')} exists (／‵Д′)／~ ╧╧ \nTry \[sudo] rm -rf {opj(dest_dir, 'neurocat')}")
        sys.exit(1)

    if ope(opj(bin_dir, 'denoiser')):
        os.remove(opj(bin_dir, 'denoiser'))
    else:
        os.system(f"ln -s {opj(dest_dir, 'neurocat', 'denoiser.py')} {opj(bin_dir, 'denoiser')}")

    log.info(f"[bold yellow]Congradulations! You have installed Neurocat!\nMain program in {opj(dest_dir, 'neurocat')}\nShortcut in {opj(bin_dir, 'denoiser')}", extra={"markup": True})
    log.info("[bold yellow]Done! Everything in control (ﾉ>ω<)ﾉ", extra={"markup": True})

if __name__ == '__main__':
    log_red_error(log, "Don't run me directly! (／‵Д′)／~ ╧╧")
    sys.exit(1)