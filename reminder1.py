import streamlit as st
import pandas as pd
import datetime
import time
import random
import schedule
import threading
import requests
from datetime import datetime, timedelta
import pytz

# Set page config
st.set_page_config(
    page_title="Mom-to-Be Reminder App",
    page_icon="👶",
    layout="wide"
)

# App title and description
st.title("Mom-to-Be Reminder App 🤰")
st.markdown("""
This app allows you to schedule friendly medication reminders for expectant mothers. 
The app generates supportive and encouraging messages via Telegram.
""")

# Set timezone to IST
ist = pytz.timezone('Asia/Kolkata')
system_tz = datetime.now().astimezone().tzinfo

# Initialize session state variables if they don't exist
if 'reminders' not in st.session_state:
    st.session_state.reminders = []
if 'scheduled_jobs' not in st.session_state:
    st.session_state.scheduled_jobs = {}

# Sidebar for Telegram Bot configuration
st.sidebar.title("Telegram Bot Configuration")
st.sidebar.info("You need to create a Telegram bot to use this app. Visit @BotFather on Telegram to create one.")
telegram_bot_token = st.sidebar.text_input("Telegram Bot Token", type="password")

# Store Telegram credentials in session state
if not st.session_state.get('telegram_configured'):
    if telegram_bot_token:
        st.session_state['telegram_bot_token'] = telegram_bot_token
        st.session_state['telegram_configured'] = True
        st.sidebar.success("Telegram bot configured!")
    else:
        st.sidebar.warning("Please provide your Telegram bot token to use the app.")

# Enhanced Medication message templates with more variety
medication_message_templates = [
    "Hello beautiful! 💕 It's time for your daily prenatal vitamins. These little nutrients are doing big work helping your baby grow strong and healthy!",
    
    "Sending you warm thoughts today! ✨ Just a friendly reminder about your prenatal vitamins/medication. Taking care of yourself means taking care of your little miracle too!",
    
    "Hope your day is going wonderfully! 💖 This is your gentle reminder to take your medication - a small act with a big impact on your baby's development.",
    
    "Good day, mom-to-be! 💫 Time for your prenatal vitamins - they're helping to build your baby's bones, brain, and body systems right now!",
    
    "Hello lovely! 🌷 Just a caring reminder that your medication/vitamins are waiting for you. Your commitment to your health supports your little one's growth journey!",
    
    "Thinking of you both today! 👼 Remember those prenatal vitamins that help prevent neural tube defects and support healthy development? It's time for them!",
    
    "Sending a gentle nudge about your medication! 🌟 These important nutrients are supporting your baby's development right now in ways you can't see but will definitely benefit from!",
    
    "Hi there beautiful mom-to-be! 💝 Your medication reminder has arrived - these vitamins are particularly important during pregnancy when your nutritional needs increase.",
    
    "A friendly reminder with love! 💊 Your prenatal vitamins are essential partners on this incredible journey - they're helping your baby develop properly every day!",
    
    "Hello sunshine! ☀️ Don't forget your medication today - it's providing important nutrients like folic acid, iron, calcium, and DHA that your growing baby needs!",
    
    "Gentle reminder time! 🕒 Your vitamins are waiting - they're supporting your immune system while you work on the amazing job of growing your little miracle!",
    
    "Thinking of you and your precious cargo! 🚢 Time to take your prenatal vitamins - they're helping prevent anemia and other complications while supporting healthy growth!",
    
    "Hello wonderful! 🌈 This is your medication reminder - consistent vitamin intake helps ensure your baby gets all the nutrients needed for optimal development!",
    
    "Special delivery! 📬 Your friendly reminder to take your prenatal medication - it's providing essential nutrients that might be hard to get enough of from diet alone!",
    
    "Sending care your way! 💗 Your medication reminder has arrived - these supplements are especially important when growing your precious little one!"
]

