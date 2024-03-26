import os
from flask import Flask, render_template, request, session, redirect, send_file
from cmt_data import CMT_Data # import CMT_Data class from cmt_data.py file

# initialise CMT_Data class with name of save data file
data = CMT_Data("Data/CMT_Data.json") 

Pass = "WeLoveAutonomy"
admin_password = "admin_pass"

# Function that creates the flask app for us
def smuc_app(test_config=None):

    # initialise flask app
    app = Flask(__name__)

    app.secret_key = 'kwer!wh83£$47dh82u&wh28?'
    print("#############################")
    print("#############################")
    print("Password: ", Pass)
    print("#############################")
    print("#############################")

    # Renders the basic template as the index
    @app.route("/", methods=['GET', 'POST'])
    def index():

        # if  logged in render  nav page
        if session.get('logged_ in') and session["logged_ in"]==True:
            return render_template("Nav.html")

        if request.method == "POST":

            pw = request.form.get("pw") 

            if pw == Pass:
                session["logged_ in"]=True
                return render_template("Nav.html")
            else:
                session["logged_ in"]=False
            
            
            
        return render_template("index.html")

    # Renders the pickup form from dynamic values
    ### Curently not in use
    #@app.route("/pickup" ,methods=['GET', 'POST']) 
    def pickupform():

        # if not logged in redirect to main page
        if not session.get('logged_ in') or session["logged_ in"]==True:
            return redirect("/")

        global data

        if request.method == 'POST':
            # add form data to the data class and return the display values
            display_values =  data.add_pickup_data(request.form.items())
            # Render response page template with form data if request method is post 
            return render_template("responsepage.html", values=display_values)
        
        return render_template("pickupform.html", dynamic_labels=data.json["food_labels"])

    # Renders the kitchen form from dynamic values
    @app.route("/kitchen",methods=['GET', 'POST'])
    def kitchenform():

        # if not logged in redirect to main page
        if not session.get('logged_ in') or session["logged_ in"]!=True:
            return redirect("/")
        
        global data

        if request.method == 'POST':
            # Add form data to data class and get display data back.
            display_values =  data.add_kitchen_data(request.form.items())
            # Render response page template with form data if request method is post 
            return render_template("responsepage.html", values=display_values)
        
        # Render form template with dynamic values
        return render_template("kitchenform.html", dynamic_labels=data.json["food_labels"],dynamic_options=data.json['kitchen_labels'])
    


     # Renders the overview page displaying data for all kitchens.
    @app.route("/overview")
    def overview():

        # if not logged in redirect to main page
        if not session.get('logged_ in') or session["logged_ in"]!=True:
            return redirect("/")

        global data  # Indicates that 'data' is a global variable

        #Get the kitchens array direclty from CMT_Data 
        kitchens = data.kitchens

        #Intialize an empty list to store display values for all kitchens
        kitchens_display_values = []

         # Iterate through each kitchen in the kitchens array
        for kitchen in kitchens:
        #Get the display value for the current kitchen
            display_val = kitchen.get_display_val()
        # Append the display value to the list
            kitchens_display_values.append(display_val)
        # Return the list of display values for all kitchens 
        return render_template("overview.html", kitchens_display_values=kitchens_display_values)
        

    @app.route('/download/<admin_pass>')
    def download_file(admin_pass):

        if admin_pass!= admin_password or not session.get('logged_ in') or session["logged_ in"]!=True:
            return redirect("/")
        
        global data

        path = data.working_file

        return send_file(path, as_attachment=True)
    

    # returns the flask app
    return app
    

    
if __name__ == "__main__":
    # run the smuc_app function and get the app
    app = smuc_app()
    # run it!
    app.run(debug=True)

    
