from bs4 import BeautifulSoup
import aiofiles
import aiohttp
import asyncio
import requests
import json
import os
import re

class Reports:
    def __init__(self, session, gmail, creds, logger):
        self.session = session
        self.gmail = gmail
        self.creds = creds
        self.logger = logger

    async def login(self):
        data = {
                "loggedIn": "loggedIn",
                "user": self.creds["user"],
                "password": self.creds["pass"]
                }
        await self.session.post(self.creds["login_url"], data=data)

    # Downloads reports and sends draft
    async def download_reports_and_send_draft(self, user_data):
        download_tasks = await self.find_user(user_data, True)

        if len(download_tasks) == 0:
            download_tasks = await self.find_user(user_data, False)

            if len(download_tasks) == 0:
                self.logger.error(f"Couldn't find any reports for {user_data['email']}")
                return -1

        done, pending = await asyncio.wait(download_tasks)

        files = []
        for task in done:
            files.append(f"pdfs/{task.result()}")

        user_data['files'] = files

        # Create draft
        self.gmail.create_draft(user_data)

        for f in files:
            if os.path.exists(f):
                os.remove(f)
            else:
                self.logger.error(f"Couldn't delete {f} - does not exist")
        
        return user_data["id"]

    # Finds a user in the database and calls download_and_send_draft 
    # for each of their reports
    async def find_user(self, user_data, search_by_email):
        self.logger.debug(f"Searching for user {user_data['email']}, by email: {search_by_email}")
        # Search through users by last name or email
        data = {'CID': '', 'CLNAME': '', 'PURCHDT': '', 'COMPLETETS': '', 'PEMAIL': '', 'CEMAIL': '', 'last24': '' }
        if search_by_email:
            data['CEMAIL'] = user_data['email']
        elif user_data['last'] != '':
            data['CLNAME'] = user_data['last']

        async with self.session.post(self.creds["gen_url"], data=data) as response:
            html = await response.text()

        soup = BeautifulSoup(html, 'html.parser')
    
        # One task is scheduled for each report to download report and create draft
        tasks = []
        # Search results are in a table, table entries are tagged dataEven or dataOdd
        for tag in soup.find_all("tr",re.compile("dataEven|dataOdd")):
            found = False

            # Indexed [Code, Name, Type, TEmail, PEmail, PName, PDate, RName, Completedate, link]
            rows = tag.find_all('td')

            if len(rows) < 10:
                self.logger.error("error!")
                return

            # Succeed if either email or name matches
            for email in rows[3:5]:
                if(email.text.strip().lower() == user_data["email"]):
                    found = True

            if not found and user_data["last"] != '':
                for name in (rows[1], rows[5]):
                    if(f'{user_data["last"]}, {user_data["first"]}' == name.text.lower()):
                        found = True
                            

            # Found our table entry!
            # Find href to admin_rpt_generate
            if found:
                href = rows[9].a["href"]
                repid = href.split('repid=')[1].split('&')[0];

                # Can't generate a combined report
                if(repid=='210256' or repid=='289663' or repid=='289170'):
                    self.logger.debug(f"Combined report for user {user_data['email']}")

                # report_name, user-lastname_user-firstname_report-type
                report_name = rows[1].text.replace(', ','_') + "_" + rows[7].text.replace(' ','') + ".pdf"
                # Start a task to download the report and create a draft, add the task to tasks array
                tasks.append(asyncio.create_task(self.download_report(href, report_name, user_data)))
                
        return tasks

    # Generates and download a single report for a user
    async def download_report(self, href, report_name, user_data):
        # Get to 'generate report' page 
        async with self.session.post(self.creds["reports_url"]+href) as response:
            html = await response.text()

        soup = BeautifulSoup(html, 'html.parser')

        # Find call to checkReport js method whose parameters are
        # url parameters to download report
        onclick = soup.find(onclick=re.compile(".*checkReport.*"))["onclick"]

        onclick = onclick.replace('return checkReport(', '').replace(');', '').replace("\'",'').split(',');

        params = zip(['cid','licid', 'pkgid', 'lid', 'repid', 'instrid', 'cdate'], onclick)

        url = self.creds["soap_url"] 
        for tup in list(params):
            url += tup[0] + '=' + tup[1] + '&'

        self.logger.debug(f"Downloading file {report_name}")
        async with self.session.get(url) as response:
            async with aiofiles.open(f"pdfs/{report_name}", 'wb') as f:
                await f.write(await response.read())

        return report_name

            

                        
