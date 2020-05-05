import json
import os
import re
import requests
import sys
import time

from jsonschema._validators import items
from tinytag import TinyTag, TinyTagException

SERVER_URL = "http://127.0.0.1:5000/"

class APIError(Exception):
    """
    Exception class used when the API responds with an error code. Gives
    information about the error in the console.
    """

    def __init__(self, code, error):
        """
        Initializes the exception with *code* as the status code from the response
        and *error* as the response body.
        """

        self.error = json.loads(error)
        self.code = code

    def __str__(self):
        """
        Returns all details from the error response sent by the API formatted into
        a string.
        """

        return "Error {code} while accessing {uri}: {msg}\nDetails:\n{msgs}".format(
            code=self.code,
            uri=self.error["resource_url"],
            msg=self.error["@error"]["@message"],
            msgs="\n".join(self.error["@error"]["@messages"])
        )

def submit_data(s, ctrl, data):
    """
    submit_data(s, ctrl, data) -> requests.Response

    Sends *data* provided as a JSON compatible Python data structure to the API
    using URI and HTTP method defined in the *ctrl* dictionary (a Mason @control).
    The data is serialized by this function and sent to the API. Returns the
    response object provided by requests.
    """

    resp = s.request(
        ctrl["method"],
        SERVER_URL + ctrl["href"],
        data=json.dumps(data),
        headers={"Content-type": "application/json"}
    )
    return resp

def create_company(s,ctrl):
    """
    create_artist(s, name, ctrl) -> string

    Compiles a dictionary for creating an artist resource by using JSON schema
    from the *ctrl* as a template. Only fills required fields, and uses "TBA"
    for location because this information is not available in tags. In case new
    required fields are introduced in the API, prompts the user for the value.
    If creation is successful, returns the URI where the artist was placed by
    the API. Otherwise raises an APIError.
    """

    body = {}
    schema = ctrl["schema"]
    for field in schema["required"]:
        if field == "name":
            body[field] = input("Provide name: ")
        elif field == "address":
            body[field] = input("Provide address of your company: ")
        elif field =="introduction":
            body[field] = input("Provide introduction: ")
        elif field =="phone_number":
            body[field] = input("Provide phone number: ")
    resp = submit_data(s, ctrl, body)
    if resp.status_code == 201:
        return resp.headers["Location"]
    else:
        raise APIError(resp.status_code, resp.content)
def edit_company(s,ctrl):
    """
    create_artist(s, name, ctrl) -> string

    Compiles a dictionary for creating an artist resource by using JSON schema
    from the *ctrl* as a template. Only fills required fields, and uses "TBA"
    for location because this information is not available in tags. In case new
    required fields are introduced in the API, prompts the user for the value.
    If creation is successful, returns the URI where the artist was placed by
    the API. Otherwise raises an APIError.
    """

    body = {}
    schema = ctrl["schema"]
    for field in schema["required"]:
        if field == "name":
            body[field] = input("Provide name: ")
        elif field == "address":
            body[field] = input("Provide address of your company: ")
        elif field =="introduction":
            body[field] = input("Provide introduction: ")
        elif field =="phone_number":
            body[field] = input("Provide phone number: ")
    resp = submit_data(s, ctrl, body)
    if resp.status_code == 204:
        return "edit successfully"
    else:
        raise APIError(resp.status_code, resp.content)
def delete_company(s,ctrl):
    resp = s.request(
        ctrl["method"],
        SERVER_URL+ctrl["href"]
    )
    if resp.status_code == 204:
        return "delete successfully"
    else:
        raise APIError(resp.status_code, resp.content)

def create_job(s,ctrl):
    """
    create_artist(s, name, ctrl) -> string

    Compiles a dictionary for creating an artist resource by using JSON schema
    from the *ctrl* as a template. Only fills required fields, and uses "TBA"
    for location because this information is not available in tags. In case new
    required fields are introduced in the API, prompts the user for the value.
    If creation is successful, returns the URI where the artist was placed by
    the API. Otherwise raises an APIError.
    """

    body = {}
    schema = ctrl["schema"]
    for field in schema["required"]:
        if field == "name":
            body[field] = input("Provide name: ")
        elif field == "salary":
            body[field] = input("Provide salary of your job: ")
        elif field =="introduction":
            body[field] = input("Provide introduction: ")
        elif field =="category":
            body[field] = input("Provide category: ")
        elif field =="region":
            body[field] = input("Provide region: ")
    resp = submit_data(s, ctrl, body)
    if resp.status_code == 201:
        return resp.headers["Location"]
    else:
        raise APIError(resp.status_code, resp.content)
def edit_job(s,ctrl):
    """
    create_artist(s, name, ctrl) -> string

    Compiles a dictionary for creating an artist resource by using JSON schema
    from the *ctrl* as a template. Only fills required fields, and uses "TBA"
    for location because this information is not available in tags. In case new
    required fields are introduced in the API, prompts the user for the value.
    If creation is successful, returns the URI where the artist was placed by
    the API. Otherwise raises an APIError.
    """

    body = {}
    schema = ctrl["schema"]
    for field in schema["required"]:
        if field == "name":
            body[field] = input("Provide name: ")
        elif field == "salary":
            body[field] = input("Provide salary of your job: ")
        elif field == "introduction":
            body[field] = input("Provide introduction: ")
        elif field == "category":
            body[field] = input("Provide category: ")
        elif field == "region":
            body[field] = input("Provide region: ")
    resp = submit_data(s, ctrl, body)
    if resp.status_code == 204:
        return "edit successfully"
    else:
        raise APIError(resp.status_code, resp.content)
