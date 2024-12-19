"""
Basic test for flask currect installation

Execute the following:
flask --app Test_Flask run

Note: with Poetry means run the following:
poetry run flask --app Test_Flask run

"""


from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"