# manage.py

from flask.ext.script import Manager
from flask_cassandra import CassandraCluster
import time

from srunner import app

manager = Manager(app)
# @TODO - hook this up to docker compose post boot task
# @TODO -
@manager.command
def create_sessions_schema():
    cassandra = CassandraCluster()
    app.config['CASSANDRA_NODES'] = ['cassandra']  # can be a string or list of nodes
    print "Connecting to Cassandra cluster..."
    # @todo: make this clever enough to try to connect and then retry exponetially.
    time.sleep(30)
    session = cassandra.connect()
    if app.debug:
        cql = "CREATE KEYSPACE IF NOT EXISTS sessionstore WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };"
    else:
        cql = "CREATE KEYSPACE IF NOT EXISTS sessionstore WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 3 };"
    r = session.execute(cql)
    print "Creating keyspace 'sessionstore'"
    print "Creating table sessions."
    cql_table = """CREATE TABLE IF NOT EXISTS SessionStore.sessions (
              quest_session_id varchar,
              data text,
            session_id varchar,
            PRIMARY KEY (quest_session_id)
            ) ;"""
    table_create = session.execute(cql_table)
    print str(table_create)
    print "[FINISH]"

if __name__ == "__main__":
    manager.run()
