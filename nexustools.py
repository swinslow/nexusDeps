# nexustools.py
#
# This module contains functions for retrieving and parsing Nexus IQ reports.
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

########## NEXUS URL HELPER FUNCTIONS ##########

# Build URL for retrieving a PDF report, without actually calling it.
# arguments:
#   1) base URL for Nexus IQ server
#   2) application name
#   3) report ID for this application
# returns: URL for retrieving PDF report, or None if error.
def getNexusReportPDFURL(baseurl, appName, reportId):
  return f"{baseurl}/rest/report/{appName}/{reportId}/printReport"

# Build URL for retrieving license JSON data, without actually calling it.
# arguments:
#   1) base URL for Nexus IQ server
#   2) application name
#   3) report ID for this application
# returns: URL for retrieving license JSON data, or None if error.
def getNexusLicenseJSONURL(baseurl, appName, reportId):
  return f"{baseurl}/rest/report/{appName}/{reportId}/browseReport/licenses.json"

########## NEXUS RETRIEVAL FUNCTIONS ##########

# Logs into NexusIQ server, retrieves details about all applications on that
# server, and returns the corresponding JSON dict.
# arguments:
#   1) base URL for Nexus IQ server
#   2) user name
#   3) user password
# returns: dict with JSON from NexusIQ server /applications API call, or None
#   if error.
def getNexusApplications(baseurl, username, password):
  auth = requests.auth.HTTPBasicAuth(username, password)
  r = requests.get(f"{baseurl}/api/v2/applications", auth=auth)
  if r.status_code != 200:
    print(f"Error: Got invalid status code {r.status_code} from /applications call")
    return None

  rj = r.json()
  return rj

# Logs into NexusIQ server, retrieves data about a specific application,
# and returns the corresponding JSON dict.
# arguments:
#   1) base URL for Nexus IQ server
#   2) user name
#   3) user password
#   4) application ID
# returns: dict with JSON from NexusIQ server /reports/applications/[appId]
#   call, or None if error.
def getNexusApplicationJSON(baseurl, username, password, appId):
  auth = requests.auth.HTTPBasicAuth(username, password)
  url = f"{baseurl}/api/v2/reports/applications/{appId}"
  r = requests.get(url, auth=auth)
  if r.status_code != 200:
    print(f"Error: Got invalid status code {r.status_code} from /reports/applications/{appId} call")
    return None

  rj = r.json()
  return rj

# Retrieve a Nexus IQ PDF report and write it out to disk.
# arguments:
#   1) base URL for Nexus IQ server
#   2) user name
#   3) user password
#   4) appplication name
#   5) report ID for this application
#   6) report filename path
# returns: filename if successfully wrote to disk, or None if error.
def getNexusReportPDF(baseurl, username, password, appName, reportId,
  filename):
  # get report URL from helper
  url = getNexusReportPDFURL(baseurl, appName, reportId)
  if not url:
    return None

  # make API call
  auth = requests.auth.HTTPBasicAuth(username, password)
  r = requests.get(url, auth=auth)
  if r.status_code != 200:
    print(f"Error: Got invalid status code {r.status_code} from PDF report retrieval call for {appName}")
    return None

  try:
    # write report data out to disk
    with open(filename, 'wb') as f:
      f.write(r.content)
    return filename

  except Exception as e:
    print(f"Couldn't output PDF report to {filename}: {str(e)}")
    return None

# Retrieve a Nexus IQ JSON license report and return it, optionally writing
# it out to disk.
# arguments:
#   1) base URL for Nexus IQ server
#   2) user name
#   3) user password
#   4) appplication name
#   5) report ID for this application
#   6) optional: report filename path; None to skip writing to disk
# returns: dict with JSON from NexusIQ server licenses.json call, or
#   None if error.
def getNexusLicenseJSON(baseurl, username, password, appName, reportId,
  filename=None):
  # get license JSON URL from helper
  url = getNexusLicenseJSONURL(baseurl, appName, reportId)
  if not url:
    return None

  # make API call
  auth = requests.auth.HTTPBasicAuth(username, password)
  r = requests.get(url, auth=auth)
  if r.status_code != 200:
    print(f"Error: Got invalid status code {r.status_code} from JSON license data retrieval call for {appName}")
    return None

  # write the JSON data to disk if asked to do so
  if filename:
    try:
      # write report data out to disk
      with open(filename, 'wb') as f:
        f.write(r.content)

    except Exception as e:
      print(f"Couldn't output JSON license data to {filename}: {str(e)}")
      return None

  # finally, return the JSON data
  rj = r.json()
  return rj

########## NEXUS PARSING FUNCTIONS ##########

# Given a NexusIQ /applications response dict, parse and return data for just
# the applications corresponding to the requested org ID.
# arguments:
#   1) Nexus IQ organization ID
#   2) dict with JSON from NexusIQ server /applications API call
#      typically obtained from getNexusApplications
# returns: list of tuples (app name, app ID) or empty list
def parseNexusApplicationsJSON(organizationId, rj):
  apps = []

  # pull applications key from JSON
  rjlist = rj.get("applications", None)
  if not rjlist:
    print("Error: couldn't get applications key from JSON response")
    return []

  for appdict in rjlist:
    # confirm it's the right organizationId
    appOrgId = appdict.get("organizationId", None)
    if not appOrgId or appOrgId != organizationId:
      # it's for a different org => skip it
      continue
    name = appdict.get("name", None)
    appId = appdict.get("id", None)
    appTuple = (name, appId)
    apps.append(appTuple)

  return apps

