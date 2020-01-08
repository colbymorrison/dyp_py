from gcal import GCal
from gmail import GMail
from gauth import Gauth
from reports import Reports
import aiohttp
import ansyncio

async def main():
    auth = GAuth()
    mail = GMail(auth.mail)
    async with aiohttp.ClientSession() as session:
        reports = Reports(session, mail)

        # Login in to DYP 
        login = asycio.create_task(reports.login())

        # Get events to process 
        calendar = GCal(gAuth.calendar, reports)
        calendar.query_calendar()

        # Make sure we're logged in & process events
        await login
        asyncio.gather(*[reports.download_report(data) for data in calendar.events])





if __name__ == "__main__":
    asyncio.run(main())

# Create auth obj
# Create requests obj

# Send requests and auth objs to calendar & mail

