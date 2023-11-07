import datetime
import random
from openpyxl import Workbook

# Create an Excel workbook
workbook = Workbook()
sheet = workbook.active
sheet.append(["Action", "Date", "Time"])

# Define the actions and their corresponding time intervals
actions = ["Check-In", "Break Start", "Break End", "Break Start", "Break End", "Check-Out"]
time_intervals = {
    "Check-In": (0, 2),
    "Break Start": (4, 10),
    "Break End": (11, 16),
    "Check-Out": (18, 23)
}

# Generate data for the past seven days
current_date = datetime.datetime.now()
data = []  # List to store the data entries

for _ in range(7):
    day_data = []  # List to store data for a single day
    for action in actions:
        start_hour, end_hour = time_intervals[action]
        action_time = current_date.replace(
            hour=random.randint(start_hour, end_hour),
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        )
        day_data.append([action, action_time.strftime('%Y-%m-%d'), action_time.strftime('%H:%M:%S')])

    data.append(day_data)

    # Move to the previous day
    current_date -= datetime.timedelta(days=1)

# Reverse the order of data entries
data.reverse()

# Append the reversed data to the sheet
for day_data in data:
    for entry in day_data:
        sheet.append(entry)

# Save the Excel file
workbook.save("dummy_data_reverse_date.xlsx")
