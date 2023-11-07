import requests
import time

# Replace with your Flask application's URL
BASE_URL = 'https://6349-2401-4900-1f3e-1532-216d-24b3-4bca-37f4.ngrok-free.app'

# Replace with your actual user ID
USER_ID = 'U03KHL4QCCA'

# Replace with your Slack token
SLACK_TOKEN = 'n1jsHwt68Qo8mpd0p6SCoiqU'

# Function to send Slack command
def send_slack_command(command):
    url = f'{BASE_URL}/slack/command'
    data = {
        'token': SLACK_TOKEN,
        'user_id': USER_ID,
        'command': command
    }
    response = requests.post(url, data=data)
    return response

# Function to display a simple progress bar
def progress_bar(duration):
    for i in range(duration):
        time.sleep(1)
        print(f"[{'#' * i}{' ' * (duration - i - 1)}] {i+1}/{duration}", end='\r')

# Test /checkin command
checkin_response = send_slack_command('/checkin')
print("/checkin Response:", checkin_response.text)
# progress_bar(40)  # Sleep for 30 seconds

# Test /breakstart command
breakstart_response = send_slack_command('/breakstart')
print("/breakstart Response:", breakstart_response.text)
# progress_bar(10)  # Sleep for 30 seconds

# Test /breakend command
breakend_response = send_slack_command('/breakend')
print("/breakend Response:", breakend_response.text)
# progress_bar(5)  # Sleep for 30 seconds

# Test /breakstart command
breakstart_response = send_slack_command('/breakstart')
print("/breakstart Response:", breakstart_response.text)
# progress_bar(10)  # Sleep for 30 seconds

# Test /breakend command
breakend_response = send_slack_command('/breakend')
print("/breakend Response:", breakend_response.text)
# progress_bar(30)  # Sleep for 30 seconds

# Test /checkout command
checkout_response = send_slack_command('/checkout')
print("/checkout Response:", checkout_response.text)


# Print a newline to clear the progress bar
print()
