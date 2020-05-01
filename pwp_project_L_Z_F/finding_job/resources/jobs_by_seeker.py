import json

from flask import request, Response, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from finding_job.constants import *
from finding_job.models import Company, seek, provide, Job, Jobseeker
from finding_job.utils import JobBuilder, create_error_response
from jsonschema import validate, ValidationError
from finding_job import db


class Jobs_By_Seeker(Resource):
    def get(self):
        body = JobBuilder()
        body["items"] = []
        body.add_namespace("mumeta", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.jobs_by_seeker"))
        body.add_control("profile", JOBSBYSEEKER_PROFILE)
        body.add_control_get_seeker()
        db_jobs_by_seeker = seek.query.all
        if db_jobs_by_seeker is None:
            return create_error_response(
                404, "Not found",
            )
        for job_id in db_jobs_by_seeker:
            db_job = Job.query.filter_by(job_id)
            item = JobBuilder(
                id=db_job.id,
                name=db_job.name,
                salary=db_job.salary,
                introduction=db_job.introduction,
                applicant_number=db_job.applicant_number,
                category=db_job.category,
                region=db_job.region
            )
            item.add_control("self", url_for("api.jobs_by_seeker"))
            item.add_control("profile", JOBSBYSEEKER_PROFILE)
            item.add_control_delete_jobs_by_seeker(job_id)
            body["items"].append(item)
        return Response(json.dumps(body), 200, mimetype=MASON)

    def delete(self, job_id):
        db_jobs_by_seeker = seek.query.filter_by(job_id=job_id).first()
        if db_jobs_by_seeker is None:
            return create_error_response(
                404, "Not found",
                "No jobs_by_seeker was found with the name {}".format(job_id)
            )
        db_job = Job.query.filter_by(id=job_id).first()
        db_job.applicant_number -= 1
        db.session.delete(db_jobs_by_seeker)
        db.session.commit()

        return Response(status=204)


class Seekers_By_Job(Resource):
    def get(self, job_id):
        body = JobBuilder()
        body["items"] = []
        body.add_namespace("mumeta", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.seekers_by_job", job_id=job_id))
        body.add_control("profile", SEEKERSBYJOB_PROFILE)
        body.add_control_add_seekers_by_job(job_id)
        db_seekers_by_job = seek.query.filter_by(job_id),
        if db_seekers_by_job is None:
            return create_error_response(
                404, "Not found",
            )
        db_seeker = Jobseeker.query.filter_by(db_seekers_by_job.seeker_id)
        for db_seeker1 in db_seeker:
            item = JobBuilder(
                id=db_seeker1.id,
                name=db_seeker1.name,
                identify=db_seeker1.identify,
                specialty=db_seeker1.specialty,
                address=db_seeker1.address,
                phone_number=db_seeker1.phone_number,
                desired_position=db_seeker1.desired_position,
                desired_address=db_seeker1.desired_address,
                CV=db_seeker1.CV
            )
            item.add_control("self", url_for("api.seekers_by_job", job_id=job_id))
            item.add_control("profile", SEEKERSBYJOB_PROFILE)
            item.add_control_get_job(job_id)
            body["items"].append(item)
        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self,job_id):
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )
        seekers_by_job = seek(
            seeker_id=request.json["seeker_id"],
            job_id=request.json["job_id"]
        )
        seeker_id = request.json["job_id"]
        db_job = Job.query.filter_by(id=job_id).first()
        db_job.applicant_number += 1
        try:
            db.session.add(seekers_by_job)
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "seeker_by_job with id '{}' already exists.".format(seeker_id, job_id)
            )
        return Response(status=201, headers={
            "Location": url_for("api.seekers_by_job", seeker_id=seeker_id, job_id=job_id)
        })
    # def delete(self, seeker_id, job_id):
    #     db_seekers_by_job = seek.query.filter_by(seeker_id=seeker_id, job_id=job_id).first()
    #     if db_seekers_by_job is None:
    #         return create_error_response(
    #             404, "Not found",
    #             "No seekers_by_job was found with the id {}".format(seeker_id, job_id)
    #         )
    #     db.session.delete(db_seekers_by_job)
    #     db.session.commit()
    #     return Response(status=204)
