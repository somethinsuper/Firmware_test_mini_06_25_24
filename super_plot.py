import numpy as np
import matplotlib.pyplot as plt
from cvs_utils import delete_files_in_directory

""" 
File to create all of the Python Plots
By Holland Sersen
"""

# Create Default Constant Global Varibles. 
NUM_FLOAT_COLUMNS = 72
NUM_STRING_COLUMNS = 2

# Set which graph types to save
save_single = True
save_avg = True



# Types for the files TODO: load one file
#file_array = ['ch1.csv', 'ch2.csv', 'ch3.csv', 'ch4.csv']
file_array = ['ref.csv']
dtype = [('id', 'U10'), ('type', 'U2')] + [('float_col'+str(i), 'f4') for i in range(NUM_FLOAT_COLUMNS)]
ptype = [('float_col'+str(i), 'f4') for i in range(NUM_FLOAT_COLUMNS)]

# dtype = [('id', 'U10'), ('type', 'U2'), ('value1', 'f4'), ('value2', 'f4'), 
#          ('value3', 'f4'), ('value4', 'f4'), ('value5', 'f4'), ('value6', 'f4'), 
#          ('value7', 'f4'), ('value8', 'f4')]
# ptype = [('value1', 'f4'), ('value2', 'f4'), ('value3', 'f4'), ('value4', 'f4'), 
#          ('value5', 'f4'), ('value6', 'f4'), 
#          ('value7', 'f4'), ('value8', 'f4')]

# Set output Dirs
output_dir = './T4_Graphs/'
out_single = 'Single_T4/'
out_avg = 'Avg_Test/'
out_single_full = output_dir + out_single
out_avg_full = output_dir + out_single

delete_files_in_directory(out_single_full)
delete_files_in_directory(out_avg_full)

# Load all the data
data = []
for file in file_array:
    new_data = np.genfromtxt(file, delimiter=',', skip_header=1, dtype=dtype)
    data.append(new_data)

# Turn Data into a 1D Array
data = np.concatenate(data)

# Barcode to filter
unique_barcodes = np.unique(data['id'])
unique_tests = np.unique(data['type'])
filtered_data = []


# Code for Each T4BLA plot
if (save_single):
    for barcode in unique_barcodes:

        # Filter the array to get only the rows with the specified barcode
        filtered_data = []
        filtered_data = data[data['id'] == barcode]

        # Print the filtered data
        print("\nFiltered Data:")
        print(filtered_data)
        
        # Init Array for the Average Values
        avg_output = np.zeros(NUM_FLOAT_COLUMNS)

        # If there is data then plot it
        if filtered_data.size > 0:
            
            # Create fig and plot obj
            fig, ax = plt.subplots()
            
            # Load each Array as x
            for x in filtered_data:
                temp = x

                # Extract the first two elements into their own variables
                title: str = temp['id']
                test_num: str = temp['type']

                # Create a new array excluding the first two elements
                """NOTE: Chat says that you can use slices to do this. However since it is a tuple 
                it counts as a 0D array. Meaning that you cannot call it like a normal array"""
                temp_values = np.array([temp['float_col'+str(i)] for i in range(NUM_FLOAT_COLUMNS)])

                # Print the results
                print("\nTitle:", title)
                print("Test Number:", test_num)
                print("Remaining Values:", temp_values)
                
                # Plot the remaining values
                ax.plot(temp_values)
                ax.set_xlabel('Test Number')
                ax.set_ylabel('Voltage Output')
                ax.set_title(f"Data for {title}")
                
                # Stack Temp values with the avg_output
                avg_output = np.vstack((avg_output, temp_values)) 
                
            # Remove the first colum of zeros in avg_output and get the mean of all Colums
            avg_output = avg_output[1:, :]
            avg_output = np.mean(avg_output, axis=0)
            
            # Plot the Avg_output and save it to file
            ax.plot(avg_output)
            ax.legend(['Test 1', 'Test 2', "Test 3", 'Test 4', 'Average']) 
            fig.savefig(f'{output_dir}{out_single}{title}.png')
            
        # If there is no data then throw error TODO: change to try except
        else:
            print(f"No data found for barcode: {barcode}")
        
# Code for Each Channel Plot
if (save_avg):
    
    # Init Array for the Average Values
    output_final = np.zeros(NUM_FLOAT_COLUMNS)
    
    # Load each Array as x
    for test in unique_tests:
        
        # Filter the array to get only the rows with the specified barcode
        filtered_data = []
        filtered_data = data[data['type'] == test]
        
        # Create fig and plot obj. Do this before the loop so you can add the averages together
        fig, ax = plt.subplots()
        if filtered_data.size > 0:
            
            # Init Output Array
            output = np.zeros(NUM_FLOAT_COLUMNS)
            
            # If there is data then plot it
            for x in filtered_data:
                temp = x

                # Extract the first two elements into their own variables
                title = temp['id']
                test_num = temp['type']

                # Create a new array excluding the first two elements
                temp_values = np.array([temp['float_col'+str(i)] for i in range(NUM_FLOAT_COLUMNS)])
                
                # Stack Temp values with the output
                output = np.vstack((output, temp_values)) 
            
            # Get the Average of each colum of the Matrix
            output = np.mean(output, axis=0)
            print(output)
            
            # Plot Output  
            ax.plot(output)
            ax.set_xlabel('Test Number')
            ax.set_ylabel('Voltage Output')
            ax.set_title(f"Data for {test_num}")
            
        # Take the Averaged Output of each Channel and stack it in output_final
        output_final = np.vstack((output_final, output)) 
        
        # Save the Figure
        fig.savefig(f'{output_dir}{out_avg}{test}.png')
        
    # Remove Zeros from output_final and restart the figure
    output_final = output_final[1:, :]
    ax.clear()
    
    # For each row of output final plot it
    for line in output_final:
        ax.plot(line)
    
    # Plot and save the file
    ax.legend(['Test 1', 'Test 2', "Test 3", 'Test 4']) 
    ax.set_xlabel('Test Number')
    ax.set_ylabel('Voltage Output')
    ax.set_title(f"Data for all Values")
    fig.savefig(f'{output_dir}{out_avg}full.png')