def delete_job(s,ctrl):
    resp = s.request(
        ctrl["method"],
        SERVER_URL+ctrl["href"]
    )
    if resp.status_code == 204:
        return "delete successfully"
    else:
        raise APIError(resp.status_code, resp.content)

def list_job(s,job_href):

    resp = s.get(SERVER_URL + job_href)
    body = resp.json()
    print("the information about your choosing job is as follows: ")
    print('id:{id}\nname:{name}\nsalary:{salary}\nintroduction:{introduction}\napplicant_number:{applicant_number}\ncategory:{category}\nregion:{region}\n'
        .format(id=body["id"], name=body["name"], salary=body["salary"], introduction=body["introduction"],
                applicant_number=body["applicant_number"], category=body["category"], region=body["region"]))
    print("if you want to edit this job, please input 'edit',if you want to delete this job, please input 'delete',if you want to retrun to last page,please input 'return'")
    choice = input()
    if choice =="edit":
        result=edit_job(s,body["@controls"]["mumeta:job-edit"])
        print(result)
        list_job(s,body["@controls"]["self"]["href"])
    elif choice=="delete":
        result=delete_job(s,body["@controls"]["mumeta:job-delete"])
        print(result)
        list_jobs_by_company(s,body["@controls"]["collection"])
    elif choice=="return":
        list_jobs_by_company(s,body["@controls"]["collection"])
def find_job_href(ID , collection):
    """
    find_artist_href(name, collection) -> string

    Finds a href for an artist from a *collection* (list of dictionaries) using
    *name* as the search criterion. If multiple artists match it prompts the user
    to choose the correct one. If there are no matches, returns None.
    """
    for item in collection:
        if int(item["id"]) == int(ID):
            return item["@controls"]["self"]["href"]

def list_jobs_by_company(s,jobs_by_company_href):
    resp = s.get(SERVER_URL + jobs_by_company_href["href"])
    body = resp.json()
    print("We provide following jobs in our company: ")
    for item in body["items"]:
        print('id:{id}\nname:{name}\nsalary:{salary}\nintroduction:{introduction}\napplicant_number:{applicant_number}\ncategory:{category}\nregion:{region}\n'
              .format(id=item["id"], name=item["name"], salary=item["salary"], introduction=item["introduction"],
                      applicant_number=item["applicant_number"],category=item["category"],region=item["region"]))
    print("if you want to select a job, please input an ID of the job,if you want to add a new job for your company, please input 'add',if you want to return ,please input 'return'")
    choice = input()
    if choice == "add":
        result = create_job(s, body["@controls"]["mumeta:add-jobs-by-company"])
        print("Location of your job: " + result)
        list_jobs_by_company(s,body["@controls"]["self"])
    elif choice =="return":
        list_company(s,body["@controls"]["mumeta:get-company"]["href"])
    else:
        job_href = find_job_href(choice, body["items"])
        list_job(s, job_href)

def list_company(s,company_href):

    resp = s.get(SERVER_URL + company_href)
    body = resp.json()
    print("the information about your choosing company is as follows: ")
    print('id:{id}\nname:{name}\naddress:{address}\nintroduction:{introduction}\nphone_number:{phone_number}\n'
            .format(id=body["id"],name=body["name"],address=body["address"],introduction=body["introduction"],phone_number=body["phone_number"]))
    print("if you want to edit this company, please input 'edit',if you want to delete this company, please input 'delete',if you want to get jobs of this company,please input 'jobs'\n"
          "if you want to return to last page, please input 'return'")
    choice = input()
    if choice =="edit":
        result=edit_company(s,body["@controls"]["mumeta:company-edit"])
        print("Location after editing information: "+result)
        list_company(s, body["@controls"]["self"]["href"])
    elif choice=="delete":
        result=delete_company(s,body["@controls"]["mumeta:company-delete"])
        print(result)
        list_companys(s, body["@controls"]["collection"]["href"])
    elif choice=="jobs":
        list_jobs_by_company(s,body["@controls"]["mumeta:get-jobs-by-company"])
    elif choice=="return":
        list_companys(s,body["@controls"]["collection"]["href"])
def find_company_href(ID , collection):
    """
    find_artist_href(name, collection) -> string

    Finds a href for an artist from a *collection* (list of dictionaries) using
    *name* as the search criterion. If multiple artists match it prompts the user
    to choose the correct one. If there are no matches, returns None.
    """
    for item in collection:
        if int(item["id"]) == int(ID):
            return item["@controls"]["self"]["href"]

def list_companys(s,companys_href):

    resp = s.get(SERVER_URL + companys_href)
    body = resp.json()
    print("we have the following companys in our system")
    for item in body["items"]:
        print('id:{id}\nname:{name}\naddress:{address}\nintroduction:{introduction}\nphone_number:{phone_number}\n'
              .format(id=item["id"],name=item["name"],address=item["address"],introduction=item["introduction"],phone_number=item["phone_number"]))
    print("if you want to select a company, please input an ID of the company,if you want to add a new company, please input 'add'")
    choice = input()
    if choice =="add":
        result=create_company(s,body["@controls"]["mumeta:add-company"])
        print("Location of your company: "+result)
        list_companys(s, body["@controls"]["self"]["href"])
    else:
        company_href=find_company_href(choice,body["items"])
        list_company(s,company_href)

if __name__ == "__main__":
    SERVER_URL = "http://127.0.0.1:5000/"
    with requests.Session() as s:
        s.headers.update({"Accept": "application/vnd.mason+json, */*"})
        resp = s.get(SERVER_URL + "/api/")
        if resp.status_code != 200:
            print("Unable to access API.")
        else:
            body = resp.json()
            list_companys(s, body["@controls"]["mumeta:companys-all"]["href"])
