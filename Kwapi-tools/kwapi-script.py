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

from ceilometer.energy import kwapi
import keystoneclient.v2_0.client as keystoneclient
from os import environ as env
from ceilometerclient import client
import time
from os import environ as env


keystone = {} 
keystone['username']=env['OS_USERNAME']
keystone['password']=env['OS_PASSWORD']
keystone['auth_url']=env['OS_AUTH_URL']
keystone['tenant_name']=env['OS_TENANT_NAME']

keystone2 = {}
keystone2['os_username']=env['OS_USERNAME']
keystone2['os_password']=env['OS_PASSWORD']
keystone2['os_auth_url']=env['OS_AUTH_URL']
keystone2['os_tenant_name']=env['OS_TENANT_NAME']


def kwapiAuth(ksclient):
    client = kwapi.KwapiClient(endpoint, token=ksclient.auth_token)
    return client


def kwapiMeter(kwapiClient):
    list = {}
    list = kwapiClient.iter_probes()
    for i in list:
        kwh = i['kwh']
        w = i['w']
        timestamp = i['timestamp']
        id = i['id']
        print (i)
        ceilometerSample(ceilo_client, kwh, w, timestamp, id)
    time.sleep(10)


def ceilometerSample(cei_client, kwh, w, timestamp, id):
    field = {'counter_name': 'energy',
             'counter_unit': 'kWh',
             'counter_type': 'cumulative',
             'counter_volume': '1',
             'project_id': 'a5f443ab3b574ff78f72c583f5dccb1e',
             'resource_id': id,
             'resource_metadata': {'kwh': kwh, 'w': w}}
    cei_client.samples.create(**field)

try:
    keys_client = keystoneclient.Client(**keystone)
    endpoint = 'http://127.0.0.1:5002/v1'
    ceilo_client = client.get_client(2, **keystone2)

except:
    print 'Username or password incorrect'

else:
    kwa_client = kwapiAuth(keys_client)

    while True:
        kwapiMeter(kwa_client)
