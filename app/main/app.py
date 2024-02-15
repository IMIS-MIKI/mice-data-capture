import json
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
    realtimecurveDict = logic.consumeAndProcess.runlogic(topics)
    # Here FHIR Stuff
    for key, valueLists in realtimecurveDict.items():
        print(f"Processing {key}")
        base = logic.createImage.createImage(valueLists[0], valueLists[1], key)
        fhir_obs = fhirizer.exporter.fhir(valueLists[1], base)
    
    # Convert the dictionary to a JSON string
    json_str = json.dumps(realtimecurveDict)

    return render_template(
       template_name_or_list='chartjs-example.html',
        # data=realtimecurveDict["ECGI.Realtimecurve.68.793F"][1][-1],
        # labels=realtimecurveDict["ECGI.Realtimecurve.68.793F"][0][-1],
        datasets = json_str,
   )


if __name__ == '__main__':
    app.run(debug=True)
