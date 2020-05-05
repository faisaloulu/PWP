from flask import Blueprint
from flask_restful import Api

from finding_job.resources.company import CompanyCollection, CompanyItem,EntryPoint
from finding_job.resources.job import JobCollection, JobItem
from finding_job.resources.jobs_by_company import Jobs_By_Company
from finding_job.resources.seeker import SeekerItem
from finding_job.resources.jobs_by_seeker import Jobs_By_Seeker, Seekers_By_Job


api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

api.add_resource(EntryPoint, "/")
api.add_resource(CompanyCollection, "/companys/")
api.add_resource(CompanyItem, "/companys/<company_id>/")
api.add_resource(Jobs_By_Company,"/companys/<company_id>/jobs/")
api.add_resource(JobCollection,"/jobs/")
api.add_resource(JobItem,"/companys/<company_id>/jobs/<job_id>/")
api.add_resource(Seekers_By_Job,"/companys/<company_id>/jobs/<job_id>/seekers_by_job/")
api.add_resource(SeekerItem,"/seekers/")
api.add_resource(Jobs_By_Seeker,"/seekers/<seeker_id>/jobs_by_seeker/")


