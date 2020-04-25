import json

from flask import request, Response, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from finding_job.constants import *
from finding_job.models import Company, seek,provide,Job,Jobseeker
from finding_job.utils import JobBuilder, create_error_response
from jsonschema import validate, ValidationError
from finding_job import db

class Jobs_By_Company(Resource):
    def get(self,company_id):
        db_jobs_by_company = provide.query.filter_by(company_id=company_id)
        if db_jobs_by_company is None:
            return create_error_response(
                404, "Not found",
            )
        for job_id in db_jobs_by_company.job_id:
            db_job = Job.query.filter_by(job_id).first()
            item = JobBuilder(
                id = db_job.id,
                name=db_job.name,
                salary=db_job.salary,
                introduction=db_job.introduction,
                applicant_number=db_job.applicant_number,
                category=db_job.category,
                region=db_job.region
            )
            item.add_control("self", url_for("api.jobs_by_company", company_id=db_job.id))
            item.add_control("profile", JOBSBYCOMPANY_PROFILE)
            body["items"].append(item)
        return Response(json.dumps(body), 200, mimetype=MASON)


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