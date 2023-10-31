from flask import Flask, request, jsonify
from openpyxl import Workbook, load_workbook
from datetime import datetime, timedelta
import os
import requests
from dotenv import load_dotenv
from openpyxl.styles import PatternFill

load_dotenv()

app = Flask(__name__)
spreadsheet_name = "attendance.xlsx"
slack_token = os.getenv("SLACK_TOKEN")  # Use environment variable for the Slack token

checkin_timestamps = {}
checkout_timestamps = {}
break_start_timestamps = {}
break_end_timestamps = {}


@app.route("/slack/command", methods=["POST"])
def slack_command():
    if request.form.get("token") == "n1jsHwt68Qo8mpd0p6SCoiqU":
        user_id = request.form.get("user_id")
        user_name, user_id = get_user_info(
            user_id
        )  # Update this function to return both user_name and user_id

        if user_name is None:
            return jsonify({"text": "User information not found."}), 404

        command = request.form.get("command")

        if command == "/checkin":
            if user_id in checkin_timestamps:
                return jsonify(
                    {
                        "text": "You have already checked in. You can check out after 5 minutes."
                    }
                )

            timestamp = datetime.now()
            checkin_timestamps[user_id] = timestamp
            response_text = f"{user_name} ({user_id}) checked in at {timestamp}"
            update_attendance(user_id, user_name, "Check-In", timestamp)
        elif command == "/checkout":
            timestamp = datetime.now()
            if user_id not in checkin_timestamps:
                return jsonify({"text": "You must check in before checking out."})

            checkin_time = checkin_timestamps[user_id]
            if timestamp - checkin_time < timedelta(minutes=5):
                return jsonify({"text": "You can only check out after 5 minutes of checking in."})

            del checkin_timestamps[user_id]
            checkout_timestamps[user_id] = timestamp
            working_hours = calculate_working_hours(checkin_time, timestamp)
            response_text = f"{user_name} ({user_id}) checked out at {timestamp}. Working hours: {working_hours}"
            update_attendance(user_id, user_name, "Check-Out", timestamp, working_hours)
        elif command == "/breakstart":
            if user_id not in checkin_timestamps:
                return jsonify(
                    {"text": "You must check in before starting your break."}
                )

            if user_id in break_start_timestamps:
                return jsonify(
                    {
                        "text": "You have already started your break. You can end it with '/breakend'."
                    }
                )

            timestamp = datetime.now()
            break_start_timestamps[user_id] = timestamp
            response_text = f"{user_name} ({user_id}) started a break at {timestamp}"
            update_attendance(user_id, user_name, "Break Start", timestamp)
        elif command == "/breakend":
            timestamp = datetime.now()
            if user_id not in checkin_timestamps:
                return jsonify({"text": "You must check in before ending your break."})

            if user_id not in break_start_timestamps:
                return jsonify(
                    {
                        "text": "You must start your break with '/breakstart' before ending it."
                    }
                )

            break_start_time = break_start_timestamps[user_id]
            break_end_time = timestamp
            break_duration = calculate_break_duration(break_start_time, break_end_time)
            del break_start_timestamps[user_id]
            response_text = f"{user_name} ({user_id}) ended the break at {timestamp}. Break duration: {break_duration}"
            update_attendance(
                user_id, user_name, "Break End", timestamp, break_duration
            )
        else:
            response_text = "Invalid command."

        return jsonify({"text": response_text})
    else:
        return jsonify({"text": "Unauthorized request."}), 401


def get_user_info(user_id):
    headers = {"Authorization": f"Bearer {slack_token}"}
    response = requests.get(
        f"https://slack.com/api/users.info?user={user_id}", headers=headers
    )
    data = response.json()

    if response.status_code == 200 and data.get("ok", False):
        user_name = data["user"]["real_name"]
        return user_name, user_id
    else:
        print(f"Error fetching user information: {data}")
        return None, user_id


def update_attendance(user_id, user_name, action, timestamp, working_hours=None):
    try:
        # Load the existing Excel file or create a new one if it doesn't exist
        try:
            workbook = load_workbook(spreadsheet_name)
        except FileNotFoundError:
            workbook = Workbook()

        # Create a new sheet for the user if it doesn't exist, or get the existing sheet
        if user_name not in workbook.sheetnames:
            worksheet = workbook.create_sheet(title=user_name)
            worksheet.append(["Action", "Date", "Time", "Working Hours"])
        else:
            worksheet = workbook[user_name]

        # Extract the date and time components from the timestamp
        date = timestamp.date()
        time = timestamp.time()

        # Append a new row with the attendance data, including working hours for check-in and check-out, and break duration for break start and break end
        if action == "Check-In" or action == "Check-Out":
            worksheet.append([action, date, time, working_hours])
        else:
            worksheet.append([action, date, time, None])

        # Apply red fill to the row if the user checked in but didn't check out on the same date
        if action == "Check-In":
            check_in_date = date
            check_out_date = None
            for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row, max_col=2, min_col=2):
                if row[0].value == "Check-Out":
                    check_out_date = row[1].value
                    break
            if check_out_date is None or check_in_date != check_out_date:
                red_fill = PatternFill(start_color="FFFF0000", end_color="FFFF0000", fill_type="solid")
                for cell in worksheet[-1]:
                    cell.fill = red_fill

        # Save the updated Excel file
        workbook.save(spreadsheet_name)

    except Exception as e:
        print(f"Error updating attendance: {str(e)}")


def calculate_working_hours(checkin_time, checkout_time):
    working_hours = checkout_time - checkin_time
    return working_hours


def calculate_break_duration(break_start_time, break_end_time):
    break_duration = break_end_time - break_start_time
    return break_duration


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
