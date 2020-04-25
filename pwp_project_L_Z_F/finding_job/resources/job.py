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
                404, "Not found","No jobs"
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
            item.add_control("profile", JOB_PROFILE)
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
            applicant_number=request.json["applicant_number"],
            category=request.json["category"],
            region=request.json["region"]
        )
        try:
            db.session.add(job)
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "Company with name '{}' already exists.".format(request.json["name"])
            )

        return Response(status=201, headers={
            "Location": url_for("api.JobItem", job=request.json["name"])
        })


class JobItem(Resource):

    def get(self, job):
        db_job = Job.query.filter_by(name=job).first()
        if db_job is None:
            return create_error_response(
                404, "Not found",
                "No job was found with the name {}".format(job)
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
        body.add_control("self", url_for("api.jobitem", name=job))
        body.add_control("profile", COMPANY_PROFILE)
        body.add_control("collection", url_for("api.jobcollection"))
        body.add_control_delete_job(job)
        body.add_control_edit_job(job)
        body.add_control_get_jobs()
        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, job):
        db_job = Job.query.filter_by(name=job).first()
        if db_job is None:
            return create_error_response(
                404, "Not found",
                "No job was found with the name {}".format(job)
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
        db_job.applicant_number = request.json["applicant_number"]
        db_job.category = request.json["category"]
        db_job.region = request.json["region"]

        try:
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "Job with name '{}' already exists.".format(request.json["name"])
            )
        return Response(status=204)

    def delete(self, job):
        db_job = Job.query.filter_by(name=job).first()
        if db_job is None:
            return create_error_response(
                404, "Not found",
                "No job was found with the name {}".format(job)
            )

        db.session.delete(db_job)
        db.session.commit()

        return Response(status=204)


