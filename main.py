from gcal import GCal
#from gmail import GMail
from gauth import GAuth
from reports import Reports
import aiohttp
import asyncio
import json

async def main():
    auth = GAuth()
    mail = GMail(auth.mail)
    with open('secrets/creds.json', 'r') as f:
        creds = json.load(f)

    session = aiohttp.ClientSession()
    reports = Reports(session, creds)
    # Login
    login = asyncio.create_task(reports.login())

    # Get events to process 
    calendar = GCal(auth.calendar, reports)
    calendar.query_calendar()

    # Make sure we're logged in & process events
    await login
    if len(calendar.events) > 0:
        # Call reports.find_user for each new event, this downloads report and creates draft
        await asyncio.wait([reports.find_user(data) for data in calendar.events])

    await session.close()





if __name__ == "__main__":
    asyncio.run(main())

# Create auth obj
# Create requests obj

# Send requests and auth objs to calendar & mail

