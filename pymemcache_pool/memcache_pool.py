import logging
import pickle
from pymemcache.client import Client
from gevent.queue import Queue
from contextlib import contextmanager

log = logging.getLogger(__name__)


def pickle_serializer(key, value):
    if type(value) == str:
        return value, 1
    return pickle.dumps(value), 2


def pickle_deserializer(key, value, flags):
    if flags == 1:
        return value
    if flags == 2:
        return pickle.loads(value)
    raise Exception("Unknown serialization format")


class PyMemcachePool(object):
    """
    Synchronized pool for memcached clients
    """
    def __init__(self, host=None, port=None, serializer=pickle_serializer, deserializer=pickle_deserializer,
                 maxsize=100, timeout=15):
        """
        Setup a new empty pool
        """
        if not isinstance(maxsize, (int, long)):
            raise Exception('Maxsize must be an integer or long, got: %s' % (maxsize, ))
        if not isinstance(timeout, (int, long)):
            raise Exception('Timeout must be an integer or long, got: %s' % (timeout, ))
        self._host = host
        self._port = port
        self._maxsize = maxsize
        self._timeout = timeout
        self._serializer = serializer
        self._deserializer = deserializer
        self._pool = Queue()
        self._size = 0

    def set_host_and_port(self, host, port):
        self._host = host
        self._port = port

    @contextmanager
    def client(self):
        try:
            client = self.get_client()
            yield client
        except:
            raise
        finally:
            self.return_client(client)

    def get_client(self):
        """
        Get an existing client, or if none are available create a new
        one. If the pool is at maxsize, return nothing.
        """
        pool = self._pool
        log.debug("Attempting to get client from pool size=%s queue_size=%s" % (self._size, pool.qsize()))
        if self._size >= self._maxsize or pool.qsize():
            client = None
            try:
                client = pool.get(timeout=2)
                if client:
                    client.stats()
            except:
                log.error("Re-connect to memcached failed!", exc_info=True)
                if client is not None:
                    client.close()
                self._size -= 1
                return self.get_client()
            else:
                return client
        else:
            self._size += 1
            try:
                new_item = self._create_client()
            except:
                self._size -= 1
                raise
            return new_item

    def return_client(self, client):
        """
        Return a client to the pool
        """
        if client is not None:
            try:
                client.stats()
            except:
                log.debug("Returned bad connection to pool")
                self._size -= 1
            else:
                log.debug("Returned OK client")
                self._pool.put(client)

    def shutdown(self):
        """
        Shutdown the clients in the pool.
        """
        while not self._pool.empty():
            client = self._pool.get_nowait()
            try:
                client.close()
            except Exception:
                log.error("Unable to close client")
                pass

    def _create_client(self):
        """
        Create a new client using smart_client to get connection details
        """
        log.debug("Creating new memcached client")
        try:
            client = Client((self._host, self._port),
                            serializer=self._serializer,
                            deserializer=self._deserializer, no_delay=True)
            client._connect()
        except:
            log.debug("Unable to connect to memcached!", exc_info=True)
            raise
        return client
