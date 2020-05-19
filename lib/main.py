from gcal import GCal
from gmail import GMail
from gauth import GAuth
from reports import Reports
import os
import logging
import aiohttp
import asyncio
import json

async def main():
    logger = get_logger()
    logger.info("Start")
    auth = GAuth(logger)
    with open(f'{os.environ.get("SECRETS")}/creds.json', 'r') as f:
        creds = json.load(f)

    mail = GMail(auth.mail, logger)
    session = aiohttp.ClientSession()
    reports = Reports(session, mail, creds, logger)
    # Login
    login = asyncio.create_task(reports.login())

    # Get events to process 
    calendar = GCal(auth.calendar, creds["cal_id"], logger)
    calendar.query_calendar()

    # Make sure we're logged in & process events
    await login
    if len(calendar.users) > 0:
        # Call reports.dowload_reports_and_send_draft for each new event, this downloads report and creates draft
        done, pending = await asyncio.wait([reports.download_reports_and_send_draft(data) for data in calendar.users])

        # Patch events that drafts were succesfully created for (returned +ve)
        for task in done:
            if result := task.result():
                calendar.patch(result)

    await session.close()

def get_logger():
    # Log to log file
    handler = logging.FileHandler("../reports.log")

    # Log to stderr
    #handler = logging.StreamHandler()

    formatter = logging.Formatter('%(asctime)s - %(filename)s - %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger("reports")
    logger.addHandler(handler)
    logger.setLevel("INFO")

    return logger

if __name__ == "__main__":
    asyncio.run(main())

