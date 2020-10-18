# README

I am so hard out of practice with GraphQL.
Bitch me too

## Running

To install requirments:

```bash
python3.9 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

To run:

```bash
./run.sh
```

Note, restart the server manually when editing .gql files.

Here is [how to write resolvers](https://ariadnegraphql.org/docs/resolvers).

The workaround to run Black globally:

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install black
```
