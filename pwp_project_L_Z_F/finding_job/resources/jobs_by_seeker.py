import json

from flask import request, Response, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from finding_job.constants import *
from finding_job.models import Company, Seek, Provide, Job, Jobseeker
from finding_job.utils import JobBuilder, create_error_response
from jsonschema import validate, ValidationError
from finding_job import db


class Jobs_By_Seeker(Resource):
    def get(self,seeker_id):
        body = JobBuilder()
        body["items"] = []
        body.add_namespace("mumeta", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.jobs_by_seeker",seeker_id=seeker_id))
        body.add_control("profile", JOBSBYSEEKER_PROFILE)
        body.add_control_get_seeker()
        db_jobs_by_seeker = Seek.query.filter_by(seeker_id=seeker_id)
        if db_jobs_by_seeker is None:
            return create_error_response(
                404, "Not found",
            )
        for job_id in db_jobs_by_seeker:
            job_id=job_id.job_id
            db_job = Job.query.filter_by(id=job_id).first()
            item = JobBuilder(
                id=db_job.id,
                name=db_job.name,
                salary=db_job.salary,
                introduction=db_job.introduction,
                applicant_number=db_job.applicant_number,
                category=db_job.category,
                region=db_job.region
            )
            item.add_control("self", url_for("api.jobs_by_seeker",seeker_id=seeker_id))
            item.add_control("profile", JOBSBYSEEKER_PROFILE)
            item.add_control_delete_jobs_by_seeker(seeker_id,job_id)
            body["items"].append(item)
        return Response(json.dumps(body), 200, mimetype=MASON)

    # def delete(self,seeker_id, job_id):
    #     db_jobs_by_seeker = Seek.query.filter_by(job_id=job_id).first()
    #     if db_jobs_by_seeker is None:
    #         return create_error_response(
    #             404, "Not found",
    #             "No jobs_by_seeker was found with the name {}".format(job_id)
    #         )
    #     db_job = Job.query.filter_by(id=job_id).first()
    #     db_job.applicant_number -= 1
    #     db.session.delete(db_jobs_by_seeker)
    #     db.session.commit()
    #
    #     return Response(status=204)


class Seekers_By_Job(Resource):
    def get(self, company_id,job_id):
        body = JobBuilder()
        body["items"] = []
        body.add_namespace("mumeta", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.seekers_by_job", company_id=company_id,job_id=job_id))
        body.add_control("profile", SEEKERSBYJOB_PROFILE)
        #body.add_control_add_seekers_by_job(company_id=company_id,job_id=job_id)
        #db_seekers_by_job = Seek.query.filter_by(job_id=job_id).first(),
        db_seekers_by_job = Seek.query.filter_by(job_id=job_id).first()
        if db_seekers_by_job is None:
            return create_error_response(
                404, "Not found",
                "No one applied for it until now"
            )
        db_seeker = Jobseeker.query.filter_by(id=db_seekers_by_job.seeker_id)
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
            item.add_control_get_job(company_id=company_id,job_id=job_id)
            body["items"].append(item)
        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self,company_id,job_id):
        # if not request.json:
        #     return create_error_response(
        #         415, "Unsupported media type",
        #         "Requests must be JSON"
        #     )
        seekers_by_job = Seek(
            seeker_id=1,
            job_id=job_id,
        )
        company_id = Provide.query.filter_by(job_id=job_id).first().company_id
        db_job = Job.query.filter_by(id=job_id).first()
        db_job.applicant_number += 1
        try:
            db.session.add(seekers_by_job)
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "seeker_by_job with id '{}' already exists.".format(job_id)
            )
        return Response(status=201, headers={
            "Location": url_for("api.seekers_by_job", company_id=company_id, job_id=job_id,seeker_id=1,)
        })

    def delete(self,company_id, job_id):
        db_jobs_by_seeker = Seek.query.filter_by(job_id=job_id).first()
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
