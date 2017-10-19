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

def createCSVReport(nd, appName):
  try:
    filename = f"{nd._reportsDir}/{appName}.csv"
    with open (filename, 'w') as fout:
      app = nd._appCatalog.getApp(appName)
      fout.write('"Threat level",Licenses,Status,Component\n')
      # FIXME don't reach into app vars to handle _dependencies directly!
      for ds in sorted(app._dependencies):
        licenseInfo = nd._depCatalog.getBestLicenseInfoForDepString(ds)
        if not licenseInfo:
          fout.write(f'"N/A","N/A","{ds}"\n')
        else:
          licString = " AND ".join(licenseInfo.licenses)
          threat = licenseInfo.threat
          status = licenseInfo.status
          fout.write(f'"{threat}","{licString}","{status}","{ds}"\n')

  except Exception as e:
    print((f"Couldn't output report to {filename}: {str(e)}"))

def getRedDependencies(nd):
  return nd._depCatalog.getRedDependencies()

def createRedReport(nd):
  print(f"Creating red dependency threat report...")
  try:
    filename = f"{nd._reportsDir}/RedDependencies.txt"
    with open (filename, 'w') as fout:
      redDeps = getRedDependencies(nd)
      for redDep in redDeps:
        (dep, licenseInfo) = redDep
        licString = " AND ".join(licenseInfo.licenses)
        fout.write(f"* {dep}:\n")
        fout.write(f"   -- Threat: {licenseInfo.threat}\n")
        fout.write(f"   -- License: {licString}\n")
        fout.write(f"   -- Used in: {dep.getAppNames()}\n")

  except Exception as e:
    print((f"Couldn't output red dependencies report to {filename}: {str(e)}"))
