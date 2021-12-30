import os

import click
from click import secho
from flask import cli
from flask.cli import with_appcontext
from flask_taxonomies.models import Base
from invenio_db import db as db_
from sqlalchemy_utils import create_database


@click.group()
def taxonomies():
    """Taxonomies commands."""


@taxonomies.group()
def index():
    """Index commands"""


@taxonomies.command("init")
@click.option('--create-db/--no-create-db', 'create_db', default=False)
@cli.with_appcontext
def init_db(create_db=False):
    """
    Management task that initialize database tables.
    """
    engine = db_.engine
    if create_db:
        create_database(engine.url)
    if db_.session.bind.dialect.name == 'postgresql':
        with engine.connect() as connection:
            connection.execute(
                "create extension if not exists ltree")
    Base.metadata.create_all(engine)


@taxonomies.command('import')
@click.argument('taxonomy_path')
@click.option('--int', 'int_conversions', multiple=True)
@click.option('--str', 'str_args', multiple=True)
@click.option('--bool', 'bool_args', multiple=True)
@click.option('--drop/--no-drop', default=False)
@click.option('--resolve/--no-resolve', default=False)
@with_appcontext
def import_taxonomy(taxonomy_path, int_conversions, str_args, bool_args, drop, resolve):
    from .import_export import import_taxonomy
    if os.path.isdir(taxonomy_path):
        for f in os.listdir(taxonomy_path):
            import_taxonomy(f, int_conversions, str_args, bool_args, drop, resolve_list=resolve)

    import_taxonomy(taxonomy_path, int_conversions, str_args, bool_args, drop, resolve_list=resolve)


@taxonomies.command('export')
@click.argument('taxonomy_code')
@with_appcontext
def export_taxonomy(taxonomy_code):
    from .import_export import export_taxonomy
    export_taxonomy(taxonomy_code)


@index.command('create')
@with_appcontext
def create():
    """
    Creates index on extra_data, it works only in postgresql environment.
    """
    engine = db_.engine
    if db_.session.bind.dialect.name == 'postgresql':
        with engine.connect() as connection:
            connection.execute(
                "CREATE INDEX index_extra_data ON taxonomy_term USING gin (extra_data)")
    else:
        secho("JSONB index is enabled only in postgresql dialect", fg="magenta")