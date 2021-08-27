# conversions.py
#
# This module contains a function to convert various license strings to other
# strings.
#
# Copyright (C) 2019 The Linux Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#
# SPDX-License-Identifier: Apache-2.0

CONVERSIONS = {
    "EDL-1.0 AND EPL-1.0": "EPL-1.0 AND BSD-3-Clause",
    "BSD-3-Clause AND EDL-1.0": "BSD-3-Clause",
    "BSD-3-Clause AND EDL-1.0 AND MIT": "BSD-3-Clause AND MIT",
    "BSD AND Generic-Liberal-Clause": "BSD-3-Clause",
    "Apache-2.0 AND BSD-3-Clause AND Generic-Open-Source-Clause": "Apache-2.0 AND BSD-3-Clause",
}

# takes: (1) license string
# returns: converted string if contains conversion, or same string otherwise
def getConvertedLicenseString(licString):
    if licString not in CONVERSIONS:
        return licString
    return CONVERSIONS[licString]
