# apps.py
#
# This module contains the NexusApp class and NexusApps collection class
# for use with Nexus IQ parsing tools.
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

class NexusApp:

  def __init__(self, name, appId, reportId=None):
    super(NexusApps, self).__init__()

    self._name = name
    self._appId = appId
    self._reportId = reportId
    self._dependencies = []

  def getAppId(self):
    return self._appId

  def getReportId(self):
    return self._reportId

  def setReportId(self, reportId):
    self._reportId = reportId

  def addDependency(self, depString):
    # FIXME should this be a set? can depstrings not be unique?
    # FIXME should we check first whether the dependency is present?
    self._dependencies.append(depString)

class NexusApps:

  def __init__(self, orgId):
    super(NexusApps, self).__init__()

    self._apps = {}
    self._orgId = orgId

  def addApp(self, name, appId):
    app = NexusApp(name, appId)
    self._apps[name] = app

  def getApp(self, name):
    return self._apps.get(name, None)

  def __len__(self):
    return len(self._apps)
