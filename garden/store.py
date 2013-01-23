from zope.interface import implements
from twisted.internet import reactor, defer
from twisted.enterprise import adbapi

from garden.interface import IDataStore


sqlite = None
try:
    from pysqlite2 import dbapi2 as sqlite
except:
    pass

if not sqlite:
    import sqlite3 as sqlite



class SqliteStore(object):

    implements(IDataStore)


    def __init__(self, connstr, reactor=reactor):
        self.pool = adbapi.ConnectionPool(sqlite.__name__, connstr,
            check_same_thread=False,
            cp_min=1, cp_max=1)
        self.pool.start()
        
        self.connstr = connstr
        self.reactor = reactor
        self._initDatabase()


    def runQuery(self, qry, params=()):
        return self.pool.runQuery(qry, params)


    def _initDatabase(self):
        return self.runQuery('''create table if not exists data (
                id integer primary key,
                entrydate timestamp default current_timestamp,
                entity text,
                name text,
                version text,
                lineage text,
                value text,
                unique (entity, name, version, lineage)
            )''')


    def put(self, entity, name, version, lineage, value):
        def interaction(c):
            c.execute('''select value from data where
                entity = ?
                and name = ?
                and version = ?
                and lineage = ?''', (entity, name, version, lineage))
            result = c.fetchone()
            changed = True
            if not result:
                c.execute('''insert into data
                    (entity, name, version, lineage, value)
                    values (?, ?, ?, ?, ?)''',
                    (entity, name, version, lineage, value))
            else:
                changed = result[0] != value
                c.execute('''update data
                    set value=?
                    where
                        entity = ?
                        and name = ?
                        and version = ?
                        and lineage = ?''',
                    (value, entity, name, version, lineage))
            return {'changed': changed}
        return self.pool.runInteraction(interaction)


    def _donePutting(self, result):
        return {'changed': True}


    def get(self, entity, name=None, version=None, lineage=None):
        qry = 'select entity, name, version, lineage, value from data'
        wheres = ['entity = ?']
        args = [entity]
        if name:
            wheres.append('name = ?')
            args.append(name)
        if version:
            wheres.append('version = ?')
            args.append(version)
        if lineage:
            wheres.append('lineage = ?')
            args.append(lineage)
        qry = qry + ' where ' + ' AND '.join(wheres)
        return self.runQuery(qry, tuple(args))



class InMemoryStore(object):
    """
    I hold entity data in memory.
    """
    
    implements(IDataStore)


    def __init__(self):
        self._data = {}


    def _matchKey(self, key, entity, name=None, version=None, lineage=None):
        if key[0] != entity:
            return False
        if name is not None and key[1] != name:
            return False
        if version is not None and key[2] != version:
            return False
        if lineage is not None and key[3] != lineage:
            return False
        return True


    def get(self, entity, name=None, version=None, lineage=None):
        keys = [x for x in self._data if self._matchKey(x, entity, name, version, lineage)]
        return defer.succeed([k + (self._data[k],) for k in keys])


    def put(self, entity, name, version, lineage, value):
        old_value = self._data.get((entity, name, version, lineage), None)
        changed = value != old_value
        self._data[(entity, name, version, lineage)] = value
        return defer.succeed({'changed': changed})