# Function to generate a cordial message
def generate_cordial_message(reminder_text, sender_name="", receiver_name=""):
    base_message = random.choice(medication_message_templates)
    
    message_parts = []
    
    # Add personalized greeting if receiver name is provided
    if receiver_name:
        message_parts.append(f"Dear {receiver_name},\n\n")
    
    # Add the main message
    message_parts.append(base_message)
    
    # Add the reminder text if provided
    if reminder_text:
        message_parts.append(f"\n\n📝 {reminder_text}")
    
    # Add sender signature if provided
    if sender_name:
        message_parts.append(f"\n\nWarmly,\n{sender_name}")
    
    return "".join(message_parts)

# Function to send message via Telegram
def send_telegram_message(chat_id, message):
    try:
        # Check if Telegram is configured
        if not st.session_state.get('telegram_configured'):
            return False, "Telegram bot token not configured. Please provide it in the sidebar."
        
        # Telegram Bot API endpoint for sending messages
        url = f"https://api.telegram.org/bot{st.session_state['telegram_bot_token']}/sendMessage"
        
        # Parameters for the API call
        params = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'  # Allow some HTML formatting
        }
        
        # Send the message
        response = requests.post(url, params=params)
        response_json = response.json()
        
        if response.status_code == 200 and response_json.get('ok'):
            return True, "Message sent successfully!"
        else:
            error_description = response_json.get('description', 'Unknown error')
            return False, f"Failed to send message: {error_description}"
    
    except Exception as e:
        return False, f"Error sending message: {str(e)}"

# Function to verify a Telegram chat ID
def verify_telegram_chat_id(chat_id):
    try:
        # Check if Telegram is configured
        if not st.session_state.get('telegram_configured'):
            return False, "Telegram bot token not configured. Please provide it in the sidebar."
        
        # Try to send a test message to the chat ID
        url = f"https://api.telegram.org/bot{st.session_state['telegram_bot_token']}/getChat"
        params = {'chat_id': chat_id}
        
        response = requests.post(url, params=params)
        response_json = response.json()
        
        if response.status_code == 200 and response_json.get('ok'):
            user_data = response_json.get('result', {})
            return True, user_data
        else:
            error_description = response_json.get('description', 'Unknown error')
            return False, error_description
    
    except Exception as e:
        return False, str(e)

# Function to execute a scheduled reminder
def execute_reminder(reminder_id):
    reminder = next((r for r in st.session_state.reminders if r['id'] == reminder_id), None)
    
    if reminder and reminder['active']:
        # Generate the message
        message = generate_cordial_message(
            reminder.get('text', ''),
            reminder.get('sender_name', ''),
            reminder.get('receiver_name', '')
        )
        
        # Send the message
        success, _ = send_telegram_message(reminder['receiver_chat_id'], message)
        
        # Log the execution (in a real app, you'd want to store this)
        now = datetime.now(ist)
        print(f"Reminder {reminder_id} executed at {now.strftime('%Y-%m-%d %H:%M:%S')} IST - Success: {success}")

# Function to delete a reminder
def delete_reminder(reminder_id):
    # Find the reminder in the list
    reminder_index = next((i for i, r in enumerate(st.session_state.reminders) if r['id'] == reminder_id), None)
    
    if reminder_index is not None:
        # Cancel the scheduled job if it exists
        if reminder_id in st.session_state.scheduled_jobs:
            schedule.cancel_job(st.session_state.scheduled_jobs[reminder_id])
            del st.session_state.scheduled_jobs[reminder_id]
        
        # Remove the reminder from the list
        st.session_state.reminders.pop(reminder_index)
        return True
    
    return False

# Function to convert IST time to system time for scheduling
def convert_ist_to_system_time(ist_time):
    # Create a datetime with today's date and the given IST time
    ist_naive = datetime.combine(datetime.now().date(), ist_time)
    
    # Localize to IST
    ist_dt = ist.localize(ist_naive)
    
    # Convert to system timezone
    system_dt = ist_dt.astimezone(system_tz)
    
    # Return just the time portion
    return system_dt.time()

