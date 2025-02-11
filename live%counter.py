import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
import subprocess
import time
from matplotlib.animation import FuncAnimation

# Function to get CPU usage data from `top` command
def get_top_output():
    # Run the `top` command and collect the output
    result = subprocess.run(['top', '-b', '-n', '1'], capture_output=True, text=True)
    lines = result.stdout.splitlines()
    
    # Extracting data after header (assuming the columns are fixed)
    data = []
    start_index = 0
    for i, line in enumerate(lines):
        if line.startswith("PID"):  # Detect the start of the process table
            start_index = i + 1
            break

    # Process each line of data after the PID line
    for line in lines[start_index:]:
        columns = line.split()
        if len(columns) > 8:  # Check for sufficient columns
            pid, user, cpu = columns[0], columns[1], columns[8]  # Columns for PID, USER, %CPU
            data.append([user, cpu])

    # Convert the data to a DataFrame
    df = pd.DataFrame(data, columns=['USER', '%CPU'])
    df['%CPU'] = pd.to_numeric(df['%CPU'], errors='coerce')  # Convert %CPU column to numeric
    
    # Filter out invalid or negative values
    df = df[df['%CPU'] >= 0]

    # DEBUG: Print out any invalid values
    if df.empty:
        print("No valid CPU usage data found.")
    else:
        print("Valid %CPU data:\n", df)
    
    return df

# Function to update the pie chart
def update_pie_chart(i):
    # Get the latest top output data
    df = get_top_output()

    if df.empty:
        print("No valid data to plot.")
        return

    # Group the data by 'USER' and sum the '%CPU' usage for each user
    cpu_usage_by_user = df.groupby('USER')['%CPU'].sum().reset_index()

    # Sort the result by %CPU usage in descending order
    cpu_usage_by_user_sorted = cpu_usage_by_user.sort_values(by='%CPU', ascending=False)

    # Calculate total %CPU usage
    total_cpu_usage = cpu_usage_by_user_sorted['%CPU'].sum()

    # Assume a maximum %CPU usage of 100 (representing full %CPU capacity)
    max_cpu_usage = 100

    # Calculate unused %CPU
    unused_cpu = max_cpu_usage - total_cpu_usage

   
    if unused_cpu < 0:
        print(f"Invalid unused CPU value: {unused_cpu}. Resetting to 0.")
        unused_cpu = 0

    
    sizes = list(cpu_usage_by_user_sorted['%CPU']) + [unused_cpu]
    labels = list(cpu_usage_by_user_sorted['USER']) + ['Unused %CPU']

   
    print("Sizes for pie chart:", sizes)

   
    if any(size < 0 for size in sizes):
        print("Error: Negative values found in sizes")
        return

  
    plt.clf()

    colors = plt.cm.viridis(np.linspace(0, 1, len(sizes)))

    plt.pie(sizes, colors=colors, autopct='%1.1f%%', startangle=140)

   
    plt.legend(labels, loc="best", bbox_to_anchor=(1, 0.5))

   
    plt.title("%CPU Usage by User and Unused %CPU")

fig = plt.figure(figsize=(7, 7))

ani = FuncAnimation(fig, update_pie_chart, interval=1000)


plt.tight_layout()
plt.show()
