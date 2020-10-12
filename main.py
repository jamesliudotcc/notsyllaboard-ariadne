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

type_defs = load_schema_from_path("./schema.gql")
# Map resolver functions to Query fields using QueryType
query = QueryType()

DATABASE = {
    "companies": [
        {"id": 1, "name": "4C Insights", "linkedIn": "4C"},
        {"id": 2, "name": "General Assembly", "linkedIn": "GA"},
    ],
    "contacts": [
        {
            "id": 1,
            "name": "James Liu",
            "email": "james@jamesliu.cc",
            "timeZone": "PDT",
            "company_ids": [1, 2],  # This may be a mistake
        },
        {
            "id": 2,
            "name": "Sarah King",
            "email": "009kings@gmail.com",
            "timeZone": "PDT",
            "company_ids": [2],  # Same here
        },
    ],
}


@query.field("contacts")
def resolve_contact(*_):
    contacts = DATABASE["contacts"]
    for contact in contacts:
        contact["companies"] = [
            company
            for company in DATABASE["companies"]
            if company["id"] in contact["company_ids"]
        ]

    return contacts


@query.field("companies")
def resolve_company(*_):
    companies = DATABASE["companies"]
    for company in companies:
        company["contacts"] = [
            contact
            for contact in DATABASE["contacts"]
            if company["id"] in contact["company_ids"]
        ]

    return companies


# Create executable GraphQL schema
schema = make_executable_schema(type_defs, query, fallback_resolvers)

# Create an ASGI app using the schema, running in debug mode
app = GraphQL(schema, debug=True)
