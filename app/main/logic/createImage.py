import matplotlib.pyplot as plt
import xml.etree.ElementTree as eT
import base64
import io

plt.switch_backend('Agg')

def createImage(xs, ys, key):
    #x, data = parseValues(stack, realtimecurve)
    print(ys)
    print(xs)
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
