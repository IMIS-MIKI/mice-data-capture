import xml.etree.ElementTree as eT
import threading
import queue
import json
import sys
from confluent_kafka import Consumer, KafkaError, KafkaException
import time
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from typing import Iterator
from flask import request
import time


def generate_data_plot(xs, ys) -> Iterator[str]:
    print('do something')


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
def process_messages(stack, xs, ys):
    print("process message")
    #    xs, ys = [0], []
    while True:
        if not stack.empty():
            message = stack.get()
            data = parse_input(message)
            data_dict = data[1]
            ecg_curve = 'ECGV.Realtimecurve.6C.64E8'
            # Converting string values to floats
            if ecg_curve in data_dict:
                print('.')
            else:
                print('key not found')
                continue
            # print(data_dict[ecg_curve])
            ys.extend(data_dict[ecg_curve])
            xs.extend(range((xs[-1]) + 1, len(ys), 1))
            print(len(ys))
            #            print(len(ys) - len(xs))
            #            print(ys)
            time.sleep(1)
        else:
            break
        return data_dict['DeterminationTime']


def msg_process(stack, recordstack, msg):
    stack.put(msg.value().decode('utf-8'))
    recordstack.put(msg.value().decode('utf-8'))
    return False


def basic_consume_loop(consumer, topics, stack, recordstack, running):
    running = running
    try:
        consumer.subscribe(topics)

        while running:
            msg = consumer.poll(timeout=60.0)
            if msg is None: continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                running = msg_process(stack, recordstack, msg)

    except:
        # Close down consumer to commit final offsets.
        consumer.close()


# def runner(start_time):  # capture start time
#     # Loop for 30 seconds
#     while time.time() - start_time < 20:
#         print (time.time() - start_time)
#         return True
#         # Here you can call your functions
#     shutdown()

def shutdown():
    print('Ich bin false')
    return False


def is_below_30_seconds(epoch_times):
    # Convert the string epoch times to integers and then to seconds
    epoch_times_seconds = [int(time) / 1000 for time in epoch_times]

    first_epoch_time = epoch_times_seconds[0]

    # Check if the list has at least one time to compare
    if not epoch_times_seconds:
        return True  # If list is empty, consider it as below 30 seconds

    for current_time in epoch_times_seconds:
        # Calculate the difference between the current time and the first time
        difference = current_time - first_epoch_time

        # If the difference is 30 seconds or more, return False
        if difference >= 30:
            return False

    # If we never hit a 30 second difference, return True
    return True


# print("Running Threads")
# print("Run Kafka Consumer in Background")
# Run Kafka Consumer in Background

def runlogic(topics):
    conf = {'bootstrap.servers': '172.26.241.166:9092',
            'group.id': 'mice',
            'enable.auto.commit': 'false',
            'auto.offset.reset': 'latest'}
    consumer = Consumer(conf)
    xs, ys = [0], []
    det_time = []
    stack = queue.Queue()
    recordstack = queue.Queue()

    while True:
        basic_consume_loop(consumer, topics, stack, recordstack, True)
        det_time.append(process_messages(stack, xs, ys))
        if not is_below_30_seconds(det_time):
            break
    #     consumer_thread = threading.Thread(target=basic_consume_loop, args=(consumer, topics, stack, True))
    #     consumer_thread.daemon = True
    #     consumer_thread.start()

    #     # Run Message Processor in Background
    #     print("Run Message Processor in Background")

    #     processor_thread = threading.Thread(target=process_messages, args=(stack,))
    #     processor_thread.daemon = True
    #     processor_thread.start()
    # # Start the animation
    # #    ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=50)
    # #    plt.show()
    #     consumer_thread.join()
    #     processor_thread.join()
    print('Feierabend')
    consumer.close()
    # return recordstack
    return xs, ys, recordstack
