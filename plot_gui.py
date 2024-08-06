import kivy
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.matplotlib import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
from kivy.properties import StringProperty
from cvs_utils import append_to_csv
import numpy as np

#TODO: Make into its own File / Utils
class MyList(list):
    def last_index(self):
        return len(self)-1
# Class creates graph and updates it on the screen 
class Plotter(BoxLayout):
    channel_barcode = ['', '', '', '']
    file_array = ['ch1.csv', 'ch2.csv', 'ch3.csv', 'ch4.csv']
    
    # Event Handler that on changeupdates graph
    pair = StringProperty('')
    
    # 4.56 4.56 3.1  2.42 1.81 1.36 1.11 0.92
    
    #default_list: int = [0]
    plot_x = np.zeros((4, 1))
    temp_array = np.zeros((4,1))
    current_index = 0

    # On class init, create canvas and intial graph
    def __init__(self, application_gui, hint: float, **kwargs):
        
        # Set Box Layout Values
        super(Plotter, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = hint
        
        # Create Default array which data will reside
        self.data: dict[str , int] = {'C1': 0, 'C2': 1, 'C3': 2, 'C4': 3}
        
        # Get Values from Array
        channel = list(self.data.keys())
        values = list(self.data.values())
        
        # Create fig
        fig, self.ax = plt.subplots()
        
        
        # Create Canvas and add it to the GUI
        self.new_canvas = FigureCanvasKivyAgg(figure=fig)
        
        # Redraw the plot
        self.delete_graph()
        
        self.add_widget(self.new_canvas)

    # Function used in event callback to update the plot
    def update_plot(self, pair: str):
        
        # Set self.pair to be equal to pair
        self.pair = pair
        
        # Get the new key value pair and add it to existing Dict
        key, value = self.pair.split(':')
        temp_ch: int = self.data.get(key)
#
        value = float(value)
        
        #print(value)
        # self.data.append(0)
        # Check for a Command that resets graph on Input
        if(key == 'A1' and value == 1):
            self.delete_graph()
            #self.current_index
        # Command to Tell python when a new value is added
        elif(key == 'A1' and value == 0):
            #arr.tofile('data2.csv', sep = ',')
            for i in range(0, 4):
                print(self.channel_barcode[i])
                append_to_csv(self.file_array[i], self.plot_x[i, :], self.channel_barcode[i], ("T" + str(i)))
        elif (key == 'B1' and value == 1):
            self.ax.clear()
        elif (key == 'B1' and value == 0):
            if (self.first):
                self.plot_x = self.temp_array
                self.first = False
                #print(self.plot_x)
            else:
                self.plot_x = np.hstack((self.plot_x, self.temp_array))
                #print(self.plot_x)
            self.__redraw()
        elif(temp_ch != None):
            self.temp_array[temp_ch, 0] = value
            #self.plot_x[self.data[key], self.current_index] = value
        # print(self.data[key].last_index)
        # print(self.data[key])
        
        # Get Values from Dict
        #channel, values = self.__parse_dict(self.data)
        
        # If not Updat the plot
        # self.__redraw(self.data, key)
        
    # Function to redraw the default graph and reduce Boilerplate
    def __redraw(self):
        self.ax.plot(self.plot_x[0, :], label ="Ch 1")
        self.ax.plot(self.plot_x[1, :], label ="Ch 2")
        self.ax.plot(self.plot_x[2, :], label ="Ch 3")
        self.ax.plot(self.plot_x[3, :], label ="Ch 4")
        #self.ax.plot(value)
        #plt.bar(channel, value, color ='maroon', width = 0.4)
        
        #Style Graph
        plt.legend() 
        plt.ylim(0, 5)
        # plt.xlabel("Courses offered")
        # plt.ylabel("No. of students enrolled")
        # plt.title("Students enrolled in different courses")
        self.new_canvas.draw()
        
    # Resets the graph so that a new one can be made
    def delete_graph(self):
        self.data = {'C1': 0, 'C2': 1, 'C3': 2, 'C4': 3}
        self.ax.plot(self.data.get("C1"), label ="Ch 1")
        self.ax.plot(self.data.get("C2"), label ="Ch 2")
        self.ax.plot(self.data.get("C3"), label ="Ch 3")
        self.ax.plot(self.data.get("C4"), label ="Ch 4")
        self.first = True
        self.new_canvas.draw()
        
        
    def update_barcode(self, channel: int, value: str):
        #print(value)
        self.channel_barcode[channel] = value
        
    # Returns a tuple from dict
    def __parse_dict(self, input: dict[str : list[float]]):
        channel = list(input.keys())
        values = input.values()
        return channel, values
        