import os
from flask import Flask, render_template, request
import requests
import sys
import textwrap
import jinja2
from jinja2 import Template, Environment, PackageLoader
from piplapis.data import Person, Name, Address, Job, Email, Username
from piplapis.search import SearchAPIRequest
import collections


#env = Environment(loader=PackageLoader('C:\users\zubrowjt\Desktop\Interalliance','templates'))

errors = []
#This method uses HIBP to recieve/send the information available
def hibpmet(username):
    breachcount = 1
    hibpurl = "https://haveibeenpwned.com/api/v2/breachedaccount/"

    accountname = username
    resp = requests.get(hibpurl + accountname)
    if accountname == "":
        print('Please re-run the program with a valid username.')
    else:
        if resp.status_code == 404:
            print("Congratulations, you have not been pwned!")
        elif resp.status_code == 400:
            print("please ensure that you do not have any trailing or leading spaces in your input, or ensure that you are entering a valid account name")
        elif resp.status_code == 403:
            print("We're sorry, but the guy who wrote this program is a big dummy.")
        elif resp.status_code == 200:
            Breachlist = {}
            for BreachItem in resp.json():
                    Breachlist['{}'.format(BreachItem['Title'])] = '{}'.format(BreachItem['Domain'])
                    breachcount += 1
            Breachlist['Times Breached'] = str(breachcount)
            return(Breachlist)

        else:
            print("Error encountered! Please run the program again with a valid username")

#This removes the additional characters that is recieved when you update and try to pull the information from both websites
def repstring(strtr):
    charrep = ['[', '\'', ']', '"']
    for ch in charrep:
        strtr = strtr.replace(ch,"")

# This method deals with the information inputed and sends the input to pipl then continues to recieve the output and send it back
def piplcall(person):

    request = SearchAPIRequest(person=person, api_key='COMMUNITY-pic8fj515nn0sgmq1wrvsa8f')
    response = request.send()
    personresponse = response.person
    personaldata = {}
    personaldata['Name'] = []
    personaldata['Email'] = []
    personaldata['Education'] = []
    personaldata['Job'] = []
    irdata  = {}
    irdata['Username'] = []
    irdata['Address'] = []
    irdata['PhoneNumber'] = []
    irdata['Gender'] = []
    irdata['DOB'] = []
    irdata['Languages'] = []
    irdata['Ethnicity'] = []
    irdata['OriginCountry'] = []
    irdata['UserID'] = []
    irdata['Images'] = []
    for name in personresponse.names:
        personaldata['Name'].append(name.display)
    for email in personresponse.emails:
        personaldata['Email'].append(email.address)
    for username in personresponse.usernames:
        irdata['Username'].append(username.content)
    for phone in personresponse.phones:
        irdata['PhoneNumber'].append(phone.display)
    for address in personresponse.addresses:
        irdata['Address'].append(address.display)
    for education in personresponse.educations:
        personaldata['Education'].append(education.display)
    for job in personresponse.jobs:
        personaldata['Job'].append(job.display)
    irdata['Gender'].append(personresponse.gender.content)
    if personresponse.dob:
        irdata['DOB'].append(personresponse.dob.date_range)
    for language in personresponse.languages:
        irdata['Languages'].append(language.display)
    for ethnicity in personresponse.ethnicities:
        irdata['Ethnicity'].append(ethnicity.content)
    for country in personresponse.origin_countries:
        irdata['OriginCountry'].append(country.country)
    for uid in personresponse.user_ids:
        irdata['UserID'].append(uid.content)
    for image in personresponse.images:
        irdata['Images'].append(image.url)

#This loop will return boolean values for personal information and irrelevent data  to protect the user to a degree
    for v in irdata:
        k = v
        if irdata[k]:
            irdata[k] = "True"
        else:
            irdata[k] = "False"
    for v in personaldata:
        k = v
        if not personaldata[k]:
            personaldata[k].append("Nothing Returned")

    f = open('logs.txt', 'w')
    print(str(personaldata), file = f)
    f.close()

    return personaldata, irdata


#This is the form regarding recieving input and recieving output
app = Flask(__name__, static_url_path = "" , static_folder = "static/images" )
@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    results = {}
    if request.method == "POST":
            username = request.form['username']
            email = request.form['email']
            fname = request.form['fname']
            lname = request.form['lname']
            country = request.form['Country']
            state = request.form['State']
            city = request.form['City']


            person = Person()
            if fname or lname:
                        name = Name(first=fname, last=lname)
                        person.add_fields([name])
            if email:
                        person.add_fields([Email(address=email)])
            if username:
                        person.add_fields([Username(content=username)])
            if country or state or city:
                        address = Address(country=country, state=state, city=city)
                        person.add_fields([address])

            Breachlist = hibpmet(username)
            try:
                response, irdata = piplcall(person)
                return success(Breachlist, response, irdata)
            except:
                errors.append("Invalid Person response received")
                return render_template('index.html', error=errors)

        #    return success(hibpmet(email))
    else:
        return render_template('index.html')

@app.route("/results", methods=['POST'])
def success(Breachlist, response, irdata):


        return render_template('results.html',Breachlist = Breachlist, response = response, irdata = irdata)
        if request.method == "POST":
            if request.form['Return']:
                return render_template('index.html')


if __name__ == '__main__':
    app.run()
