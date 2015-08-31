import pytest


@pytest.mark.run_loop
def test_cursor(conn):
    cur = yield from conn.cursor()
    assert cur.connection is conn
    assert cur._loop, conn.loop
    assert cur.arraysize == 1
    assert cur.rowcount == -1

    r = yield from cur.setinputsizes()
    assert r is None

    yield from cur.setoutputsize()
    assert r is None
    yield from cur.close()


@pytest.mark.run_loop
def test_close(conn):
    cur = yield from conn.cursor()
    assert not cur.closed
    yield from cur.close()
    yield from cur.close()
    assert cur.closed


@pytest.mark.run_loop
def test_description(conn):
    cur = yield from conn.cursor()
    assert cur.description is None
    yield from cur.execute('SELECT 1;')
    expected = (('1', float, None, 54, 54, 0, True), )
    assert cur.description == expected
    yield from cur.close()


@pytest.mark.run_loop
def test_description_with_real_table(conn, table):
    cur = yield from conn.cursor()
    yield from cur.execute("SELECT * FROM t1;")

    expected = (('n', int, None, 10, 10, 0, True),
                ('v', str, None, 10, 10, 0, True))
    assert cur.description == expected
    yield from cur.close()


@pytest.mark.run_loop
def test_rowcount_with_table(conn, table):
    cur = yield from conn.cursor()
    yield from cur.execute("SELECT * FROM t1;")
    yield from cur.fetchall()
    # sqlite does not provide working rowcount attribute
    # http://stackoverflow.com/questions/4911404/in-pythons-sqlite3-
    # module-why-cant-cursor-rowcount-tell-me-the-number-of-ro
    assert cur.rowcount == 0
    yield from cur.close()


@pytest.mark.run_loop
def test_arraysize(conn):
    cur = yield from conn.cursor()
    assert 1 == cur.arraysize
    cur.arraysize = 10
    assert 10 == cur.arraysize
    yield from cur.close()


@pytest.mark.run_loop
def test_fetchall(conn, table):
    cur = yield from conn.cursor()
    yield from cur.execute("SELECT * FROM t1;")
    resp = yield from cur.fetchall()
    expected = [(1, '123.45'), (2, 'foo')]

    for row, exp in zip(resp, expected):
        assert exp == tuple(row)

    yield from cur.close()


@pytest.mark.run_loop
def test_fetchmany(conn, table):
    cur = yield from conn.cursor()
    yield from cur.execute("SELECT * FROM t1;")
    resp = yield from cur.fetchmany(1)
    expected = [(1, '123.45')]

    for row, exp in zip(resp, expected):
        assert exp == tuple(row)

    yield from cur.close()


@pytest.mark.run_loop
def test_fetchone(conn, table):
    cur = yield from conn.cursor()
    yield from cur.execute("SELECT * FROM t1;")
    resp = yield from cur.fetchone()
    expected = (1, '123.45')

    assert expected == tuple(resp)
    yield from cur.close()