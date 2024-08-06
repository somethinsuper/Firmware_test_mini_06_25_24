import numpy as np
import matplotlib.pyplot as plt

save_single = True
save_avg = True

# File Names
file_array = ['ch1.csv', 'ch2.csv', 'ch3.csv', 'ch4.csv']
dtype = [('id', 'U10'), ('type', 'U2'), ('value1', 'f4'), ('value2', 'f4'), 
         ('value3', 'f4'), ('value4', 'f4'), ('value5', 'f4'), ('value6', 'f4'), 
         ('value7', 'f4'), ('value8', 'f4')]
ptype = [('value1', 'f4'), ('value2', 'f4'), ('value3', 'f4'), ('value4', 'f4'), 
         ('value5', 'f4'), ('value6', 'f4'), 
         ('value7', 'f4'), ('value8', 'f4')]

output_dir = './T4_Graphs/'
out_single = 'Single_T4/'
out_avg = 'Avg_Test/'
data = []

# Load all the data
for file in file_array:
    new_data = np.genfromtxt(file, delimiter=',', skip_header=1, dtype=dtype)
    data.append(new_data)

data = np.concatenate(data)


# Barcode to filter
unique_barcodes = np.unique(data['id'])
unique_tests = np.unique(data['type'])
filtered_data = []
#barcode = 'TE03174'
if (save_single):
    for barcode in unique_barcodes:

        filtered_data = []

        # # Filter the array to get only the rows with the specified barcode
        filtered_data = data[data['id'] == barcode]
        # for code in unique_barcodes:
        #     filtered_data.append(data[data['id'] == code])

        # Print the filtered data
        print("\nFiltered Data:")
        print(filtered_data)
        avg_output = np.zeros(8)


        if filtered_data.size > 0:
            fig, ax = plt.subplots()
            for x in filtered_data:
                temp = x

                # Extract the first two elements into their own variables
                title = temp['id']
                test_num = temp['type']

                # Create a new array excluding the first two elements
                temp_values = [temp['value1'], temp['value2'], temp['value3'], temp['value4'], 
                            temp['value5'], temp['value6'], temp['value7'], temp['value8']]

                # Print the results
                print("\nTitle:", title)
                print("Test Number:", test_num)
                print("Remaining Values:", temp_values)
                
                # Plot the remaining values
                ax.plot(temp_values)
                ax.set_xlabel('Test Number')
                ax.set_ylabel('Voltage Output')
                ax.set_title(f"Data for {title}")
                avg_output = np.vstack((avg_output, temp_values)) 
            avg_output = avg_output[1:, :]
            avg_output = np.mean(avg_output, axis=0)
            ax.plot(avg_output)
            ax.legend(['Test 1', 'Test 2', "Test 3", 'Test 4', 'Average']) 
            fig.savefig(f'{output_dir}{out_single}{title}.png')
            #plt.show()
        else:
            print(f"No data found for barcode: {barcode}")
            
if (save_avg):
    output_final = np.zeros(8)
    for test in unique_tests:
        filtered_data = []
        filtered_data = data[data['type'] == test]
        #filtered_data = [arr[2:] for arr in filtered_data]
        # print("\nFiltered Data:")
        # print(filtered_data)
        fig, ax = plt.subplots()
        if filtered_data.size > 0:
            output = np.zeros(8)
            for x in filtered_data:
                temp = x

                # Extract the first two elements into their own variables
                title = temp['id']
                test_num = temp['type']

                # Create a new array excluding the first two elements
                temp_values = np.array([temp['value1'], temp['value2'], temp['value3'], temp['value4'], 
                            temp['value5'], temp['value6'], temp['value7'], temp['value8']])
                
                #print(temp_values)
                # temp_values = np.array(temp_values)
                output = np.vstack((output, temp_values)) 
            output = np.mean(output, axis=0)
            print(output)  
            ax.plot(output)
            ax.set_xlabel('Test Number')
            ax.set_ylabel('Voltage Output')
            ax.set_title(f"Data for {test_num}")
        output_final = np.vstack((output_final, output)) 
        fig.savefig(f'{output_dir}{out_avg}{test}.png')
    output_final = output_final[1:, :]
    ax.clear()
    
    for line in output_final:
        ax.plot(line)
        # print("Output Final")
        # print(output_final)
    ax.legend(['Test 1', 'Test 2', "Test 3", 'Test 4']) 
    ax.set_xlabel('Test Number')
    ax.set_ylabel('Voltage Output')
    ax.set_title(f"Data for all Values")
    fig.savefig(f'{output_dir}{out_avg}full.png')