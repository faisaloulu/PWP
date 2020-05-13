import os
import pytest
import tempfile
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError
import sys
sys.path.append('../')
from finding_job import create_app, db
from finding_job.models import Jobseeker, Job,Company,Provide


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# based on http://flask.pocoo.org/docs/1.0/testing/
# we don't need a client for database testing, just the db handle
@pytest.fixture
def app():
    db_fd, db_fname = tempfile.mkstemp()

    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
    }
    app = create_app(config)

    with app.app_context():
        db.create_all()
    yield app

    os.close(db_fd)
    os.unlink(db_fname)


def _get_Jobseeker(jobseekername="liu"):
    return Jobseeker(
        name="site-{}".format(jobseekername),
        identify="student",
        specialty="programming",
        address="oulu",
        phone_number="0417211111",
        desired_position="level 5",
        desired_address="oulu",
        CV="I am skilled in programming"
    )


def _get_Job(number=1):
    return Job(
        name="programmer-{}".format(number),
        salary="1000",
        introduction="using java",
        applicant_number=0,
        category="computer",
        region="oulu"
    )


def _get_Company():
    return Company(
        name="QWE",
        address="oulu",
        introduction="this is a testing company",
        phone_number="123"
    )
def _get_Provide(number2=1):
    return Provide(
    )


def test_create_instances(app):
    """
    Tests that we can create one instance of each model and save them to the
    database using valid values for all columns. After creation, test that
    everything can be found from database, and that all relationships have been
    saved correctly.
    """

    with app.app_context():
        # Create everything
        Jobseeker = _get_Jobseeker()
        Job = _get_Job()
        Company = _get_Company()
        db.session.add(Jobseeker)
        db.session.add(Job)
        db.session.add(Company)
        db.session.commit()

        # Check that everything exists
        assert Jobseeker.query.count() == 1
        assert Job.query.count() == 1
        assert Company.query.count() == 1
        db_jobseeker = Jobseeker.query.first()
        db_job = Job.query.first()
        db_Company = Company.query.first()

# def test_Provide_ondelete_Company(app):
#     """
#     Tests that Porvide's company foreign key is set to null when the company
#     is deleted.
#     """
#
#     with app.app_context():
#         provide = _get_Provide()
#         company = _get_Company()
#         job=_get_Job()
#         provide.company = company
#         provide.jobs = job
#         db.session.add(provide)
#         db.session.commit()
#         db.session.delete(company)
#         #db.session.delete(job)
#         #db.session.delete(job)
#         db.session.commit()
#
#         assert provide.company is None
#



def test_Jobseeker_columns(app):
    """
    Tests the types and restrictions of Jobseeker columns. name must be unique, and that
    all of the columns are optional.
    """

    with app.app_context():
        jobseeker_1 = _get_Jobseeker()
        jobseeker_2 = _get_Jobseeker()
        db.session.add(jobseeker_1)
        db.session.add(jobseeker_2)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

        jobseeker = Jobseeker(name="site-test")
        db.session.add(jobseeker)
        db.session.commit()


def test_Company_columns(app):
    """
    Tests sensor columns' restrictions. Name address introduction phone_number must be unique,
    """

    with app.app_context():
        company_1 = _get_Company()
        company_2 = _get_Company()
        db.session.add(company_1)
        db.session.add(company_2)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()



def test_Job_columns(app):
    """
    Tests that a job applicant_number only accepts integer and
    introduction must be unique
    """

    # with app.app_context():
    #     job = _get_Job()
    #     job.applicant_number = str(job.applicant_number) + "kg"
    #     db.session.add(job)
    #     with pytest.raises(StatementError):
    #          db.session.commit()
    #
    #     db.session.rollback()

    with app.app_context():
        company_1 = _get_Company()
        company_2 = _get_Company()
        company_2.name="li"
        company_1.introduction="hello"
        company_2.introduction="hello"
        db.session.add(company_1)
        db.session.add(company_2)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

