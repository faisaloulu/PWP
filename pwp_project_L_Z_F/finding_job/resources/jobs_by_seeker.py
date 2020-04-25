import json

from flask import request, Response, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from finding_job.constants import *
from finding_job.models import Company, seek,provide,Job,Jobseeker
from finding_job.utils import JobBuilder, create_error_response
from jsonschema import validate, ValidationError
from finding_job import db

class Jobs_By_Seeker(Resource):
    def get(self):
        db_jobs_by_seeker = seek.query.all
        if db_jobs_by_seeker is None:
            return create_error_response(
                404, "Not found",
            )
        body = JobBuilder(
            seeker_name=seeker["name"],
            job_name=job["name"]
        )
        body.add_namespace("mumeta", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.jobs_by_seeker", seeker=seeker,job=job))
        body.add_control("profile", JOBSBYSEEKER_PROFILE_PROFILE)
        body.add_control_add_jobs_by_seeker(seeker,job)
        body.add_control_delete_jobs_by_seeker(seeker,job)
        body.add_control_get_job(job)
        body.add_control_get_seeker(seeker)
        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self,seeker_id,job_id):
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )
        jobs_by_seeker = seek(
            seeker_id=seeker_id,
            job_id=job_id
        )
        try:
            db.session.add(jobs_by_seeker)
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "jobs_by_seeker with name '{}' already exists.".format(jobs_by_seeker)
            )
        return Response(status=201, headers={
            "Location": url_for("api.Jobs_By_Seeker", seeker_id=seeker_id,job_id=job_id)
        })
    def delete(self, seeker_id,job_id):
        db_jobs_by_seeker = seek.query.filter_by(seeker_id=seeker_id, job_id=job_id).first()
        if db_jobs_by_seeker is None:
            return create_error_response(
                404, "Not found",
                "No jobs_by_seeker was found with the name {}".format(seeker_id,job_id)
            )
        db.session.delete(db_jobs_by_seeker)
        db.session.commit()
        return Response(status=204)