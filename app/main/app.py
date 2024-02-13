import subprocess
from flask import Flask, render_template, Response
import logic.consumeAndProcess
import logic.createImage
import fhirizer.exporter
from confluent_kafka import Consumer, KafkaError, KafkaException

app = Flask(__name__)


@app.route('/')
def index():
    conf = {'bootstrap.servers': '172.26.241.166:9092',
            'group.id': 'mice',
            'enable.auto.commit': 'false',
            'auto.offset.reset': 'latest'}
    consumer = Consumer(conf)
    temp = consumer.list_topics().topics.keys()
    topics = []
    for t in temp:
        if t.startswith('sdc'):
            topics.append(t)
    # Render these topics in the index.html template
    return render_template('index.html', topics=topics)


# Other routes and functions...

@app.route('/process/<topic_name>')
def process_topic(topic_name):
    topics = [topic_name]
    realtimecurveDict, record = logic.consumeAndProcess.runlogic(topics)
    # Here FHIR Stuff
    for key, valueLists in realtimecurveDict.items():
        print(f"Processing {key}")
        xs, ys = [], []
        for lists in valueLists[0]:
            for values in lists:
                xs.append(values) 
        for lists in valueLists[1]:
            for values in lists:
                ys.append(values)  
        base = logic.createImage.createImage(xs, ys, key)
        fhir_obs = fhirizer.exporter.fhir(ys, base)

    return render_template(
       template_name_or_list='chartjs-example.html',
    #    data=data,
    #    labels=labels,
         datasets = realtimecurveDict
   )


if __name__ == '__main__':
    app.run(debug=True)
