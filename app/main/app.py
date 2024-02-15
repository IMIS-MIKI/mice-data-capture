import json
from flask import Flask, render_template, Response
import logic.consumeAndProcess
import logic.exporter
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
    realtimecurveDict = logic.consumeAndProcess.runlogic(topics)
    # Here FHIR Stuff
    fhir_obs = logic.exporter.fhir(realtimecurveDict)
    print(fhir_obs.json(indent=2))

    # Convert the dictionary to a JSON string
    json_str = json.dumps(realtimecurveDict)

    return render_template(
        template_name_or_list='chartjs-example.html',
        datasets=json_str,
    )


if __name__ == '__main__':
    app.run(debug=True)