# Function for the scheduler to run
def run_scheduled_jobs():
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

# Start the scheduler in a separate thread
if 'scheduler_thread' not in st.session_state:
    st.session_state.scheduler_thread = threading.Thread(target=run_scheduled_jobs, daemon=True)
    st.session_state.scheduler_thread.start()

# Create two columns for sender and receiver information
col1, col2 = st.columns(2)

with col1:
    st.subheader("Sender Information")
    sender_name = st.text_input("Your Name", key="sender_name")

with col2:
    st.subheader("Receiver Information")
    receiver_name = st.text_input("Mom-to-Be Name", key="receiver_name")
    receiver_chat_id = st.text_input("Telegram Chat ID", 
                                     help="The recipient must start a conversation with your bot first. You can find their Chat ID using @userinfobot on Telegram.")
    due_date = st.date_input("Expected Due Date", min_value=datetime.now(ist).date())

    # Verify Chat ID button
    if st.button("Verify Chat ID"):
        if not st.session_state.get('telegram_configured'):
            st.error("Please configure your Telegram bot token in the sidebar first.")
        elif not receiver_chat_id:
            st.error("Please enter a Chat ID to verify.")
        else:
            with st.spinner("Verifying Chat ID..."):
                success, result = verify_telegram_chat_id(receiver_chat_id)
                if success:
                    username = result.get('username', 'Not available')
                    first_name = result.get('first_name', 'Not available')
                    st.success(f"Valid Chat ID! User: {first_name} (@{username})")
                else:
                    st.error(f"Invalid Chat ID: {result}")

# Display IST time note
st.info(f"Current IST time: {datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')}. All reminders will be scheduled in IST.")

# Create reminder form
st.subheader("Add a New Medication Reminder")

with st.form(key="reminder_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        reminder_text = st.text_area("Additional Medication Details (optional)", 
                                     help="Specify medication name, dosage, or special instructions if needed", 
                                     height=100)
    
    with col2:
        frequency = st.selectbox(
            "Frequency",
            ["Daily", "Weekly", "Monthly", "One-time"]
        )
        
        if frequency == "Daily":
            # Use IST as default time
            default_time = datetime.now(ist).time()
            selected_time = st.time_input("Time of Day (IST)")
        elif frequency == "Weekly":
            day_of_week = st.selectbox(
                "Day of Week",
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            )
            # Use IST as default time
            default_time = datetime.now(ist).time()
            selected_time = st.time_input("Time of Day (IST)")
        elif frequency == "Monthly":
            day_of_month = st.number_input("Day of Month", min_value=1, max_value=31, value=1)
            # Use IST as default time
            default_time = datetime.now(ist).time()
            selected_time = st.time_input("Time of Day (IST)")
        else:  # One-time
            date = st.date_input("Date", min_value=datetime.now(ist).date())
            # Use IST as default time
            default_time = datetime.now(ist).time()
            selected_time = st.time_input("Time (IST)")
    
    submit_button = st.form_submit_button(label="Add Medication Reminder")

