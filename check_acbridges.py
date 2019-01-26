from sim900 import LNX, Sim921
import sim900
import time
import sys

#Config file specifying the AC bridges:
CONFIG_FILE = '/home/polarbear/pb2housekeepings/sim900/sim900_map.json'

#Default values for devices that don't specify
TARGET_RANGE = 7
TARGET_EXCITATION = 6

RESET_RANGE = 5
RESET_EXCITATION = 7

MAX_RETRIES = 5

def fix_val(setf, getf, val):
    for _ in range(MAX_RETRIES):
        setf(val)
        if getf() == val:
            return True
        else:
            continue
    return False

SCRNAME = sys.argv[0]
HELP_STR = '''
Usage: 
    {0} - display ranges and excitations.
    {0} fix - display ranges and excitations, and attempt to correct bad values.
    {0} fixexcite - same as fix but only for excitation
    {0} fixrange - same as fix but only for range
    {0} reset - reset ranges and excitations to a bad value, then correct them.
    {0} resetexcitation - same as reset but only for excitation.
    {0} resetrange - same as reset but only for range.
'''
HELP_STR = HELP_STR.format(SCRNAME)

def check_acbridges(resetrange=False, resetexcite=False, fixexcite=False, fixrange=False) :

    devices = sim900.load_json(CONFIG_FILE)
    bridges = []
    for device in devices:
        for chan in device.channels:
            if 'Sim921' in type(chan).__name__:
                bridges.append((device,chan))
    for bpair in bridges:
        dev = bpair[0]    
        b = bpair[1] 

        try:
            b.properties['Excitation']
        except AttributeError:
            b.properties['Excitation'] = TARGET_EXCITATION
        try:
            b.properties['Range']
        except AttributeError:
            b.properties['Range'] = TARGET_RANGE
        try:
            b.properties['ResetExcitation']
        except AttributeError:
            b.properties['ResetExcitation'] = RESET_EXCITATION
        try:
            b.properties['ResetRange']
        except AttributeError:
            b.properties['ResetRange'] = RESET_RANGE

        with dev.connection() as conn:
            print('----{0}----'.format(b.name))
            if resetexcite:
                print('Setting excitation to wrong value.')
                if fix_val(setf=b.set_excitation, getf=b.get_excitation, val=b.properties['ResetExcitation']):
                    time.sleep(1)
                    print('Done.')
                else:
                    print('Failed!')
            if resetrange:
                print('Setting range to wrong value.')
                if fix_val(setf=b.set_range, getf=b.get_range, val=b.properties['ResetRange']):
                    time.sleep(1)
                    print('Done.')
                else:
                    print('Failed!')
            rng = b.get_range()
            excite = b.get_excitation()
            print('Current excitation is: {0}'.format(b.excitations[excite]))
            if excite==b.properties['Excitation']:
                print('(expected value)')
            else:
                print('(UNEXPECTED value)')
                if fixexcite:
                    print('Attempting to correct...')
                    if fix_val(setf=b.set_excitation, getf=b.get_excitation, val=b.properties['Excitation']):
                        print('Fixed.')
                    else:
                        print('Unable to fix.')
                else:
                    print('NOT attempting to fix. Use "{0} help" for more information.'.format(SCRNAME))
            print('Current range is: {0}'.format(b.ranges[rng]))
            if rng==b.properties['Range']:
                print('(expected value)')
            else:
                print('(UNEXPECTED value)')
                if fixrange:
                    print('Attempting to correct...')
                    if fix_val(setf=b.set_range, getf=b.get_range, val=b.properties['Range']):
                        print('Fixed.')
                    else:
                        print('Unable to fix.')
                else:
                    print('NOT attempting to fix. Use "{0} help" for more information.'.format(SCRNAME))
            print('----------')

    return 0;

if __name__ == '__main__':
        resetrange = False
        resetexcite = False
        fixexcite = False
        fixrange = False
        try:
            if sys.argv[1] == 'fix':
                fixrange=True
                fixexcite=True
            elif sys.argv[1] == 'fixrange':
                fixrange=True
            elif sys.argv[1] == 'fixexcite':
                fixexcite=True
            elif sys.argv[1] == 'reset':
                fixrange=True
                fixexcite=True
                resetrange=True
                resetexcite=True
            elif sys.argv[1] == 'resetrange':
                resetrange=True
                fixrange=True
            elif sys.argv[1] == 'resetexcite':
                resetrange=True
                fixrange=True
            elif sys.argv[1] == 'help':
                print(HELP_STR)
                quit()
            else:
                fixrange=False
                fixexcite=False
        except IndexError:
            pass

        check_acbridges(resetrange, resetexcite, fixexcite, fixrange);



