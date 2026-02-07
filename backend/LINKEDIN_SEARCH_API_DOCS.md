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

Perform Linkedin search
post
https://{subdomain}.unipile.com:{port}/api/v1/linkedin/search

Search people and companies from the Linkedin Classic as well as Sales Navigator APIs. Check out our Guide with examples to master LinkedIn search : https://developer.unipile.com/docs/linkedin-search
Recent Requests
Log in to see full request history
Time	Status	User Agent	
Make a request to see history.
0 Requests This Month

Query Params
cursor
string
length ≥ 1

A cursor for pagination purposes. To get the next page of entries, you need to make a new request and fulfill this field with the cursor received in the preceding request. This process should be repeated until all entries have been retrieved.
limit
integer
0 to 100
Defaults to 10

A limit for the number of items returned in the response. Can bet set up to 100 results for Sales Navigator and Recruiter, but Linkedin Classic shouldn't exceed 50.
account_id
string
required

The ID of the account to trigger the request from.
Body Params
Responses
Response body
object
object
string
enum
required

LinkedinSearch
items
array
required
config
object
required
params
paging
object
required
start
required
page_count
number
required
total_count
number
required
cursor
required
metadata
object
search_history_id
string
search_context_id
string
search_request_id
string

Updated 5 months ago
Retrieve LinkedIn search parameters
List all job postings
Did this page help you?
Language
Credentials
Header
URL

1

curl --request POST \

2

     --url https://api1.unipile.com:13111/api/v1/linkedin/search \

3

     --header 'accept: application/json' \

4

     --header 'content-type: application/json' \

5

     --data '

6

{

7

  "api": "classic",

8

  "category": "people"

9

}

10

'

1

{

2

  "object": "LinkedinSearch",

3

  "items": [

4

    {

5

      "object": "SearchResult",

6

      "type": "PEOPLE",

7

      "id": "string",

8

      "public_identifier": "string",

9

      "public_profile_url": "string",

10

      "profile_url": "string",

11

      "profile_picture_url": "string",

12

      "profile_picture_url_large": "string",

13

      "member_urn": "string",

14

      "name": "string",

15

      "first_name": "string",

16

      "last_name": "string",

17

      "network_distance": "SELF",

18

      "location": "string",

19

      "industry": "string",

20

      "keywords_match": "string",

21

      "headline": "string",

22

      "connections_count": 0,

23

      "followers_count": 0,

24

      "pending_invitation": true,

25

      "can_send_inmail": true,

26

      "hiddenCandidate": true,

27

      "interestLikelihood": "string",

28

      "privacySettings": {

29

        "allowConnectionsBrowse": true,

30

        "showPremiumSubscriberIcon": true

31

      },

32

      "skills": [

33

        {

34

          "name": "string",

35

          "endorsement_count": 0

36

        }

37

      ],

38

      "recruiter_candidate_id": "string",

39

      "recruiter_pipeline_category": "string",

40

      "premium": true,

41

      "verified": true,

42

      "open_profile": true,

43

      "shared_connections_count": 0,

44

      "recent_posts_count": 0,

45

      "recently_hired": true,

46

      "mentioned_in_the_news": true,

47

      "last_outreach_activity": {

48

        "type": "SEND_MESSAGE",

49

        "performed_at": "string"

