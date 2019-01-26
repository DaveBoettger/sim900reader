import sim900 as sim

def takeonedata(config_file, device):
    devices = sim.load_json(config_file)
    device = devices[[d.name for d in devices].index(device)]
    data = device.get_temp(return_raw=True)
    output_data = {}
    output_data['SENSOR_UNIT'] = data['raw_temp'].values()
    output_data['TEMP'] = data['converted_temp'].values()
    output_data['LABELS'] = data['raw_temp'].keys()
    return output_data
if __name__ == '__main__':
    print takeonedata('sim900_map.json', device='SIM900')
