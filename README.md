# XML to JSON Converter
This GitHub repository provides a Python script that converts XML files to JSON format and uploads the cleaned JSON files to Google Cloud Storage buckets. The script uses various Python libraries such as shutil, datetime, json, os, time, pathlib, xml.dom, xml.parsers, google.cloud.storage, xmltodict, and termcolor.

## Features
Converts XML files to JSON format, cleaning unnecessary characters.
Handles different types of XML formats, including SPEC, ABST, and CLM.
Uploads the cleaned JSON files to Google Cloud Storage buckets.
Provides error handling and logging for a seamless conversion process.
## Installation and Usage
1. Clone the repository to your local machine:
   ```
   git clone https://github.com/abubakkar32/xml-to-json-converter.git
   ```
2. Navigate to the repository directory:
   ```
    cd xml-to-json-converter
   ```
3. Install the required Python packages:
   ```
    pip install -r requirements.txt
   ```
4. Run the script:
   ```
    python xml_to_json_converter.py
   ```

# File Structure
The repository includes the following files:

* `xml_to_json_converter.py`: The main Python script that converts XML files to JSON format and uploads them to Google Cloud Storage buckets.
* `requirements.txt`: A text file containing the required Python packages for the script to run.
* `README.md`: The README file containing information about the repository and its usage.

# Contributing
If you find any issues or have suggestions for improvements, feel free to create a pull request or open an issue. Contributions are welcome!

# License
This repository is licensed under the MIT License. You can find the license details in the LICENSE file.

# Acknowledgments
The script uses the google.cloud.storage library to access Google Cloud Storage. Special thanks to the developers and maintainers of this library for their contributions.

# Disclaimer
This script is provided as-is, and the author makes no warranties regarding its performance or results. Use it at your own risk. The author is not responsible for any data loss or damage caused by the use of this script. Always review and test the script before using it in a production environment.


