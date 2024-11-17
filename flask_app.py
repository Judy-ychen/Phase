from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Streamlit in Flask</title>
    </head>
    <body>
        <h1>Streamlit App Embedded in Flask</h1>
        <iframe src="http://127.0.0.1:8501" width="100%" height="800" frameborder="0"></iframe>
    </body>
    </html>
    """
