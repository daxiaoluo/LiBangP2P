__author__ = 'taoluo'
import platform
import subprocess
import xml.etree.ElementTree as ET

from random import Random

commands = {
    'Darwin': {'ipv4': "ifconfig  | grep -E 'inet.[0-9]' | grep -v '127.0.0.1' | awk '{ print $2}'", 'ipv6': "ifconfig  | grep -E 'inet6.[0-9]' | grep -v 'fe80:' | awk '{ print $2}'"},
    'Linux': {'ipv4': "/sbin/ifconfig  | grep 'inet addr:'| grep -v '127.0.0.1' | cut -d: -f2 | awk '{ print $1}'", 'ipv6': "/sbin/ifconfig  | grep 'inet6 addr:'| grep 'Global' | grep -v 'fe80' | awk '{print $3}'"}
}

def ip_addresses(version):
	proc = subprocess.Popen(commands[platform.system()][version], shell=True,stdout=subprocess.PIPE)
	return proc.communicate()[0].split('\n')


def get_port(protocol):
    return protocol.split("/")[0].lower()

def random_str(randomlength=26, suffix=None):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789-'
    length = len(chars) - 1
    random = Random()
    strList = []
    for i in range(randomlength):
        strList.append(chars[random.randint(0, length)])
    if suffix:
        strList.append("_")
        strList.append(suffix)
    return ''.join(strList)

def set_crontab_configuration(path=None, val='False'):
    if not path:
        return
    tree = ET.parse(path)
    root = tree.getroot()
    for threadChild in root:
        for child in threadChild:
            if child.tag == 'isRun':
                child.text = val
    tree.write(path)


def get_crontab_configuration(path=None, name=None):
    if not path or not name:
        return None
    tree = ET.parse(path)
    root = tree.getroot()
    for threadChild in root:
        if threadChild.attrib.get('className') == name:
            for child in threadChild:
                if child.tag == 'isRun':
                    return child.text
    return None