import json
from flask import Response, request, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from jsonschema import validate, ValidationError
from finding_job import db
from finding_job.models import Company, seek,provide,Job,Jobseeker
from finding_job.constants import *
from finding_job.utils import JobBuilder, create_error_response


class JobCollection(Resource):

    def get(self):
        body = JobBuilder()
        body["items"] = []
        body.add_namespace("mumeta", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.jobcollection"))
        body.add_control("profile", JOB_PROFILE)
        body.add_control("collection", url_for("api.jobcollection"))
        body.add_control_get_companys()


        db_job = Job.query.all
        if db_job is None:
            return create_error_response(
                404, "Not found","No jobs"
            )
        for db_job in Job.query.all():
            item = JobBuilder(
                id=db_job.id,
                name=db_job.name,
                salary=db_job.salary,
                introduction=db_job.introduction,
                applicant_number=db_job.applicant_number,
                category=db_job.category,
                region=db_job.region
            )
            item.add_control("self", url_for("api.jobitem", job_id=db_job.id))
            item.add_control("profile", JOB_PROFILE)
            db_company = provide.query.filter_by(db_job.id)
            company_id = db_company.company_id
            item.add_control_get_jobs_by_company(company_id)
            body["items"].append(item)
        return Response(json.dumps(body), 200, mimetype=MASON)
    def post(self):
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Job.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))
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
                "Company with introduction '{}' already exists.".format(request.json["introduction"])
            )
        return Response(status=201, headers={
            "Location": url_for("api.jobitem", job=request.json["name"])
        })


class JobItem(Resource):

    def get(self, job_id):
        db_job = Job.query.filter_by(id=job_id).first()
        if db_job is None:
            return create_error_response(
                404, "Not found",
                "No job was found with the id {}".format(job_id)
            )

        body = JobBuilder(
            id=db_job.id,
            name=db_job.name,
            salary=db_job.salary,
            introduction=db_job.introduction,
            applicant_number=db_job.applicant_number,
            category=db_job.category,
            region=db_job.region
        )
        body.add_namespace("mumeta", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.jobitem",id=job_id))
        body.add_control("profile", JOB_PROFILE)
        body.add_control("collection", url_for("api.jobcollection"))

        body.add_control_edit_job(job_id)
        body.add_control_get_jobs()
        db_company = provide.query.filter_by(job_id)
        company_id = db_company.company_id
        body.add_control_delete_job(company_id, job_id)
        body.add_control_get_jobs_by_company(company_id)
        body.add_control_add_seekers_by_job(job_id)
        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self,job_id):
        db_job = Job.query.filter_by(id=job_id).first()
        if db_job is None:
            return create_error_response(
                404, "Not found",
                "No job was found with the id {}".format(job_id)
            )

        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Job.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        db_job.name = request.json["name"]
        db_job.salary = request.json["salary"]
        db_job.introduction = request.json["introduction"]
        db_job.category = request.json["category"]
        db_job.region = request.json["region"]

        try:
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "Job with id '{}' already exists.".format(job_id)
            )
        return Response(status=204)

    def delete(self, company_id,job_id):
        db_job = Job.query.filter_by(id=job_id).first()
        if db_job is None:
            return create_error_response(
                404, "Not found",
                "No job was found with the id {}".format(job_id)
            )

        db.session.delete(db_job)
        db.session.commit()
        db_job1 = provide.query.filter_by(job_id=job_id,company_id=company_id)
        db.session.delete(db_job1)
        db.session.commit()
        return Response(status=204)


