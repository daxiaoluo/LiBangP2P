__author__ = 'taoluo'

import os
if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "libangp2p.settings")
    from core.crontab import openCrontab
    from utils.utils import set_crontab_configuration
    rootPath = os.path.dirname(os.path.realpath(__file__))
    set_crontab_configuration(rootPath + "/configuration/crontabControl.xml", "True")
    openCrontab("crontabControl.xml")