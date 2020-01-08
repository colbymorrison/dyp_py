from bs4 import BeautifulSoup
import aiohttp
import asyncio
import re
import json

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

    # Finds and downloads report for this user, returns filename of downlaoded file
    #async def download_report(data):

        

    async def get_gen_page(last, email):

        data = {'CID': '', 'CLNAME': last, 'PURCHDT': '', 'COMPLETETS': '', 'PEMAIL': '', 'CEMAIL': email, 'last24': '' }

        async with session.post(self.creds["gen_url"], data) as response:
            return response.text

    async def parse_html(self, first, last, email):
        with open('response.html', 'r') as f:
            html = f.readlines()
        html = ''.join(html)
        soup = BeautifulSoup(html, 'html.parser')

        # Table entries for respondents are tagged dataEven or dataOdd
        for tag in soup.find_all("tr",re.compile("dataEven|dataOdd")):
            found = False
            print(tag)

            # If we find either a matching email or name, we call it a match

            for rpt_email in tag.find_all(href=re.compile("mailto:*")):
                if(rpt_email.text.strip() == email):
                    print("!")
                    found = True

            if found == False and last != '':
                for name in tag.find_all(string=re.compile(".*,.*")):
                    if(f"{last}, {first}" == name.lower()):
                        print("NM")
                        found = True
                            

            # Found our table entry!
            # Find href to admin_rpt_generate
            if found:
                report_str = tag.find(href=re.compile("admin_rpt_generate*"))
                href = report_str["href"]
                repid = href.split('repid=')[1].split('&')[0];

                if(repid=='210256' or repid=='289663' or repid=='289170'):
                    print("Combined report")
                    return

                # TODO create_task for each
                await self.gen_and_download_pdf(href)


    # Generate and download a single report
    async def gen_and_download_pdf(self, html):
        # Get to 'generate report' page 
        #async with self.session.post(self.creds["reports_url"]+href) as response:
        #    html = await response.text()

        soup = BeautifulSoup(html, 'html.parser')

        # Find call to checkReport js method whose parameters are
        # url parameters to download report
        onclick = soup.find(onclick=re.compile(".*checkReport.*"))["onclick"]

        onclick = onclick.replace('return checkReport(', '').replace(');', '').split(',');

        params = zip(['cid','licid', 'pkgid', 'lid', 'repid', 'instrid', 'cdate'], onclick)

        async with self.session.post(self.creds["soap_url"], params = dict(params)) as response:
            with open('test.pdf', 'wb') as f:
                f.write(await response.read())




        
            

                        
##### TEST ####
async def test():
    with open ('secrets/creds.json')  as f:
        creds = json.load(f)

    with open('./reports-repsonse.html', 'r') as f:
        html = f.readlines()

    html = ''.join(html)

    async with aiohttp.ClientSession() as session:
        reports = Reports(session, creds)
        #await reports.login()
        #await reports.parse_html("brooke", "myrland","brookieleilani83@gmail.com")
        await reports.gen_and_download_pdf(html)

asyncio.run(test())
