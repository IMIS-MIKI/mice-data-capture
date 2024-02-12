import matplotlib.pyplot as plt
import xml.etree.ElementTree as eT
import numpy as np
import base64
import os

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
            xs.extend(range((xs[-1]) + 1,len(ys), 1))
            print(len(ys))
        else:
            break     
        return ys

def createImage(stack):
    
    data = parseValues(stack)
    
    # Step 2: Plot the data and save as an image in a temporary folder
    plt.figure(figsize=(10, 6))
    plt.plot(data)
    plt.title('ECG')
    temp_folder = 'tmp/'
    image_path = os.path.join(temp_folder, 'plot.png')
    plt.savefig(image_path)
    print("save image")
    plt.close()
    
    # Step 3: Convert the saved image to base64
    with open(image_path, "rb") as image_file:
        base64_string = base64.b64encode(image_file.read()).decode()
    
    os.remove(image_path)
    # Providing the path to the saved image for reference
    return base64_string
