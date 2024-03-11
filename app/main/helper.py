import matplotlib.pyplot as plt
import base64
import io
import os
import uuid
import requests
from dotenv import load_dotenv

load_dotenv()
plt.switch_backend('Agg')


def get_consumer_conf(group_type):
    bootstrap = os.environ['kafka_server']

    match group_type:
        case 'live':
            group_id = os.environ['kafka_group_live']
        case 'capture':
            group_id = os.environ['kafka_group_capture']
        case _:
            group_id = str(uuid.uuid4())

    return {'bootstrap.servers': bootstrap,
            'group.id': group_id,
            'enable.auto.commit': 'false',
            'auto.offset.reset': 'latest'}


def push_fhir_data(outgoing_data):
    endpoint = os.environ['fhir_endpoint']
    r = requests.post(endpoint, data=outgoing_data)
    print(r.status_code)


def create_image(xs, ys, key):
    data_floats = [float(y) for y in ys[-1]]
    plt.figure(figsize=(10, 6))
    plt.plot(xs[-1], data_floats)
    plt.title(str(key))
    buf = io.BytesIO()
    plt.savefig(buf, format='jpg')
    buf.seek(0)
    base64_string = base64.b64encode(buf.read()).decode()
    buf.close()
    plt.close()
    return base64_string
