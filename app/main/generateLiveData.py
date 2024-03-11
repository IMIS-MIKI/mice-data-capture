import time
import json
import xml.etree.ElementTree as eT
import helper

from datetime import datetime
from confluent_kafka import Consumer


def parse_input(incoming):
    root = eT.fromstring(incoming)
    values = dict()
    for state in root[1][0]:
        for nested_elements in state:
            if 'MetricValue' in nested_elements.tag:
                values['DeterminationTime'] = nested_elements.attrib['DeterminationTime']
                values[state.attrib['DescriptorHandle']] = nested_elements.attrib['Samples'].split(' ')
    return root[1][0].attrib['MdibVersion'], values


def runlive(topics):
    conf = helper.get_consumer_conf(group_type='live')
    consumer = Consumer(conf)
    consumer.subscribe(topics)

    while True:
        msg = consumer.poll(timeout=60.0)
        if msg is None:
            continue
        else:
            data = parse_input(msg.value().decode('utf-8'))
            data_dict = data[1]
            if 'ECGV.Realtimecurve.6C.64E8' in data_dict:
                for value in data_dict['ECGV.Realtimecurve.6C.64E8']:
                    json_data = json.dumps(
                        {'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': value})
                    yield f"data:{json_data}\n\n"
                    time.sleep(0.01)
            else:
                continue
    consumer.close()
