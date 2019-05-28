import argparse
from amaze.validate_solution import validate_solution_text
parser = argparse.ArgumentParser(description='Compare solutions.')
parser.add_argument('file1', type=str, help='first file')
parser.add_argument('file2', type=str, help='second file')
args = parser.parse_args()
first_file = args.file1
second_file = args.file2

with open(first_file, 'r') as file:
    first_data = file.read().split('\n')
with open(second_file, 'r') as file:
    second_data = file.read().split('\n')

count = 0
for line in first_data:
    count+=1
    filename1 = first_data[count].split(",")[0]
    scount = 0
    found = False
    for s in second_data:
        if second_data[scount].split(",")[0] == filename1:
            found = True
            break
        scount+=1
    if not found:
        print("Missing file:"+filename1+" for "+second_file)
        continue
    filename2 = second_data[scount].split(",")[0]
    both_valid = True
    if not validate_solution_text(first_data[count], 0, True):
        print("wrong solution for "+filename1+" at "+first_file)
        both_valid = False
    try:
        f = second_data[scount]
        if not validate_solution_text(second_data[scount], 0, True):
            print("wrong solution for "+filename2+" at "+second_file)
            both_valid = False
    except:
        print("wrong (error) solution for "+filename2+" at "+second_file)
        both_valid = False
    if not both_valid:
        continue
    data1 = first_data[count].split(",")[2:]
    data2 = second_data[scount].split(",")[2:]
    if len(data1)>len(data2):
        print(f"{filename1}==> won {second_file} {len(data1)}:{len(data2)}")
    elif len(data2)>len(data1):
        print(f"{filename1}==> won {first_file} {len(data1)}:{len(data2)}")
    else:
        print(filename1+"==> same")


