from keras.preprocessing.image import img_to_array
from keras.models import load_model
from flask_restplus import Api, Resource, fields
from flask import Flask, request, jsonify
import numpy as np
from werkzeug.datastructures import FileStorage
from PIL import Image
# import Image
from keras.models import model_from_json
import tensorflow as tf
import pymongo
import os
import datetime
import dns

# Connect to mongo via production or localhost
if os.environ.get("MONGOUSER"):
    user = os.environ.get("MONGOUSER")
    password = os.environ.get("PASSWORD")
    url = os.environ.get("URL")
    client = pymongo.MongoClient(f"mongodb+srv://{user}:{password}@{url}")
    db = client.logs
else:
    client = pymongo.MongoClient(f"mongodb://localhost/mnist")
    db = client.logs

application = app = Flask(__name__)
api = Api(app, version='1.0', title='MNIST Classification', description='CNN for Mnist')
ns = api.namespace('Make_School', description='Methods')

single_parser = api.parser()
single_parser.add_argument('file', location='files', type=FileStorage, required=True)

model = load_model('my_model.h5')
graph = tf.get_default_graph()

@ns.route('/prediction')
class CNNPrediction(Resource):

    """Uploads your data to the CNN"""
    @api.doc(parser=single_parser, description='Upload an mnist image')
    def post(self):
        args = single_parser.parse_args()
        image_file = args.file
        image_file.save('milad.png')
        img = Image.open('milad.png')
        image_red = img.resize((28, 28))
        image = img_to_array(image_red)
        print(image.shape)
        x = image.reshape(1, 28, 28, 1)
        x = x/255
        # model = load_model('my_model.h5')
        with graph.as_default():
            out = model.predict(x)
        print(out[0])
        print(np.argmax(out[0]))
        r = np.argmax(out[0])

        # Create a dictionary to insert into db
        db_info = {
            "pred": str(r),
            "filename": args.file.filename,
            "time": datetime.datetime.now()
        }

        # insert into logs collection in db
        db.logs.insert_one(db_info)

        return {'prediction': str(r)}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)