import re
import os
import argparse
import subprocess
import time

get_first = lambda x:x[0]
get_second = lambda x:x[1]

def get_test_seed(all_seed):
    needed_seed = list()
    global global_num
    if os.path.isdir(os.path.join(all_seed, 'queue')):
        for queue in os.listdir(os.path.join(all_seed, 'queue')):
            if os.path.isfile(os.path.join(os.path.join(all_seed, 'queue'), queue)):
                needed_seed.append(os.path.getmtime(os.path.join(os.path.join(all_seed, 'queue'), queue)))
        needed_seed.sort()
        start_time = needed_seed[0]
    needed_seed = []
    if os.path.isdir(os.path.join(all_seed, 'crashes')):  
            for crash in os.listdir(os.path.join(all_seed, 'crashes')):
                if os.path.isfile(os.path.join(os.path.join(all_seed, 'crashes'), crash)):
                    global_num += 1
                    if (os.path.getmtime(os.path.join(os.path.join(all_seed, 'crashes'), crash)) - start_time) /60/60.0 < 5:
                        needed_seed.append((os.path.getmtime(os.path.join(os.path.join(all_seed, 'crashes'), crash)), os.path.join(os.path.join(all_seed, 'crashes'), crash)))
    needed_seed.sort(key=get_first)
    return map(get_second, needed_seed)


def update_id(bug_info, seed):
    global global_id
    global id_seed
    # print bug_info
    for temp_id in get_id.findall(bug_info):
        if temp_id in global_id:
            continue
        else:
            global_id.append(temp_id)
            id_seed[temp_id] = seed

def get_addition_seed(validate_file):
    global global_id
    num_discovered = 0
    num_add = 0
    with open(validate_file, 'r') as f:
        for i in f:
            if i.strip('\n') in global_id:
                global_id.remove(i.strip('\n'))
            else:
                num_discovered += 1
                print "id: %s can't been discovred"%i.strip('\n')
    for i in global_id:
        num_add += 1
        print "addition id is: %s, seed is: %s"%(i, id_seed[i])
    return num_discovered, num_add

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-out", metavar="out directory",
                        type=str,
                        help="lava-m out directory", required=True)
    parser.add_argument("-bin", metavar="test program",
                        type=str,
                        help="lava-m program for test", required=True)    
    parser.add_argument("-stdin", metavar="if input is stdin",
                        type=bool,
                        help="stdin input")     
    parser.add_argument("-validate", metavar="validate number",
                        type=str,
                        help="lava-m validate file")     
    parser.add_argument("-timeout", metavar="timeout for program run",
                        type=int,
                        help="timeout for program")     
    args = parser.parse_args()
    get_id = re.compile(r' .*bug (\d+), crashing now!')
    global_id = list()
    id_seed = dict()
    num = 0
    global_num = 0
    for crash in get_test_seed(args.out):
        if not args.stdin:
            test = subprocess.Popen(args.bin.replace('@@', crash), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # print(args.command.replace('@@', os.path.join(args.crash, seed)), os.path.join(args.crash, seed))
        else:
            test = subprocess.Popen(args.bin + ' < ' + crash, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if args.timeout:
            time.sleep(args.timeout)
            if test.poll() is None:
                test.kill()
                print "%s : timeout"%crash
                continue
        out, err = test.communicate()
        print "process: %d"%num
        num += 1
        update_id(out, crash)

    print id_seed
    print len(global_id), len(id_seed), str(num), str(global_num)
    if args.validate:
        print "can't discovered id: %s, addition id: %s"%(get_addition_seed(args.validate))

