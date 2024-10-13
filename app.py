import asyncio
from events.event_handler import start_event_listener
from server.server import app
from threading import Thread
import os
import sys
import logging
from datetime import datetime



# Function to run Flask in a separate thread
def run_flask():
    app.run(host='0.0.0.0', port=5000)

async def main():
    # Change the current working directory to the script's directory
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    os.chdir(script_dir)

    # Set up logging
    log_folder = 'logs/'
    os.makedirs(log_folder, exist_ok=True)  # Create the folder if it doesn't exist
    current_date = datetime.now().strftime('%Y-%m-%d')
    log_filename = f'{log_folder}{current_date}.log'

    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO, 
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Start Flask server in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Start the EventSub listener asynchronously
    await start_event_listener()
    print("Exit...")
    input("Press Enter to exit...")

# Run the main app
if __name__ == "__main__":
    asyncio.run(main())
