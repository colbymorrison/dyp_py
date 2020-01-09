import os
import datetime
from googleapiclient.errors import HttpError


class GCal:
    def __init__(self, service, cal_id,logger):
        self.cal_id = cal_id
        self.token_file = "secrets/sync-token"
        self.service = service
        self.events = []
        self.logger = logger

    def query_calendar(self):
        if os.stat(self.token_file).st_size == 0:
            self.__list_events(None)
        else:
           with open(self.token_file, 'r') as f:
                sync_token = f.read()
           self.__list_events(sync_token)


    def __list_events(self, sync_token):
        events_api = self.service.events()
        page_token = ""

        if not sync_token:
            self.logger.info("Full sync")
            # Get all items from 5 days ago until now
            today = datetime.datetime.today()
            time_min = (today - datetime.timedelta(days=5)).isoformat() + 'Z'
            request = events_api.list(calendarId=self.cal_id, timeMin=time_min, pageToken=page_token)
        else:
            request = events_api.list(calendarId=self.cal_id, pageToken=page_token, syncToken=sync_token)

        while True:
            try:
                events = request.execute()
            except HttpError as err:
                if err.resp.status == 410:
                    self.logger.error("Invalid SyncToken")
                    self.__list_events(None)
                else:
                    raise err

            # Return if no items
            if not (items := events.get("items")):
                return

            for item in items:
                 self.__process_item(item)

            if events.get("nextPageToken"):
                # Get next page, returns None if no more results
                if not (request := events_api.list_next(request,events)):
                    break
            else:
                break

        sync_token = events.get("nextSyncToken")

        with open(self.token_file, 'w') as f:
            f.write(sync_token)
        
    # Extract name, email, and event id from event and add to events array
    def __process_item(self, item):
        if not (attendees := item.get("attendees")):
            self.logger.debug("No attendees!")
            email = item.get("summary")
            return

        attendees = attendees[0]

        first = ""
        last = ""
        if name := attendees.get("displayName"):
            name = name.split()
            first = name[0]

            length = len(name)
            if length >= 2:
                last = name[length-1]

        email = attendees.get("email")
        self.logger.debug({"id": item.get('id'), "first":first, "last":last, "email":email})
        self.events.append({"id": item.get('id'), "first":first.lower(), "last":last.lower(), "email":email})

