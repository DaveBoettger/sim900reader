import sys
import time
import os
import takealldata_csv_lib as td
#reload(td)
import slowdaq.pb2 as daq

update_rate = 5 # seconds

DAEMON_PATH = os.path.dirname(os.path.abspath(__file__))
DAEMONIZE = True
#DAEMONIZE = False

DEVICES = [{'config_file':'/home/polarbear/pb2housekeepings/sim900/sim900_map.json', 'device':'SIM900'}]

def main():
    iin = 0 # internal incremental number since startup

    pub = daq.Publisher('SIM900','192.168.2.10',3141)

    while True:
        d = {'index': iin, 'time': time.time()}

        for dev in DEVICES:
            count=1
            try:
                values = td.takeonedata(**dev)
                d[dev['device']] = values
            except:
                print 'Error. Trying again...'.format(count)
                continue

        data = pub.pack(d)
        print data
        pub.queue(data)
        pub.serve()

        # message from aggregator or subscriber
        while len(pub.inbox) > 0:
            print pub.inbox.pop()
        
        iin += 1
        time.sleep(update_rate)

def daemonize():
    pid = os.fork()
    if pid == 0:
        os.setsid()
        main()
    else:
        print "Started fridge monitor daemon with PID %d"%pid

if __name__=='__main__':
    if DAEMONIZE:
        print 'Daemonize'
        daemonize()
    else:
        main()
