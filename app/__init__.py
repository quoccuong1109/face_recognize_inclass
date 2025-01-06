from flask import Flask

app = Flask(__name__)

# Import các route mới
from app.routes import home
from app.routes import add_face
from app.routes import train_model
from app.routes import delete_data  # Import the delete_data module
from app.routes import video_feed
from app.routes import get_next_id
from app.routes import attendance

# Register the blueprint
app.register_blueprint(delete_data.delete_data_bp, url_prefix='/')