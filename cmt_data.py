
from datetime import datetime
import json
from train_evaluate import load_model_for_inference, classify
import numpy as np



class CMT_Data:

    json = None

    def __init__(self, file_name, start_fresh=False):

        try:
            self.load_JSON(file_name)
            
            if start_fresh==True:
                self.save_JSON(time_stamp=True)
                self.load_JSON('./Data/CMT_Data_Lables.json')

        except:
            self.load_JSON('./Data/CMT_Data_Lables.json')
        

        self.working_file = file_name

        self.model = load_model_for_inference('./trained_models/example_model')




    def load_JSON(self, file_name):
        #Load data from a JSON file 
        with open(file_name,"r") as read_file:
            self.json = json.load(read_file)
        self.setup_kitchens()




    def save_JSON(self, time_stamp = False):


        file_name = "./Data/CMT_Data"
        if time_stamp:
            file_name += "_"+str(datetime.now())
        file_name += ".json"


        #save data from a JSON file 
        with open(file_name,"w") as write_file:
            json.dump(self.json, write_file, indent=4, default=str)



    def add_kitchen_data(self, form_data):

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
        kitchen_data['kitchen_lable'] = kitchen_index
        kitchen_data['food_data'] = values[1:]
        kitchen_data['time_stamp'] = datetime.now()
        self.kitchens[kitchen_index].food_data = kitchen_data['food_data']
        
        print(self.kitchens[kitchen_index].food_data)

        try:

            self.json["kitchen_data"].append(kitchen_data)


        except:
            self.json["kitchen_data"]=[kitchen_data]


        self.save_JSON()

        return display_values;

    def add_pickup_data(self, form_data):

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

        for indx, kitchen in enumerate(self.json['kitchen_labels']):

            if kitchen == this_kitchen:
                return indx
        
        return -1
    
    def setup_kitchens(self):

        self.kitchens = [Kitchen(self.json['food_labels'], name) for name in self.json['kitchen_labels']]

        indxs = np.zeros(len(self.kitchens), dtype=np.int32)

        for kitchen_data in self.json['kitchen_data']:

            label = kitchen_data['kitchen_lable'] 

            if indxs[label] == 0:
                indxs[label] = 1
                self.kitchens[label].restor_kitchen(kitchen_data['food_data'], kitchen_data['time_stamp'])
                
            
            if np.sum(indxs) == len(self.kitchens):
                break

        print("Indxs: ",indxs)



    def run_classify(self, values):
        """
        Takes in the values and then forms them into the right array shape for the model, runs it through classifier to be displayed and svaed.
        :param values: A list of the food values taken from the form
        :return display_values: a set of the kitchens chosen and the food to be taken there
        :return classification_data: input, raw_output, classification and timestamp to be saved to json
        """

        np_kitchen_data = [] 
        np_classify_data = []

        first =True
        for kitchen in self.kitchens:
            np_kitchen_data.append(kitchen.food_data)
        
        np_kitchen_data = np.array(np_kitchen_data, dtype=np.float32)

        for i, value in enumerate(values):
            this_value = np.zeros(shape=[len(values)])
            this_value[i] = value
            this_value = np.vstack((np_kitchen_data, this_value))
            np_classify_data.append(this_value)
            
        np_classify_data =np.array(np_classify_data, dtype=np.float32)

        print("SHAPE: ", np.shape(np_classify_data))

        raw_classifications = classify(self.model[0] , np_classify_data)

        classifications = raw_classifications.argmax(axis=1)#np.where(raw_classifications > 0.1)

        classification_data =  {}

        classification_data['input'] = np_classify_data
        classification_data['raw_classification'] = raw_classifications
        classification_data['classification'] = classifications
        classification_data['time_stamp'] = datetime.now()

        display_values = {}

        for i, classification in enumerate(classifications):

            if values[i] == 0:
                continue
            kitchen_lable = self.json['kitchen_labels'][classification]
            food_lable = self.json['food_labels'][i]
            display_values[food_lable] = kitchen_lable

        return display_values, classification_data



class Kitchen:

    def __init__(self, food_lables, name):

        self.food_data = [0]*len(food_lables)
        self.name = name
        self.last_modified = datetime.now()
        self.food_lables = food_lables


    def set_foods(self, new_food_data):

        self.food_data = new_food_data
        self.last_modified = datetime.now()

        self.display_val = {}

        for key, val in zip(self.food_lables,self.food_data):
            self.display_val[key]=val

        self.display_val['last_modified']=self.last_modified

        
    def restor_kitchen(self, food_data, last_modified):
        self.food_data = food_data
        self.last_modified = last_modified


