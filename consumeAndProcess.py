import xml.etree.ElementTree as eT
import threading
import queue
from confluent_kafka import Consumer
import time
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
# from matplotlib import style
matplotlib.use('tkagg')

# Create figure for plotting
# Initialize your figure for plotting
fig, ax = plt.subplots()
xs, ys = [0], []
plot_key = ""
ecg_curve = 'ECGV.Realtimecurve.6C.64E8'

def animate(i, xs, ys):

    # Limit x and y lists to 20 items
    xs = xs[-620:]
    ys = ys[-620:]

    # Draw x and y lists
    try:
        plt.xticks(rotation=45, ha='right')
        plt.subplots_adjust(bottom=0.30)
        plt.title(plot_key)
        plt.ylabel('mV')
        ax.clear()
        ax.set_ylim([-0.4, 1.0])
        high_floats = [float(y) for y in ys]
        ax.plot(xs, high_floats)
    except:
        pass

print("Initializing Stack")
stack = queue.Queue()

def parse_input(incoming):
    root = eT.fromstring(incoming)
    values = dict()
    for state in root[1][0]:
        for nested_elements in state:
            if 'MetricValue' in nested_elements.tag:
                values[state.attrib['DescriptorHandle']] = nested_elements.attrib['Samples'].split(' ')
    return root[1][0].attrib['MdibVersion'], values

# Message Processing Function
def process_messages():
    print("process message")
    while True:
        if not stack.empty():
            message = stack.get()
            data = parse_input(message)
            data_dict = data[1]
    # Converting string values to floats
            if ecg_curve in data_dict:
                print('.')
            else:
                print('key not found')
                continue
            print(data_dict[ecg_curve])
            ys.extend(data_dict[ecg_curve])
            xs.extend(range((xs[-1]) + 1,len(ys), 1))
            print(len(ys))
            print(len(ys) - len(xs))
            time.sleep(.3)

conf = {'bootstrap.servers': '172.26.241.166:9092',
        'group.id': 'mice',
        'enable.auto.commit': 'false',
        'auto.offset.reset': 'latest'}

consumer = Consumer(conf)
topics = ['sdc_865d26ad-ee40-5368-a215-4950e69b4a60_ws']

def msg_process(msg):
    stack.put(msg.value().decode('utf-8'))
    #print(f"key: {msg.key().decode('utf-8')}, value: {msg.value().decode('utf-8')}")

running = True

def basic_consume_loop(consumer, topics):
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
                msg_process(msg)
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()

def shutdown():
    running = False


print("Running Threads")
print("Run Kafka Consumer in Background")
# Run Kafka Consumer in Background
consumer_thread = threading.Thread(target=basic_consume_loop, args=(consumer, topics))
#consumer_thread.daemon = True
consumer_thread.start()

# Run Message Processor in Background
print("Run Message Processor in Background")
processor_thread = threading.Thread(target=process_messages)
#processor_thread.daemon = True
processor_thread.start()   


# Start the animation
ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=50)
plt.show()

consumer_thread.join()
processor_thread.join()   
