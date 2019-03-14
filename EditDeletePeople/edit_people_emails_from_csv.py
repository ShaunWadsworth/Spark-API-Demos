import requests
import json
import time
from urllib.parse import quote

def sendGET(url):
    response = requests.get(url,
                           headers={"Accept" : "application/json",
                                    "Content-Type":"application/json",
                                    "Authorization": "Bearer "+bearer})
    return response

def sendPUT(url, data):
    response = requests.put(url, data=json.dumps(data),
                           headers={"Accept" : "application/json",
                                    "Content-Type":"application/json",
                                    "Authorization": "Bearer "+bearer})
    return response

bearer = "ADMIN_TOKEN" #your admin token
filepath = "/Users/tahanson/Documents/people_emails.csv" #each user on a new line.
from_domain = "@domone.com"
to_domain = "@domtwo.com"

lines = []
with open(filepath, 'r') as f:
    lines = f.readlines()

people_url = 'https://api.ciscospark.com/v1/people?email={0}'
edit_url = 'https://api.ciscospark.com/v1/people/{0}'
failure = False
for line in lines[1:]:#basically, this is 'for every email address in the list'
    try:
        if failure:
            break
        retry = True
        while retry and not failure:
            #First, you have to get the person's personId, by looking them up via email
            person_email = line.strip('\r\n')
            print("Person Email to look up: <{0}>".format(person_email))
            result = sendGET(people_url.format(quote(person_email)))
            if result.status_code < 300:
                person_details = result.json().get('items') #could print full person_details if you really wanted to.
                if len(person_details) > 0:
                    person_id = person_details[0]['id']
                    print("Person Id to edit is: {0}".format(person_id)) #we'll just print this person's Id.
                    print("Editing person...")
                    new_email = person_email.replace(from_domain, to_domain)
                    data = person_details[0]
                    data.update({"emails":[new_email]})
                    result = sendPUT(edit_url.format(person_id), data)
                    print("Edit result (200 is success): {0}".format(result.status_code))
                else:
                    print("That user does not seem to exist.")
                retry = False
            else:
                print("Failed due to lookup user because: ")
                print(result.status_code)
                if result.status_code == 429:
                    sleep_time = result.headers.get('Retry-After')
                    if sleep_time is None:
                        print("429 received without a Retry-After header... defaulting to 60.")
                        sleep_time = 60
                    else:
                        sleep_time = int(sleep_time)
                    print("Sleeping for {0} seconds before trying again.".format(sleep_time))
                    time.sleep(sleep_time)
                else:
                    print(result.json())
                    print("Stopping here because this error will likely repeat.")
                    failure = True
                    break
    except Exception as e:
        print(e)
        print(e.headers)
        print(e.read())
