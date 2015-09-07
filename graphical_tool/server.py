from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/')
def hello2(name=None):
    return render_template('graphical_tool.html', name=name)

if __name__ == "__main__":
    app.run()
