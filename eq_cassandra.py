import time
import os
from cassandra.cluster import NoHostAvailable, Cluster

cassandra_nodes = [os.environ.get('CASSANDRA_NODE', 'cassandra')]


def connect_to_cassandra(keyspace=None):
    attempt = 0
    while True:
        try:
            print("Connecting to cassandra")
            cassandra_cluster = Cluster(cassandra_nodes)
            cassandra_session = cassandra_cluster.connect()
            break
        except NoHostAvailable:
            if attempt < 30:
                print("Trying cassandra connection, attempt number {attempt}".format(attempt=attempt))
                attempt += 1
                time.sleep(attempt)
            else:
                raise
    if keyspace:
        cassandra_session.set_keyspace(keyspace)
    return cassandra_cluster, cassandra_session


def create_cassandra_schema(cassandra_session):
    print("Creating keyspace sessionstore")
    cql = "CREATE KEYSPACE IF NOT EXISTS sessionstore WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };"

    cassandra_session.execute(cql)
    print("Creating table sessions.")
    cql_table = """CREATE TABLE IF NOT EXISTS SessionStore.sessions (
                    quest_session_id varchar,
                    data text,
                    session_id varchar,
                    PRIMARY KEY (quest_session_id)
                ) ;"""
    cassandra_session.execute(cql_table)


if __name__ == '__main__':
    cassandra_cluster, cassandra_session = connect_to_cassandra()
    create_cassandra_schema(cassandra_session)
    cassandra_cluster.shutdown()