# Process the form submission
if submit_button:
    if not receiver_chat_id:
        st.error("Please enter the receiver's Telegram Chat ID.")
    elif not st.session_state.get('telegram_configured'):
        st.error("Please configure your Telegram bot token in the sidebar first.")
    else:
        # Create a unique reminder ID
        reminder_id = len(st.session_state.reminders)
        
        # Convert the selected IST time to system timezone for scheduling
        system_time = convert_ist_to_system_time(selected_time)
        time_str = system_time.strftime('%H:%M')
        
        # Format the schedule information for display using the IST time
        if frequency == "Daily":
            schedule_display = f"Daily at {selected_time.strftime('%I:%M %p')} IST"
            schedule_key = f"daily-{selected_time.strftime('%H:%M')}"
            
            # Schedule the job using the system time
            job = schedule.every().day.at(time_str).do(execute_reminder, reminder_id)
            st.session_state.scheduled_jobs[reminder_id] = job
            
        elif frequency == "Weekly":
            schedule_display = f"Every {day_of_week} at {selected_time.strftime('%I:%M %p')} IST"
            schedule_key = f"weekly-{day_of_week}-{selected_time.strftime('%H:%M')}"
            
            # Schedule the job using the system time
            if day_of_week == "Monday":
                job = schedule.every().monday.at(time_str).do(execute_reminder, reminder_id)
            elif day_of_week == "Tuesday":
                job = schedule.every().tuesday.at(time_str).do(execute_reminder, reminder_id)
            elif day_of_week == "Wednesday":
                job = schedule.every().wednesday.at(time_str).do(execute_reminder, reminder_id)
            elif day_of_week == "Thursday":
                job = schedule.every().thursday.at(time_str).do(execute_reminder, reminder_id)
            elif day_of_week == "Friday":
                job = schedule.every().friday.at(time_str).do(execute_reminder, reminder_id)
            elif day_of_week == "Saturday":
                job = schedule.every().saturday.at(time_str).do(execute_reminder, reminder_id)
            else:  # Sunday
                job = schedule.every().sunday.at(time_str).do(execute_reminder, reminder_id)
                
            st.session_state.scheduled_jobs[reminder_id] = job
            
        elif frequency == "Monthly":
            schedule_display = f"Monthly on day {day_of_month} at {selected_time.strftime('%I:%M %p')} IST"
            schedule_key = f"monthly-{day_of_month}-{selected_time.strftime('%H:%M')}"
            
            # For monthly jobs, use the system time
            job = schedule.every().day.at(time_str).do(
                lambda: execute_reminder(reminder_id) if datetime.now(ist).day == day_of_month else None
            )
            st.session_state.scheduled_jobs[reminder_id] = job
            
        else:  # One-time
            schedule_display = f"Once on {date.strftime('%b %d, %Y')} at {selected_time.strftime('%I:%M %p')} IST"
            schedule_key = f"once-{date.strftime('%Y-%m-%d')}-{selected_time.strftime('%H:%M')}"
            
            # For one-time jobs, we'll need a more complex approach
            # Create a datetime object in IST timezone
            naive_datetime = datetime.combine(date, selected_time)
            scheduled_datetime_ist = ist.localize(naive_datetime)
            
            # Convert to system timezone for comparison with system now
            scheduled_datetime_system = scheduled_datetime_ist.astimezone(system_tz)
            
            # Get current time in system timezone
            current_time_system = datetime.now(system_tz)
            
            if scheduled_datetime_system <= current_time_system:
                st.error("The scheduled time has already passed.")
            else:
                # Calculate seconds until the scheduled time
                delta = (scheduled_datetime_system - current_time_system).total_seconds()
                
                # Schedule a job to run once after the delay
                job = schedule.every(int(delta)).seconds.do(
                    lambda: (execute_reminder(reminder_id), schedule.cancel_job(st.session_state.scheduled_jobs[reminder_id]))
                )
                st.session_state.scheduled_jobs[reminder_id] = job
        
        # Store the IST time for reference
        ist_time_str = selected_time.strftime('%H:%M')
        
        # Create the reminder object
        reminder = {
            "id": reminder_id,
            "type": "Medication",
            "text": reminder_text,
            "frequency": frequency,
            "schedule_display": schedule_display,
            "schedule_key": schedule_key,
            "sender_name": sender_name,
            "receiver_name": receiver_name,
            "receiver_chat_id": receiver_chat_id,
            "active": True,
            # Store both IST and system time for reference
            "selected_time_ist": ist_time_str,
            "selected_time_system": time_str,
            # For one-time reminders, store the full datetime
            "scheduled_datetime_ist": scheduled_datetime_ist.isoformat() if frequency == "One-time" else None
        }
        
        # Generate a sample message for preview
        sample_message = generate_cordial_message(reminder_text, sender_name, receiver_name)
        
        # Add the reminder to the session state
        st.session_state.reminders.append(reminder)
        
        # Show success message with preview
        st.success(f"Medication reminder added successfully! Will send at {selected_time.strftime('%I:%M %p')} IST.")
        with st.expander("Preview Message", expanded=True):
            st.markdown(f"**Sample message that will be sent:**\n\n{sample_message}")

