import re
import os
import argparse


def check_new(bug_info):
    global global_context
    global id_num
    # print bug_info
    temp_context = get_context.findall(bug_info)
    # print temp_context
    for utilmate_target in target:
        if utilmate_target in temp_context[0][1]:
            id_num += 1
            change = 1
            # print temp_context
            if len(global_context) !=0:
                for context in global_context:
                    if len(context) != len(temp_context):
                        continue
                    num = 0
                    for line in context:
                        if line[1] != temp_context[num][1]:
                            continue
                        num += 1
                    change = 0
                    break
                if change:
                    global_context.append(temp_context)
            else:
                global_context.append(temp_context)



global_context = list()
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-target", metavar="target file",
                        type=str,
                        help="target file", required=True)
    parser.add_argument("-bugfile", metavar="sanitizer bug output",
                        type=str,
                        help="address sanitizer bug output file", required=True)         
    args = parser.parse_args()
    process_bug = ''
    get_context = re.compile(r' .*#(\d+) .*/(.*:\d+:\d+)')
    id_num = 0
    total_num = 0
    with open(args.target, 'r') as file:
        target = file.readlines()
        target = [_.strip('\n') for _ in target]
    with open(args.bugfile, 'r') as buf_file:
        for temp_process in buf_file:
            # print temp_process
            # print process_bug
            if "id:" in temp_process and process_bug:
                total_num += 1
                check_new(process_bug)
                process_bug = temp_process
            else:
                process_bug += temp_process
    print str(total_num), str(id_num), len(global_context)
    print global_context
