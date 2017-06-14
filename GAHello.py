"""A simple example of how to access the Google Analytics API."""

import argparse

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools
import csv
import json
import datetime
import time
import re

def get_service(api_name, api_version, scope, key_file_location,
                service_account_email):
  """Get a service that communicates to a Google API.

  Args:
    api_name: The name of the api to connect to.
    api_version: The api version to connect to.
    scope: A list auth scopes to authorize for the application.
    key_file_location: The path to a valid service account p12 key file.
    service_account_email: The service account email address.

  Returns:
    A service that is connected to the specified API.
  """

  credentials = ServiceAccountCredentials.from_p12_keyfile(
    service_account_email, key_file_location, scopes=scope)

  http = credentials.authorize(httplib2.Http())

  # Build the service object.
  service = build(api_name, api_version, http=http)

  return service



def accountID(analytics):
  try:
    accounts = analytics.management().accounts().list().execute()
    print accounts
  except TypeError, error:
    # Handle errors in constructing a query.
    print ('There was an error in constructing your query : %s' % error)


def getProfiles(analytics, accountId, webPropertyId):
  try:
    profiles = analytics.management().profiles().list(
      accountId=accountId,
      webPropertyId= webPropertyId).execute()
    print profiles
  except TypeError, error:
    print 'There was an error in constructing your query : %s' % error

def getUsers(analytics, accountId):
  try:
    account_links = analytics.management().accountUserLinks().list(
      accountId=accountId
    ).execute()

    print account_links
  except TypeError, error:
    print 'There was an error in constructing your query : %s' % error

def addUser(analytics, accountId):
  try:
    analytics.management().accountUserLinks().insert(
      accountId= accountId,
      body={
        'permissions': {
          'local': [
            'EDIT',
            'MANAGE_USERS'
          ],
          'effective': ['COLLABORATE', 'EDIT', 'READ_AND_ANALYZE']
        },
        'userRef': {
          'email': 'ksara@sph.com.sg'
        }
      }
    ).execute()

  except TypeError, error:
    # Handle errors in constructing a query.
    print 'There was an error in constructing your query : %s' % error


def checkDuplicateEmail(users, email):
  for user in users:
    if(user['userRef']['email'] == email):
      print  "found"
      print  email
      return 1
      break
  return 0


def createUser(accountId, analytics, email, permission):
  try:
    # analytics.management().accountUserLinks().insert(
    #   accountId=accountId,
    #   body={
    #     'permissions': permission,
    #     'userRef': {
    #       'email': email
    #     }
    #   }
    # ).execute()

    print "User created"
    print email

  except TypeError, error:
    # Handle errors in constructing a query.
    print 'There was an error in constructing your query : %s' % error

def processUpdate(analytics, accountId):
  try:
    account_links = analytics.management().accountUserLinks().list(
      accountId=accountId
    ).execute()

    print account_links

    fuser = csv.writer(open('files/' + accountId + '_ log.csv', 'w'))

    if account_links is not None:
      users = account_links['items']
      print users

      if users is not None:
        for user in users:
          email = user['userRef']['email']
          emailSpilit = email.split("@")
          emailid = emailSpilit[0]
          new_email =  emailid + "@sph.com.sg"

          if((email.find('biz') != -1) and (emailSpilit[1] != "@sph.com.sg") and (checkDuplicateEmail(users, new_email) != 1)):

            permission = user['permissions']
            ts = time.time()
            st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            temp = (user['userRef']['id'], emailid, email, json.dumps(permission), st)

            createUser(accountId, analytics, new_email, permission)

            fuser.writerow(temp)

          else:
            print 'Invalid email \n'
            print email

  except TypeError, error:
    print 'There was an error in constructing your query : %s' % error


def main():
  # Define the auth scopes to request.
  scope = ['https://www.googleapis.com/auth/analytics.manage.users']

  service_account_email = 'ga-access-service@ga-access-170702.iam.gserviceaccount.com'
  key_file_location = 'GA-access-c04b0c95bda0.p12'

  # Authenticate and construct service.
  service = get_service('analytics', 'v3', scope, key_file_location,
    service_account_email)

  accountId = '43181262'

  processUpdate(service, accountId)

if __name__ == '__main__':
  main()