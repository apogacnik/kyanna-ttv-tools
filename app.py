import asyncio
from events.event_handler import start_event_listener

# Main entry point
async def main():
    # Start the EventSub listener
    await start_event_listener()
    print("Exit...")

# Run the main app
if __name__ == "__main__":
    asyncio.run(main())
