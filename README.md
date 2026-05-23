# Flower Shop Client-Server Application

Flower Shop is a Flask client-server application for managing a flower catalog with role-based permissions, internationalization, structured API errors, and real-time chat.

## Roles

- Visitor: browses the catalog, filters/sorts flowers, exports data, and uses chat.
- Florist: all Visitor permissions plus stock quantity updates.
- Administrator: full CRUD access for flowers.

Default accounts:

```text
Admin:   admin@flowershop.com / admin123
Florist: florist@flowershop.com / flower123
```

## Architecture

- `identity_service/`: authentication service, runs on `localhost:5001`.
- `catalog_service/`: catalog API, business logic, persistence, exports, and WebSocket chat, runs on `localhost:5002`.
- `client/`: browser client that communicates with the server through `/api/...` endpoints and Socket.IO.

The final UI is API-driven. The server enforces permissions even if a client tries to call protected endpoints manually.

## Features

- Client-server architecture with JSON API endpoints.
- Visitor, Florist, and Administrator role behavior.
- Flower catalog filtering, sorting, export to JSON/CSV.
- Administrator add/edit/delete flower operations.
- Florist/Admin stock updates.
- Dynamic English/Romanian interface switching.
- Real-time global chat using WebSockets/Socket.IO.
- Consistent API error format with `message`, `code`, and `timestamp`.

## Install

From the project root:

```powershell
cd C:\An3\SD\proiect
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If `python` is not available in PATH, create the environment with any installed Python 3.12+ executable, then keep using `.\.venv\Scripts\python.exe`.

## Initialize Databases

```powershell
cd C:\An3\SD\proiect
& .\.venv\Scripts\python.exe .\identity_service\db_setup.py
& .\.venv\Scripts\python.exe .\catalog_service\db_setup.py
```

## Run

Open two terminals.

Terminal 1:

```powershell
cd C:\An3\SD\proiect
& .\.venv\Scripts\python.exe .\identity_service\app.py
```

Terminal 2:

```powershell
cd C:\An3\SD\proiect
& .\.venv\Scripts\python.exe .\catalog_service\app.py
```

Open:

```text
http://127.0.0.1:5002
```

## Tests

```powershell
cd C:\An3\SD\proiect\catalog_service
& ..\.venv\Scripts\python.exe -m unittest test_catalog.py test_api.py -v

cd C:\An3\SD\proiect\identity_service
& ..\.venv\Scripts\python.exe -m unittest test_identity.py -v
```

## Important API Endpoints

- `POST /api/login`
- `POST /api/visitor`
- `POST /api/logout`
- `GET /api/session`
- `GET /api/flowers`
- `POST /api/flowers`
- `PUT /api/flowers/<id>`
- `PATCH /api/flowers/<id>/stock`
- `DELETE /api/flowers/<id>`
- `GET /api/export/json`
- `GET /api/export/csv`

Example structured error:

```json
{
  "message": "Only administrators can perform this action.",
  "code": "FORBIDDEN",
  "timestamp": "2026-05-23T12:00:00+00:00"
}
```
