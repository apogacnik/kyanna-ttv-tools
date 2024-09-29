import asyncio
from events.event_handler import start_event_listener
from server.server import app
from threading import Thread

# Function to run Flask in a separate thread
def run_flask():
    app.run(host='0.0.0.0', port=5000)

async def main():
    # Start Flask server in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Start the EventSub listener asynchronously
    await start_event_listener()
    print("Exit...")

# Run the main app
if __name__ == "__main__":
    asyncio.run(main())
