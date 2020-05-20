#! /usr/bin/env python3

# You will need 'python-psutil' for python3 installed, and you need to install and configure lm_sensors as well
# Everything else you need should be included by default with any distribution you might use

import psutil, subprocess, datetime, time, sys, re

class SysInfo():

    def __init__(self):
        # Initiate all sysinfo values, add the time we save them, actual value, and cache time in seconds
        current_time = datetime.datetime.now()
        self.cpu_per = (current_time, psutil.cpu_percent(), 3)
        self.cpu_tmp = (current_time, round(psutil.sensors_temperatures()['k10temp'][0][1], 1), 3)
        self.gpu_tmp = (current_time, round(psutil.sensors_temperatures()['amdgpu'][0][1], 1), 3)
        self.mem = (current_time, psutil.virtual_memory()[2], 3)
        self.swp = (current_time, psutil.swap_memory()[3], 3)
        self.ssd = (current_time, psutil.disk_usage('/')[3], 3)
        self.wifi = (current_time, psutil.net_if_stats()['wlp3s0'][0], 10)
        self.vpn = (current_time, bool(subprocess.run(('pgrep', '--exact', 'openvpn'), stdout=subprocess.PIPE).stdout), 10)
        self.upd = (current_time, re.sub('[\'bn\\\]', '', str(subprocess.run('checkupdates | wc -l', shell=True, stdout=subprocess.PIPE).stdout)), 60*30)
        self.aur = (current_time, re.sub('[\'bn\\\]', '', str(subprocess.run('auracle sync -q | wc -l', shell=True, stdout=subprocess.PIPE).stdout)), 60*30)

    def update_cache(self):
        current_time = datetime.datetime.now()
        if (current_time - self.cpu_per[0]).seconds > self.cpu_per[2]:
            self.cpu_per = (current_time, psutil.cpu_percent(), self.cpu_per[2])
        if (current_time - self.cpu_tmp[0]).seconds > self.cpu_tmp[2]:
            self.cpu_tmp = (current_time, round(psutil.sensors_temperatures()['k10temp'][0][1], 1), self.cpu_tmp[2])
        if (current_time - self.gpu_tmp[0]).seconds > self.gpu_tmp[2]:
            self.gpu_tmp = (current_time, round(psutil.sensors_temperatures()['amdgpu'][0][1], 1), self.gpu_tmp[2])
        if (current_time - self.mem[0]).seconds > self.mem[2]:
            self.mem = (current_time, psutil.virtual_memory()[2], self.mem[2])
        if (current_time - self.swp[0]).seconds > self.swp[2]:
            self.swp = (current_time, psutil.swap_memory()[3], self.swp[2])
        if (current_time - self.ssd[0]).seconds > self.ssd[2]:
            self.ssd = (current_time, psutil.disk_usage('/')[3], self.ssd[2])
        if (current_time - self.wifi[0]).seconds > self.wifi[2]:
            self.wifi = (current_time, psutil.net_if_stats()['wlp3s0'][0], self.wifi[2])
        if (current_time - self.vpn[0]).seconds > self.vpn[2]:
            self.vpn = (current_time, bool(subprocess.run(('pgrep', '--exact', 'openvpn'), stdout=subprocess.PIPE).stdout), self.vpn[2])
        if (current_time - self.upd[0]).seconds > self.upd[2]:
            self.upd = (current_time, re.sub('[\'bn\\\]', '', str(subprocess.run('checkupdates | wc -l', shell=True, stdout=subprocess.PIPE).stdout)), self.upd[2])
        if (current_time - self.aur[0]).seconds > self.aur[2]:
            self.aur = (current_time, re.sub('[\'bn\\\]', '', str(subprocess.run('auracle sync -q | wc -l', shell=True, stdout=subprocess.PIPE).stdout)), self.aur[2])

    def print_out(self):
        print_time = datetime.datetime.now()
        self.outputs = 'UPD: ' + self.upd[1] + ' AUR: ' + self.aur[1] + ' | WIFI: '
        if self.wifi[1]:
            self.outputs += 'UP'
        else:
            self.outputs += 'DOWN'
        self.outputs += ' VPN: '
        if self.vpn[1]:
            self.outputs += 'UP'
        else:
            self.outputs += 'DOWN'
        self.outputs += ' | SSD: ' + str(self.ssd[1]) + '% | MEM: ' + str(self.mem[1]) + '% SWAP: ' + str(self.swp[1]) + '% | CPU: ' + str(self.cpu_per[1]) + '% '
        self.outputs += str(self.cpu_tmp[1]) + '°C | GPU: ' + str(self.gpu_tmp[1]) + '°C | '
        self.outputs += print_time.date().isoformat() + ' ' + print_time.time().isoformat('seconds')
        sys.stdout.write('%s\n' % self.outputs)
        sys.stdout.flush()


# main
sio = SysInfo()

while True:
    sio.print_out()
    sio.update_cache()
    time.sleep(1)
