import json
import os
import pytest
import tempfile
from jsonschema import validate
from sqlalchemy.engine import Engine
from sqlalchemy import event
import sys
sys.path.append('../')
from finding_job import create_app, db
from finding_job.models import Seek, Provide, Jobseeker, Job,Company

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

@pytest.fixture
def client():
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
    }
    app=create_app(config)
    with app.app_context():
        db.create_all()
        _populate_db()

    yield app.test_client()

    os.close(db_fd)
    os.unlink(db_fname)

def _populate_db():
    for i in range(1, 4):
        s = Company(
            name="test-company-{}".format(i),
            address="test-address-{}".format(i),
            introduction="test-introduction-{}".format(i),
            phone_number="test-phone_number-{}".format(i),
        )
        db.session.add(s)
    db.session.commit()


def _get_Company_json(number=1):
    """
    Creates a valid sensor JSON object to be used for PUT and POST tests.
    """

    return {"name": "extra-company-{}".format(number), "address": "extra-address-{}".format(number),"introduction":"extra-introduction-{}".format(number),"phone_number":"extra-phone_number-{}".format(number)}


def _check_namespace(client, response):
    """
    Checks that the "mumeta" namespace is found from the response body, and
    that its "name" attribute is a URL that can be accessed.
    """

    ns_href = response["@namespaces"]["mumeta"]["name"]
    resp = client.get(ns_href)
    assert resp.status_code == 200


def _check_control_get_method(ctrl, client, obj):
    """
    Checks a GET type control from a JSON object be it root document or an item
    in a collection. Also checks that the URL of the control can be accessed.
    """

    href = obj["@controls"][ctrl]["href"]
    resp = client.get(href)
    assert resp.status_code == 200


def _check_control_delete_method(ctrl, client, obj):
    """
    Checks a DELETE type control from a JSON object be it root document or an
    item in a collection. Checks the contrl's method in addition to its "href".
    Also checks that using the control results in the correct status code of 204.
    """

    href = obj["@controls"][ctrl]["href"]
    method = obj["@controls"][ctrl]["method"].lower()
    assert method == "delete"
    resp = client.delete(href)
    assert resp.status_code == 204


def _check_control_put_method(ctrl, client, obj):
    """
    Checks a PUT type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid sensor against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 204.
    """

    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "put"
    assert encoding == "json"
    body = _get_Company_json()
    body["name"] = obj["name"]
    validate(body, schema)
    resp = client.put(href, json=body)
    assert resp.status_code == 204


def _check_control_post_method(ctrl, client, obj):
    """
    Checks a POST type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid sensor against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 201.
    """

    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "post"
    assert encoding == "json"
    body = _get_Company_json()
    validate(body, schema)
    resp = client.post(href, json=body)
    assert resp.status_code == 201


class TestCompanyCollection(object):
    RESOURCE_URL = "http://127.0.0.1:5000/api/companys/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        _check_control_post_method("mumeta:add-company", client, body)
        assert len(body["items"]) == 3
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)

    def test_post(self, client):
        valid = _get_Company_json()

        # test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        #assert resp.headers["Location"].endswith(self.RESOURCE_URL + valid["name"] + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200

        # send same data again for 409
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

        # remove model field for 400
        valid.pop("address")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400


class TestCompanyItem(object):
    RESOURCE_URL = "http://127.0.0.1:5000/api/companys/1/"
    INVALID_URL = "http://127.0.0.1:5000/api/companys/non-sensor-x/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("collection", client, body)
        _check_control_put_method("mumeta:company-edit", client, body)
        _check_control_delete_method("mumeta:company-delete", client, body)
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        valid = _get_Company_json()

        def test_put(self, client):
            valid = _get_Company_json()

            # test with wrong content type
            resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
            assert resp.status_code == 415

            resp = client.put(self.INVALID_URL, json=valid)
            assert resp.status_code == 404

            # test with another sensor's name
            valid["name"] = "test-company-2"
            resp = client.put(self.RESOURCE_URL, json=valid)
            assert resp.status_code == 409

            # test with valid (only change model)
            valid["name"] = "test-company-1"
            resp = client.put(self.RESOURCE_URL, json=valid)
            assert resp.status_code == 204

            # remove field for 400
            valid.pop("address")
            resp = client.put(self.RESOURCE_URL, json=valid)
            assert resp.status_code == 400

    def test_delete(self, client):
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404

