# Given a NexusIQ /reports/applications/[appId] response dict, parse and
# return the report ID for that application.
# arguments:
#   1) application ID
#   2) dict with JSON from NexusIQ server /reports/applications/[appId] API
#      call; typically obtained from getNexusApplicationJSON
# returns: report ID, -1 if no report available, or None if error.
def parseNexusApplicationJSONForReportID(appId, rj):
  if rj == []:
    print(f"No report available for {appId}.")
    return -1
  # this endpoint gives a list of apps; we just want the dict from
  # the first one
  rjd = rj[0]
  htmlUrl = rjd.get('reportHtmlUrl', None)
  if not htmlUrl:
    print(f"Couldn't get reportHtmlUrl key when parsing /reports/applications/{appId} data.")
    return None
  fragments = htmlUrl.split("/")
  reportId = fragments[-1]
  return reportId

# Given a NexusIQ licenses JSON dict, parse and return data for components and
# corresponding licenses for this application.
# arguments:
#   1) dict with JSON from NexusIQ server licenses.json API call
#      typically obtained from getNexusLicenseJSON
# returns: list of tuples or empty list
#   tuple format:    (component name, group name, version, licenses dict)
#   licenses format: { "declared" => [list of license strings],
#                      "observed" => [list of license strings],
#                      "effective" => [list of license strings] }
def parseNexusLicenseJSON(rj):
  components = []

  # pull aaData key from JSON
  rjlist = rj.get("aaData", None)
  if not rjlist:
    print("Error: couldn't get aaData key from JSON response")
    return []

  for componentDict in rjlist:
    # extract data from JSON for each component
    name = componentDict.get("artifactId", None)
    group_name = componentDict.get("groupId", None)
    version = componentDict.get("version", None)
    licenses_declared = componentDict.get("declaredLicenses", [])
    licenses_observed = componentDict.get("observedLicenses", [])
    licenses_effective = componentDict.get("effectiveLicenses", [])

    # build licenses dict, keeping licenses as lists of strings
    licenses = {}
    licenses["declared"] = licenses_declared
    licenses["observed"] = licenses_observed
    licenses["effective"] = licenses_effective

    # build tuple and append to components list
    componentTuple = (name, group_name, version, licenses)
    components.append(componentTuple)

  return components

# Given a single license string parsed from a NexusIQ file, normalize it and
# return an SPDX-style-formatted license string.
# NOTE: Does NOT incorporate "LicenseRef-" tags into non-standard SPDX
#   license names!
# arguments:
#   1) license_str: single license string from NexusIQ
#   2) multiple_strs: if True, this component has multiple license strings
# returns: string with single licenses in SPDX-like form.
def getNormalizedSPDXStyleString(license_str, multiple_strs=True):
  new_str = license_str

  # if there's an " or " in the string, capitalize it
  new_str = new_str.replace(" or ", " OR ")

  # if any changes have been made, AND if multiple_strs is True, then we
  # need to surround this with parentheses b/c it'll be AND'd with other
  # license strings
  if new_str != license_str and multiple_strs:
    new_str = f"({new_str})"

  return new_str

# Given a dict of licenses parsed from a NexusIQ file, parse and return a
# normalized, SPDX-style-formatted license string.
# NOTE: Does NOT incorporate "LicenseRef-" tags into non-standard SPDX
#   license names!
# All licenses (declared, observed or effective) should be collapsed together,
# de-duplicated, normalized (fixing capitalization and OR'ing + ()'ing as
# needed), and then AND'd into a single string.
# Disregard "Not detected" and equivalents if at least one license is found.
# arguments:
#   1) licenses dict in format: { "declared" => [list of license strings],
#                                 "observed" => [list of license strings],
#                                 "effective" => [list of license strings] }
# returns: string with all licenses in SPDX-like form.
def getSPDXStyleString(licenses):
  declared = licenses.get("declared", [])
  observed = licenses.get("observed", [])
  effective = licenses.get("effective", [])

  # First, collapse all strings together into a de-duped list
  licenses_set = set().union([declared, observed, effective])
  licenses_list = list(licenses_set)

  # Next, get the normalized version of each string
  multiple_strs = (len(licenses_list) > 1)
  normalized_licenses = [
    getNormalizedSPDXStyleString(lic, multiple_strs) for lic in licenses_list
  ]

  # Now, if all we've got is a single license, then just return it as-is
  if len(normalized_licenses) == 1:
    return normalized_licenses[0]

  # Then, extract and leave out licenses that we don't care about in combos
  excluded_strings = [
    "No Source License",
    "Not Declared",
    "No Sources",
    "Not Provided",
  ]
  final_licenses = [
    lic for lic in normalized_licenses if lic not in excluded_strings
  ]
  # ...but if all we have is excluded licenses, then keep them all
  if len(final_licenses) == 0:
    final_licenses = normalized_licenses

  # Finally, combine them all
  lic_string = " AND ".join(final_licenses)

  return lic_string
