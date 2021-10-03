# main.py
#
# This module contains the main entry point for retrieving and parsing
# Nexus IQ reports.
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

import sys
import time
import json
from pathlib import Path

from apps import NexusApp, NexusAppCatalog
from deps import Dependency, DependencyCatalog
from reports import createCSVReport, createRedReport, createExcelReportAllLicenses
import jenkinstools
import nexustools

class NexusData:

  def __init__(self):
    super(NexusData, self).__init__()

    self._appCatalog = None
    self._depCatalog = DependencyCatalog()

    self._username = ""
    self._password = ""
    self._baseurl = ""
    self._jenkinsbaseurl = ""
    self._orgId = ""
    self._jsonDir = ""
    self._pdfReportsDir = ""
    self._reportsDir = ""
    self._statusJSON = ""

  def configure(self, configFilename):
    try:
      with open(configFilename, 'r') as f:
        js = json.load(f)

        # pull out the expected top-level parameters
        self._username = js.get('username', "")
        self._password = js.get('password', "")
        self._baseurl = js.get('baseurl', "")
        self._jenkinsbaseurl = js.get('jenkinsBaseurl', "")
        self._orgId = js.get('organizationId', "")
        self._jsonDir = js.get('jsonDir', "")
        self._pdfReportsDir = js.get('pdfReportsDir', "")
        self._reportsDir = js.get('reportsDir', "")
        self._statusJSON = js.get('statusJSON', "")

        isValid = True
        if self._username == "":
          print(f"No username found in config file.")
          isValid = False
        if self._password == "":
          print(f"No password found in config file.")
          isValid = False
        if self._baseurl == "":
          print(f"No baseurl found in config file.")
          isValid = False
        if self._jenkinsbaseurl == "":
          print(f"No jenkinsBaseurl found in config file.")
          isValid = False
        if self._orgId == "":
          print(f"No organizationId found in config file.")
          isValid = False
        if self._jsonDir == "":
          print(f"No jsonDir found in config file.")
          isValid = False
        if self._pdfReportsDir == "":
          print(f"No pdfReportsDir found in config file.")
          isValid = False
        if self._reportsDir == "":
          print(f"No reportsDir found in config file.")
          isValid = False
        if self._statusJSON == "":
          print(f"No statusJSON found in config file.")
          isValid = False

        if not isValid:
          return False

        # configure the app catalog with the org ID
        self._appCatalog = NexusAppCatalog(self._orgId)
        return True

    except json.decoder.JSONDecodeError as e:
      print(f'Error loading or parsing {configFilename}: {str(e)}')
      return False

  def loadAppInitialData(self):
    # get list of all Nexus applications and app IDs
    apps_rj = nexustools.getNexusApplications(
      self._baseurl,
      self._username,
      self._password
    )

    # parse it for the given org ID and get app (name, id) tuples
    apps = nexustools.parseNexusApplicationsJSON(self._orgId, apps_rj)

    # create apps in catalog
    # don't get report IDs yet (don't want to keep pinging the server)
    for name, appId in apps:
      self._appCatalog.addApp(name, appId)

  def loadAppInitialDataFromJenkins(self):
    print(f"getting main URLs list from Jenkins...")
    job_url_branch_ts = jenkinstools.getMainUrlList(self._jenkinsbaseurl)

    job_report_urls = []
    print(f"getting report IDs from Jenkins...")
    for (job_url, job_branch_id) in job_url_branch_ts:
      report_id, job_app_id = jenkinstools.getReportIDs(job_url)
      if report_id:
        # don't have the hash appID yet, just the short app id (publicID)
        self._appCatalog.addApp(job_app_id, "", job_branch_id, report_id)
        print(f"  => Added app {job_app_id} with branch {job_branch_id}")
      else:
        print(f"  => Couldn't get report ID for branch {job_branch_id}; skipping")

      time.sleep(0.25)

  
  def loadReportId(self, appName):
    app = self._appCatalog.getApp(appName)
    if not app:
      print(f"Couldn't get app {appName} from known apps.")
      return False

    reportId = app.getReportId()
    if reportId:
      # already present, no need to re-load
      return reportId

    # get Nexus JSON data for this app
    appId = app.getAppId()
    app_rj = nexustools.getNexusApplicationJSON(
      self._baseurl,
      self._username,
      self._password,
      appId
    )
    if not app_rj:
      print(f"Couldn't load application JSON data for app {appName}.")
      return False

    # parse it to extract reportId
    reportId = nexustools.parseNexusApplicationJSONForReportID(appId, app_rj)
    if reportId == -1 or reportId is None:
      print(f"Couldn't get reportId for app {appName}.")
      return False

    # and add to app object
    app.setReportId(reportId)
    return reportId

  def getLicenses(self, appBranch):
    # first, make sure we can get the app data
    app = self._appCatalog.getApp(appBranch)
    if not app:
      print(f"Couldn't load app branch {appBranch} from internal app catalog; skipping.")
      return False

    # make sure report ID was obtained
    if not app._reportId:
      print(f"No report ID for {appBranch}; skipping.")
      return False

    # get the license JSON data
    lic_rj = nexustools.getNexusLicenseJSON(
      self._baseurl,
      self._username,
      self._password,
      app._name,
      app._reportId,
      f"{self._jsonDir}/{appBranch}.orig.json"
    )
    if not lic_rj:
      print(f"Couldn't get data from report for {appBranch}; skipping.")
      return False

    # don't parse it using nexustools
    # just extract the list from aaData key and start parsing for dependencies
    components = lic_rj.get("aaData", [])
    for component in components:
      ds = self._depCatalog.addDependency(
        component,
        appName=appBranch,
        update=True
      )
      app.addDependency(ds)

  def getAllLicensesAndReports(self):
    for appBranch in self._appCatalog.getAllAppBranches():
      print(f"{appBranch}: getting license data...")
      self.getLicenses(appBranch)
      time.sleep(0.25)


########## initial entry point ##########

if __name__ == "__main__":
  ran_command = False
  
  if len(sys.argv) == 2:
    command = sys.argv[1]
    if command == "licenses":
      ran_command = True

      nd = NexusData()
      # FIXME let config file be user-definable
      homedir = str(Path.home())
      nd.configure(f"{homedir}/.nexusiq/config.json")
      nd.loadAppInitialDataFromJenkins()
      time.sleep(0.5)

      nd.getAllLicensesAndReports()
      xlsx_filename = f"{nd._reportsDir}/report.xlsx"
      print(f"creating report at {xlsx_filename}...")
      createExcelReportAllLicenses(nd, xlsx_filename)
      print(f"creating red report...")
      createRedReport(nd)

      print("Exiting.")
  
  if ran_command == False:
    print(f"Usage: {sys.argv[0]} <command>")
    print(f"Commands:")
    print(f"  licenses:       Get licenses for all dependencies")
    print(f"")
