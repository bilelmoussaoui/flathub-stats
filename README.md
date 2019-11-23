# Flathub Stats API

### Requirements:

-   Python 3.4
-   `pipenv`

### Setup:

-   The `flathub/stats.py` is a script that should be run daily to update the SQLite database
-   `flathub/server.py` runs a simple web server with one unique endpoint

### Web server endpoints:

-   `/<app-id>`

Returns

```json
{
    "app_id": "the actual app-id",
    "downloads": "total downloads since april 2018",
    "updates": "total updates since april 2018"
}
```
