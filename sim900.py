import fcntl
from misc_instrument.moxa import moxa_serial
import time
import json
from collections import OrderedDict

import RuO2spline as ruspline
import Diodespline as diodespline
import Hexspline as hexspline

#The file lock needs an absolute path so that no matter where we run
#the script from we use the same lock
FILE_LOCK = '/home/polarbear/pb2housekeepings/sim900/accesslock'

end_cmd = '\r\n'

SPLINES = {'Diode': diodespline, 'RuO2':ruspline, 'Hex':hexspline}

class Sim900():

    def __init__(self, IP, Port, name=None, Channels=None):
        self.ip = IP
        self.port = Port
        self.channels = self._proc_channels(Channels)
        self.name = name

    def _proc_channels(self, channels):
        return_channels = []
        for ch in channels:
            chantype = ch.pop('ChannelType')
            #chname = str(ch.pop('ChannelName'))
            if chantype == 'SIM921':
                return_channels.append(Sim921(**ch))
            elif chantype == 'SIM922Diode':
                return_channels.append(Sim922Diode(**ch))
            else:
                raise ValueError('Unsupported channel type - {0}'.format(chantype))
        return return_channels

    def connection(self):
        ln = LNX(ip=self.ip, port=self.port)
        for c in self.channels:
            c.rs232 = ln
        return ln

    def _channels_to_idx(self, channels):
        if channels is None:
            sample_channels = range(len(self.channels))
        elif type(channels) == str:
            sample_channels = [self.channelnames.index(channels)]
        elif type(channels) == list:
            channel_names = self.channelnames
            sample_channels = []
            for c in channels:
                sample_channels.append(channel_names.index(c))            
        return sample_channels

    def get_raw_temp(self, channels = None):
        sample_channels = self._channels_to_idx(channels)

        data = OrderedDict()
        with self.connection() as conn:
            for c in sample_channels:
                val = self.channels[c].get_raw_temp()
                data[self.channels[c].name] = val
        return data

    def get_temp(self, channels=None, return_raw=False):

        raw_temps = self.get_raw_temp(channels)
        sample_chans = self._channels_to_idx(channels)
        temps = OrderedDict()
        for chan in sample_chans:
            chname = self.channels[chan].name
            temps[chname] = self.channels[chan].convert_temp_val(raw_temps[chname])
        if return_raw:
            return {'raw_temp':raw_temps, 'converted_temp':temps}
        else:
            return temps

    def __getattr__(self, name):

        if name == 'channelnames':
            return [d.name for d in self.channels]
        elif name == 'channeltypes':
            return [type(d) for d in self.channels]
        else:
            raise AttributeError('{0} does not exist.'.format(name))

    def __dir__(self):

        real_keys = self.__dict__.keys()
        real_keys.append('channelnames')
        real_keys.append('channeltypes')
        return real_keys

    def __repr__(self):
        return '{0} (SIM900@{1}:{2})'.format(self.name, self.ip, self.port)

class LNX(moxa_serial.Serial_TCPServer):

        def __init__(self,ip,port,acquire_lock=True, debug=False):

            self.debug = debug 
            self.acquire_lock= acquire_lock
            self._acquire_lock()
            try:
                super(LNX,self).__init__((ip,port))
            except:
               self._release_lock() 
               raise
            self.flushInput()
            self.timeout = 1

        def _acquire_lock(self):
            if self.acquire_lock:
                self._lockf = open(FILE_LOCK, 'w')    
                #This blocks unitl lock is acquired:
                if self.debug:
                    print('Acquiring lock on {0}'.format(FILE_LOCK))
                fcntl.flock(self._lockf,fcntl.LOCK_EX)
                if self.debug:
                    print('Acquired lock on {0}'.format(FILE_LOCK))
            else:
                if self.debug:
                    print('NOT acquiring lock.')

        def _release_lock(self):
            if self.acquire_lock:
                if self.debug:
                    print('Releasing lock on {0}'.format(FILE_LOCK))
                fcntl.flock(self._lockf,fcntl.LOCK_UN)
                self._lockf.close()
            else:
                if self.debug:
                    print('NOT releasing lock.')

        def __enter__(self):
            return self

        def __exit__(self, exception_type, exception_value, traceback):
            self.close()

        def w(self,x):
            msg = x.upper()+end_cmd
            if self.debug:
                print(repr('Write "{0}"'.format(msg)))
            self.write(msg)

        def send_to_port(self, port, message, flush_port = True):
            port = int(port)
            if flush_port:
                self.w(b'FLSH {0}'.format(port))
                time.sleep(.15)
            self.w(b'SNDT {0},"{1}"'.format(port, message))

        def read_from_port(self, port, nbytes=110):
            port = int(port)
            bytes = int(nbytes)
            self.w(b'GETN? {0},{1}'.format(port, nbytes))
            time.sleep(.15)#Do we really need this? 
            return self.clean_output(self.readline())

        def send_read_port(self, port, message, nbytes=110, flush_port=False, sleep_time=.1):
            self.flushInput()
            self.send_to_port(message=message, port=port, flush_port=flush_port)
            time.sleep(sleep_time)
            self.flushInput()
            return self.read_from_port(port=port, nbytes=nbytes)

        def r(self):
            str = ""
            while True:
                c = self.readexactly(1)
                if c == '\n': return str
                if c == '': return False
                str += c
                str = str.replace('\r','')
            return str

        def clean_output(self, msg):
            if msg[0] == '#':
                bval_len = int(msg[1])
                rmessage = msg[bval_len+2:] 
            else:
                rmessage = msg
            return rmessage.strip()

        def wr(self,x):
                self.flushInput()
                self.w(x)
                return self.r()

        def close(self):
            try: 
                self.sock.close()
            except:
                pass
            try:
                self._release_lock()
            except:
                pass

