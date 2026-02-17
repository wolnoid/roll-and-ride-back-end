# Flask JWT Auth Template

## About

This repo is a Flask JWT Auth template meant to be paired with a front-end app utilizing JWT authentication. It includes a basic user model, routes for user registration and login, and a JWT token generator.

## Getting started

Fork and clone this repository to your local machine.

After moving into the cloned directory, activate a new virtual environment:

```bash
pipenv shell
```

Install the dependencies:

```bash
pyenv sync
```

Run the Flask app:

```bash
python app.py
```

## Database schema

This backend expects Postgres tables for `users` (auth) and `saved_directions`.

You can create them with:

```bash
psql <your_db_name> -f schema.sql
```

To deactivate the virtual environment when you're done, run:

```bash
exit
```
