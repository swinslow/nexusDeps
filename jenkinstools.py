# jenkinstools.py
#
# This module contains functions for retrieving and parsing Jenkins details
# so we can get the right list of repos to look up in Nexus.
#
# Copyright (C) 2017 The Linux Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

import os
import time

import bs4
import requests

def getMainUrlList(jenkinsbaseurl):
  r = requests.get(jenkinsbaseurl)

  soup = bs4.BeautifulSoup(r.content, "lxml")
  elt = soup.find(id="projectstatus")
  trs = elt.find_all("tr")
  jobs = []
  for tr in trs:
    tr_id = tr.attrs.get("id", "")
    if tr_id.startswith("job_"):
      job = tr_id.split("_", maxsplit=1)[1]
      jobs.append(job)

  job_url_branch_ts = []
  for job in jobs:
    job_url = f"{jenkinsbaseurl}/job/{job}"
    job_url_branch_t = (job_url, job)
    job_url_branch_ts.append(job_url_branch_t)

  return job_url_branch_ts

def getReportIDs(job_url):
  # try main report link
  r = requests.get(job_url)

  soup = bs4.BeautifulSoup(r.content, "lxml")
  t = soup.find(class_="iq-block")
  if t:
    t1 = t.find("a")
    if t1:
      report_url = t1.attrs.get("href", "")
      if report_url:
        report_id = report_url.rsplit("/", maxsplit=1)[1]
        job_id_partial_url = report_url.split("application/", maxsplit=1)[1]
        job_app_id = job_id_partial_url.split("/", maxsplit=1)[0]
        return (report_id, job_app_id)

  # couldn't get it from main screen; try last successful build, if there is one
  r = requests.get(f"{job_url}/lastSuccessfulBuild")
  if r.status_code != 200:
    return "", ""

  soup = bs4.BeautifulSoup(r.content, "lxml")
  t = soup.find(class_="iq-block")
  if t:
    t1 = t.find("a")
    if t1:
      report_url = t1.attrs.get("href", "")
      if report_url:
        report_id = report_url.rsplit("/", maxsplit=1)[1]
        job_id_partial_url = report_url.split("application/", maxsplit=1)[1]
        job_app_id = job_id_partial_url.split("/", maxsplit=1)[0]
        return (report_id, job_app_id)

  return "", ""

######## OLD JENKINS FUNCTIONS BELOW HERE ########

# OLD ######### JENKINS URL HELPER FUNCTIONS ##########

# Build URL for retrieving list of apps in Jenkins.
# arguments:
#   1) base URL for Nexus IQ server
# returns: URL for retrieving JSON data.
def getJenkinsMainURL(baseurl):
  return f"{baseurl}/api/json"

# OLD ######### JENKINS RETRIEVAL FUNCTIONS ##########

# Retrieves details about all applications from Jenkins server, and returns
# the corresponding JSON dict.
# arguments:
#   1) base URL for Nexus IQ server
# returns: dict with JSON from Jenkins server API call, or None if error.
def getJenkinsAllApplications(baseurl):
  url = getJenkinsMainURL(baseurl)
  r = requests.get(url)
  if r.status_code != 200:
    print(f"Error: Got invalid status code {r.status_code} from {url}")
    return None

  rj = r.json()
  return rj

# OLD ######### Jenkins PARSING FUNCTIONS ##########

# Given a Jenkins response dict from a main CLM JSON call, parse and return
# data for those applications.
# If a filter is provided, filter for just apps containing those chars.
# arguments:
#   1) dict with JSON from Jenkins server main CLM API call
#      typically obtained from getJenkinsAllApplications()
# returns: list of tuples (app name, CLM app URL) or empty list
def parseJenkinsAllApplicationsJSON(rj, filtertext=None):
  apps = []

  # pull jobs key from JSON
  rjlist = rj.get("jobs", None)
  if not rjlist:
    print("Error: couldn't get 'jobs' key from JSON response")
    return []

  for appdict in rjlist:
    name = appdict.get("name", None)
    url = appdict.get("url", None)
    appTuple = (name, url)
    if (filtertext is None or filtertext in name):
      apps.append(appTuple)

  return apps

