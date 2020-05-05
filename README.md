# PWP SPRING 2020
# PROJECT NAME
Finding_job
# Group information
* Student 1. Liutianzhao 768829964@QQ.com
* Student 2. Name and email
* Student 3. Name and email

__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__

We write this project following Flask API Project Layout in exercise. the layout include two parts mainly, which are finding_job and tests. Besides, there is a setup that interpret some configuration information. The client end is included in static folder in finding_job folder.
This project is providing a platform for a seeker to find a job or a company to release a job. It can support one seeker and several Companys. Here's some example on how to use resources in our project.
a seeker applying a job: Seeker--Companys--Company--JobsByCompany--Job--SeekersByJob(using post method in this resource, so you can send a apply request./Seeker--Jobs--Job--SeekersByJob
a seeker cancel a job application:Seeker--JobsBySeeker(using delete method in this resource, so you can cancel an application)
a company check who has send a job application to its: Companys--Company--JobsByCompany--Job--SeekersByJob(using get method in this resource, so a company can check who has applied this job)
Of cource, a company can edit it's own information and release a new job, a seeker can edit it's own information.

The submission includes:
pwp_project_L_Z_F: source code
ER diagram, job_database.py: those needed for backend
API map, jobseekapi.apib: those needed for api design, documented using Apiary

We use pycharm for our IDE, To run and test this project, you need input following command in terminal if you use Windows:
set FLASK_APP=finding_job
set FLASK_ENV=development
flask init-db
flask run
Then you can run company_user in static as a client end.

It is worth declaring:
We didn't implement JobsByCategory and JobsByRegion resources in the API implementing process. You can test other functions using a url with the help of Talend API Tester.
And we only implement company_user part in the client implementing process
