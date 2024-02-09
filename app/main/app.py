import subprocess
from flask import Flask, render_template, Response
import logic.consumeAndProcess

app = Flask(__name__)

@app.route('/')
def index():
    # Execute the shell script and get output
    result = subprocess.run(['app/scripts/get_topics.sh'], stdout=subprocess.PIPE, text=True)
    # Split the output into a list of topics
    topics = result.stdout.splitlines()
    # Render these topics in the index.html template
    return render_template('index.html', topics=topics)

# Other routes and functions...

@app.route('/process/<topic_name>')
def process_topic(topic_name):
    topics = [topic_name]
    recordedstack = logic.consumeAndProcess.runlogic(topics)
    # Here, call the function that processes the topic
    # For demonstration, this will just return a simple message
    # In real use, you might redirect to another page that shows the processing result or status
    return f"Processing topic: {type(recordedstack)}"

if __name__ == '__main__':
    app.run(debug=True)