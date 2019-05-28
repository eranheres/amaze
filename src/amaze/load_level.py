from xml.etree import ElementTree as ET


def env_from_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    data = root.findall('.//data')[0].text
    level = "".join(data.replace('\n', '').replace('3', '1').replace('2', '1').replace('0', '2').replace('1', '0').split(','))
    width = int(root.findall('.//layer')[0].get('width'))
    height = int(root.findall('.//layer')[0].get('height'))

    start_pos = -1
    for i in range(0,width):
        for j in list(range(i, len(level), width))[::-1]:
            if level[j] == '0':
                start_pos = j
                break
        if start_pos != -1:
            break
    #for i in list(range(0, len(level), width))[::-1]:
    #    zero_pos = level[i:i+width].find('0')
    #    if zero_pos != -1:
    #        start_pos = zero_pos + i
    #        break
    #start_pos = level.find('0')
    #start_pos = 12*10+2
    return list(level), start_pos, width, height
