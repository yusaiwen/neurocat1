from pip import main as pipmain
from os.path import abspath as opa 
import yaml
import os
import sys

import logging
from rich.logging import RichHandler
from rich.console import Console

sys.path.append("..")
from util.alert import *


console = Console()
# configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
log = logging.getLogger("rich")

if not os.getuid():
    log_red_error(log, red_error("Why give me sudo mode? (σﾟ∀ﾟ)σ.."))
    sys.exit(1)

yml_file = opa('install.yml')

with open(yml_file,'r', encoding='UTF-8') as f:
    pip = yaml.load(f, Loader=yaml.Loader).get('pip')


if pip:
    req_file = opa('requirements.txt')
    with console.status("[bold green]Installing dependencies...", spinner='moon') as status:
        pipmain(['install', f'-r{req_file}'])
    console.log("Dependency installed!") # for no reason, log doesn't work here!