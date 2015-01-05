__author__ = 'taoluo'

import os
from utils.utils import set_crontab_configuration

if __name__ == "__main__":
    rootPath = os.path.dirname(os.path.realpath(__file__))
    set_crontab_configuration(rootPath + "/configuration/crontabControl.xml", "False")