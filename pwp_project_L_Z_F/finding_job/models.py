import click
from flask.cli import with_appcontext
from finding_job import db
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table,Column,String,create_engine,MetaData

# seek = db.Table("seek",
#                 db.Column("seeker_id", db.Integer, db.ForeignKey("jobseeker.id"), primary_key=True),
#                 db.Column("job_id", db.Integer, db.ForeignKey("job.id"), primary_key=True)
#                 )
# provide = db.Table("provide",
#                    db.Column("job_id", db.Integer, db.ForeignKey("job.id"), primary_key=True),
#                    db.Column("company_id", db.Integer, db.ForeignKey("company.id"), primary_key=True)
#                    )
class Seek(db.Model):
    seeker_id = db.Column(db.Integer,db.ForeignKey("jobseeker.id"),primary_key=True)
    job_id = db.Column(db.Integer,db.ForeignKey("job.id"),primary_key=True)
    seeker=db.relationship("Jobseeker",back_populates="seek")
    job  = db.relationship("Job",back_populates="seeks")
class Provide(db.Model):
    job_id = db.Column(db.Integer,db.ForeignKey("job.id"),primary_key=True)
    company_id = db.Column(db.Integer,db.ForeignKey("company.id"),primary_key=True)
    jobs = db.relationship("Job",back_populates="provides")
    company = db.relationship("Company",back_populates="provide")
class Jobseeker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=True,unique=True)
    identify = db.Column(db.String(20), nullable=True)
    specialty = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(20), nullable=True)
    phone_number = db.Column(db.String(20), unique=True)
    desired_position = db.Column(db.String(20), nullable=True)
    desired_address = db.Column(db.String(20), nullable=True)
    CV = db.Column(db.String(400), nullable=True, unique=True)
    seek = db.relationship("Seek", back_populates="seeker")
    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["name", "identify","specialty","address","phone_number","desired_position","desired_address","CV"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "jobseeker's unique name",
            "type": "string"
        }
        props["identify"] = {
            "description": "identify of the jobseeker",
            "type": "string"
        }
        props["specialty"] = {
            "description":"specialty of the jobseeker",
            "type":"string"
        }
        props["address"] = {
            "description": "home address of the jobseeker",
            "type": "string"
        }
        props["phone_number"] = {
            "description": "phone_number of the jobseeker",
            "type": "string"
        }
        props["desired_position"] = {
            "description": "what job the jobseeker wants",
            "type": "string"
        }
        props["desired_address"] = {
            "description": "where the jobseeker wants to work",
            "type": "string"
        }
        props["CV"] = {
            "description": "CV of the jobseeker",
            "type": "string"
        }
        return schema

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    salary = db.Column(db.String(20), nullable=False)
    introduction = db.Column(db.String(20), nullable=False, unique=True)
    applicant_number = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(20), nullable=False)
    region = db.Column(db.String(20), nullable=False)
    seeks = db.relationship("Seek", back_populates="job")
    provides = db.relationship("Provide",  back_populates="jobs")
    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["name", "salary","introduction","category","region"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "job's unique name",
            "type": "string"
        }
        props["salary"] = {
            "description": "salary of the job",
            "type": "string"
        }
        props["introduction"] = {
            "description":"introduction of the job",
            "type":"string"
        }
        props["category"] = {
            "description": "category of the job",
            "type": "string"
        }
        props["region"] = {
            "description": "region of the job",
            "type": "string"
        }
        return schema

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    address = db.Column(db.String(20), nullable=False)
    introduction = db.Column(db.String(20), nullable=False, unique=True)
    phone_number = db.Column(db.String(20), nullable=False, unique=True)
    provide = db.relationship("Provide", back_populates="company")
    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["name","address","introduction","phone_number"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "name of the company",
            "type": "string"
        }
        props["address"] = {
            "description": "address of the company",
            "type": "string",
        }
        props["introduction"] = {
            "description": "introduction of the company",
            "type": "string",
        }
        props["phone_number"] = {
            "description": "telephone of the company",
            "type": "string",
        }
        return schema



@click.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()


#@click.command("testgen")
#@with_appcontext
# def generate_test_data():
#     import datetime
#     import random
#     s = Job(
#         name="test-sensor-1",
#         model="testsensor"
#     )
#     now = datetime.datetime.now()
#     interval = datetime.timedelta(seconds=10)
#     for i in range(1000):
#         m = Measurement(
#             value=round(random.random() * 100, 2),
#             time=now
#         )
#         now += interval
#         s.measurements.append(m)
#
#     db.session.add(s)
#     db.session.commit()
