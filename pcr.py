#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# -----------------------------
# Quick Python interface for PCR Educator.
# Written by Alek Zieba
# April 18, 2014

# Load our credentials.
username = "15ziebaa"
password = ""

# Import the necessities.
from bs4 import BeautifulSoup # Needed to parse HTML
import datetime # Needed to decide which assignments to get.
import requests # Needed to make requests.
import sys # Needed to obtain data from the user.

# Date, get it from the user.
date = sys.argv[1]
dateTime = datetime.datetime.strptime(date, '%m/%d/%Y')
weekday = dateTime.weekday()
weekNumber = dateTime.isocalendar()[1]
bottomTop = weekNumber % 2

# Find out which date to get.
idPrefixesForWeekday = ['m', 't', 'w', 'h', 'f', 's', 'su']
day = idPrefixesForWeekday[weekday]
numberSuffix = bottomTop + 1
idToGet = "ctl00_cph2_" + idPrefixesForWeekday[weekday] + str(numberSuffix)

# So our terminal can look colorful.
class bcolors:
	DARK_GREY = "\033[90m"
	GREEN = "\033[32m"
	LIGHT_BLUE = "\033[94m"
	LIGHT_MAGENTA = "\033[95m"
	ENDC = "\033[0m"

# Just some constants so we don't have to deal with magic strings.
ClassName = "ClassName"
AssignmentTitles = "AssignmentTitle"
NoAssignmentsMessage = "No assignments for that day!"

# Complicated URI and cookie data obtained through research.
login_url = 'https://webapps.pcrsoft.com/ParentPortal/Secure/Login.aspx?ReturnUrl=%2fParentPortal%2f&scn=Sayre&appId=2'
# Checked for multiple accounts, this payload always works.
payload = {'__EVENTARGUMENT': '', 'ctl00$cph2$Login1$LoginButton': 'Log In', '__VIEWSTATE': '/wEPDwULLTEzMjA4MzUwNTQPZBYCZg9kFgQCAg9kFgICAQ8WAh4EaHJlZgUXfi9TdHlsZS9zYXlyZXNjaG9vbC5jc3NkAgQPZBYGAgEPZBYCAgEPZBYCAgEPDxYCHgRUZXh0BQpMb2dpbiBQYWdlZGQCBQ9kFgQCAQ9kFgJmD2QWAgINDxAPFgIeB0NoZWNrZWRoZGRkZAIFDw8WAh4HVmlzaWJsZWdkFgICAQ8PFgIeC05hdmlnYXRlVXJsBR1tYWlsdG86ZGprbHVzQHNheXJlc2Nob29sLm9yZ2RkAgkPZBYCAgEPZBYEAgEPDxYCHwEFBDIwMTRkZAIDDw8WAh8BBQMgLSBkZBgBBR5fX0NvbnRyb2xzUmVxdWlyZVBvc3RCYWNrS2V5X18WAQUcY3RsMDAkY3BoMiRMb2dpbjEkUmVtZW1iZXJNZbcF1vfuWsWWUDvKu2YJ57DHkS0X3/DbzuCb7ji0Oup0', 'ctl00$cph2$ForgotPasswordV6Ctrl1$tbEmailAddress': '', 'ctl00$cph2$Login1$UserName': username, '__EVENTVALIDATION': '/wEdAAgXOjvMdEU/pwgMGjdpPc/UQWVj6n3E5i0tFZaHePUKfXSkTcnu2t2MGcgTJ3IJgksEddmyUIGR381Pe1/uJXfljPlMn2rfDbvwTtWlR6WzHAd6E/n+itZOx2ED1MPq9/Uu0SnHv5QNFPDLyfbEGiKHNRXEGgMMSadsL+N1U2DRPsHxxdxR7AWfcWaommqGvNBDCyie3cA3b75bH6OuvBFc', '__EVENTTARGET': '', 'ctl00$cph2$ForgotPasswordV6Ctrl1$tbUserName': '', 'ctl00$cph2$Login1$Password': password}
headers = {'content-type': 'application/x-www-form-urlencoded'}

# Required to obtain the session cookies.
session = requests.session()

# Make the login POST request.
loginPage = session.post(login_url, data=payload, headers=headers)

# Obtain the authentication cookies in a dictionary.
authentication_cookies = requests.utils.dict_from_cookiejar(session.cookies)

# Find the new URI
loginHTML = BeautifulSoup(loginPage.text)
calendarURI = loginHTML.find(attrs={"id": "cl_cl"}).a.attrs['href']

# Make the calendar GET request.
calendar = requests.get('https://webapps.pcrsoft.com' + calendarURI, cookies=authentication_cookies)

