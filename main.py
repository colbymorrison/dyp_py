from gcal import GCal
from gmail import GMail
from gauth import GAuth
from reports import Reports
import logging
import aiohttp
import asyncio
import json

async def main():
    logger = get_logger()
    logger.debug("Start")
    auth = GAuth(logger)
    with open('secrets/creds.json', 'r') as f:
        creds = json.load(f)

    mail = GMail(auth.mail, logger)
    session = aiohttp.ClientSession()
    reports = Reports(session, mail, creds, logger)
    # Login
    login = asyncio.create_task(reports.login())

    # Get events to process 
    calendar = GCal(auth.calendar, creds["cal_id"], logger)
    calendar.query_calendar()
    #calendar.users=[{'id': 0, 'first': 'Peter', 'last': 'Simpson', 'email': '7peter.simpson@gmail.com'},{'id': 1, 'first': 'Laura', 'last': 'Simpson', 'email': 'laura.simpson141@gmail.com'},{'id': 2, 'first': 'Maylon', 'last': 'Tate', 'email': 'maylon.tate@yahoo.com'}]
    #calendar.event_data=[['2k99anobhcco0kdnhumjp5dvmr', 'Peter Simpson - Strong Interest Inventory Feedback Session'], ['0b7dnqfqh1d116cmf190ifseld', 'Laura Simpson - Strong Interest Inventory Feedback Session'], ['1hlaqu80kbpputnvkvs9jebi76', 'Maylon Tate - Myers-Briggs Feedback Session']]


    # Make sure we're logged in & process events
    await login
    if len(calendar.users) > 0:
        # Call reports.find_user for each new event, this downloads report and creates draft
        done, pending = await asyncio.wait([reports.download_reports_and_send_draft(data) for data in calendar.users])

        for task in done:
            calendar.patch(task.result())

    await session.close()

def get_logger():
    formatter = logging.Formatter('%(asctime)s - %(filename)s - %(message)s')
    handler = logging.FileHandler("reports.log")
    handler.setFormatter(formatter)

    logger = logging.getLogger("reports")
    logger.addHandler(handler)
    logger.setLevel("DEBUG")

    return logger

if __name__ == "__main__":
    asyncio.run(main())

