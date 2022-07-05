from flask import Flask, request, jsonify
import util

app = Flask(__name__)


@app.route('/classify_image', methods=['GET', 'POST'])
def classify_image():
    #request object is from flask module
    #the UI sends the image data in a request object
    image_data = request.form['image_data']  #the form has a header image_data and we access that dictionary
    #image_data is in the form of base64 string
    response = jsonify(util.classify_image(image_data)) #i pass the base64 string into the clssifier
    #jsonify returns a response JSON object
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

if __name__ == "__main__":
    #we execute the main block first
    print("Starting Python Flask Server For Sports Celebrity Image Classification")
    util.load_saved_artifacts()  #IMP line. load models
    app.run(port=5000) # we run the app on port=5000