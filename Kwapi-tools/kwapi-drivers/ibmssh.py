# Copyright 2014 Zuercher Hochschule fuer Angewandte Wissenschaften
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from random import randrange
import time
import subprocess
from fabric.api import *
from driver import Driver


class Ibmssh(Driver):

    def __init__(self, probe_ids, **kwargs):
        Driver.__init__(self, probe_ids, kwargs)
        self.hosts = (kwargs.get('host'))
        self.temp = (kwargs.get('time'))
    def run(self):
        fab_exe = Support()
        tempo = self.temp
        host = self.hosts
        while not self.stop_request_pending():
            measurements = {}
            watts = self.get_watts(fab_exe,tempo,host)
            for probe_id in self.probe_ids:
                measurements['w'] = watts
                self.send_measurements(probe_id, measurements)


    def get_watts(self,fab_exec, temp,host):
        initial = time.time()
        before = fab_exec.run(host)

        time.sleep(temp)
        
        after = fab_exec.run(host)
        fin = time.time()
        tempo = fin - initial
        watts = ((int(after) - int(before)) / 1000000) / int(tempo)
        return watts

class Support:
    def __init__ (self):
        pass

    def run(self, host):
        env.host_string = "%s" % (host)
        meter = run('cat /sys/devices/platform/aem.0/energy2_input')
        return meter
