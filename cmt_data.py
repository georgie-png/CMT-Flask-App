
from datetime import datetime
import json
from train_evaluate import load_model_for_inference, classify, print_summary
import numpy as np
from os import path


# CMT_Data class that handles all the processes for the apps form inputs, outputs and json saving
class CMT_Data:

    def __init__(self, file_name, start_fresh=False):
        """CMT_Data class  handles all the processes for the apps form inputs from forms, managing the classifier and saving data to json.

        Args:
            file_name (sting): Path to save(d) data file
            start_fresh (bool, optional): If set to true it will reset data, and save the old (if there was one) with a timestamp.
        """
        self.working_file = file_name
        try:
            self.load_JSON(file_name)
            
            if start_fresh==True:
                self.save_JSON(time_stamp=True)
                self.load_JSON('./Data/CMT_Data_Lables.json')

        except:
            self.load_JSON('./Data/CMT_Data_Lables.json')
        



        self.model, self.model_summary = load_model_for_inference('./trained_models/example_model')
        

    def load_JSON(self, file_name):
        """Loads a json at `file_name` into self.json 

        Args:
            file_name (string): path to json file
        """

        #Load data from a JSON file 
        with open(file_name,"r") as read_file:
            self.json = json.load(read_file)
        self.setup_kitchens()

    def save_JSON(self, time_stamp = False):
        """Saves the file at in the same place, or with a time stamp.

        Args:
            time_stamp (bool, optional): if true saves json file with a timestamp
        """

        file_name = path.splitext(self.working_file)[0]
        if time_stamp:
            file_name += "_"+str(datetime.now())
        file_name += ".json"

        #save data from a JSON file 
        with open(file_name,"w") as write_file:
            json.dump(self.json, write_file, indent=4, cls=NumpyArrayEncoder)


    def add_kitchen_data(self, form_data):
        """Adds kitchen data to the class by saving it to the json and updating its kitchen class data

        Args:
            form_data (_type_): raw data from the flask form

        Returns:
            dict: A dictionary pairing of all the entered values and the labels (e.g. dict["fruit"] = 200g) to be displayed in flask
        """

        display_values = {}
        values = [] 
        for key, value in form_data:

            #Values is now dictionary data structure store values as a key-value pair.
            display_values[key] =value    

            if key != 'Kitchen':
                value = float(value)
            
            values.append(value)    

        kitchen_data = {}
        kitchen_index = self.check_kitchen_indx(values[0])
        kitchen_data['kitchen_label'] = kitchen_index
        kitchen_data['food_data'] = values[1:]
        kitchen_data['time_stamp'] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        self.kitchens[kitchen_index].food_data = kitchen_data['food_data']
        
        np_food_data = self.stack_data(kitchen_data['food_data'])


        try:

            self.json["kitchen_data"].append(kitchen_data)
            self.json["food_data"].append(np_food_data)

        except:
            self.json["kitchen_data"]=[kitchen_data]
            self.json["food_data"]=np_food_data



        self.save_JSON()

        return display_values

    def add_pickup_data(self, form_data):
        """Adds pickup data to the json and also runs it through the classifier, and then returns the results so they can be displayed by flask. 

        Args:
            form_data (_type_): Raw form data from flask

        Returns:
            dist: A dictionary pairing of all the classified values and the labels (e.g. dict["fruit"] = kitchen 3) to be displayed in flask
        """

        values = [] 
        for key, value in form_data:

            value = float(value)
            
            values.append(value)    

        display_values, classified_data = self.run_classify(values)


        pickup_data = {}
        pickup_data['food_data'] = values
        pickup_data['time_stamp'] = datetime.now()

        try:
            self.json["classified_data"].append(classified_data)
            self.json["pickup_data"].append(pickup_data)

        except:
            self.json["classified_data"]=[classified_data]
            self.json["pickup_data"]=[pickup_data]

        self.save_JSON()

        return display_values


    def check_kitchen_indx(self, this_kitchen):
        """returns the index of the this_kitchen in the json data

        Args:
            this_kitchen (sting): Name of a kitchen

        Returns:
            int: The index of that kitchen in the json data
        """

        for indx, kitchen in enumerate(self.json['kitchen_labels']):

            if kitchen == this_kitchen:
                return indx
        
        return -1
    
    def setup_kitchens(self):
        """Sets up all the kitchen classes that have been read from the json data and restores their values if possible.
        """

        self.kitchens = [Kitchen(self.json['food_labels'], name) for name in self.json['kitchen_labels']]

        indxs = np.zeros(len(self.kitchens), dtype=np.int32)

        kitchen_data_array = self.json.get('kitchen_data')

        if kitchen_data_array:

            for kitchen_data in kitchen_data_array:

                label = kitchen_data['kitchen_label'] 

                if indxs[label] == 0:
                    indxs[label] = 1
                    self.kitchens[label].restore_kitchen(kitchen_data['food_data'], kitchen_data['time_stamp'])
                    
                if np.sum(indxs) == len(self.kitchens):
                    break

    def stack_data(self, values):



        np_kitchen_data = [] 
        np_classify_data = []

        for kitchen in self.kitchens:
            np_kitchen_data.append(kitchen.food_data)
        
        np_kitchen_data = np.array(np_kitchen_data, dtype=np.float32)

        for i, value in enumerate(values):
            this_value = np.zeros(shape=[len(values)])
            this_value[i] = value
            this_value = np.vstack((np_kitchen_data, this_value))
            np_classify_data.append(this_value)
            


        return np_classify_data

    def run_classify(self, values):
        """Takes in the values and then forms them into the right array shape for the model, runs it through classifier to be displayed and saved

        Args:
            values (list): A list of the food values taken from the form

        Returns:
            tuple {dict|dict}: two dictionaries the first holding the key value pairs for flask to display. The second all of the input/outputs of the  classification.
        """

        np_classify_data = self.stack_data(values)


        raw_classifications = classify(self.model , np_classify_data)

        classifications = raw_classifications.argmax(axis=1)

        classification_data =  {}

        classification_data['input'] = np_classify_data
        classification_data['raw_classification'] = raw_classifications
        classification_data['classification'] = classifications
        classification_data['time_stamp'] = datetime.now()

        display_values = {}

        for i, classification in enumerate(classifications):

            if values[i] == 0:
                continue

            kitchen_label = self.json['kitchen_labels'][classification]
            food_label = self.json['food_labels'][i]
            display_values[food_label] = kitchen_label

        return display_values, classification_data



