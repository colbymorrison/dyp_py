from bs4 import BeautifulSoup
import gmail
import aiohttp
import asyncio
import json
import re

class Reports:
    def __init__(self, session, creds):
        self.session = session
        self.creds = creds

    async def login(self):
        data = {
                "loggedIn": "loggedIn",
                "user": self.creds["user"],
                "password": self.creds["pass"]
                }
        await self.session.post(self.creds["login_url"], data=data)


    # Finds a user in the database and calls download_and_send_draft 
    # for each of their reports
    async def find_user(self, user_data):
        # Search through users by last name & email
        data = {'CID': '', 'CLNAME': user_data["last"], 'PURCHDT': '', 'COMPLETETS': '', 'PEMAIL': '', 'CEMAIL': user_data["email"], 'last24': '' }

        print(f"Searching for user {user_data['email']}")
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
                print("error!")
                return

            # Succeed if either email or name matches
            for email in rows[3:5]:
                if(email.text.strip().lower() == user_data["email"]):
                    found = True

            if not found and user_data["last"] != '':
                for name in (rows[1], rows[5]):
                    print(f"Testing name {name}")
                    if(f'{user_data["last"]}, {user_data["first"]}' == name.text.lower()):
                        print("NM")
                        found = True
                            

            # Found our table entry!
            # Find href to admin_rpt_generate
            if found:
                href = rows[9].a["href"]
                repid = href.split('repid=')[1].split('&')[0];

                # Can't generate a combined report
                if(repid=='210256' or repid=='289663' or repid=='289170'):
                    print(f"Combined report for user {user_data['email']}")
                    return

                # Start a task to download the report and create a draft and add the task to tasks
                tasks.append(asyncio.create_task(self.download_and_send_draft(href, rows[7].text, user_data))
                
        # Return when all tasks have completed
        await asyncio.wait(tasks)

    # Generates and download a single report for a user
    async def download_and_send_draft(self, href, report_name, user_data):
        # Get to 'generate report' page 
        print(f"Generating report for user {user_data['email']}")
        async with self.session.post(self.creds["reports_url"]+href) as response:
            html = await response.text()

        soup = BeautifulSoup(html, 'html.parser')

        # Find call to checkReport js method whose parameters are
        # url parameters to download report
        onclick = soup.find(onclick=re.compile(".*checkReport.*"))["onclick"]

        onclick = onclick.replace('return checkReport(', '').replace(');', '').split(',');

        params = zip(['cid','licid', 'pkgid', 'lid', 'repid', 'instrid', 'cdate'], onclick)

        file_name = f"{user_data['first']}_{user_data['last']}_{report_name.replace(' ','')}"
        user_data["file_name"] = file_name

        print(f"Downloading file {file_name} with params {dict(params)}")
        async with self.session.post(self.creds["soap_url"], params = dict(params)) as response:
            async with open(file_name, 'wb') as f:
                await f.write(await response.read())

        gmail.create_draft(user_creds)
        os.unlink(file_name)

            

                        
##### TEST ####
#async def test():
 #   with open ('secrets/creds.json')  as f:
 #       creds = json.load(f)
#
#    with open('./response.html', 'r') as f:
#        html = f.readlines()
#
#    html = ''.join(html)
#
#    async with aiohttp.ClientSession() as session:
#        reports = Reports(session, creds)
#        await reports.login()
#        await reports.find_user({"first": "brooke", "last": "myrland", "email": "brookieleilani83@gmail.com"}, html)
##        #await reports.download_and_send_draft(html)
#
#asyncio.run(test())
