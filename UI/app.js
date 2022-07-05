Dropzone.autoDiscover = false;

function init() {
    // we create the dropzone
    let dz = new Dropzone("#dropzone", {
        url: "/",
        maxFiles: 1,
        addRemoveLinks: true,
        dictDefaultMessage: "Some Message",
        autoProcessQueue: false
    });

    // these functions are called when the file dropped
    dz.on("addedfile", function() {
        if (dz.files[1]!=null) {
            dz.removeFile(dz.files[0]);        
        }
    });
    //when the upload is completed the 'file' has the object that we uploaded?
    dz.on("complete", function (file) {
        let imageData = file.dataURL;
        //file.dataurl contains the base64 string of the image that we dragged and dropped
        var url = "http://127.0.0.1:5000/classify_image";
        /*
        $post(url,{},function (data,status){
        });
         */

        //$ is a jquery sympbol
        //i make a 'POST' call to this URL
        //inside the post call,the first argument is the URL
        //2nd argument is a dictionary(or JSON object maybe idk) which contains the form data

        //send POST request. {} is the forma data. and 'data' is the returned dictionary from the flask server
        $.post(url, {
            image_data: file.dataURL //i send the image as a base64 string
        },function(data, status) {
            /* 
            Below is a sample response if you have two faces in an image lets say virat and roger together.
            Most of the time if there is one person in the image you will get only one element in below array
            data = [
                {
                    class: "viral_kohli",
                    class_probability: [1.05, 12.67, 22.00, 4.5, 91.56],
                    class_dictionary: {
                        lionel_messi: 0,
                        maria_sharapova: 1,
                        roger_federer: 2,
                        serena_williams: 3,
                        virat_kohli: 4
                    }
                },
                {
                    class: "roder_federer",
                    class_probability: [7.02, 23.7, 52.00, 6.1, 1.62],
                    class_dictionary: {
                        lionel_messi: 0,
                        maria_sharapova: 1,
                        roger_federer: 2,
                        serena_williams: 3,
                        virat_kohli: 4
                    }
                }
            ]
            */
            console.log(data);
            //if data array is empty?
            if (!data || data.length==0) {
                $("#resultHolder").hide();
                $("#divClassTable").hide();                
                $("#error").show();
                dz.removeFile(file);
                //iniitially i was hiding the error but now if i dont detect face then i show error
                return;
            }
            let players = ["lionel_messi", "maria_sharapova", "roger_federer", "serena_williams", "virat_kohli"];
            
            let match = null; //match will contain the correct dictipnary of the face
            let bestScore = -1;
            //if there are more than 2 faces the data.length will be =2 because there will be 2 dictionaries in the data list
            //we just consider the face which has the highest probability

            //we find the face with the max score
            for (let i=0;i<data.length;++i) {
                let maxScoreForThisClass = Math.max(...data[i].class_probability);
                //maximum element in the array 'data[i].class_probability'
                if(maxScoreForThisClass>bestScore) {
                    match = data[i];
                    bestScore = maxScoreForThisClass;
                }
            }
            //if i have a match (a face found
            if (match) {
                $("#error").hide();
                $("#resultHolder").show(); //display the table and result holder now
                $("#divClassTable").show();

                //match.class is the name of the class(celebrity)
                //resultholder is the box which shows the image of the identified image
                $("#resultHolder").html($(`[data-player="${match.class}"`).html());

                //this is for showing data in the table
                let classDictionary = match.class_dictionary;
                for(let personName in classDictionary) //iterate through each of the players and return their names
                {
                    //classDictionary just contains the key=celebrity name, value=index of that class
                    let index = classDictionary[personName];
                    //class_probability contains the prob of all the different class
                    let proabilityScore = match.class_probability[index];
                    let elementName = "#score_" + personName;
                    //HTML element name is created as '0.4lionel_messi'
                    //
                    $(elementName).html(proabilityScore);
                }
            }
            // dz.removeFile(file);
        });
    });
    // this function is called when the submit button is pressed
    $("#submitBtn").on('click', function (e) {
        dz.processQueue();		
    });
}

//this functon is called when the HTML is rendered by the web browser.
//initially we want to hide the error
$(document).ready(function() {
    console.log( "ready!" );
    $("#error").hide();
    $("#resultHolder").hide();
    $("#divClassTable").hide();

    init();
});