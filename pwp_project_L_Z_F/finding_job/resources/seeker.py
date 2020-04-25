import json

from flask import request, Response, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from finding_job.constants import *
from finding_job.models import Company, seek,provide,Job,Jobseeker
from finding_job.utils import JobBuilder, create_error_response
from jsonschema import validate, ValidationError
from finding_job import db

class SeekerItem(Resource):

    def get(self):
        db_seeker = Jobseeker.query.all
        if db_seeker is None:
            return create_error_response(
                404, "Not found",
                "No jobseeker was found with the name {}"
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
        body.add_control("self", url_for("api.seekeritem", name=seeker))
        body.add_control("profile", JOBSEEKER_PROFILE)
        body.add_control_edit_seeker()
        body.add_control_get_companys()
        return Response(json.dumps(body), 200, mimetype=MASON)
    def put(self):
        db_seeker = Jobseeker.query.filter_by(name=seeker).first()
        if db_seeker is None:
            return create_error_response(
                404, "Not found",
                "No jobseeker was found with the name {}".format(seeker)
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
