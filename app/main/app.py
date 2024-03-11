import json
from flask import Flask, render_template, Response, stream_with_context
import consume_process
import helper
import exporter
import generateLiveData
from confluent_kafka import Consumer

app = Flask(__name__)
topic_list = list()


@app.route('/')
def index():
    conf = helper.get_consumer_conf('live')
    consumer = Consumer(conf)
    temp = consumer.list_topics().topics.keys()
    for t in temp:
        if t.startswith('sdc'):
            topic_list.append(t)
    return render_template('liveplot.html', topics=topic_list)


@app.route('/chart-data')
def chart_data():
    topic_filter = (topic for topic in topic_list
                    if "_ws" in topic)
    response = Response(stream_with_context(generateLiveData.runlive([next(topic_filter)])),
                        mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response


@app.route('/process/<topic_name>')
def process_topic(topic_name):
    topics = [topic_name]
    realtime_curve = consume_process.runlogic(topics)
    fhir_bundle = exporter.fhirize(realtime_curve)
    helper.push_fhir_data(fhir_bundle.json(indent=2))
    json_str = json.dumps(realtime_curve)

    return render_template(
        template_name_or_list='chartjs-example.html',
        datasets=json_str,
    )


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
