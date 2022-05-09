import yaml
from os.path import abspath as opa 
from os.path import exists as ope
from os.path import join as opj
from os.path import islink as opi
import os
import sys
from shutil import rmtree
import rich
import logging
from rich.logging import RichHandler
import sys
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

def main(argv=None):
    yml_file = opa('install.yml')

    with open(yml_file,'r', encoding='UTF-8') as f:
        ins = yaml.load(f, Loader=yaml.Loader)

    dest_dir = ins.get('dest')
    bin_dir = ins.get('bin')

    if ope(opj(bin_dir, 'denoiser')) | opi(opj(bin_dir, 'denoiser')):
        os.remove(opj(bin_dir, 'denoiser'))
        log.info(f"Shortcut {opj(bin_dir, 'denoiser')} deleted!")

    if ope(opj(dest_dir, 'neurocat')):
        rmtree(opj(dest_dir, 'neurocat'))
        log.info(f"Main program {opj(dest_dir, 'neurocat')} deleted!")


    log.info("[bold yellow]Done! Everything in control (ﾉ>ω<)ﾉ", extra={"markup": True})
    
if __name__ == '__main__':
    main()