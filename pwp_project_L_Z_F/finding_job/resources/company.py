import json

from flask import request, Response, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from finding_job.constants import *
from finding_job.models import Company, seek,provide,Job,Jobseeker
from finding_job.utils import JobBuilder, create_error_response
from jsonschema import validate, ValidationError
from finding_job import db
class CompanyCollection(Resource):

    def get(self):
        body = JobBuilder()
        body["items"] = []
        body.add_namespace("mumeta", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.companycollection"))
        body.add_control("profile", COMPANY_PROFILE)
        body.add_control("collection", url_for("api.companycollection"))
        body.add_control_add_company()
        db_company = Company.query.all
        if db_company is None:
            return create_error_response(
                404, "Not found", "No companys"
            )
        for db_company in Company.query.all():
            item = JobBuilder(
                id=db_company.id,
                name=db_company.name,
                address=db_company.address,
                introduction=db_company.introduction,
                phone_number=db_company.phone_number,
            )
            item.add_control("self", url_for("api.companyitem", company_id=db_company.id))
            item.add_control("profile", COMPANY_PROFILE)
            item.add_control_get_company(db_company.id)
            body["items"].append(item)
        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self):
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Company.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))
        company = Company(
            name=request.json["name"],
            address=request.json["address"],
            introduction=request.json["introduction"],
            phone_number=request.json["phone_number"]
        )
        try:
            db.session.add(company)
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "Company with name '{}' already exists.".format(request.json["name"])
            )

        return Response(status=201, headers={
            "Location": url_for("api.companyitem", company=request.json["name"])
        })

class CompanyItem(Resource):

    def get(self, company_id):
        db_company = Company.query.filter_by(id=company_id).first()
        if db_company is None:
            return create_error_response(
                404, "Not found",
                "No company was found with the name {}".format(company_id)
            )
        body = JobBuilder(
            id=db_company.id,
            name=db_company.name,
            address=db_company.address,
            introduction=db_company.introduction,
            phone_number=db_company.phone_number
        )
        body.add_namespace("mumeta", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.companyitem", company_id=company_id))
        body.add_control("profile", COMPANY_PROFILE)
        body.add_control("collection", url_for("api.companycollection"))
        body.add_control_delete_company(company_id)
        body.add_control_edit_company(company_id)
        body.add_control_get_companys()
        body.add_control_get_jobs_by_company(company_id)
        return Response(json.dumps(body), 200, mimetype=MASON)
    def put(self, company_id):
        db_company = Company.query.filter_by(id=company_id).first()
        if db_company is None:
            return create_error_response(
                404, "Not found",
                "No company was found with the name {}".format(company_id)
            )

        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )

        try:
            validate(request.json, Company.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        db_company.name = request.json["name"]
        db_company.address = request.json["address"]
        db_company.introduction = request.json["introduction"]
        db_company.phone_number = request.json["phone_number"]

        try:
            db.session.commit()
        except IntegrityError:
            return create_error_response(
                409, "Already exists",
                "Company with name '{}' already exists.".format(request.json["name"])
            )
        return Response(status=204)

    def delete(self, company_id):
        db_company = Company.query.filter_by(id=company_id).first()
        if db_company is None:
            return create_error_response(
                404, "Not found",
                "No company was found with the name {}".format(company_id)
            )

        db.session.delete(db_company)
        db.session.commit()

        return Response(status=204)
