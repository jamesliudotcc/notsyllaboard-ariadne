import pymongo
from bson.objectid import ObjectId
from urllib.parse import quote_plus
from datetime import datetime
from zoneinfo import ZoneInfo

import os
from dotenv import load_dotenv

load_dotenv()

MONGO_DB_PASSWORD = quote_plus(os.getenv("MONGO_DB_PASSWORD"))
MONGO_DB_USERNAME = quote_plus(os.getenv("MONGO_DB_USERNAME"))


client = pymongo.MongoClient(
    f"mongodb+srv://{MONGO_DB_USERNAME}:{MONGO_DB_PASSWORD}@db.eubgx.mongodb.net/db?retryWrites=true&w=majority"
)
db = client.db



mads = {
    "id": 1,
    "name": "Madison Edmiston",
    "info": "Student ops director for Seattle campus, go-to-gal for many ppl, loves dogs, can't eat gluten",
    "contacts": [
        {
            "id": 1,  # embedded docs get their own ID
            "type": "work email",
            "content": "madison.edmiston@ga.co",
        },
        {"id": 2, "type": "work phone", "content": "(206) 334-0998"},
        {"id": 3, "type": "personal phone", "content": "(206) 333-9903"},
    ],
    "actions": [
        {
            "id": 1,
            "title": "Set up phone interview",
            "due": int(
                datetime(
                    2020, 10, 12, 17, tzinfo=ZoneInfo("America/Los_Angeles")
                ).timestamp()
            ),
            "completed": {
                "content": "Have a phone screen set up, just behavioural stuff.",
                "time": int(
                    datetime(
                        2020, 10, 12, tzinfo=ZoneInfo("America/Los_Angeles")
                    ).timestamp()
                ),
            },
            "notes": [
                {
                    "content": "Sent an intro email with my availability",
                    "time": int(
                        datetime(
                            2020, 10, 7, tzinfo=ZoneInfo("America/Los_Angeles")
                        ).timestamp()
                    ),
                },
                {
                    "content": "She needed my references so I sent her Anna and Brandi's contact info",
                    "time": int(
                        datetime(
                            2020, 10, 9, tzinfo=ZoneInfo("America/Los_Angeles")
                        ).timestamp()
                    ),
                },
            ],
        },
        {
            "id": 2,
            "title": "Follow up for Tech interview",
            "due": int(
                datetime(
                    2020, 10, 25, 17, tzinfo=ZoneInfo("America/Los_Angeles")
                ).timestamp()
            ),
            "notes": [
                {
                    "content": "Sent an email with my availability",
                    "time": int(
                        datetime(
                            2020, 10, 12, tzinfo=ZoneInfo("America/Los_Angeles")
                        ).timestamp()
                    ),
                },
                {
                    "content": "Have a practice sesh with James set up",
                    "time": int(
                        datetime(
                            2020, 10, 15, 17, 30, tzinfo=ZoneInfo("America/Los_Angeles")
                        ).timestamp()
                    ),
                },
            ],
        },
    ],
}
users = [
    {
        "id": 1,
        "name": "Sarah King",
        "email": "009kings@gmail.com",
        "password": "123123123",
    },
    {
        "id": 2,
        "name": "James Liu",
        "email": "james@jamesliu.cc",
        "password": "God dammit jim I'm a hash not a password",
    },
]

def start_over():
    db.connections.delete_many({})
    db.users.delete_many({})

    db.users.insert_many(users)
    db.connections.insert_one(mads)

    mads_id = str(db.connections.find_one()["_id"])

    db.users.find_one_and_update({'email': "009kings@gmail.com"}, {'$set': {'connections': [mads_id]}})


def create_indexes():
    db.users.create_index([("email", pymongo.ASCENDING)], unique=True)