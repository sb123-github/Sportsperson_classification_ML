import joblib
import json
import numpy as np
import base64
import cv2
from wavelet import w2d

__class_name_to_number = {} # we directly load the dictionary which gives the celeb rity names mapped to numbers
__class_number_to_name = {} #we do the opposite. this dictionary maps number to celebrity name

__model = None

def classify_image(image_base64_data, file_path=None):
    # if we get a face with 2 eyes in the 'file _path' or the base 64 string in 'image_base64_data'
    # then only we get some value from the function 'get_cropped_image_if_2_eyes'
    # otherwise we just get back 'none'
    imgs = get_cropped_image_if_2_eyes(file_path, image_base64_data)

    result = []
    #same thing below as we did in notebook
    for img in imgs:  #we take each image in the returned imgs
        #inside this for loop i just resize the given image into a standard image of size 32x32

        scalled_raw_img = cv2.resize(img, (32, 32))
        img_har = w2d(img, 'db1', 5) #we then find the waveleft transformation
        scalled_img_har = cv2.resize(img_har, (32, 32)) #scale the wavelet img
        combined_img = np.vstack((scalled_raw_img.reshape(32 * 32 * 3, 1), scalled_img_har.reshape(32 * 32, 1)))
        #flatten the images and stack them

        len_image_array = 32*32*3 + 32*32
        final = combined_img.reshape(1,len_image_array).astype(float) #we change the size and fata type to float
        #final has a shape of (1,4096) . this is because our model predictor expects X in this format
        #model predict expects that each row will be a complete data sample
        #and the different rows are the diff test images

        #we now use the model to predict the output classes probabilities
        #by this point we have already loaded the '__model' in this file. we do it from the __main__
        #we also have the  'class_number_to_name' loaded
        #__model.predict(final)[0] just returns the class number
        # np.round(x,2) rounds to 2 decimals
        # print("Hello there")
        # print(__model.predict(final)) #it is a 1D numpy array
        # print(__model.predict_proba(final)) #2D array. it has so many decimal places
        #class 5 has highest prob.
        result.append({
            'class': class_number_to_name(__model.predict(final)[0]),
            'class_probability': np.around(__model.predict_proba(final)*100,2).tolist()[0],
            'class_dictionary': __class_name_to_number
        })

    return result

def class_number_to_name(class_num):
    return __class_number_to_name[class_num]

def load_saved_artifacts(): #we call this from the __main__
    print("loading saved artifacts...start")
    global __class_name_to_number  #we wanna edit the global variables
    global __class_number_to_name
    #class_dictionary.json has the column names
    with open("./artifacts/class_dictionary.json", "r") as f:
        __class_name_to_number = json.load(f)
        # we directly load the dictionary which gives the celeb rity names mapped to numbers
        __class_number_to_name = {v:k for k,v in __class_name_to_number.items()}
        #v= key in this new dictionary , which was the value in the old dictionary __class_name_to_number
        #we do the opposite. this dictionary maps number to celebrity name

    global __model
    if __model is None:
        with open('./artifacts/saved_model.pkl', 'rb') as f:
            __model = joblib.load(f) #we load the function using joblib
    print("loading saved artifacts...done")


#we take the base 64 encoded string and convert it into opencv img(a numpy array)
def get_cv2_image_from_base64_string(b64str):

    '''
    credit: https://stackoverflow.com/questions/33754935/read-a-base-64-encoded-image-from-memory-using-opencv-python-library
    :param uri:
    :return:
    '''

    encoded_data = b64str.split(',')[1]
    nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


#we take an image path or a base64 string and then
#returns the cropped image if the haar algorithm finds a face with 2 eyes
#this is the same function as jupyter notebook function
def get_cropped_image_if_2_eyes(image_path, image_base64_data):
    face_cascade = cv2.CascadeClassifier('./opencv/haarcascades/haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('./opencv/haarcascades/haarcascade_eye.xml')
    if image_path:
        img = cv2.imread(image_path)
    else:
        img = get_cv2_image_from_base64_string(image_base64_data)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    cropped_faces = []
    for (x,y,w,h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray)
            if len(eyes) >= 2:
                cropped_faces.append(roi_color)
    return cropped_faces

def get_b64_test_image_for_virat():
    with open("b64.txt") as f:
        return f.read()

if __name__ == '__main__':
    load_saved_artifacts()
    #we just test our model on a base 64 encoded string present in the b64.txt for testing purpose
    # print(classify_image(get_b64_test_image_for_virat(), None))

    # print(classify_image(None, "./test_images/federer1.jpg"))
    # print(classify_image(None, "./test_images/federer2.jpg"))
    # print(classify_image(None, "./test_images/virat1.jpg"))
    # print(classify_image(None, "./test_images/virat2.jpg"))

    # print(classify_image(None, "./test_images/virat3.jpg")) #we have 2 faces #so we get a list of 2 dictionaries
    # we get different results from the predict_proba and the predict function
    # Inconsistent result could be due to https://github.com/scikit-learn/scikit-learn/issues/13211
    # print(classify_image(None, "./test_images/serena1.jpg"))
    # print(classify_image(None, "./test_images/serena2.jpg"))
    # print(classify_image(None, "./test_images/sharapova1.jpg"))
