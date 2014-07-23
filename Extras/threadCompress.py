#!/usr/bin/python
# -*- coding: utf-8 -*-
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
import threading
import subprocess
import time


class myThread (threading.Thread):
    def __init__(self, threadID, compression):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.compression = compression

    def run(self):
        run(self.threadID, self.compression)


def run(threadID, compression):
        thread = str(threadID)
        compress = str(compression)
        path = './compressEnergy.sh -i ' + thread + ' -c ' + compress
        subprocess.call(path, shell=True)

ini = time.time()
f = open('/sys/devices/platform/aem.0/energy2_input', 'r')
before = f.read()
f.close()

threadLock = threading.Lock()
threads = []


core = input("Number of threads: ")
compression = input("Number of compressions: ")


for i in range(0, core):
    thread = myThread(i, compression)
    thread.start()
    threads.append(thread)

for t in threads:
    t.join()

f = open('/sys/devices/platform/aem.0/energy2_input', 'r')
after = f.read()
f.close()

result = (int(after) - int(before)) / 1000000
print str(result) + 'J'

fim = time.time()
tempo = fim-ini
print 'Tempo Total:', tempo

g = open('./energy.txt', 'a')
g.write('Cores: ' + str(core) + '\nEnergy: ' + str(result) +
        '\nTime: ' + str(tempo) + '\n\n')
g.close()
