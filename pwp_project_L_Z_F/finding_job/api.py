from flask import Blueprint
from flask_restful import Api

from finding_job.resources.company import CompanyCollection, CompanyItem
from finding_job.resources.location import #LocationItem, LocationSensorPairing
from finding_job.resources.measurement import #MeasurementCollection

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

api.add_resource(CompanyCollection, "/companys/")
api.add_resource(CompanyItem, "/companys/<company>/")
api.add_resource(LocationItem, "/locations/<location>/")
api.add_resource(MeasurementCollection, "/sensors/<sensor>/measurements/")
api.add_resource(LocationSensorPairing, "/locations/<location>/<sensor>/")