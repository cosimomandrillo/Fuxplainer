from flask import Flask
import config
from routes import register_routes

app = Flask(__name__)
app.secret_key = config.FLASK_SECRET_KEY

#REGISTRAZIONE DELLE ROTTE
register_routes(app)

if __name__ == "__main__":
    app.run(debug=True, port=5001)