# INZ Update Checker

## Introduction
Get information from INZ website and compare them to previous day information to see if anything changed.

The script download the content of a few INZ pages in a local directory and compare them with the pages downloaded the previous day.

Pages checked:

- https://www.immigration.govt.nz/about-us/covid-19/coronavirus-update-inz-response
- https://www.immigration.govt.nz/about-us/covid-19/border-closures-and-exceptions
- https://www.immigration.govt.nz/about-us/covid-19/border-closures-and-exceptions/critical-purpose-reasons-you-can-travel-to-new-zealand

## Usage

run the script with the following command:

```bash
python inz-update-watcher.py --inz-info-dir ./path_to_directory
```

`--inz-info-dir` is where the content of the various pages will be downloaded. One subfolder will be created for each day. The script doesn't rotate those files, you will need to manually delete old ones if needed

If a change is detected, a diff file will be written to the directory used to download the page to easily see what changed. It's an html file and can be open with a browser.
