Ran out of time to make it pretty. :)


Running the code:
    PYTHONPATH=. python tests/schema_test.py


Paths:
    project/clockmap.py:
        Implements the consistent hash algorithm.

    project/storage.py:
        Bind clockmap to sqlite3, ultra basic sharded model classes.

    project/schema.py:
        Bind storage.py to our demo 4/6-way sharded comment models.

    tests/storage_test.py:
        Fill SQlite3 with 1024 dummy comments, count them, rebalance, count
        them again.
