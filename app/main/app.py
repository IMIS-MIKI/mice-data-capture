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
    labels, data, record = logic.consumeAndProcess.runlogic(topics)
    # Here FHIR Stuff
    base = logic.createImage.createImage(record)
    fhir_obs = fhirizer.exporter.fhir(data, base)
    # Here, call the function that processes the topic
    # For demonstration, this will just return a simple message
    # In real use, you might redirect to another page that shows the processing result or status
    # return f"Processing topic: {type(recordedstack)}"
    return render_template(
        template_name_or_list='chartjs-example.html',
        data=data,
        labels=labels,
    )


if __name__ == '__main__':
    app.run(debug=True)
