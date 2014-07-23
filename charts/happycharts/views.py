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
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.core.exceptions import PermissionDenied
from ceilometerclient import client
from django.utils import simplejson
from django.http import HttpResponse
from django.core.cache import cache
import keystoneclient.v2_0.client as ksclient
from novaclient.v1_1.client import Client
import collections


def home(request):
    return render_to_response("home.html",
                              {}, context_instance=RequestContext(request))


def getenergyconsuption(request):
    start = str(request.GET.get('start', '')) + 'T00:00:00'
    end = str(request.GET.get('end', '')) + 'T23:59:00'
    server = str(request.GET.get('server', ''))
    q = [{'field': 'timestamp', 'op': 'gt', 'value': str(start)},
         {'field': 'timestamp', 'op': 'lt', 'value': str(end)},
         {'field': 'resource', 'op': 'eq', 'value': str(server)}]

    meter_list = []
    energy_list = []
    time_list = []
    timestamp_list = []
    meter_sum = 0
    meter_dict = {'energy_list': energy_list, 'timestamp': timestamp_list}
    try:
        meters = ceilometer_get_sample(q)
        for meter in meters:
            meter_metadata = meter.resource_metadata
            meter_list.append(meter_metadata['w'])
            timestamp = meter.timestamp
            timestamp = timestamp[:-7]
            time_list.append(timestamp)
        if not meter_list:
            status = 0
        else:
            status = 1
        length = len(meter_list)
        div = length / 500
        start = 0
        end = start + div
        for num in range(0, (length/div)):
            energy_list.append(0)
            timestamp_list.append(0)
            energy_list[num] = sum(map(lambda m: float(m),
                                     meter_list[start:end]))
            energy_list[num] = energy_list[num]/div
            timestamp_list[num] = time_list[start+div]
            start = start + div
            end = end + div
        meter_sum = sum(map(lambda m: float(m),meter_list))
        energy_list = energy_list.reverse()
        timestamp_list = timestamp_list.reverse()
        dict_sum_length = {'sum': meter_sum, 'length': length}
    except:
        status = 0
    return HttpResponse(simplejson.dumps({'status': status,
                                          'response': meter_dict,
                                          'sum_length':dict_sum_length
                                         }))


def getmeters(request):
    cache_key = 'meters'
    cache_time = 1800
    result = cache.get(cache_key)
    if not result:
        ceilo = get_credentials()
        meters = ceilo.meters.list()
        energy = []
        for i in meters:
            if i.name == 'energy':
                energy.append(i.resource_id)
        cache.set(cache_key, energy, cache_time)
        return HttpResponse(simplejson.dumps({'energy': energy}))
    return HttpResponse(simplejson.dumps({'energy': result}))


def ceilometer_get_sample(query):
    ceilo = get_credentials()

    return ceilo.samples.list(meter_name='energy', q=query)


def ceilometer_get_instances(request):
    ceilo = get_credentials()
    nova = get_admin_credentials()
    start = str(request.GET.get('start', '')) + 'T00:00:00'
    end = str(request.GET.get('end', '')) + 'T23:59:00'
    server = str(request.GET.get('server',''))
    query = [{'field': 'timestamp', 'op': 'gt', 'value': str(start)},
             {'field': 'timestamp', 'op': 'lt', 'value': str(end)}]
    try:
        hypervisor = nova.hypervisors.servers(hypervisor = server)
    except:
        hypervisor = []
    try:
        samples = ceilo.samples.list(meter_name='instance', q=query)
        instance_id = []
        instance_metadata = []
        server_name = []
        [server_name.append(n['name'])
         for z in hypervisor for n in z.servers]
        for sample in samples:
            if not instance_id or sample.resource_id not in instance_id:
                instance_id.append(sample.resource_id)
                metadata = sample.resource_metadata
                if  metadata['name'] in server_name :
                    flavor = metadata['flavor.name']
                    image = metadata['image.name']
                    display = metadata['display_name']
                    query2 = [{'field': 'resource',
                               'op': 'eq',
                               'value': sample.resource_id}]
                    user = sample.user_id
                    project = sample.project_id
                    instancedata = {3: flavor,
                                    1: user,
                                    2: project,
                                    4: image,
                                    5: display}
                    instance_metadata.append(collections.OrderedDict
                                            (sorted
                                            (instancedata.items())))
        status = 1
    except:
        status = 0
    return HttpResponse(simplejson.dumps({'status': status,
                                          'response': instance_metadata,
                                          'resource': instance_id}))


def get_credentials():
    keystone = {}
    keystone['os_username']=env['OS_USERNAME']
    keystone['os_password']=env['OS_PASSWORD']
    keystone['os_auth_url']=env['OS_AUTH_URL']
    keystone['os_tenant_name']=env['OS_TENANT_NAME']

    return client.get_client(2, **keystone)


def get_admin_credentials():
    keystone = {}
    keystone['os_username']=env['OS_USERNAME']
    keystone['os_password']=env['OS_PASSWORD']
    keystone['os_auth_url']=env['OS_AUTH_URL']
    keystone['os_tenant_name']=env['OS_TENANT_NAME']

    return Client(**keystone)
