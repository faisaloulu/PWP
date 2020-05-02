import json

from flask import request, Response, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from finding_job.constants import *
from finding_job.models import Company, Seek,Provide,Job,Jobseeker
from finding_job.utils import JobBuilder, create_error_response
from jsonschema import validate, ValidationError
from finding_job import db

class SeekerItem(Resource):

    def get(self):
        db_seeker = Jobseeker.query.filter_by(id=1).first()
        if db_seeker is None:
            return create_error_response(
                404, "Not found",
                "No jobseeker was found,please add a new one(you can only add one seeker)"
                "use post method, the information includes name, identify, specialty, address,"
                "phone_number, desired_position, desired_address, CV"
            )
        body = JobBuilder(
            id=db_seeker.id,
            name=db_seeker.name,
            identify=db_seeker.identify,
            specialty=db_seeker.specialty,
            address=db_seeker.address,
            phone_number=db_seeker.phone_number,
            desired_position=db_seeker.desired_position,
            desired_address=db_seeker.desired_address,
            CV=db_seeker.CV
        )
        body.add_namespace("mumeta", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.seekeritem"))
        body.add_control("profile", JOBSEEKER_PROFILE)
        body.add_control_edit_seeker()
        body.add_control_get_companys()
        body.add_control_get_jobs()
        body.add_control_get_jobs_by_seeker(db_seeker.id)
        db_job=Seek.query.filter_by(seeker_id=1).first()
        if db_job is not None:
            job_id=db_job.job_id
            company_id=Provide.query.filter_by(job_id=job_id).first().company_id
            body.add_control_delete_jobs_by_seeker(company_id=company_id,job_id=job_id)
        return Response(json.dumps(body), 200, mimetype=MASON)
    def post(self):
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Jobseeker.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))
        seeker = Jobseeker(
            name=request.json["name"],
            identify=request.json["identify"],
            specialty=request.json["specialty"],
            address=request.json["address"],
            phone_number=request.json["phone_number"],
            desired_position=request.json["desired_position"],
            desired_address=request.json["desired_address"],
            CV=request.json["CV"]
        )
        try:
            db.session.add(seeker)
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "Seeker with name '{}' already exists.".format(request.json["name"])
            )

        return Response(status=201, headers={
            "Location": url_for("api.seekeritem")
        })
    def put(self):
        db_seeker = Jobseeker.query.filter_by(id=1).first()
        if db_seeker is None:
            return create_error_response(
                404, "Not found",
            )

        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Jobseeker.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        db_seeker.name = request.json["name"],
        db_seeker.identify = request.json["identify"],
        db_seeker.specialty = request.json["specialty"],
        db_seeker.address = request.json["address"],
        db_seeker.phone_number = request.json["phone_number"],
        db_seeker.desired_position = request.json["desired_position"],
        db_seeker.desired_address = request.json["desired_address"],
        db_seeker.CV = request.json["CV"],

        try:
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "Jobseeker with name '{}' already exists.".format(request.json["name"])
            )
        return Response(status=204)
