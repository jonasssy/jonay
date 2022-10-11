#!/usr/bin/python3

import time
from flask import url_for
from .util import live_server_setup

def set_original_response():
    test_return_data = """
        A few new lines
        Where there is more lines originally
    """

    with open("test-datastore/endpoint-content.txt", "w") as f:
        f.write(test_return_data)

def set_delete_response():
    test_return_data = """
        A few new lines
    """

    with open("test-datastore/endpoint-content.txt", "w") as f:
        f.write(test_return_data)

def test_diff_filtering_no_del(client, live_server):
    live_server_setup(live_server)

    sleep_time_for_fetch_thread = 3

    set_original_response()
    # Give the endpoint time to spin up
    time.sleep(1)

    # Add our URL to the import page
    test_url = url_for('test_endpoint', _external=True)
    res = client.post(
        url_for("import_page"),
        data={"urls": test_url},
        follow_redirects=True
    )

    assert b"1 Imported" in res.data
    time.sleep(sleep_time_for_fetch_thread)

    # Add our URL to the import page
    res = client.post(
        url_for("edit_page", uuid="first"),
        data={"trigger_add": "y",
              "trigger_del": "n",
              "url": test_url,
              "fetch_backend": "html_requests"},
        follow_redirects=True
    )
    assert b"Updated watch." in res.data
    assert b'unviewed' not in res.data

    #  Make an delete change
    set_delete_response()

    time.sleep(sleep_time_for_fetch_thread)
    # Trigger a check
    client.get(url_for("form_watch_checknow"), follow_redirects=True)

    # Give the thread time to pick it up
    time.sleep(sleep_time_for_fetch_thread)

    # We should NOT see the change
    res = client.get(url_for("index"))
    assert b'unviewed' not in res.data

    #  Make an delete change
    set_original_response()

    time.sleep(sleep_time_for_fetch_thread)
    # Trigger a check
    client.get(url_for("form_watch_checknow"), follow_redirects=True)

    # Give the thread time to pick it up
    time.sleep(sleep_time_for_fetch_thread)

    # We should see the change
    res = client.get(url_for("index"))
    assert b'unviewed' in res.data
