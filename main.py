"""
Entry point for Not Syllaboard
"""

from __future__ import annotations

from itertools import chain

from ariadne import (
    QueryType,
    MutationType,
    fallback_resolvers,
    make_executable_schema,
    load_schema_from_path,
)
from ariadne.asgi import GraphQL
from starlette.middleware.cors import CORSMiddleware

import bcrypt
import jwt

import pymongo
from bson.objectid import ObjectId
from urllib.parse import quote_plus

import os
from dotenv import load_dotenv

from constants import ERRORS

JWT_KEY = os.getenv("JWT_KEY")

# Load The MongoDB

load_dotenv()

MONGO_DB_PASSWORD = quote_plus(os.getenv("MONGO_DB_PASSWORD"))
MONGO_DB_USERNAME = quote_plus(os.getenv("MONGO_DB_USERNAME"))

client = pymongo.MongoClient(
    f"mongodb+srv://{MONGO_DB_USERNAME}:{MONGO_DB_PASSWORD}@db.eubgx.mongodb.net/db?retryWrites=true&w=majority"
)
db = client.db

# The GraphQL

# Basic Heirarchy is as such
# User
# Connection
#   [Contact]
#   [Action]
#     completed: Note
#     [Note]

type_defs = load_schema_from_path("./schema.gql")
# Map resolver functions to Query fields using QueryType
query = QueryType()
mutation = MutationType()

# TODO Connections should be own file
@query.field("connections")
def resolve_connections(*_) -> list[dict]:
    return [connection for connection in db.connections.find()]


@query.field("connection")
def resolve_connection(*_, _id):
    return db.connections.find_one({"_id": ObjectId(_id)})


# TODO Actions should be own file
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


# TODO Auth should be own file
@query.field("me")
def resolve_me(_, info):
    token = info.context["request"].headers["authorization"].removeprefix("Bearer ")
    decoded = jwt.decode(token.encode("utf-8"), JWT_KEY)

    user = db.users.find_one(decoded)
    user["_id"] = str(user["_id"])
    user["password"] = ""

    return user


@mutation.field("signup")
def resolve_signup(*_, name: str, email: str, password: str):
    if not name or not email or not password:
        return ERRORS["UNKNOWN"]
    try:
        hashed = bcrypt.hashpw(
            password.encode("utf-8"),
        )
        db.users.insert_one({"name": name, "email": email, "password": hashed})

    except:
        # TODO Give useful error message for email address in use.
        return ERRORS["UNKNOWN"]
    return {
        "status": "ok",
        "jwt": ((jwt.encode({"email": email}, JWT_KEY)).decode("utf-8")),
    }


@mutation.field("login")
def resolve_login(_, info, email: str, password: str):
    user = db.users.find_one({"email": email})
    if not user:
        return ERRORS["USER_NOT_FOUND"]
    if bcrypt.checkpw(password.encode("utf-8"), user["password"]):
        return {
            "status": "ok",
            "jwt": (jwt.encode({"email": user["email"]}, JWT_KEY)).decode("utf-8"),
        }
    return ERRORS["BAD_CREDS"]


# Create executable GraphQL schema
schema = make_executable_schema(type_defs, query, mutation, fallback_resolvers)

# Create an ASGI app using the schema, running in debug mode
app = CORSMiddleware(
    GraphQL(schema, debug=True),
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST", "OPTIONS"],
)
