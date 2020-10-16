"""
Entry point for Not Syllaboard
"""

from __future__ import annotations

from ariadne import (
    QueryType,
    fallback_resolvers,
    make_executable_schema,
    load_schema_from_path,
)
from ariadne.asgi import GraphQL
from starlette.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from pytz import timezone
import os
from bson.objectid import ObjectId
from dotenv import load_dotenv
from urllib.parse import quote_plus
import pymongo
from itertools import chain

load_dotenv()

MONGO_DB_PASSWORD = quote_plus(os.getenv("MONGO_DB_PASSWORD"))
MONGO_DB_USERNAME = quote_plus(os.getenv("MONGO_DB_USERNAME"))

type_defs = load_schema_from_path("./schema.gql")
# Map resolver functions to Query fields using QueryType
query = QueryType()

client = pymongo.MongoClient(
    f"mongodb+srv://{MONGO_DB_USERNAME}:{MONGO_DB_PASSWORD}@db.eubgx.mongodb.net/db?retryWrites=true&w=majority"
)
db = client.db

# Tabs are so BIG and not, like thicc, just so much space. But I changed for you

# Basic Heirarchy is as such
# User
# Connection
#   [Contact]
#   [Action]
#     completed: Note
#     [Note]


@query.field("connections")
def resolve_connections(*_) -> list[dict]:
    return [connection for connection in db.connections.find()]


@query.field("connection")
def resolve_connection(*_, _id):
    return db.connections.find_one({"_id": ObjectId(_id)})


@query.field("actions")
def resolve_actions(*_, active=False):
    user = db.users.find_one()  # TODO: Make logged in user, not the first user
    print(f'✨ {user["name"]}')
    # find all connections for a user, don't unpack
    connections = chain.from_iterable(
        db.connections.find({"_id": ObjectId(id)}) for id in user["connections"]
    )
    # lazily unpack actions from connections cursors
    all_actions = (
        action for connection in connections for action in connection["actions"]
    )
    if not active:
        return [action for action in all_actions]
    raise NotImplementedError  # TODO Refactor dates, after, should look like
    # return [action for action in all_actions if actionable(action)]
    # TODO write helper function for actionable(action: Action) -> Boolean


@query.field("me")
def resolve_me(*_, id):
    raise NotImplementedError


# Create executable GraphQL schema
schema = make_executable_schema(type_defs, query, fallback_resolvers)

# Create an ASGI app using the schema, running in debug mode
app = CORSMiddleware(
    GraphQL(schema, debug=True),
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST", "OPTIONS"],
)
