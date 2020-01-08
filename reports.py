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
        await self.session.post(self.creds["login_url"], data)

    # Finds and downloads report for this user, returns filename of downlaoded file
    #async def download_report(data):

        

    async def get_gen_page(last, email,self.creds):

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
                for name in tag.find_all(string=re.compile(".*\,.*")):
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
                await gen_and_download_pdf(href)

    
     async def gen_and_download_pdf(href):
        async with sesson.post(self.creds["reports_url"]+href) as response:
            print(response.text)

            with open('reports-repsonse.html', 'r') as f:
                f.write(response.text)

            

            
            
                        
##### TEST ####
async def test():
    with open ('secrets/creds.json')  as f:
        creds = json.load(f)

    async with aiohttp.ClientSession() as session:
        reports = Reports(session, creds)
        await reports.parse_html("brooke", "myrland","brookieleilani83@gmail.com")

asyncio.run(test())
