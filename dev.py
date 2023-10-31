from flask import Flask, request, jsonify
from openpyxl import Workbook, load_workbook
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
spreadsheet_name = 'attendance.xlsx'
slack_token = os.getenv('SLACK_TOKEN')

# Use a more scalable data structure for storing timestamps and user data
user_data = {}

# Define fixed dummy timestamps
dummy_checkin_timestamp = '2023-10-27 10:00:00'
dummy_breakstart_timestamp = '2023-10-27 10:30:00'
dummy_breakend_timestamp = '2023-10-27 10:40:00'
dummy_checkout_timestamp = '2023-10-27 10:50:00'

@app.route('/slack/command', methods=['POST'])
def slack_command():
    if request.form.get('token') == 'n1jsHwt68Qo8mpd0p6SCoiqU':
        user_id = request.form.get('user_id')
        user_name, user_id = get_user_info(user_id)

        if user_name is None:
            return jsonify({"text": "User information not found."}), 404

        command = request.form.get('command')

        if command == '/checkin':
            if user_id in user_data:
                return jsonify({"text": "You have already checked in. You can check out after 5 minutes."})

            user_data[user_id] = {'checkin_time': dummy_checkin_timestamp}
            response_text = f"{user_name} ({user_id}) checked in at {dummy_checkin_timestamp}"
            update_attendance(user_id, user_name, 'Check-In', dummy_checkin_timestamp)

        elif command == '/checkout':
            if user_id not in user_data:
                return jsonify({"text": "You must check in before checking out."})

            checkin_time = user_data[user_id]['checkin_time']

            del user_data[user_id]
            break_duration = get_break_duration(user_id)
            working_hours = calculate_working_hours(checkin_time, dummy_checkout_timestamp)
            adjusted_working_hours = working_hours - break_duration
            response_text = f"{user_name} ({user_id}) checked out at {dummy_checkout_timestamp}. Adjusted working hours: {adjusted_working_hours}"
            update_attendance(user_id, user_name, 'Check-Out', dummy_checkout_timestamp, adjusted_working_hours, break_duration)

        elif command == '/breakstart':
            if user_id not in user_data:
                return jsonify({"text": "You must check in before starting your break."})

            if 'break_start_time' in user_data[user_id]:
                return jsonify({"text": "You have already started your break. You can end it with '/breakend'."})

            user_data[user_id]['break_start_time'] = dummy_breakstart_timestamp
            response_text = f"{user_name} ({user_id}) started a break at {dummy_breakstart_timestamp}"
            update_attendance(user_id, user_name, 'Break Start', dummy_breakstart_timestamp)

        elif command == '/breakend':
            if user_id not in user_data:
                return jsonify({"text": "You must check in before ending your break."})

            if 'break_start_time' not in user_data[user_id]:
                return jsonify({"text": "You must start your break with '/breakstart' before ending it."})

            break_start_time = user_data[user_id]['break_start_time']
            del user_data[user_id]['break_start_time']
            response_text = f"{user_name} ({user_id}) ended the break at {dummy_breakend_timestamp}."
            break_duration = calculate_break_duration(break_start_time, dummy_breakend_timestamp)
            update_break_duration(user_id, break_duration)
            update_attendance(user_id, user_name, 'Break End', dummy_breakend_timestamp)

        else:
            response_text = "Invalid command."

        return jsonify({"text": response_text})
    else:
        return jsonify({"text": "Unauthorized request."}), 401

# The rest of your code remains unchanged

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
