from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
slack_token = os.getenv("SLACK_TOKEN")
channel_id = "C063XRS7VKL"  # Replace with the ID of your Slack channel
bot_user_id = "U062M4APVGV"  # Replace with the ID of your Slack bot user

# Dictionary to store user IDs and their status (checked in or checked out)
user_status = {}

# Message timestamp for the user status message
user_status_message_ts = None

@app.route("/slack/command", methods=["POST"])
def slack_command():
    if request.form.get("token") == "n1jsHwt68Qo8mpd0p6SCoiqU":
        user_id = request.form.get("user_id")
        user_name, user_id = get_user_info(user_id)

        if user_name is None:
            return jsonify({"text": "User information not found."}), 404

        command = request.form.get("command")

        if command == "/checkin":
            user_status[user_id] = "online"
            response_text = f"{user_name} ({user_id}) checked in."
        elif command == "/checkout":
            user_status[user_id] = "offline"
            response_text = f"{user_name} ({user_id}) checked out."
        else:
            response_text = "Invalid command."

        update_slack_status(user_id, user_status[user_id])  # Update user status in Slack

        # Create a list of user statuses with online (green dot) and offline (red dot) indicators
        user_status_list = create_user_status_list()

        # Update the user status message in the Slack channel
        update_status_message(user_status_list)

        return jsonify({"text": response_text})
    else:
        return jsonify({"text": "Unauthorized request."}), 401

def get_user_info(user_id):
    headers = {"Authorization": f"Bearer {slack_token}"}
    response = requests.get(f"https://slack.com/api/users.info?user={user_id}", headers=headers)
    data = response.json()

    if response.status_code == 200 and data.get("ok", False):
        user_name = data["user"]["real_name"]
        return user_name, user_id
    else:
        print(f"Error fetching user information: {data}")
        return None, user_id

def update_slack_status(user_id, status):
    headers = {"Authorization": f"Bearer {slack_token}"}
    data = {
        "token": slack_token,
        "user": user_id,
        "presence": status
    }
    response = requests.post("https://slack.com/api/users.setPresence", data=data)

def create_user_status_list():
    user_status_list = []

    for user_id, status in user_status.items():
        user_name, _ = get_user_info(user_id)
        indicator = ":large_green_circle:" if status == "online" else ":red_circle:"  # You can use different icons

        user_status_list.append(f"{user_name} {indicator}")

    return "\n".join(user_status_list)

def update_status_message(text):
    global user_status_message_ts  # Use the message timestamp defined at the top of the script

    if user_status_message_ts:
        headers = {
            "Authorization": f"Bearer {slack_token}",
            "Content-Type": "application/json"
        }
        message = {
            "channel": channel_id,
            "text": text,
            "ts": user_status_message_ts
        }
        response = requests.post("https://slack.com/api/chat.update", headers=headers, json=message)

        if response.status_code == 200:
            return
        else:
            print(f"Error updating message in Slack. Status code: {response.status_code}")
            print(response.text)

    # If the message doesn't exist, create it
    headers = {
        "Authorization": f"Bearer {slack_token}",
        "Content-Type": "application/json"
    }
    message = {
        "channel": channel_id,
        "text": text,
        "as_user": bot_user_id
    }
    response = requests.post("https://slack.com/api/chat.postMessage", headers=headers, json=message)

    if response.status_code == 200:
        data = response.json()
        user_status_message_ts = data.get("ts")  # Store the timestamp of the created message
    else:
        print(f"Error posting message to Slack. Status code: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
