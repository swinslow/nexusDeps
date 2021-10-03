# nexusDeps

nexusDeps is a command-line tool to retrieve license scanning and clearing results from a Nexus IQ CLM server, and preparing reports for delivery to project maintainers.

## Installation

In order to use nexusDeps, you will need a Nexus IQ CLM server to be separately set up.

nexusDeps requires Python 3. You may want to create a [virtual environment](https://pypi.org/project/virtualenvwrapper/) for the installation.

Install the requirements from requirements.txt: `pip install -r requirements.txt`

## Initial Configuration

In your home directory, create a subfolder `.nexusiq/`, and inside that subfolder create a file `config.json` with the contents from the sample at [`config-template.json`](./config-template.json).

Update the website and login fields with the appropriate URLs and credentials.

On your local machine, create a directory where the results will be retrieved and stored, and create subfolders as shown in the `config.json` file, updating the locations in that file accordingly. (Note that pdfReports and status.json are not actually implemented yet, so although it's necessary to include them in the `config.json` file because the config loader looks for those values, they will not actually be used.)

## Running nexusDeps

To run nexusDeps, from the directory where its code is stored, run: `python main.py licenses`

This will do the following:
1. Parse the Jenkins CLM page and its subpages to obtain the list of Nexus IQ reports
2. Log into the Nexus IQ server using the given credentials and Org ID
3. One by one, access each Nexus IQ report that was listed in step 1:
  - download its data and save it in `REPORTS-DIR/json/[reportname].orig.json`
  - parse that JSON file to extract its effective licenses data
  - apply any conversions defined in [`conversions.py`](./conversions.py), if desired, to clean up oddities in the way that Nexus IQ reports some license findings
  - apply categorizations defined in [`categories.py`](./categories.py), to categorize the license combinations into the desired buckets
4. After applying the above to all reports listed on the Jenkins CLM page, combine the results together
5. Create and save two reports in the `REPORTS-DIR/reports/` directory:
  - `report.xlsx`: An XLSX spreadsheet with (1) an overall summary listing of all categorized licenses on the first tab, and (2) subsequent tabs for each category showing the specific dependencies for each; and
  - `RedDependencies.txt`: A text file briefly describing any dependencies that were detected as currently being in the "red" (highest priority) level of concern for usage / compatibility, according to the policies defined within Nexus IQ.

## Notes on workflow

The categories in [`categories.py`](./categories.py) are configured for an Apache-2.0 project.

After the first (and each subsequent) run of nexusDeps, you'll likely want to copy and save the JSON and report files into a separate directory, to archive them so they won't be overwritten by the next time it is run. Typically, I do this by creating a subfolder in each with the name for the previous run's date, e.g. `2021-08-23/`, and then move the JSON and report files into those archive directories.

Any licenses that aren't found in [`categories.py`](./categories.py) will be included in the category called "Other". After running nexusDeps, it is helpful to review the findings that landed in this category, in order to determine whether (1) to change their clearing result within Nexus IQ, or (2) to add the license combination to one of the other categories; and then to re-run nexusDeps after taking these actions.

Note that one record is stored for each version of each dependency, together with a list of all Nexus IQ reports in which that dependency-version appeared. After a license is cleared for a dependency-version within Nexus IQ, it is typically necessary to then also go into each other Nexus IQ report with that same dependency-version, and tell it to refresh its results / policies so that the new clearing is applied. This is unfortunately necessary to do for each report in Nexus IQ containing the dependency-version, in order to avoid the license combination getting misreported or out of sync between reports.

Nexus IQ will label each detected dependency as the _highest_ level of concern for any of its detected licenses -- even if those licenses are dual licensed, such that the user can choose which one applies. Because of this, before running nexusDeps it may be necessary to go into Nexus IQ and review each report manually, to clear any red / orange / yellow findings that are actually dual-licensed choices between (for instance) a strong copyleft license and a weak copyleft alternative option.

After completing a run of nexusDeps, I will typically review the `RedDependencies.txt` report and directly notify any subproject maintainers of any "red" findings (where they could not be resolved to a lower level of concern, as described in the preceding paragraph).

For more fulsome license reports out to the project community, I will take the `report.xlsx` file and modify as follows:
- reorder the category sheets and License Summary categories to be a more useful listing (e.g., first Project Licenses; then the remainder in decreasing order of concern)
- annotate / modify the spreadsheet with any applicable comments, in particular for any findings that might require additional explanation
- deliver the `report.xlsx` file to the project maintainers and/or legal subcommittee for review, highlighting any key areas of concern.

## License

nexusDeps is licensed under the [Apache License, version 2.0 (Apache-2.0)](./LICENSE).