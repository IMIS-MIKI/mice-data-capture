import json
from flask import Flask, render_template, Response, stream_with_context
import consumeAndProcess
import create_image
import exporter
import generateLiveData
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
    print(topics)
    return render_template('liveplot.html', topics=topics)


@app.route('/chart-data')
def chart_data():
    # response = Response(stream_with_context(livedataplot.generateLiveData.generateRandomData()), mimetype="text/event-stream")
    response = Response(stream_with_context(generateLiveData.runlive(['sdc_865d26ad-ee40-5368-a215-4950e69b4a60_ws'])),
                        mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response
    # Other routes and functions...


@app.route('/process/<topic_name>')
def process_topic(topic_name):
    topics = [topic_name]
    realtimecurveDict = consumeAndProcess.runlogic(topics)
    # Here FHIR Stuff
    fhir_bundle = exporter.fhirize(realtimecurveDict)
    print(fhir_bundle.json(indent=2))

    # Convert the dictionary to a JSON string
    json_str = json.dumps(realtimecurveDict)

    return render_template(
        template_name_or_list='chartjs-example.html',
        datasets=json_str,
    )


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
