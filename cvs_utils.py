import numpy as np
import os


def append_to_csv(filename: str, new_data, title: str, channel: str):
    if (title != 'EEEEEEE'):
        # Read the existing data
        old_data = read_csv(filename)
        old_data = old_data.astype(str)
        #old_data = old_data.reshape(1, -1)
        #new_data = new_data.flatten()
        #new_data = new_data.reshape(1, -1)
        new_data = new_data.astype(str)
        
        print(channel)
        print(title)
        
        new_data = np.insert(new_data, 0, channel)
        new_data = np.insert(new_data, 0, title)
        #print(new_data)
        
        #print(new_data)
        
        # If the old data is empty, create the header
        if old_data.size == 0:
            combined_data = new_data
        else:
            # Combine old and new data
            combined_data = np.vstack((old_data, new_data))
        
        # Save the combined data to the CSV file
        np.savetxt(filename, combined_data, delimiter=',', fmt='%s')
    
# Function to read existing data
def read_csv(filename):
    if os.path.exists(filename):
        # Read the existing data
        return np.genfromtxt(filename, delimiter=',', dtype=str)
    else:
        # Return an empty array if the file does not exist
        return np.array([])