# Display existing reminders
if st.session_state.reminders:
    st.subheader("Your Scheduled Medication Reminders")
    
    # Convert to DataFrame for easier display
    df = pd.DataFrame(st.session_state.reminders)
    
    # Select columns to display
    display_df = df[['id', 'schedule_display', 'active']].copy()
    display_df.columns = ['ID', 'Schedule', 'Active']
    
    # Display as a table
    st.table(display_df)
    
    # Add options for testing and deleting reminders
    st.subheader("Manage Reminders")
    
    manage_col1, manage_col2 = st.columns(2)
    
    with manage_col1:
        st.markdown("#### Test a Reminder")
        if not st.session_state.get('telegram_configured'):
            st.warning("Please configure your Telegram bot token in the sidebar to test sending messages.")
        else:
            test_reminder_id = st.selectbox(
                "Select a reminder to test",
                options=[r['id'] for r in st.session_state.reminders],
                format_func=lambda x: f"ID {x}: {next((r['schedule_display'] for r in st.session_state.reminders if r['id'] == x), '')}"
            )
            
            test_button = st.button("Send Test Message Now")
            
            if test_button:
                # Find the selected reminder
                selected_reminder = next((r for r in st.session_state.reminders if r['id'] == test_reminder_id), None)
                
                if selected_reminder:
                    # Generate the message
                    message = generate_cordial_message(
                        selected_reminder.get('text', ''),
                        selected_reminder.get('sender_name', ''),
                        selected_reminder.get('receiver_name', '')
                    )
                    
                    # Send the test message
                    with st.spinner("Sending test message..."):
                        success, result = send_telegram_message(selected_reminder['receiver_chat_id'], message)
                        
                        if success:
                            st.success(result)
                        else:
                            st.error(result)
    
    with manage_col2:
        st.markdown("#### Delete a Reminder")
        delete_reminder_id = st.selectbox(
            "Select a reminder to delete",
            options=[r['id'] for r in st.session_state.reminders],
            format_func=lambda x: f"ID {x}: {next((r['schedule_display'] for r in st.session_state.reminders if r['id'] == x), '')}",
            key="delete_select"
        )
        
        delete_button = st.button("Delete Selected Reminder", type="primary")
        
        if delete_button:
            if delete_reminder(delete_reminder_id):
                st.success(f"Reminder ID {delete_reminder_id} has been deleted successfully!")
                st.experimental_rerun()  # Refresh the page to reflect changes
            else:
                st.error("Failed to delete the reminder. Please try again.")
else:
    st.info("No medication reminders have been added yet. Add a reminder using the form above.")

# Add information about how to set up the Telegram bot
st.markdown("---")
st.subheader("How to Set Up Your Telegram Bot")
st.markdown("""
1. **Create a bot on Telegram**:
   - Open Telegram and search for [@BotFather](https://t.me/botfather)
   - Start a chat and send `/newbot`
   - Follow the instructions to create your bot
   - You'll receive a token that looks like `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`
   - Copy this token and paste it in the sidebar of this app

2. **Get the Chat ID of recipients**:
   - The recipient must start a conversation with your bot by sending it a message
   - To find their Chat ID, tell them to:
     - Search for [@userinfobot](https://t.me/userinfobot) on Telegram
     - Start a chat and send any message
     - They will receive their Chat ID (usually a number like `123456789`)
     - Share this Chat ID with you to add to the app
""")

# Footer
st.markdown("---")
st.markdown("💊 **Medication Reminder App** - Supporting expectant mothers with care and compassion")
