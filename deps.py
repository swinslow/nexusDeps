# deps.py
#
# This module contains the Dependency class for use with Nexus IQ
# parsing tools.
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

# helper function for dependency references
def depString(groupId, artifactId, version):
  if groupId:
    return f"{groupId} : {artifactId} : {version}"
  else:
    return f"{artifactId} : {version}"

def parseCoords(depData):
    gId = depData.get("groupId", None)
    aId = depData.get("artifactId", None)
    ver = depData.get("version", None)
    # FIXME temp fix; this is NOT the right way to do this
    if aId == None:
      identifier = depData.get("componentIdentifier", {})
      coordinates = identifier.get("coordinates", {})
      gId = None
      aId = coordinates.get("name", None)
      ver = coordinates.get("version", None)
    return (gId, aId, ver)


class DependencyError(Exception):
  """Exception raised when a dependency cannot be to the catalog.
  
  Attributes:
    message -- explanation of the error
  """

  def __init__(self, message):
    self.message = message

class Dependency:

  def __init__(self):
    super(Dependency, self).__init__()

    self._groupId = ""
    self._artifactId = ""
    self._version = ""
    self._status = ""
    self._licenses = {
      "final": [],
      "effective": [],
      "observed": [],
      "declared": []
    }
    self._overriddenLicenseThreat = -1
    self._effectiveLicenseThreat = -1

  def __repr__(self):
    return f"Dependency {self.depString()}"

  def depString(self):
    return depString(self._groupId, self._artifactId, self._version)

  def setValuesWithDict(self, depData):
    self._groupId = depData.get("groupId", None)
    self._artifactId = depData.get("artifactId", None)
    self._version = depData.get("version", None)
    self._status = depData.get("status", None)
    self._licenses["final"] = depData.get("overriddenLicenses", [])
    self._licenses["effective"] = depData.get("effectiveLicenses", [])
    self._licenses["observed"] = depData.get("observedLicenses", [])
    self._licenses["declared"] = depData.get("declaredLicenses", [])
    self._overriddenLicenseThreat = depData.get("overriddenLicenseThreat", None)
    self._effectiveLicenseThreat = depData.get("effectiveLicenseThreat", None)

    # FIXME temp fix; this is NOT the right way to do this
    if self._artifactId == None:
      identifier = depData.get("componentIdentifier", {})
      coordinates = identifier.get("coordinates", {})
      self._artifactId = coordinates.get("name", None)
      self._version = coordinates.get("version", None)

class DependencyCatalog:

  def __init__(self):
    super(DependencyCatalog, self).__init__()

    self._dependencies = {}

  def getDependency(self, groupId, artifactId, version):
    ds = depString(groupId, artifactId, version)
    return self._dependencies.get(ds, None)

  def hasDependency(self, groupId, artifactId, version):
    return bool(self.getDependency(groupId, artifactId, version))

  def addDependency(self, depData, update=False):
    # setting update=True causes us to update the dependency data, if already
    # present in the catalog

    # first, pull coordinates and check if dependency is already present
    groupId, artifactId, version = parseCoords(depData)
    ds = depString(groupId, artifactId, version)
    
    dep = self.getDependency(groupId, artifactId, version)
    if dep:
      if update:
        # remove it from the dict before we update; we will need to
        # reinsert it if the key changes
        self.delDependency(groupId, artifactId, version)
      else:
        raise DependencyError("Dependency already in catalog")
    else:
      # dependency not found, so create a new one
      dep = Dependency()
    
    # update Dependency contents and [re]insert into dict
    dep.setValuesWithDict(depData)
    self._dependencies[ds] = dep

    # return dependency string to caller
    return ds

  def delDependency(self, groupId, artifactId, version):
    ds = depString(groupId, artifactId, version)
    del self._dependencies[ds]

  def getDependencyList(self):
    return self._dependencies.values()

  # returns tuple (threat value #, licenses) or None if not found
  def getFinalLicenseForDepString(self, ds):
    dep = self._dependencies.get(ds, None)
    if not dep:
      return None
    finalLics = dep._licenses.get("final", None)
    if not finalLics:
      return None
    return (dep._overriddenLicenseThreat, sorted(finalLics))
