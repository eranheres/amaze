from xml.etree import ElementTree as ET
from env import Env


def env_from_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    data = root.findall('.//data')[0].text
    level = "".join(data.replace('\n', '').replace('3', '1').replace('2', '1').replace('0', '2').replace('1', '0').split(','))
    width = int(root.findall('.//layer')[0].get('width'))
    height = int(root.findall('.//layer')[0].get('height'))


    start_pos = level.find('0')
    #start_pos = 12*10+2
    return Env(list(level), start_pos % width, int(start_pos / width), width, height)
