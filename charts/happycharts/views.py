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
from datetime import *
import time
import pytz
import hashlib
import collections


class Activity():
    def __init__(self, resource_id, start_date, end_date):
        self.resource = resource_id
        self.start_date = start_date
        self.end_date = end_date

    def start(self):
        self.total_time = self.get_total_time()
        query = [{'field': 'metadata.status',
                           'op': 'eq',
                           'value': 'active'},
                 {'field': 'resource_id',
                           'op': 'eq',
                           'value': self.resource},
                 {'field': 'timestamp',
                           'op': 'gt',
                           'value': self.start_date},
                 {'field': 'timestamp',
                           'op': 'le',
                           'value': self.end_date}]
        self.samples = self.get_sample_list(query)     
        self.activity = self.set_activity()

    def set_activity(self):
        active_samples = len(self.samples)
        return (active_samples*100)/self.total_time

    def get_activity(self):
        return self.activity
        
    def get_activity_date(self):
        return self.activity_date    

    def get_total_time(self):
        fmt = '%Y-%m-%dT%H:%M:%S'
        st_dt = datetime.strptime(self.start_date, fmt)
        ed_dt = datetime.strptime(self.end_date, fmt)
        d1 = time.mktime(st_dt.timetuple())
        d2 = time.mktime(ed_dt.timetuple())
        return int(d2-d1)/600   

    def get_sample_list(self, query):
        ceilometer = get_credentials()
        sample_list = ceilometer.samples.list(meter_name='instance',
                                              q=query)
        return sample_list
      

def home(request):
    return render_to_response("home.html",
                              {}, context_instance=RequestContext(request))


def getenergycomsuption(request):
    start = str(request.GET.get('start', '')) + 'T00:00:00'
    end = str(request.GET.get('end', ''))
    server = str(request.GET.get('server', ''))
    end = set_end_date(end)
    q = [{'field': 'timestamp', 'op': 'gt', 'value': str(start)},
         {'field': 'timestamp', 'op': 'lt', 'value': str(end)},
         {'field': 'resource_id', 'op': 'eq', 'value': str(server)}]

    energy_meter = []
    energy_list = []
    time_list = []
    timestamp_list = []
    meter_sum = 0
    meter_dict = {'energy_list': energy_list, 'timestamp': timestamp_list}
    try:
        meter_list = ceilometer_get_sample(q)
        for meter in meter_list:
            meter_metadata = meter.resource_metadata
            energy_meter.append(meter_metadata['w'])
            timestamp = meter.timestamp
            timestamp = timestamp[:-7]
            time_list.append(timestamp)
        if not meter_list:
            status = 0
        else:
            status = 1
            meter_list_len = len(energy_meter)
            div = meter_list_len/500
            start = 0
            end = start + div
            for num in range(0, (meter_list_len/div)):
                energy_list.append(0)
                timestamp_list.append(0)
                energy_list[num] = sum(map(lambda m: float(m),
                                         energy_meter[start:end]))
                energy_list[num] = energy_list[num]/div
                timestamp_list[num] = time_list[start+div]
                start += div
                end += div
            meter_sum = sum(map(lambda m: float(m),energy_meter))
            energy_list = energy_list.reverse()
            timestamp_list = timestamp_list.reverse()
            dict_sum_length = {'sum': meter_sum, 'length': meter_list_len}
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
        ceilometer = get_credentials()
        meter_list = ceilometer.meters.list()
        energy = []
        for meter in meter_list:
            if meter.name == 'energy':
                energy.append(meter.resource_id)
        cache.set(cache_key, energy, cache_time)
        return HttpResponse(simplejson.dumps({'energy': energy}))
    return HttpResponse(simplejson.dumps({'energy': result}))


def ceilometer_get_sample(query):
    ceilometer = get_credentials()
    return ceilometer.samples.list(meter_name='energy', q=query)


def inst_server(instance, server):
    server = 'test-VirtualBox'
    sha_hash = hashlib.sha224(instance.project_id + server)  
    sha_hash = sha_hash.hexdigest()
    metadata = instance.resource_metadata
    if metadata['host'] == sha_hash:
       return True
    return False
    
    
def set_end_date(end):
    end_date = datetime.strptime(end, "%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")
    current_date = datetime.today()
    current_date = current_date.strftime("%Y-%m-%d")
    if end_date == current_date:
        end = str(datetime.today())
        end = end.replace(" ", "T")
        end = end[:-7]
    else:
        end = end + "T23:59:59"
    return end
    
    
def ceilometer_get_instances(request):
    ceilo = get_credentials()
    start = str(request.GET.get('start', '')) + 'T00:00:00'
    end = str(request.GET.get('end', ''))
    end = set_end_date(end)
    server = str(request.GET.get('server',''))
    host_inserver = False
    try:
        instance_metadata = []
        instance_activity_list = []
        activity = []
        resource_id = get_meter_instance_list(ceilo)
        instances_active = 0
        for ids in resource_id:
            query = [{'field': 'timestamp', 'op': 'gt', 'value': str(start)},
                     {'field': 'timestamp', 'op': 'lt', 'value': str(end)},
                     {'field': 'resource_id', 'op': 'eq', 'value': ids}]
            samples = ceilo.samples.list(meter_name='instance', q=query, limit=1)
            for sample in samples:
                host_inserver = inst_server(sample, server)
                if host_inserver:
                    instances_active += 1                
                    instance = Activity(ids, start, end)
                    instance.start()
                    activity = instance.get_activity()
                    instance_activity_dict = {'id': sample.resource_id,
                                              'activity': activity}
                    instance_activity_list.append(instance_activity_dict)
                    instancedata = get_instance_data(sample)
                    instance_metadata.append(collections.OrderedDict
                                            (sorted
                                            (instancedata.items())))
        status = 1
    except:
        status = 0
    return HttpResponse(simplejson.dumps({'status': status,
                                          'response': instance_metadata,
                                          'resource_activity': instance_activity_list,
                                          'insts_active': instances_active}))


def get_instance_data(sample):
    metadata = sample.resource_metadata
    flavor = metadata['flavor.name']
    image = metadata['image.name']
    display = metadata['display_name']
    user = sample.user_id
    project = sample.project_id
    instancedata = {3: flavor,
                    1: user,
                    2: project,
                    4: image,
                    5: display}
    return instancedata


def get_meter_instance_list(ceilometer):
    resource_meter = []
    meter_list = ceilometer.meters.list()
    for meter in meter_list:
        if meter.name == 'instance':
            resource_meter.append(meter.resource_id)
    resource_id = []
    for instance_id in resource_meter:
        if instance_id not in resource_id:
            resource_id.append(instance_id)
    return resource_id


def get_credentials():
    keystone = {}
    keystone['os_username'] = ''
    keystone['os_password'] = ''
    keystone['os_auth_url'] = ''
    keystone['os_tenant_name'] = ''

    return client.get_client(2, **keystone)
