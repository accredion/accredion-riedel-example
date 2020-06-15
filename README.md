# Riedel API Consumer Reference Implementation

This is an example implementation of the webhook consumer for Accredion written in Python/Flask. It shows the usage of the following subjects:

-   Sender verification using `X-Accredion-Signature`.
-   Handlers for events.
-   Usage of API for reverse communication.

## Installation

```
$ pip install -r requirements.txt
```

## Usage

Run the application using the terminal.

```
$ flask run
```

Behaviour can be changed using one or more of the following environment variables.

- `API_HOST`: Change the target of the API (default `https://ebu.staging.accredion.com/`)
- `API_ACCESS_KEY`: Access token for using the API.
- `EVENT_ID`: Identifier of the Accredion event used for retrieving data.
- `SECRET`: Secret used for verifying the webhook sender.
