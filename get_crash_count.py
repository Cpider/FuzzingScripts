import re
import os
import argparse
import subprocess
import time

def get_count(directory):
    seed_time = list()
    for seed in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, seed)):
            seed_time.append(os.path.getmtime(os.path.join(directory, seed)))
    seed_time.sort()
    num = 0
    # seed_time = seed_time[1:]
    start_time = os.path.getmtime(args.first_seed)
    for i in seed_time:
        if (i - start_time)/(60*60.0) > args.timeout:
            break
        else:
            num += 1
    return num

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-out", metavar="out directory",
                        type=str,
                        help="lava-m out directory", required=True)  
    parser.add_argument("-timeout", metavar="timeout for program run",
                        type=int,
                        help="timeout for program")     
    parser.add_argument("-first_seed", metavar="sanitizer bug output",
                        type=str,
                        help="address sanitizer bug output file", required=True)    
    args = parser.parse_args()

    print "%s has %d seed in %s time !" % (args.out, get_count(args.out), args.timeout)