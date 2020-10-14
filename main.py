"""
Entry point for Not Syllaboard
"""

from ariadne import (
    QueryType,
    fallback_resolvers,
    make_executable_schema,
    load_schema_from_path,
)
from ariadne.asgi import GraphQL
from datetime import datetime, timedelta
from pytz import timezone

type_defs = load_schema_from_path("./schema.gql")
# Map resolver functions to Query fields using QueryType
query = QueryType()

# This fake db took, like, an hour, mongodb will be easier
DATABASE = {
    "users": [
        {
            "id": 1,
            "name": "Sarah King",
            "email": "009kings@gmail.com",
            "password": "123123123",
            "connections": [1],
        },
        {
            "id": 2,
            "name": "James Liu",
            "email": "james@jamesliu.cc",
            "password": "God dammit jim I'm a hash not a password",
        },
    ],
    "connections": [
        {
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
                    "due": datetime(
                        2020, 10, 12, 17, tzinfo=timezone("America/Los_Angeles")
                    ).strftime("%c"),
                    "completed": {
                        "content": "Have a phone screen set up, just behavioural stuff.",
                        "time": datetime(
                            2020, 10, 12, tzinfo=timezone("America/Los_Angeles")
                        ).strftime("%c"),
                    },
                    "notes": [
                        {
                            "content": "Sent an intro email with my availability",
                            "time": datetime(
                                2020, 10, 7, tzinfo=timezone("America/Los_Angeles")
                            ).strftime("%c"),
                        },
                        {
                            "content": "She needed my references so I sent her Anna and Brandi's contact info",
                            "time": datetime(
                                2020, 10, 9, tzinfo=timezone("America/Los_Angeles")
                            ).strftime("%c"),
                        },
                    ],
                },
                {
                    "id": 2,
                    "title": "Follow up for Tech interview",
                    "due": datetime(
                        2020, 10, 25, 17, tzinfo=timezone("America/Los_Angeles")
                    ).strftime("%c"),
                    "notes": [
                        {
                            "content": "Sent an email with my availability",
                            "time": datetime(
                                2020, 10, 12, tzinfo=timezone("America/Los_Angeles")
                            ).strftime("%c"),
                        },
                        {
                            "content": "Have a practice sesh with James set up",
                            "time": datetime(
                                2020,
                                10,
                                15,
                                17,
                                30,
                                tzinfo=timezone("America/Los_Angeles"),
                            ).strftime("%c"),
                        },
                    ],
                },
            ],
        }
    ],
}
# Tabs are so BIG and not, like thicc, just so much space. But I changed for you

# Basic Heirarchy is as such
# User
# Connection
#   [Contact]
#   [Action]
#     completed: Note
#     [Note]


@query.field("connections")
def resolve_connections(*_):
    connections = DATABASE["connections"]
    return connections


@query.field("connection")
def resolve_connection(*_, id):
    for connection in DATABASE["connections"]:
        if connection["id"] == int(id):
            return connection
        return None


# This will be MUCH easier with an actual ODM
@query.field("actions")
def resolve_actions(*_, user_id, active=False):
    print("🧨", user_id)
    user = next(
        user_obj for user_obj in DATABASE["users"] if user_obj["id"] == int(user_id)
    )
    print(f'✨ {user["name"]}')
    # find all connections for a user
    connections = [
        connection
        for connection in DATABASE["connections"]
        if connection["id"] in user["connections"]
    ]
    print(f"🗿 {connections}")
    # iterate through all connections
    # Push each action to a list (unless active is True and date is later than now)
    if active is False:
        all_actions = [
            action for connection in connections for action in connection["actions"]
        ]
    else:
        all_actions = []
        for connection in connections:
            for action in connection["actions"]:
                # Older is bigger, will only show action with due dates in da future
                if datetime.strptime(action["due"], "%c") > datetime.now():
                    all_actions.append(action)
    return all_actions


@query.field("me")
def resolve_me(*_, id):
    for user in DATABASE["users"]:
        if user["id"] == int(id):
            return user
    return None


# Create executable GraphQL schema
schema = make_executable_schema(type_defs, query, fallback_resolvers)

# Create an ASGI app using the schema, running in debug mode
app = GraphQL(schema, debug=True)
