Jump to Content
Unipile
Create Unipile Account
Dashboard
Website
v1.0
Documentation
API Reference
Changelog
Unipile API Reference

    Accounts
    Messaging
    Users
    Posts
    LinkedIn Specific
        Retrieve Recruiter hiring projectsget
        Retrieve Recruiter hiring project from IDget
        Perform an action with a user profilepost
        Retrieve a company profileget
        Get raw data from any endpointpost
        Get inmail credit balanceget
        Retrieve LinkedIn search parametersget
        Perform Linkedin searchpost
        List all job postingsget
        Create a job postingpost
        Get job offerget
        Edit a job postingpatch
        Publish a job postingpost
        Solve a job publishing checkpointpost
        Close a job postingpost
        List all applicants to a job postingget
        Get a specific applicant to a job postingget
        Download the resume of a job applicantget
        Endorse a user profile specific skillpost
    Emails
    Webhooks
    Calendars

Powered by 

    Unipile API Reference
    LinkedIn Specific

Create a job posting
post
https://{subdomain}.unipile.com:{port}/api/v1/linkedin/jobs

Create a new job offer draft.
Recent Requests
Log in to see full request history
Time	Status	User Agent	
Make a request to see history.
0 Requests This Month

Body Params
account_id
string
required
length ≥ 1

An Unipile account id.
job_title
required
company
required
workplace
string
enum
required
Allowed:
location
string
required

The ID of the parameter. Use type LOCATION on the List search parameters route to find out the right ID.
employment_status
string
enum
Allowed:
description
string
required

You can use HTML tags to structure your description.
auto_rejection_template
string

You can define a rejection message template to be automatically sent to applicants that don't pass screening questions.
screening_questions
array
recruiter
object
Responses
Response body
object
object
string
enum
required

LinkedinJobPostingDraftCreated
job_id
string
required
project_id
string

The ID of the Project for Recruiter job postings.
publish_options
object
required
free
object
required
promoted
object
required

Updated 5 months ago
List all job postings
Get job offer
Did this page help you?
Language
Credentials
Header
URL

1

curl --request POST \

2

     --url https://api1.unipile.com:13111/api/v1/linkedin/jobs \

3

     --header 'accept: application/json' \

4

     --header 'content-type: application/json' \

5

     --data '

6

{

7

  "workplace": "ON_SITE"

8

}

9

'

1

{

2

  "object": "LinkedinJobPostingDraftCreated",

3

  "job_id": "string",

4

  "project_id": "string",

5

  "publish_options": {

6

    "free": {

7

      "eligible": true,

8

      "ineligible_reason": "string",

9

      "estimated_monthly_applicants": 0

10

    },

11

    "promoted": {

12

      "estimated_monthly_applicants": 0,

13

      "currency": "string",

14

      "daily_budget": {

15

        "min": 0,

16

        "max": 0,

17

        "recommended": 0

18

      },

19

      "monthly_budget": {

20

        "min": 0,

21

        "max": 0,

22

        "recommended": 0

23

      }

24

    }

25

  }

26

}

