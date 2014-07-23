#!/usr/bin/python
#-*- coding: utf-8 -*-
import MySQLdb
import MySQLdb.cursors
import pymongo
from pymongo import MongoClient
import json
import datetime

connection = MySQLdb.connect(host = "***.**.*.*", user = "*****", passwd = "****", db = "ceilometer",
                              cursorclass = MySQLdb.cursors.DictCursor)

cursor = connection.cursor()
cursor.execute ("select distinct r.id, r.resource_metadata, r.project_id, r.user_id, s.source_id from resource as r inner join sourceassoc as s on s.resource_id = r.id where  r.id = 'instance'")

resource_data = cursor.fetchall()
cursor.close()

for resource in resource_data:
    resource['_id'] = resource.pop('id')
    resource['source'] = resource.pop('source_id')
    resource['metadata'] = resource.pop('resource_metadata')
    resource['metadata'] = json.loads(resource['metadata'])

cursor = connection.cursor()
cursor.execute ("select distinct counter_name, counter_unit, counter_type, resource.id from meter, resource where resource.id = meter.resource_id")
meter_resource_data = cursor.fetchall()
cursor.close()

try:
   for meter_resource in meter_resource_data:
     for resource in resource_data:
      if resource['_id'] == meter_resource['id'] :
            del meter_resource['id']
            meter_list = []
            meter_list.append(meter_resource)
            resource['meter'] = meter_list
            break
   ok = True             
except:
    print 'Error iterating over resource samples'

cursor = connection.cursor()
cursor.execute ("select m.*, s.source_id from meter as m inner join sourceassoc as s on s.meter_id = m.id and m.counter_name = 'instance';")

meters = cursor.fetchall()
connection.close()

try:
    for meter in meters:
     meter['resource_metadata'] = json.loads(meter['resource_metadata'])
     meter['source'] = meter.pop('source_id')
     meter['timestamp'] = datetime.datetime.fromtimestamp(meter['timestamp'])
     meter.pop('id')
    ok2 = True
except:
     print 'Error iterating over meter samples'

if ok and ok2:
    client = MongoClient()

    db = client.ceilometer
    collection_resource = db.resource
    for row in resource_data:
        collection_resource.insert(row)

    collection_meter = db.meter
    for row in meters:
        collection_meter.insert(row)
