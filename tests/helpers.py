import psycopg


class DummyCursor:
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail
        self.executed = None
        self.sql = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass

    def execute(self, sql, params=None):
        if self.should_fail:
            raise psycopg.Error("boom")
        self.sql = sql
        if params is not None:
            self.executed = (sql, params)


class DummyConnection:
    def __init__(self, cursor: DummyCursor):
        self.cursor_obj = cursor
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def cursor(self):
        return self.cursor_obj

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
