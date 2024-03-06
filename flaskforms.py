from flask import Flask, render_template, request
import json


app = Flask(__name__)

data = None

def loadDataJSON():
    #Load data from a JSON file 
    with open("CMT_Data.json","r") as read_file:
        global data
        data = json.load(read_file)

def saveDataJSON(values):
    
    global data

    try:
        food_data = data["food_data"]
        food_data.append(values)
        data["food_data"] = food_data

    except:
        data["food_data"] = [values]

    #Load data from a JSON file 
    with open("CMT_Data.json","w") as write_file:
        json.dump(data, write_file, indent=4)

    

# Renders the basic template as the index
@app.route("/")
def index():
    
    loadDataJSON()
    return render_template("template.html")

# Renders the pickup form from dynamic values
@app.route("/pickup" ,methods=['GET', 'POST'])
def pickupform():

    if request.method == 'POST':
        # Print the form data to the console
        for key, value in request.form.items():
            print(f'{key}: {value}')

    global data

    return render_template("pickupform.html", dynamic_labels=data["food_labels"])

# Renders the pickup form from dynamic values
@app.route("/kitchen",methods=['GET', 'POST'])
def kitchenform():
    global data


 
    if request.method == 'POST':
        # Print the form data to the console
        values = []
        for key, value in request.form.items():
            print(f'{key}: {value}')
            values.append(value)            

        saveDataJSON(values)
    return render_template("kitchenform.html", dynamic_labels=data["food_labels"],dynamic_options=data['kitchen_labels'])

    
if __name__ == "__main__":
    app.run(debug=True)

    