class Kitchen:

    def __init__(self, food_labels, name):
        """A class to run the functions of a kitchen

        Args:
            food_labels (list): list of food labels
            name (string): name of kitchen
        """

        self.food_data = [0]*len(food_labels)
        self.name = name
        self.last_modified = datetime.now()
        self.food_labels = food_labels
        


    def set_foods(self, new_food_data):
        """Sets the food data and updates the last_modified to now

        Args:
            new_food_data (list): list of food values
        """

        self.food_data = new_food_data
        self.last_modified = datetime.now()


        
    def restore_kitchen(self, food_data, last_modified):
        """Restores a kitchen to data and time provided

        Args:
            food_data (list): list of food values
            last_modified (timestamps): a timestamp of last modified
        """
        self.food_data = food_data
        self.last_modified = last_modified


    def get_display_val(self):
        """Returns a dict of the values and labels to  be displayed by flask

        Returns:
            dict: a dict of all the food labels and their values (e.g. display_val['fruit'] == 100g)
        """
   
        display_val = {}

        for key, val in zip(self.food_labels,self.food_data):
            display_val[key]=val

        display_val['last_modified']=self.last_modified

        return display_val

        
class NumpyArrayEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)
    

class NumpyArrayEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NumpyArrayEncoder, self).default(obj)