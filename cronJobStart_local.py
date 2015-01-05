__author__ = 'taoluo'

import os

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "libangp2p.settings_local")
    import libangp2p.settings_local
    from utils.utils import set_crontab_configuration
    from core.crontab import openCrontab
    rootPath = os.path.dirname(os.path.realpath(__file__))
    set_crontab_configuration(rootPath + "/configuration/crontabControl_dev.xml", "True")
    openCrontab("crontabControl_dev.xml")