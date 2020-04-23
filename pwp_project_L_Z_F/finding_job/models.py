import click
from flask.cli import with_appcontext
from finding_job import db

seek = db.Table("seek",
                db.Column("seeker_id", db.Integer, db.ForeignKey("seeker.id"), primary_key=True),
                db.Column("job_id", db.Integer, db.ForeignKey("job.id"), primary_key=True)
                )
provide = db.Table("provide",
                   db.Column("job_id", db.Integer, db.ForeignKey("job.id"), primary_key=True),
                   db.Column("company_id", db.Integer, db.ForeignKey("company.id"), primary_key=True)
                   )


class Jobseeker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=True)
    identify = db.Column(db.String(20), nullable=True)
    specialty = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(20), nullable=True)
    phone_number = db.Column(db.String(20), unique=True)
    desired_position = db.Column(db.String(20), nullable=True)
    desired_address = db.Column(db.String(20), nullable=True)
    CV = db.Column(db.String(400), nullable=True, unique=True)
    jobs = db.relationship("Job", secondary=seek, back_populates="jobseekers")


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    salary = db.Column(db.String(20), nullable=False)
    introduction = db.Column(db.String(20), nullable=False, unique=True)
    applicant_number = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(20), nullable=False)
    region = db.Column(db.String(20), nullable=False)
    jobseekers = db.relationship("Jobseeker", secondary=seek, back_populates="jobs")
    companys = db.relationship("Company", secondary=provide, back_populates="jobss")
    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["name", "salary","introduction","applicant_number","category","region"]
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
            "introduction":"introduction of the job",
            "type":"string"
        }
        props["applicant_number"] = {
            "introduction": "number of applicants of the job, please set it as 0 as a new one",
            "type": "integer"
        }
        props["category"] = {
            "introduction": "category of the job",
            "type": "string"
        }
        props["region"] = {
            "introduction": "region of the job",
            "type": "string"
        }
        return schema

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    address = db.Column(db.String(20), nullable=False)
    introduction = db.Column(db.String(20), nullable=False, unique=True)
    phone_number = db.Column(db.String(20), nullable=False, unique=True)
    jobss = db.relationship("Job", secondary=provide, back_populates="companys")
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

# class Sensor(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(32), nullable=False, unique=True)
#     model = db.Column(db.String(128), nullable=False)
#     location_id = db.Column(db.Integer, db.ForeignKey("location.id"), unique=True)
#
#     location = db.relationship("Location", back_populates="sensor")
#     measurements = db.relationship("Measurement", back_populates="sensor")
#     deployments = db.relationship("Deployment", secondary=deployments, back_populates="sensors")
#
#     @staticmethod
#     def get_schema():
#         schema = {
#             "type": "object",
#             "required": ["name", "model"]
#         }
#         props = schema["properties"] = {}
#         props["name"] = {
#             "description": "Sensor's unique name",
#             "type": "string"
#         }
#         props["model"] = {
#             "description": "Name of the sensor's model",
#             "type": "string"
#         }
#         return schema
#
#
# class Measurement(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     sensor_id = db.Column(db.Integer, db.ForeignKey("sensor.id", ondelete="SET NULL"))
#     value = db.Column(db.Float, nullable=False)
#     time = db.Column(db.DateTime, nullable=False)
#
#     sensor = db.relationship("Sensor", back_populates="measurements")
#
#     @staticmethod
#     def get_schema():
#         schema = {
#             "type": "object",
#             "required": ["value"]
#         }
#         props = schema["properties"] = {}
#         props["value"] = {
#             "description": "Measured value.",
#             "type": "number"
#         }
#         props["time"] = {
#             "description": "Measurement timestamp",
#             "type": "string",
#             "pattern": "^[0-9]{4}-[01][0-9]-[0-3][0-9]T[0-9]{2}:[0-5][0-9]:[0-5][0-9]Z$"
#         }
#         return schema


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
