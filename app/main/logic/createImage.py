import matplotlib.pyplot as plt
import xml.etree.ElementTree as eT
import base64
import os
import io

plt.switch_backend('Agg')


def parse_input(incoming):
    root = eT.fromstring(incoming)
    values = dict()
    for state in root[1][0]:
        for nested_elements in state:
            if 'MetricValue' in nested_elements.tag:
                values['DeterminationTime'] = nested_elements.attrib['DeterminationTime']
                values[state.attrib['DescriptorHandle']] = nested_elements.attrib['Samples'].split(' ')
    return root[1][0].attrib['MdibVersion'], values


def parseValues(stack):
    print("parse values")
    xs, ys = [0], []
    while True:
        if not stack.empty():
            message = stack.get()
            data = parse_input(message)
            data_dict = data[1]
            ecg_curve = 'ECGV.Realtimecurve.6C.64E8'
            # Converting string values to floats
            ys.extend(data_dict[ecg_curve])
            xs.extend(range((xs[-1]) + 1, len(ys), 1))
            print(len(ys))
        else:
            break
        return ys


def createImage(stack):
    data = parseValues(stack)
    plt.figure(figsize=(10, 6))
    plt.plot(data)
    plt.title('ECG')
    buf = io.BytesIO()
    plt.savefig(buf, format='jpg')
    buf.seek(0)
    base64_string = base64.b64encode(buf.read()).decode()
    buf.close()
    plt.close()
    return base64_string
