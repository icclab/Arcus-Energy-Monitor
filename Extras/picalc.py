#!/usr/bin/python
#-*- coding: utf-8 -*-
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

from multiprocessing import Process
import subprocess
import time

def arccot(x, unity):
    sum = xpower = unity // x
    n = 3
    sign = -1
    while 1:
        xpower = xpower // (x*x)
        term = xpower // n
        if not term:
            break
        sum += sign * term
        sign = -sign
        n += 2
    return sum


def pi(digits):
    unity = 10**(digits + 10)
    pi = 4 * (4*arccot(5, unity) - arccot(239, unity))
    return pi // 10**10


def readFile():
    f = open('/sys/devices/platform/aem.0/energy2_input','r')
    joules = f.read()
    f.close()
    return joules


threads = []
core = 1
for i in range(0,20):
    print "Cores: ", core

    ini = time.time()
    before = readFile()
    for i in range(0,core): 
        thread = Process(target=pi, args = (100000,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    after = readFile()
    result = (int(after) - int(before)) / 1000000
    print str(result) + 'J'

    end = time.time()
    total_time = end-ini
    print 'Total Time:', total_time

    g = open('./energy.txt','a')
    g.write('Cores: ' + str(core) +'\nEnergy: ' + str(result) + '\nTime: ' + str(total_time)+ '\n\n')
    g.close()
    core = core + 1
