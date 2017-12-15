# categories.py
#
# This module contains a function to categorize various license strings.
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

# takes: (1) license string
# returns: string for category to use in reporting
def getCategoryForLicenseString(licString):
  if licString == "Apache-2.0":
    return "Apache-2.0"

  if licString in [
    "Apache-2.0 AND BSD-4-Clause",
    "BSD-3-Clause AND BSD-4-Clause",
    "BSD-4-Clause",
  ]:
    return "Advertising Clause"

  if licString in [
    "AFL-2.1",
    "AFL-2.1 AND Apache-2.0",
    "ANTLR-PD AND BSD-3-Clause",
    "Apache",
    "Apache-1.1",
    "Apache-1.1 AND Apache-2.0",
    "Apache-1.1 AND Apache-2.0 AND BSD-2-Clause AND BSD-3-Clause AND Public Domain AND XPP-1.1.1 AND XPP-1.2",
    "Apache-1.1 AND Apache-2.0 AND BSD-3-Clause",
    "Apache-1.1 AND Apache-2.0 AND MIT",
    "Apache-1.1 AND Apache-2.0 AND XPP-1.2",
    "Apache-1.1 AND BSD-3-Clause",
    "Apache-1.1 AND Public Domain AND XPP-1.1.1 AND XPP-1.2",
    "Apache-2.0 AND BSD",
    "Apache-2.0 AND BSD AND BSD-3-Clause",
    "Apache-2.0 AND BSD-2-Clause",
    "Apache-2.0 AND BSD-2-Clause AND BSD-3-Clause AND Non-Standard",
    "Apache-2.0 AND BSD-3-Clause",
    "Apache-2.0 AND BSD-3-Clause AND CC-BY-2.5",
    "Apache-2.0 AND BSD-3-Clause AND MIT",
    "Apache-2.0 AND BSD-3-Clause AND MIT AND Public Domain",
    "Apache-2.0 AND CC-BY-2.5",
    "Apache-2.0 AND ISC",
    "Apache-2.0 AND MIT",
    "Apache-2.0 AND Public Domain",
    "Apache-2.0 AND Public Domain AND W3C",
    "Apache-2.0 AND W3C",
    "Artistic-2.0",
    "BSD",
    "BSD AND MIT",
    "BSD AND WTFPL",
    "BSD-2-Clause",
    "BSD-2-Clause AND BSD-3-Clause",
    "BSD-2-Clause AND BSD-3-Clause AND MIT",
    "BSD-2-Clause AND MIT",
    "BSD-2-Clause AND WTFPL",
    "BSD-3-Clause",
    "BSD-3-Clause AND MIT",
    "BSD-3-Clause AND WTFPL",
    "CC-BY-2.5",
    "CC-BY-3.0 AND MIT",
    "CC-BY-3.0 AND MIT AND OFL-1.1",
    "ISC",
    "MIT",
    "MIT AND OFL-1.1",
    "MIT AND Public Domain",
    "NTP",
    "PostgreSQL",
    "Public Domain AND W3C AND Zlib",
    "Public Domain AND XPP-1.2",
    "Zlib",
  ]:
    return "Attribution"

  if licString in [
    "Apache-2.0 AND CC0-1.0",
    "Apache-2.0 AND CC0-1.0 AND Public Domain",
    "BSD-3-Clause AND CC0-1.0",
    "CC0-1.0",
    "CC0-1.0 AND Public Domain",
  ]:
    return "CC0"

  if licString in [
    "Apache-1.1 AND Apache-2.0 AND GPL-3.0",
    "Apache-2.0 AND BSD-3-Clause AND GPL-2.0-with-classpath-exception AND MIT",
    "Apache-2.0 AND GPL-3.0",
    "GPL",
    "GPL-2.0",
    "GPL-2.0-with-classpath-exception AND MIT",
    "GPL-3.0",
    "GPL-3.0 AND MIT",
  ]:
    return "Copyleft"

  if licString in [
    "Apache-1.1 AND Sun-IP",
    "Apache-2.0 AND Public Domain AND Sun-IP AND W3C",
    "Sun-IP",
    "Sun-Restricted",
    "MIT AND Public Domain AND Sun-IP",
    "Apache-1.1 AND Apache-2.0 AND CDDL-1.0 AND Sun-IP AND Sun-Restricted",
    "Apache-1.1 AND Apache-2.0 AND Sun-IP",
  ]:
    return "Proprietary Notices"

  if licString in [
    "Public Domain"
  ]:
    return "Public Domain"

  if licString in [
    "Apache-2.0 AND BSD-2-Clause AND BSD-3-Clause AND ISO-8879",
    "Apache-2.0 AND OASIS AND W3C AND WS-Addressing-200408",
    "Apache-2.0 AND W3C AND WS-Addressing-200403 AND WS-Addressing-200408",
    "Apache-2.0 AND OASIS",
    "Apache-2.0 AND OASIS AND W3C",
    "Apache-2.0 AND OASIS AND WS-Addressing-200408",
    "ISO-8879",
    "OASIS",
    "OASIS AND WS-Addressing-200408",
    "WS-Addressing-200403 AND WS-Addressing-200408",
    "WS-Addressing-200408",
  ]:
    return "Standards Bodies"

  if licString in [
    "Apache-2.0 AND CDDL-1.1 AND JSON AND Sun-IP",
    "Apache-2.0 AND JSON",
    "CC-BY-NC-3.0",
    "COMMERCIAL",
    "JSON",
    "Sun",
  ]:
    return "Use Restrictions"

  if licString in [
    "Adobe-AFM AND Apache AND BSD-3-Clause AND CC-BY-2.5 AND MIT AND MPL-1.1 AND Non-Standard AND Public Domain AND Unicode",
    "Adobe-AFM AND Apache-2.0 AND BSD-3-Clause AND MPL-1.1 AND Non-Standard AND Public Domain AND Unicode",
    "Apache-1.1 AND Apache-2.0 AND LGPL-2.1 AND Non-Standard AND W3C",
    "Apache-1.1 AND CDDL-1.1 AND Sun-Restricted",
    "Apache-1.1 AND CPL-1.0 AND EPL-1.0",
    "Apache-1.1 AND EPL-1.0",
    "Apache-1.1 AND LGPL-3.0",
    "Apache-2.0 AND BSD-3-Clause AND CDDL-1.0 AND CDDL-1.1 AND EPL-1.0 AND MIT AND Non-Standard AND Public Domain AND Sun-IP",
    "Apache-2.0 AND BSD-3-Clause AND CDDL-1.1",
    "Apache-2.0 AND BSD-3-Clause AND CDDL-1.1 AND MIT",
    "Apache-2.0 AND BSD-3-Clause AND CPL-1.0 AND Public Domain",
    "Apache-2.0 AND BSD-3-Clause AND EPL-1.0",
    "Apache-2.0 AND BSD-3-Clause AND EPL-1.0 AND MIT AND MPL-1.1 AND Non-Standard AND Public Domain AND Sun-IP AND Sun-Restricted AND W3C",
    "Apache-2.0 AND CC0-1.0 AND CDDL-1.1 AND Public Domain",
    "Apache-2.0 AND CDDL-1.0",
    "Apache-2.0 AND CDDL-1.0 AND CDDL-1.1",
    "Apache-2.0 AND CDDL-1.0 AND CDDL-1.1 AND EPL-1.0 AND Sun-IP",
    "Apache-2.0 AND CDDL-1.1",
    "Apache-2.0 AND CDDL-1.1 AND EPL-1.0",
    "Apache-2.0 AND CDDL-1.1 AND Public Domain",
    "Apache-2.0 AND BSD-3-Clause AND CC-BY-2.5 AND CPL-1.0 AND Public Domain",
    "Apache-2.0 AND CPL-1.0 AND MIT",
    "Apache-2.0 AND CPL-1.0 AND Public Domain",
    "Apache-2.0 AND EPL-1.0",
    "Apache-2.0 AND HPND AND LGPL-2.1",
    "Apache-2.0 AND LGPL-2.1",
    "Apache-2.0 AND LGPL-2.1 AND LGPL-3.0",
    "Apache-2.0 AND LGPL-2.1 AND Public Domain",
    "Apache-2.0 AND MPL-1.1",
    "Apache-2.0 AND MPL-1.1 AND Public Domain",
    "Apache-1.1 AND Apache-2.0 AND CPL-1.0 AND LGPL-2.1",
    "Apache-1.1 AND Apache-2.0 AND EPL-1.0",
    "BSD-3-Clause AND CDDL-1.0 AND CDDL-1.1",
    "BSD-3-Clause AND CDDL-1.1",
    "BSD-3-Clause AND EPL-1.0",
    "BSD-3-Clause AND LGPL-2.1",
    "BSD-3-Clause AND MPL-2.0",
    "BSD-3-Clause AND MPL-2.0 AND Public Domain",
    "BSD-4-Clause AND EPL-1.0",
    "CC-BY-2.5 AND LGPL-3.0",
    "CDDL-1.0",
    "CDDL-1.0 AND Sun-IP",
    "CDDL-1.0 AND Sun-IP AND Sun-Restricted",
    "CDDL-1.1",
    "CDDL-1.1 AND Sun-IP",
    "CDDL-1.1 or GPL-2.0",
    "CDDL-1.1 or GPL-2.0 AND CDDL-1.1 or GPL-2.0-CPE",
    "CPL-1.0",
    "CPL-1.0 AND ISO-8879",
    "EPL-1.0",
    "LGPL",
    "LGPL-2.1",
    "LGPL-3.0",
    "MPL-1.1",
  ]:
    return "Weak Copyleft"

  return "Other"
