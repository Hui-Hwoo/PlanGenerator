import requests
import json
import datetime


class Notion:
    def __init__(self, token, database_id, calendar_id, review_cycle) -> None:
        # base information
        self.token = token
        self.database_id = database_id
        self.calendar_id = calendar_id
        self.review_cycle = review_cycle
        self.database = "./database.json"
        self.calendar = "./calendar.json"
        self.dates = "./dates.json"
        self.headers = {
            "Authorization": "Bearer " + self.token,
            "Accept": "application/json",
            "Notion-Version": "2022-02-22",
            "Content-Type": "application/json"
        }

    def searchDatabase(self) -> None:
        """
        search the data in database page, reorganize and save them
        """
        # read data
        url = f'https://api.notion.com/v1/databases/{self.database_id}/query'
        response = requests.request("POST", url, headers=self.headers)
        if response.status_code != 200:
            raise ValueError("database_id is wrong")
        database = response.json()

        # reorganize data
        data = {}  # empty dictionary to save data
        for page in database["results"]:
            # find all pages that are not organized
            # and save their dates and url
            if not page["properties"]["Organized"]["checkbox"]:
                key = page["id"]
                value = {
                    "Date": page["properties"]["Date"]["date"]["start"],
                    "url": page["properties"]["URL"]["url"]
                }
                data[key] = value

        # save data
        with open(self.database, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)

    def compute_date(self) -> dict:
        """
        compute the dates need to review
        """
        review = {}  # empty dictionary to store data
        with open(self.database, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for id, value in data.items():
            first_day = value['Date']
            dt = datetime.datetime.strptime(first_day, "%Y-%m-%d")
            days = []  # empty list to save dates for one page

            # compute the days that need to review
            for day in self.review_cycle:
                res = (dt + datetime.timedelta(days=day)).strftime("%Y-%m-%d")
                days.append(res)

            # combine all the ids that need to review in the same day
            for d in days:
                if d in review:
                    review[d].append(id)
                else:
                    review[d] = [id]

            # save the data
            with open(self.dates, 'w', encoding='utf-8') as f:
                json.dump(review, f, ensure_ascii=False)
        return review

    def updatePage(self) -> None:
        """
        update the properties of all pages having been orgnazied
        """
        with open(self.database, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for page_id in data.keys():
            url = f"https://api.notion.com/v1/pages/{page_id}"
            updateData = {
                "properties": {
                    "Organized": {
                            "checkbox": True
                        }
                }
            }
            response = requests.patch(url, headers=self.headers, json=updateData)
            if response.status_code != 200:
                return ValueError("Can not update pages")

    def readCalendar(self) -> dict:
        """
        read the data in calendar page and save them to calendar.json
        """

        # read the data
        url = f'https://api.notion.com/v1/databases/{self.calendar_id}/query'
        response = requests.request("POST", url, headers=self.headers)
        if response.status_code != 200:
            raise ValueError("calendar_id is wrong")
        data = response.json()

        # filter the data
        filtered_data = {}
        for page in data["results"]:
            date = page["properties"]["Date"]["date"]["start"]
            page_id = page["id"]
            filtered_data[date] = page_id

        # save the date
        with open(self.calendar, 'w', encoding='utf-8') as f:
            json.dump(filtered_data, f, ensure_ascii=False)

        return filtered_data

    def appendBlock(self, block_id, type="todo", linked_id="") -> str:
        """
        Add a new block in the one page
        Blocks can be headings, todos or quotes
        """
        url = f"https://api.notion.com/v1/blocks/{block_id}/children"
        heading = {
            "object": "block",
            "has_children": False,
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "LeetCode",
                        },
                        "annotations": {
                            "bold": True,
                            "color": "blue"
                        },
                        "plain_text": "LeetCode",
                    }
                ],
                "color": "default"
            }
        }
        quote = {
            "object": "block",
            "type": "quote",
            "quote": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "😶",
                        },
                        "plain_text": "😶",
                    }
                ]
            }
        }
        todo = {
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [
                        {
                            "type": "mention",
                            "mention": {
                                "type": "page",
                                "page": {
                                    "id": linked_id
                                }
                            },
                            "href": f"https://www.notion.so/{linked_id.replace('-', '')}"
                        },
                    ],
                    "checked": False,
                }
            }

        if type == "heading":
            content = heading
        elif type == "quote":
            content = quote
        elif type == "todo":
            content = todo
        else:
            raise ValueError

        response = requests.patch(url,
                                  headers=self.headers,
                                  json={"children": [content]})
        if response.status_code != 200:
            raise ValueError("can not add new blocks")
        # return the id of the block that we have added
        return response.json()['results'][0]['id']

    def createPage(self, date) -> str:
        """
        create a new page and return block id
        """
        url = "https://api.notion.com/v1/pages"
        newPage = {
            "object": "page",
            "icon": {
                "type": "emoji",
                "emoji": "😶"
            },
            "parent": {
                "type": "database_id",
                "database_id": "10c55107-2e56-4b45-80b5-cc697c73ce2f"
            },
            "properties": {
                "Date": {
                    "id": "dq%3DM",
                    "type": "date",
                    "date": {
                        "start": date,
                    }
                },
                "Tags": {
                    "id": "~qWm",
                    "type": "multi_select",
                    "multi_select": [
                        {
                            "id": "249d49eb-9afe-4bf7-8134-af91595a1e8a",
                            "name": "LeetCode",
                            "color": "blue"
                        }
                    ]
                },
                "Name": {
                    "id": "title",
                    "type": "title",
                    "title": [
                        {
                            "type": "text",
                            "text": {
                                "content": "Review",
                            },
                            "plain_text": "Review",
                        }
                    ]
                }
            },
        }
        response = requests.post(url, json=newPage, headers=self.headers)
        if response.status_code != 200:
            raise ValueError("can not create new page")
        page_id = response.json()["id"]

        self.appendBlock(page_id, type="heading")
        block_id = self.appendBlock(page_id, type="quote")
        return block_id

    def readBlock(self, block_id, job="find_id"):
        """
        read block and return its id
        """
        url = f"https://api.notion.com/v1/blocks/{block_id}/children?page_size=100"
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            raise ValueError("block_id is wrong")

        blocks = response.json()["results"]
        if job == "find_id":
            for block in blocks:
                if block["type"] == "quote":
                    return block["id"]
        elif job == "find_num":
            return len(blocks)
        else:
            raise ValueError

    def updateBlock(self, block_id) -> None:
        """
        update the number of icons which is the number of pages
        that we need to review
        """
        n = self.readBlock(block_id, job="find_num")
        url = f"https://api.notion.com/v1/blocks/{block_id}"
        updatedata = {
            "quote": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "😶" * n,
                        },
                        "plain_text": "😶" * n,
                    }
                ],
                "color": "default"
            }
        }
        response = requests.patch(url, json=updatedata, headers=self.headers)
        if response.status_code != 200:
            raise ValueError("can not update blocks")

def main():
    # creat a notion object according the provided base information
    base_info = {
        "token": 'secret_OiAX1w2anZHHXDhzkozBIJd5PWLJMaoy04ZsM1vix48',
        "database_id": '46aadc437ddd4017a2c4508801091956',
        "calendar_id": '10c551072e564b4580b5cc697c73ce2f',
        "review_cycle": [2, 7, 14]
    }
    notion = Notion(**base_info)

    # Search database and calendar
    notion.searchDatabase()
    calendar = notion.readCalendar()

    # get the dates and update corresponding pages or create a new page
    dates = notion.compute_date()
    for day, ids in dates.items():
        if day in calendar:
            block_id = notion.readBlock(calendar[day])
        else:
            block_id = notion.createPage(day)

        for id in ids:
            notion.appendBlock(block_id, linked_id=id)
        notion.updateBlock(block_id)
    # update the properties of each page
    notion.updatePage()


if __name__ == '__main__':
    main()
