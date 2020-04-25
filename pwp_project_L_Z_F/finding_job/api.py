from flask import Blueprint
from flask_restful import Api

from finding_job.resources.company import CompanyCollection, CompanyItem
from finding_job.resources.job import JobCollection, JobItem
from finding_job.resources.seeker import SeekerItem
from finding_job.resources.jobs_by_seeker import Jobs_By_Seeker

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

api.add_resource(CompanyCollection, "/companys/")
api.add_resource(CompanyItem, "/companys/<company>/")
api.add_resource(JobCollection, "/jobs/")
api.add_resource(JobItem, "/jobs/<job>/")
