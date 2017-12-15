# reports.py
#
# This module contains functions for generating analysis reports for
# Nexus IQ dependencies.
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

from operator import itemgetter
from xlsxwriter.workbook import Workbook

from categories import getCategoryForLicenseString

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
          licString = " AND ".join(sorted(licenseInfo.licenses))
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

# takes: (1) NexusData
# returns: (1) dict of {category, {licString => [Dependencies]}}
#          (2) dict of {licString => # of occurrences}
def collectAllLicenses(nd):
  licCatalog = {}
  licCount = {}

  for ds, dep in nd._depCatalog._dependencies.items():
    # get license info for this dependency
    licenseInfo = dep.getBestLicenseInfo()
    if licenseInfo:
      licString = " AND ".join(sorted(licenseInfo.licenses))
      category = getCategoryForLicenseString(licString)
    else:
      licString = "NOT FOUND"
      category = "Not found"

    # if we've already seen this threat, check for this license
    ld = licCatalog.get(category, None)
    if ld is None:
      ld = {}
      licCatalog[category] = ld

    # within this threat, if we've already seen this license, add this dep
    # to the list
    dl = ld.get(licString, None)
    if dl is not None:
      dl.append(dep)
    else:
      ld[licString] = [dep]

    # add to licCount if first instance or increment if already seen
    licCount[licString] = licCount.get(licString, 0) + 1

  return licCatalog, licCount

# takes: (1) NexusData, (2) filename for Excel file to create
# returns: True if successfully created report, False otherwise
def createExcelReportAllLicenses(nd, xlsx_filename):
  licCatalog, licCount = collectAllLicenses(nd)
  #print(f"licCount = {licCount}")

  try:
    with Workbook(xlsx_filename) as workbook:

      # prepare formats
      bold = workbook.add_format({'bold': True})
      bold.set_font_size(16)
      normal = workbook.add_format()
      normal.set_font_size(14)
      normal.set_text_wrap(True)

      ##### STATS PAGE #####

      # build stats page
      statsSheet = workbook.add_worksheet("License counts")
      statsSheet.write(0, 0, "License", bold)
      statsSheet.write(0, 2, "# of files", bold)
      # set column widths
      statsSheet.set_column(0, 0, 2)
      statsSheet.set_column(1, 1, 58)
      statsSheet.set_column(2, 2, 10)

      total = 0
      row = 2

      for category, catDict in licCatalog.items():
        # print category name in bold in column A
        statsSheet.write(row, 0, category + ":", bold)
        row = row + 1

        # now, loop through licenses in this category,
        # outputting name in col B and count in col C
        for licString, deps in sorted(catDict.items()):
          numDeps = len(deps)
          statsSheet.write(row, 1, licString, normal)
          statsSheet.write(row, 2, numDeps, normal)
          total = total + numDeps
          row = row + 1
      # lic_tuples = sorted(licCount.items())
      # for license, count in lic_tuples:
      #   statsSheet.write(row, 1, license, normal)
      #   statsSheet.write(row, 2, count, normal)
      #   total = total + count
      #   row = row + 1

      # at the end, skip another row, then output the total
      row = row + 1
      statsSheet.write(row, 1, "TOTAL", bold)
      statsSheet.write(row, 2, total, bold)

      ##### CATEGORY PAGES #####

      for threat, licdict in licCatalog.items():
        # build dep / license page for each threat
        depSheet = workbook.add_worksheet(f"{threat}")
        depSheet.write(0, 0, "License", bold)
        depSheet.write(0, 1, "Dependency", bold)
        depSheet.write(0, 2, "Apps", bold)
        # set column widths
        depSheet.set_column(0, 0, 80)
        depSheet.set_column(1, 1, 80)
        depSheet.set_column(2, 2, 80)

        # create list of tuples: (license, depstring, [appNames]) so we can
        # sort it
        deptuples = []
        for licString, deps in licdict.items():
          for dep in deps:
            appNamesString = ", ".join(dep.getAppNames())
            #print(f"licString = {licString}, dep = {dep.depString()}, appNamesString = {appNamesString}")
            dt = (licString, dep.depString(), appNamesString)
            deptuples.append(dt)

        # now, sort by license and then by dependency
        deptuples = sorted(deptuples, key=itemgetter(0, 1))

        # now, loop through deps and licenses in this category,
        # outputting license in col A, dep in col B and apps in col C
        row = 1
        for licString, depString, appNamesString in deptuples:
          depSheet.write(row, 0, licString, normal)
          depSheet.write(row, 1, depString, normal)
          depSheet.write(row, 2, appNamesString, normal)
          row = row + 1

    # ... and that's it!
    return True

  except Exception as e:
    print(f"Couldn't output Excel full listing to {xlsx_filename}: {str(e)}")
    return False
