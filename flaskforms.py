from flask import Flask, render_template, request
import json


app = Flask(__name__)

def loadJSON():
    #Load data from a JSON file 
    with open("CMT_Data_Lables.json","r") as read_file:
        data=json.load(read_file)
     #returns the value associated with the key "food_labels" from the loaded JSON data
        return data["food_labels"]


   

@app.route("/" ,methods=['GET', 'POST'])
def pickupform():
    # Dynamic data to be passed to the template which is food_labels
    dynamic_labels =  loadJSON()
    if request.method == 'POST':
        # Print the form data to the console
        for key, value in request.form.items():
            print(f'{key}: {value}')
    return render_template("pickupform.html", dynamic_labels=dynamic_labels)

@app.route("/kitchen")
def kitchenform():
    return render_template("kitchenform.html")


    
if __name__ == "__main__":
    app.run(debug=True)

    