class Sim921(object):
    def __init__(self, channel=None, name=None, rs232=None, spline=None, **kwargs):
        #channel=ch['ChannelNum'], name=chname, spline=spline
        self.name=name
        self.channel = channel
        self.spline = spline
        if channel is None:
            try:
                self.channel = int(kwargs.pop('ChannelNum'))
            except KeyError:
                pass
        if self.spline is None:
            try:
                self.spline = SPLINES[str(kwargs.pop('CalibrationSpline'))]
            except KeyError:
                pass
        if self.name is None:
            try:
                self.name = str(kwargs.pop('ChannelName'))
            except KeyError:
                pass
        if self.name is None:
            self.name = 'SIM921 on channel {0}'.format(self.channel)
        self.rs232 = rs232

        #Store other properties
        self.properties = kwargs

        self.excitations = {
            -1: 'OFF',
            0: '3 uV',
            1: '10 uV',
            2: '30 uV',
            3: '100 uV',
            4: '300 uV',
            5: '1 mV',
            6: '3 mV',
            7: '10 mV',
            8: '30 mV'
        }
        self.ranges = {
            0: '20 mOhm',
            1: '200 mOhm',
            2: '2 Ohm',
            3: '20 Ohm',
            4: '200 Ohm',
            5: '2 kOhm',
            6: '20 kOhm',
            7: '200 kOhm',
            8: '2 MOhm',
            9: '20 MOhm'
        }

    def get_range(self, translate=False):
        rng = int(self.rs232.send_read_port(self.channel, 'RANG?'))
        if translate:
            return self.ranges[rng]
        else:
            return rng

    def get_excitation(self, translate=False):
        exi = int(self.rs232.send_read_port(self.channel, 'EXCI?'))
        
        if translate:
            return self.excitations[exi]
        else:
            return exi

    def get_frequency(self, translate=False):
        freq = float(self.rs232.send_read_port(self.channel, 'FREQ?'))
        return freq

    def get_resistance(self):
        return float(self.rs232.send_read_port(self.channel, 'RVAL? 1'))

    def get_raw_temp(self):
        '''Convenience method defined for all objects to get a raw value
        of whatever the object does to read temperature'''
        return self.get_resistance()

    def convert_temp_val(self, raw_val):
        if self.spline is not None:
            return self.spline.splinepoint(raw_val)
        else:
            raise AttributeError('Attempt to convert raw temperature without defining a spline!')

    def get_temp(self):
        return convert_temp_val(self.get_raw_temp())

    def set_range(self, rng):
        rng = int(rng)
        if rng<0 or rng>9:
            raise ValueError('Range must be an integer between 0-9.')    
        self.rs232.send_to_port(self.channel, 'RANG {0}'.format(rng))
        time.sleep(1)

    def set_excitation(self, exci):
        exci = int(exci)
        if exci<-1 or exci>9:
            raise ValueError('Excitation must be an integer between -1-9.')    
        self.rs232.send_to_port(self.channel, 'EXCI {0}'.format(exci))
        time.sleep(1)

    def set_frequency(self, freq):
        freq = float(freq)
        if freq < 1.95 or freq > 61.1:
            raise ValueError('freq must be in the range 1.95 <= f <= 61.1.')
        self.rs232.send_to_port(self.channel, 'FREQ {0}'.format(freq))
        time.sleep(.1)

    def __repr__(self):
        return '{0} (SIM921@Channel {1})'.format(self.name, self.channel)

class Sim922Diode(object):
    def __init__(self, devicechannel=None, diodechannel=None, name=None, rs232=None, spline=None, **kwargs):
        self.devicechannel = devicechannel
        self.diodechannel = diodechannel
        self.rs232 = rs232
        self.spline = spline
        self.name = name
        if devicechannel is None:
            try:
                self.devicechannel = int(kwargs.pop('ChannelNum'))
            except KeyError:
                pass
        if diodechannel is None:
            try:
                self.diodechannel = int(kwargs.pop('SubChannelNum'))
            except KeyError:
                pass
        if self.spline is None:
            try:
                self.spline = SPLINES[str(kwargs.pop('CalibrationSpline'))]
            except KeyError:
                pass
        if self.name is None:
            try:
                self.name = str(kwargs.pop('ChannelName'))
            except KeyError:
                pass
        if self.name is None:
            self.name = 'SIM922 on channel {0}, diode Channel {1}'.format(self.devicechannel, diodechannel)

    def get_voltage(self):
        val=self.rs232.send_read_port(self.devicechannel, 'VOLT? {0},1'.format(self.diodechannel), sleep_time=.3)
        return float(val)

    def get_raw_temp(self):
        '''Convenience method defined for all objects to get a raw value
        of whatever the object does to read temperature'''
        return self.get_voltage()

    def convert_temp_val(self, raw_val):
        if self.spline is not None:
            return self.spline.splinepoint(raw_val)
        else:
            raise AttributeError('Attempt to convert raw temperature without defining a spline!')

    def get_temp(self):
        return convert_temp_val(self.get_raw_temp())

    def __repr__(self):
        return '{0} (SIM921 Diode @ Channel {1}/{2})'.format(self.name, self.devicechannel, self.diodechannel)

def load_json(fName):
    if type(fName) == file:
        readout = json.load(fName)
    elif type(fName) == str:
        with open(fName) as f:
            readout = json.load(f)
    devices = []
    for device in readout:
        dtype = device.pop('DeviceType')
        dname = device.pop('DeviceName')
        if dtype == 'SIM900':
            devices.append(Sim900(name=str(dname), **device))
    return devices