# Create a parsable object.
parsableHTML = BeautifulSoup(calendar.text)

# See if we need to go up or down pages.
difference = weekNumber - (datetime.datetime.now()).isocalendar()[1]

# Set up the payloads.
moveForwardsPayload = {'__EVENTARGUMENT':'', '__EVENTTARGET': '', '__EVENTVALIDATION':parsableHTML.find('input', attrs={"name":"__EVENTVALIDATION"})['value'], '__VIEWSTATE':parsableHTML.find('input', attrs={"name":"__VIEWSTATE"})['value'], 'ctl00$ResourceCombined1$ResourceDisplay1$hfresourcename':'Calendar.aspx','ctl00$ResourceCombined1$ResourceDisplay1$hftype':'PageText','ctl00$cph2$cbCoursesDocs':'-1001','ctl00$cph2$cbCrssAssgnmnt':'-1001','ctl00$cph2$imgBtnNext.x':'9','ctl00$cph2$imgBtnNext.y':'7','ctl00_RadScriptManager1_TSM':'','h_main_menu':'','h_main_menuscroll':''}
moveBackwardsPayload = {'__EVENTARGUMENT':'', '__EVENTTARGET': '', '__EVENTVALIDATION':parsableHTML.find('input', attrs={"name":"__EVENTVALIDATION"})['value'], '__VIEWSTATE':parsableHTML.find('input', attrs={"name":"__VIEWSTATE"})['value'], 'ctl00$ResourceCombined1$ResourceDisplay1$hfresourcename':'Calendar.aspx','ctl00$ResourceCombined1$ResourceDisplay1$hftype':'PageText','ctl00$cph2$cbCoursesDocs':'-1001','ctl00$cph2$cbCrssAssgnmnt':'-1001','ctl00$cph2$imgBtnPrev.x':'9','ctl00$cph2$imgBtnPrev.y':'7','ctl00_RadScriptManager1_TSM':'','h_main_menu':'','h_main_menuscroll':''}

# If we're on a bottom week and we need to go to the next week, go forward.
if (difference == 1 and bottomTop == 0 and weekday != 0): # if the day is Sunday, the calendar automatically moves forward
	# Make the POST request to go forward
	calendar = requests.post('https://webapps.pcrsoft.com' + calendarURI, cookies=authentication_cookies, data=moveForwardsPayload, headers=headers)
	difference -= 2

# If we're on a top week and we need to go to the previous week, go backward.
if (difference == -1 and bottomTop == 1):
	# Make the POST request to go backwards
	calendar = requests.post('https://webapps.pcrsoft.com' + calendarURI, cookies=authentication_cookies, data=moveBackwardsPayload, headers=headers)
	difference += 2

# Fix remaining forwards if necessary.
while (difference > 1):
	# Make the POST request to go forward
	calendar = requests.post('https://webapps.pcrsoft.com' + calendarURI, cookies=authentication_cookies, data=moveForwardsPayload, headers=headers)
	difference -= 2

# Fix remaining backwards if necessary.
while (difference < -1):
	# Make the POST request to go backwards
	calendar = requests.post('https://webapps.pcrsoft.com' + calendarURI, cookies=authentication_cookies, data=moveBackwardsPayload, headers=headers)
	difference += 2

# Recreate a parsable object.
parsableHTML = BeautifulSoup(calendar.text)

# Get today's panel.
today = parsableHTML.find(attrs={"id": idToGet})

# Get an array of the assignment table data objects.
assignment_td = today.find_all('td', attrs={"width": "145"}) # This is just an observed characteristic of each assignment td

# Iterate through the data and add dictionaries to the following array.
assignments = {}
currentClasses = []
for td in assignment_td:
	assignClass = td.tr.td.text.replace(":", " ")
	# Just some formatting.
	assignTitle = td.find(attrs={"class":"AssgnmntLink"}).text.replace(assignClass + "\r\n", "").replace("\n", "\n\t")
	# Get rid of extraneous stuff at beginning.
	assignTitle = (assignTitle[assignTitle.index(":")+2:]).replace("\r\n\t", ": ")
	if (assignClass in currentClasses):
		assignments[assignClass].append(assignTitle)
	else:
		assignments[assignClass] = [assignTitle]
		currentClasses.append(assignClass)

# Pretty-print!
if len(assignments) > 0:
	for className in assignments:
		print(bcolors.LIGHT_MAGENTA + "* " + className + ":" + bcolors.ENDC)
		for assignTitle in assignments[className]:
			print(bcolors.GREEN + "\t- " + assignTitle + bcolors.ENDC)
else:
	print(bcolors.LIGHT_MAGENTA + NoAssignmentsMessage + bcolors.ENDC)
