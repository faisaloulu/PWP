import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from finding_job import db
from finding_job.models import Company, seek,provide,Job,Jobseeker
from finding_job.constants import *
from finding_job.utils import JobBuilder, create_error_response


class JobCollection(Resource):

    def get(self):
        body = JobBuilder()
        body.add_namespace("mumeta", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.jobcollection"))
        body.add_control("profile", JOB_PROFILE)
        body.add_control("collection", url_for("api.jobcollection"))
        body.add_control_get_companys()
        #body.add_control_get_jobs_by_company()
        body.add_control_add_job()


        db_job = Job.query.all
        if db_job is None:
            return create_error_response(
                404, "No jobs"
            )
        for db_job in Job.query.all():
            item = JobBuilder(
                name=db_job.name,
                salary=db_job.salary,
                introduction=db_job.introduction,
                applicant_number=db_job.applicant_number,
                category=db_job.category,
                region=db_job.region
            )
            item.add_control("self", url_for("api.jobitem", job=db_job.name))
            item.add_control("profile", SENSOR_PROFILE)
            body["items"].append(item)
        return Response(json.dumps(body), 200, mimetype=MASON)


class JobItem(Resource):

    def get(self, job):
        db_job = Job.query.filter_by(name=job)
        if db_loc is None:
            return create_error_response(
                404, "Not found",
                "No location was found with the name {}".format(location)
            )

        body = SensorhubBuilder(
            name=db_loc.name,
            latitude=db_loc.latitude,
            longitude=db_loc.longitude,
            altitude=db_loc.altitude,
            description=db_loc.description
        )
        body.add_namespace("senhub", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.locationitem", location=location))
        body.add_control("profile", LOCATION_PROFILE)
        body.add_control("collection", url_for("api.locationcollection"))
        if db_loc.sensor is not None:
            body.add_control(
                "senhub:sensor",
                url_for("api.sensoritem", sensor=db_loc.sensor)
            )
            body.add_control_change_sensor(location)
            body.add_control_remove_sensor(location)
        else:
            body.add_control_assign_sensor(location)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self, location):
        db_loc = Location.query.filter_by(name=location).first()
        if db_loc is None:
            return create_error_response(
                404, "Not found",
                "No location was found with the name {}".format(location)
            )

        if db_loc.sensor is not None:
            return create_error_response(
                409, "Location '{}' already contains a sensor.",
                "Use the 'senhub:change-sensor' control to change to another sensor."
            )

        try:
            validate(request.json, Location.get_pairing_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        sensor = request.json["sensor_name"]
        db_sensor = Sensor.query.filter_by(name=sensor).first()
        if db_sensor is None:
            return create_error_response(
                404, "Not found",
                "No sensor was found with the name {}".format(sensor)
            )

        db_loc.sensor = db_sensor
        try:
            db.session.commit()
        except IntegrityError as e:
            return create_error_response(
                409, "Sensor already assigned",
                "Sensor with name '{}' has already been assigned to another location.".format(sensor)
            )

        return Response(status=201, headers={
            "Location": url_for("locationsensorpairing", location=location, sensor=sensor)
        })


