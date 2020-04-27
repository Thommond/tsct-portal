
import os
import psycopg2
import psycopg2.extras

import click
import csv
from flask import current_app, g
from flask.cli import with_appcontext

rom werkzeug.security import check_password_hash, generate_password_hash



PASSWORD = password
test = generate_password_hash(PASSWORD)

print(generate_password_hash(PASSWORD))
