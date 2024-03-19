import os
from flask import Flask, render_template, request
from cmt_data import CMT_Data # import CMT_Data class from cmt_data.py file


# initialise CMT_Data class with name of save data file
data = CMT_Data("./Data/CMT_Data.json", True) 

# Function that creates the flask app for us
def smuc_app(test_config=None):

    # initialise flask app
    app = Flask(__name__)

    # Renders the basic template as the index
    @app.route("/")
    def index():
        return render_template("template.html")

    # Renders the pickup form from dynamic values
    @app.route("/pickup" ,methods=['GET', 'POST'])
    def pickupform():
        global data

        if request.method == 'POST':
            # add form data to the data class and return the display values
            display_values =  data.add_pickup_data(request.form.items())
            # Render response page template with form data if request method is post 
            return render_template("responsepage.html", values=display_values)
        
        return render_template("pickupform.html", dynamic_labels=data.json["food_labels"])

    # Renders the pickup form from dynamic values
    @app.route("/kitchen",methods=['GET', 'POST'])
    def kitchenform():
        global data

        if request.method == 'POST':
            # Add form data to data class and get display data back.
            display_values =  data.add_kitchen_data(request.form.items())
            # Render response page template with form data if request method is post 
            return render_template("responsepage.html", values=display_values)
        
        # Render form template with dynamic values
        return render_template("kitchenform.html", dynamic_labels=data.json["food_labels"],dynamic_options=data.json['kitchen_labels'])

    # returns the flask app
    return app

    
if __name__ == "__main__":
    # run the smuc_app function and get the app
    app = smuc_app()
    # run it!
    app.run(debug=True)

    
