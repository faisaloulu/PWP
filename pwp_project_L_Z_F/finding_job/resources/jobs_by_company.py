import json

from flask import request, Response, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from finding_job.constants import *
from finding_job.models import Company, seek,provide,Job,Jobseeker
from finding_job.utils import JobBuilder, create_error_response
from jsonschema import validate, ValidationError
from finding_job import db

class Jobs_By_Company(Resource):
    def get(self,company_id):
        body = JobBuilder()
        body["items"] = []
        body.add_namespace("mumeta", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.jobs_by_company", company_id=company_id))
        body.add_control("profile", JOBSBYCOMPANY_PROFILE)
        body.add_control_get_company(company_id)
        body.add_control_get_jobs()
        db_jobs_by_company = Session.query(provide).filter_by(company_id)
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
            item.add_control("self", url_for("api.jobs_by_company", company_id=company_id))
            item.add_control("profile", JOBSBYCOMPANY_PROFILE)
            item.add_control_get_job(job_id)
            body["items"].append(item)
        body.add_control_add_jobs_by_company(company_id)
        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self,company_id):
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )
        job = Job(
            name=request.json["name"],
            salary=request.json["salary"],
            introduction=request.json["introduction"],
            applicant_number=0,
            category=request.json["category"],
            region=request.json["region"]
        )
        try:
            db.session.add(job)
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "Job with introduction '{}' already exists.".format(request.json["introduction"])
            )
        introduction=request.json["introduction"]
        job_id = Job.query.filter_by(introduction=introduction).id
        jobs_by_company = provide(
            job_id=job_id,
            company_id=company_id,
        )
        try:
            db.session.add(jobs_by_company)
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "Company with id '{}' already exists.".format(request.json["job_id"],request.json["company_id"])
            )
        return Response(status=201, headers={
            "Location": url_for("api.jobs_by_company", company_id=company_id,job_id=job_id)
        })