import pytest


class Student():
    firstname: str
    lastname: str
    age: int

    def __init__(self, firstname, lastname, age):
        self.firstname = firstname
        self.lastname = lastname
        self.age = age


@pytest.fixture
def default_student():
    return Student("Ivan", "Smith", 25)


def test_default_student(default_student):
    assert default_student.firstname == "Ivan", "firstname should be Ivan"
    assert default_student.lastname == "Smith"
    assert default_student.age == 25, "age should be 25"


def test_equal_or_not_equal():
    assert 3 == 3


def test_is_instance():
    assert isinstance('this is a string', str)
    assert not isinstance('10', int)


def test_boolean():
    validated = True
    assert validated is True
    assert ('hello' == 'world') is False


def test_type():
    assert type(True) is bool
    assert type('asf') is str


def test_gt_and_lt():
    assert 3 < 10
    assert 2 > -5


def test_list():
    num_list = [1, 2, 3]
    any_list = [1, 'sasfd', False]
    assert num_list == [1, 2, 3]
    assert 1 in num_list
    assert all(num_list)
    assert any(num_list)
    assert not all(any_list)
    assert any(any_list)
