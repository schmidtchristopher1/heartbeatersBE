import pytest
from app.utilities.util import Util
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True


def test_email_regex():
    assert Util.check_email_address("test@lasld.cos")
    assert not Util.check_email_address("test@lasld")
    assert not Util.check_email_address("test@lasld.")
    assert Util.check_email_address("test@lasld.c")
    assert not Util.check_email_address("@gmail.com")
    assert not Util.check_email_address("test@gmail")
    assert not Util.check_email_address("test@gmail.")
    assert not Util.check_email_address("test@.com")
    assert not Util.check_email_address("test@")
    assert not Util.check_email_address("test")
    assert not Util.check_email_address("test@.com")
    assert Util.check_email_address("test@user.sk")
