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

import requests

########## JENKINS URL HELPER FUNCTIONS ##########

# Build URL for retrieving list of apps in Jenkins.
# arguments:
#   1) base URL for Nexus IQ server
# returns: URL for retrieving JSON data.
def getJenkinsMainURL(baseurl):
  return f"{baseurl}/api/json"

########## JENKINS RETRIEVAL FUNCTIONS ##########

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

########## Jenkins PARSING FUNCTIONS ##########

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

