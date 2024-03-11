import xml.etree.ElementTree as eT
import queue
import sys
import time
import helper
from confluent_kafka import Consumer, KafkaError, KafkaException


def parse_input(incoming):
    root = eT.fromstring(incoming)
    values = dict()
    for state in root[1][0]:
        for nested_elements in state:
            if 'MetricValue' in nested_elements.tag:
                values['DeterminationTime'] = nested_elements.attrib['DeterminationTime']
                values[state.attrib['DescriptorHandle']] = nested_elements.attrib['Samples'].split(' ')
    return root[1][0].attrib['MdibVersion'], values


# Message Processing Function
def process_messages(stack, realtimecurveDict):
    while True:
        if not stack.empty():
            message = stack.get()
            data = parse_input(message)
            data_dict = data[1]
            ecg_curve = list(data_dict.keys())
            for keys in ecg_curve[1:]:
                xs, ys = [0], []
                ys.extend(data_dict[keys])
                if keys not in realtimecurveDict:
                    xs.extend(range((xs[-1]) + 1, len(ys), 1))
                    realtimecurveDict[keys] = [[xs], [ys]]
                else:
                    for items in ys:
                        realtimecurveDict[keys][1][-1].append(items)
                    xs = []
                    xs.extend(range(realtimecurveDict[keys][0][-1][-1] + 1, len(realtimecurveDict[keys][1][-1]), 1))
                    for items in xs:
                        realtimecurveDict[keys][0][-1].append(items)
        else:
            break
        return data_dict['DeterminationTime']


def msg_process(stack, msg):
    stack.put(msg.value().decode('utf-8'))
    return False


def basic_consume_loop(consumer, stack, running):
    running = running

    while running:
        try:
            msg = consumer.poll(timeout=60.0)
            if msg is None or not msg:
                print("Wait for new messages")
                time.sleep(5)

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                print(msg.partition())
                print(msg.offset())
                running = msg_process(stack, msg)

        except:
            print("Close down consumer to commit final offsets in basic_consume_loop")


def shutdown():
    return False


def timespan_in_seconds(epoch_times):
    epoch_times_seconds = [int(time) / 1000 for time in epoch_times]
    first_epoch_time = epoch_times_seconds[0]
    if not epoch_times_seconds:
        return True
    for current_time in epoch_times_seconds:
        difference = current_time - first_epoch_time
        if difference >= 5:
            return False
    return True


def runlogic(topics):
    conf = helper.get_consumer_conf('capture')
    consumer = Consumer(conf)
    consumer.subscribe(topics)
    realtimecurveDict = {}
    det_time = []
    stack = queue.Queue()

    while True:
        basic_consume_loop(consumer, stack, True)
        det_time.append(process_messages(stack, realtimecurveDict))
        if not timespan_in_seconds(det_time):
            break

    print('End of data capture')
    consumer.close()
    return realtimecurveDict
