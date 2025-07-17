from flask import Flask, render_template
from core.main import main



app = Flask(__name__)
app.register_blueprint(main)

@app.errorhandler(404)
def not_found(e):
    render_template("404.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
