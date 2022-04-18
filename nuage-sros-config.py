#!/usr/bin/env python3

import sys
from modules.functions import *

if __name__ == '__main__':
    if len(sys.argv) == 3:
        if sys.argv[1] == 'generate':
            config_generate(sys.argv[2])
        elif sys.argv[1] == 'upload':
            config_upload(sys.argv[2])
        elif sys.argv[1] == 'reboot':
            node_reboot(sys.argv[2])
        else:
            help_print()
    else:
        help_print()
