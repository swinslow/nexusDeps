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
import nexustools

class NexusData:

  def __init__(self):
    super(NexusData, self).__init__()

    self._appCatalog = None
    self._depCatalog = DependencyCatalog()

    self._username = ""
    self._password = ""
    self._baseurl = ""
    self._orgId = ""
    self._reportsDir = ""

  def configure(self, configFilename):
    try:
      with open(configFilename, 'r') as f:
        js = json.load(f)

        # pull out the expected top-level parameters
        self._username = js.get('username', "")
        self._password = js.get('password', "")
        self._baseurl = js.get('baseurl', "")
        self._orgId = js.get('organizationId', "")
        self._reportsDir = js.get('reportsDir', "")

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
        if self._orgId == "":
          print(f"No organizationId found in config file.")
          isValid = False
        if self._reportsDir == "":
          print(f"No reportsDir found in config file.")
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

  def getLicenses(self, appName):
    # first, make sure we can get the app data
    app = self._appCatalog.getApp(appName)
    if not app:
      print(f"Couldn't load app {appName} from internal app catalog.")

    # make sure report ID is already loaded
    reportId = self.loadReportId(appName)
    if not reportId:
      print(f"Couldn't load report ID for {appName}.")
      return False

    # get the license JSON data
    lic_rj = nexustools.getNexusLicenseJSON(
      self._baseurl,
      self._username,
      self._password,
      appName,
      reportId,
      f"{self._reportsDir}/{appName}.orig.json"
    )

    # don't parse it using nexustools
    # just extract the list from aaData key and start parsing for dependencies
    components = lic_rj.get("aaData", [])
    for component in components:
      ds = self._depCatalog.addDependency(component, update=True)
      app.addDependency(ds)

  def createReport(self, appName):
    try:
      filename = f"{self._reportsDir}/{appName}.csv"
      with open (filename, 'w') as fout:
        app = self._appCatalog.getApp(appName)
        fout.write('"Threat level", Licenses, Component\n')
        # FIXME don't reach into app vars to handle _dependencies directly!
        for ds in sorted(app._dependencies):
          retval = self._depCatalog.getFinalLicenseForDepString(ds)
          if retval:
            (threat, lics) = retval
            finalStr = ""
          else:
            # if not finalized, check the effective licenses
            retval2 = self._depCatalog.getEffectiveLicenseForDepString(ds)
            if retval2:
              (threat, lics) = retval2
              threat = "*" + str(threat)
              finalStr = "***"
            else:
              # if still couldn't get that, leave a blank
              (threat, lics) = "***", []
              finalStr = "***"
          licString = finalStr + " AND ".join(lics)
          fout.write(f'"{threat}","{licString}","{ds}"\n')
          #print(f"  -- {threat} [{lics}]: {ds}")

    except Exception as e:
      print((f"Couldn't output report to {filename}: {str(e)}"))

  def getAllLicensesAndReports(self):
    for appName in self._appCatalog.getAllAppNames():
      print(f"{appName}: getting license data...")
      self.getLicenses(appName)
      print(f"{appName}: creating report...")
      self.createReport(appName)
      time.sleep(0.5)

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
      nd.loadAppInitialData()
      time.sleep(0.5)

      #nd.getAllLicensesAndReports()
      # TEMP
      appName = "aai-aai-service"
      print(f"{appName}: getting license data...")
      nd.getLicenses(appName)
      print(f"{appName}: creating report...")
      nd.createReport(appName)

      print("Exiting.")
  
  if ran_command == False:
    print(f"Usage: {sys.argv[0]} <command>")
    print(f"Commands:")
    print(f"  licenses:       Get licenses for all dependencies")
    print(f"  pdfs(NOT YET):  Get PDF reports for all dependencies")
    print(f"")
