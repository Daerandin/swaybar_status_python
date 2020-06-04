#! /usr/bin/env python3

# You will need 'python-psutil' for python3 installed, and you need to install and configure lm_sensors as well
# Everything else you need should be included by default with any distribution you might use

import psutil, subprocess, datetime, time, sys, re

class SysInfo():

    def __init__(self):
        # Initiate all sysinfo values, add the time we save them, actual value, and cache time in seconds
        current_time = datetime.datetime.now()
        self.cpu_per = (current_time, self.get_cpu_per())
        self.cpu_tmp = (current_time, self.get_cpu_tmp())
        self.gpu_tmp = (current_time, self.get_gpu_tmp())
        self.mem = (current_time, self.get_mem_per())
        self.swp = (current_time, self.get_swp_per())
        self.ssd = (current_time, self.get_ssd_per())
        self.wifi = (current_time, self.get_wifi_status())
        self.vpn = (current_time, self.get_vpn_status())
        self.upd = (current_time, ('0', 5))
        self.aur = (current_time, ('0', 10))
        # The last two are initialized to 0 with different initial cache times so we prevent both to require network access at the same update

    # Methods for retrieving system info, returns tuple with two elements, (return_value, cache_time)
    def get_cpu_per(self):
        return (psutil.cpu_percent(), 3)
    def get_cpu_tmp(self):
        tmps = psutil.sensors_temperatures()['k10temp']
        for element in tmps:
            if element[0] == 'Tdie':
                return (element[1], 3)
        return ('N/A', 3)
    def get_gpu_tmp(self):
        tmps = psutil.sensors_temperatures()['amdgpu']
        for element in tmps:
            if element[0] == 'edge':
                return (element[1], 3)
        return ('N/A', 3)
    def get_mem_per(self):
        return (psutil.virtual_memory().percent, 3)
    def get_swp_per(self):
        return (psutil.swap_memory().percent, 3)
    def get_ssd_per(self):
        return (psutil.disk_usage('/').percent, 3)
    def get_wifi_status(self):
        return (psutil.net_if_stats()['wlp3s0'].isup, 10)
    def get_vpn_status(self):
        return (bool(subprocess.run(('pgrep', '--exact', 'openvpn'), stdout=subprocess.PIPE).stdout), 10)
    def get_arch_updates(self):
        return (re.sub('[\'bn\\\]', '', str(subprocess.run('checkupdates | wc -l', shell=True, stdout=subprocess.PIPE).stdout)), 60*30)
    def get_aur_updates(self):
        return (re.sub('[\'bn\\\]', '', str(subprocess.run('auracle sync -q | wc -l', shell=True, stdout=subprocess.PIPE).stdout)), 60*30)

    def update_cache(self):
        current_time = datetime.datetime.now()
        if (current_time - self.cpu_per[0]).seconds > self.cpu_per[1][1]:
            self.cpu_per = (current_time, self.get_cpu_per())
        if (current_time - self.cpu_tmp[0]).seconds > self.cpu_tmp[1][1]:
            self.cpu_tmp = (current_time, self.get_cpu_tmp())
        if (current_time - self.gpu_tmp[0]).seconds > self.gpu_tmp[1][1]:
            self.gpu_tmp = (current_time, self.get_gpu_tmp())
        if (current_time - self.mem[0]).seconds > self.mem[1][1]:
            self.mem = (current_time, self.get_mem_per())
        if (current_time - self.swp[0]).seconds > self.swp[1][1]:
            self.swp = (current_time, self.get_swp_per())
        if (current_time - self.ssd[0]).seconds > self.ssd[1][1]:
            self.ssd = (current_time, self.get_ssd_per())
        if (current_time - self.wifi[0]).seconds > self.wifi[1][1]:
            self.wifi = (current_time, self.get_wifi_status())
        if (current_time - self.vpn[0]).seconds > self.vpn[1][1]:
            self.vpn = (current_time, self.get_vpn_status())
        if (current_time - self.upd[0]).seconds > self.upd[1][1]:
            self.upd = (current_time, self.get_arch_updates())
        if (current_time - self.aur[0]).seconds > self.aur[1][1]:
            self.aur = (current_time, self.get_aur_updates())

    def print_out(self):
        print_time = datetime.datetime.now()
        self.outputs = 'UPD: ' + self.upd[1][0] + ' AUR: ' + self.aur[1][0] + ' | WIFI: '
        if self.wifi[1][0]:
            self.outputs += 'UP'
        else:
            self.outputs += 'DOWN'
        self.outputs += ' VPN: '
        if self.vpn[1][0]:
            self.outputs += 'UP'
        else:
            self.outputs += 'DOWN'
        self.outputs += ' | SSD: ' + str(self.ssd[1][0]) + '% | MEM: ' + str(self.mem[1][0]) + '% SWAP: ' + str(self.swp[1][0]) + '% | CPU: ' + str(self.cpu_per[1][0]) + '% '
        self.outputs += '{:.1f}'.format(self.cpu_tmp[1][0]) + '°C | GPU: ' + '{:.1f}'.format(self.gpu_tmp[1][0]) + '°C | '
        self.outputs += print_time.date().isoformat() + ' ' + print_time.time().isoformat('seconds')
        sys.stdout.write('%s\n' % self.outputs)
        sys.stdout.flush()


# main
sio = SysInfo()

while True:
    sio.print_out()
    sio.update_cache()
    time.sleep(1)
