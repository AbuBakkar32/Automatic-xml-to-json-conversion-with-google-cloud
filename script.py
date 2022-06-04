try:
    import shutil
    import datetime
    import json
    import os
    import time
    from pathlib import Path
    from xml.dom import minidom
    from xml.parsers import expat
    from google.cloud import storage
    import google.cloud.storage
    import xmltodict
    from termcolor import colored
except Exception as e:
    print("Error : {} ".format(e))


# source file Name should like this below
# gs://search-ai-lab-bdr-landing-zone/2022-03-15/12000008-FA48RMU5PPOPPY5-SPEC.xml
# https://cloud.google.com/appengine/docs/standard/python/googlecloudstorageclient/read-write-to-cloud-storage

def google_bucket_conn():
    # Google Cloud Storage Credentials for accessing the bucket
    PATH = os.path.join(os.getcwd(), 'asl-project-demo-013a807f0641.json')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = PATH
    storage_client = storage.Client(PATH)
    return storage_client


class XmlToJsonConverter:
    def __init__(self, xmlFilePath: any = None):
        self.xmlFilePath = xmlFilePath  # path of xml file
        self.cleanJsonPath = 'c:/cleanjson/'  # path of json where clean json file will be created
        self.storage_client = google_bucket_conn()  # Google Cloud Storage Credentials for accessing the bucket
        self.source_bucket_name = 'search-ai-data-landings'  # bucket name where xml file will be uploaded
        self.destination_bucket_name = 'search-ai-data-landing-clean-file'  # bucket name where clean json file will be uploaded
        self.bucket = self.storage_client.get_bucket(self.source_bucket_name)

        # current date format
        self.dt = datetime.datetime.now()
        self.today = self.dt.strftime("%Y-%m-%d")
        self.ctf = self.xmlFilePath + self.today
        self.file_path = Path(self.ctf)

        # previous date format
        self.pre_date = datetime.datetime.today() - datetime.timedelta(days=1)
        self.pre_date = self.pre_date.strftime("%Y-%m-%d")
        self.ptf = self.xmlFilePath + self.pre_date

        if not os.path.exists(self.cleanJsonPath):
            os.mkdir(self.cleanJsonPath)
            print(colored("Directory " + self.cleanJsonPath + " Created", 'green'))
        else:
            pass

        if not os.path.exists(self.xmlFilePath):
            os.mkdir(self.xmlFilePath)
            print(colored("Directory " + self.xmlFilePath + " Created", 'green'))
        else:
            pass

        self._create_folder()
        # call convert_xml_file_to_json function for processing xml file to json file
        self.convert_xml_file_to_json()

    def upload_destination_bucket(self, blob_name, file_path, bucket_name):
        bucket = self.storage_client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(file_path)

    def _create_folder(self):
        if not os.path.exists(self.ctf):
            os.mkdir(self.ctf)
            print(colored("Directory " + self.ctf + " Created", 'green'))
            if 'xml_file.txt' in os.listdir(self.file_path):
                pass
            else:
                with open(self.file_path.joinpath('xml_file.txt'), 'w') as f:
                    f.write("")
        else:
            if 'xml_file.txt' in os.listdir(self.file_path):
                pass
            else:
                with open(self.file_path.joinpath('xml_file.txt'), 'w') as f:
                    f.write("")
            print(colored("Directory " + self.ctf + " Already Exists", 'red'))

    def convert_xml_file_to_json(self):
        filename = [filename.name for filename in list(self.bucket.list_blobs(prefix=self.pre_date))]
        if len(filename) > 1:
            for file in filename[1:]:
                file_path = file
                file = file.split('/')[1]
                if file.endswith('.xml'):
                    blob = self.bucket.blob(blob_name=file_path).download_as_string()
                    with open(self.ptf + '/' + file, 'wb') as f:
                        f.write(blob)
                    with open(self.ptf + '/' + "xml_file.txt", 'r') as f:
                        if file not in f.read():
                            try:
                                with open(self.ptf + '/' + file, 'r') as f:  # read XML file one by one
                                    xml = f.read()
                                    xml = minidom.parseString(xml)
                                    xml = xml.toprettyxml()
                                    xml = xmltodict.parse(xml, attr_prefix='', encoding='utf-8', expat=expat)
                                    baseFileName = file.split('.xml')[0]
                                    data = json.dumps(xml, indent=4)
                                    json_file = baseFileName + '.json'
                                    self.clean_json(json_file, data)
                            except Exception as e:
                                print(f"{file} File Not Converted XML to JSON")
                        else:
                            print(f"{file} File already exists")
                else:
                    print(f"{file} File Not ends with .xml")
        else:
            print(f"No XML file found")

    def new_spec_xml_format_clean_to_json(self, data, file_name, file):
        applicationNumber = \
            int(data['us-patent-application']['us-bibliographic-data-application'][
                    'application-reference'][
                    'document-id'][
                    'doc-number'])
        date = \
            data['us-patent-application']['us-bibliographic-data-application'][
                'application-reference'][
                'document-id'][
                'date']
        documentType = 'SPEC'
        sections = []
        for i in range(len(data['us-patent-application']['description']['p'])):
            try:
                if 'boundary-data' in data['us-patent-application']['description']['p'][i]:
                    if type(data['us-patent-application']['description']['p'][i]['boundary-data']) == dict:
                        try:
                            text = data['us-patent-application']['description']['p'][i]['text'].strip()
                            text = " ".join(text.split())
                            section = {
                                "text": text,
                                "type": data['us-patent-application']['description']['p'][i]['boundary-data'][
                                    'type']
                            }
                            sections.append(section)
                        except:
                            section = {
                                "text": " ",
                                "type": data['us-patent-application']['description']['p'][i]['boundary-data'][
                                    'type']
                            }
                            sections.append(section)
                    elif type(data['us-patent-application']['description']['p'][i]['boundary-data']) == list:
                        try:
                            text = data['us-patent-application']['description']['p'][i]['text'].strip()
                            text = " ".join(text.split())
                            section = {
                                "text": text,
                                "type": data['us-patent-application']['description']['p'][i]['boundary-data'][0][
                                    'type']
                            }
                            sections.append(section)
                        except:
                            section = {
                                "text": " ",
                                "type": data['us-patent-application']['description']['p'][i]['boundary-data'][0][
                                    'type']
                            }
                            sections.append(section)
            except Exception as e:
                pass

        getjson = {
            'applicationNumber': applicationNumber,
            'date': date,
            'documentType': documentType,
            'sections': sections
        }

        with open(self.cleanJsonPath + "/" + file, 'w') as f:
            json.dump(getjson, f, indent=4)

        # upload clean json file into the GCP bucket
        try:
            self.upload_destination_bucket(file, self.cleanJsonPath + "/" + file, self.destination_bucket_name)
            print(f"{file} is successfully uploaded to bucket")
        except Exception as e:
            print(f"{file} is not uploaded to bucket")

        with open(self.ptf + '/' + "xml_file.txt", 'a') as f:
            f.write(file_name + ".xml\n")

    def old_spec_xml_format_clean_to_json(self, data, file_name, file):
        applicationNumber = \
            int(data['SpecificationDocument']['DocumentHeaderDetails']['ApplicationHeaderDetails'][
                    'ApplicationNumber'])
        date = \
            data['SpecificationDocument']['MailRoomDate']
        documentType = 'SPEC'
        sections = []
        try:
            for i in range(len(data['SpecificationDocument']['Specification']['P'])):
                try:
                    text = data['SpecificationDocument']['Specification']['P'][i]['text']
                    text = ' '.join(text.split())
                    section = {
                        "text": text,
                        "type": data['SpecificationDocument']['Specification']['P'][i]['id']
                    }
                    sections.append(section)
                except:
                    section = {
                        "text": " ",
                        "type": data['SpecificationDocument']['Specification']['P'][i]['id']
                    }
                    sections.append(section)

        except Exception as e:
            pass
        getjson = {
            'applicationNumber': applicationNumber,
            'date': date,
            'documentType': documentType,
            'sections': sections
        }

        with open(self.cleanJsonPath + "/" + file, 'w') as f:
            json.dump(getjson, f, indent=4)

        # upload clean json file into the GCP bucket
        try:
            self.upload_destination_bucket(file, self.cleanJsonPath + "/" + file, self.destination_bucket_name)
            print(f"{file} is successfully uploaded to bucket")
        except Exception as e:
            print(f"{file} is not uploaded to bucket")

        with open(self.ptf + '/' + "xml_file.txt", 'a') as f:
            f.write(file_name + ".xml\n")

    def clean_spec_file(self, file, data, file_name):
        if 'us-patent-application' in data:
            # this method will be cleaned new SPEC type of xml file into json file
            self.new_spec_xml_format_clean_to_json(data, file_name,
                                                   file)
        elif 'SpecificationDocument' in data:
            # this method will be cleaned old SPEC type of xml file into json file
            self.old_spec_xml_format_clean_to_json(data, file_name,
                                                   file)
        else:
            print(colored(f"{file} is not a valid file", 'red'))

    def clean_new_abst_file_to_json(self, file, data, file_name):
        applicationNumber = \
            int(data['us-patent-application']['us-bibliographic-data-application'][
                    'application-reference'][
                    'document-id'][
                    'doc-number'])
        date = \
            data['us-patent-application']['us-bibliographic-data-application'][
                'application-reference'][
                'document-id'][
                'date']
        documentType = 'ABST'
        sections = []
        try:
            if type(data['us-patent-application']['abstract']['p']) == list:
                for i in range(len(data['us-patent-application']['abstract']['p'])):
                    try:
                        text = data['us-patent-application']['abstract']['p'][i]['text']
                        text = " ".join(text.split())
                        sections.append(text)
                    except:
                        sections.append(" ")
            elif type(data['us-patent-application']['abstract']['p']) != list:
                try:
                    text = data['us-patent-application']['abstract']['p']['text']
                    text = " ".join(text.split())
                    sections.append(text)
                except:
                    sections.append(" ")
        except Exception as e:
            pass

        getjson = {
            'applicationNumber': applicationNumber,
            'date': date,
            'documentType': documentType,
            'sections': sections
        }

        with open(self.cleanJsonPath + "/" + file, 'w') as f:
            json.dump(getjson, f, indent=4)

        # upload clean json file into the GCP bucket
        try:
            self.upload_destination_bucket(file, self.cleanJsonPath + "/" + file, self.destination_bucket_name)
            print(f"{file} is successfully uploaded to bucket")
        except Exception as e:
            print(f"{file} is not uploaded to bucket")

        with open(self.ptf + '/' + "xml_file.txt", 'a') as f:
            f.write(file_name + ".xml\n")

    def clean_abst_file(self, file, data, file_name):
        if 'us-patent-application' in data:
            # this method will be cleaned new ABST type of xml file into json file
            self.clean_new_abst_file_to_json(file, data, file_name)
        else:
            print(colored(f"{file} is not a valid file", 'red'))

    def new_clm_xml_format_clean_to_json(self, data, file_name, file):
        applicationNumber = \
            int(data['us-patent-application']['us-bibliographic-data-application'][
                    'application-reference'][
                    'document-id'][
                    'doc-number'])
        date = \
            data['us-patent-application']['us-bibliographic-data-application'][
                'application-reference'][
                'document-id'][
                'date']
        documentType = 'CLM'
        # for handle the unknown id to claim id
        claim_id_format = "CLM-00000"
        sections = []
        try:
            for i in range(len(data['us-patent-application']['claims']['claim'])):
                if data['us-patent-application']['claims']['claim'][i]['id'].split('-')[0] != 'UNKNOWN':
                    if type(data['us-patent-application']['claims']['claim'][i]['claim-text']) != list:
                        try:
                            text = data['us-patent-application']['claims']['claim'][i]['claim-text']['text']
                            text = " ".join(text.split())
                            section = {
                                "id": data['us-patent-application']['claims']['claim'][i]['id'],
                                "text": [text]
                            }
                            sections.append(section)
                        except TypeError:
                            text = data['us-patent-application']['claims']['claim'][i]['claim-text']
                            text = " ".join(text.split())
                            section = {
                                "id": data['us-patent-application']['claims']['claim'][i]['id'],
                                "text": [text]
                            }
                            sections.append(section)
                        except:
                            section = {
                                "id": data['us-patent-application']['claims']['claim'][i]['id'],
                                "text": []
                            }
                            sections.append(section)
                    elif type(data['us-patent-application']['claims']['claim'][i]['claim-text']) == list:
                        try:
                            text = data['us-patent-application']['claims']['claim'][i]['claim-text'][0]['text']
                            text = " ".join(text.split())
                            section = {
                                "id": data['us-patent-application']['claims']['claim'][i]['id'],
                                "text": [text]
                            }
                            sections.append(section)
                        except TypeError:
                            try:
                                text = data['us-patent-application']['claims']['claim'][i]['claim-text'][-1]['text']
                                text = " ".join(text.split())
                                section = {
                                    "id": data['us-patent-application']['claims']['claim'][i]['id'],
                                    "text": [text]
                                }
                                sections.append(section)
                            except TypeError:
                                text = data['us-patent-application']['claims']['claim'][i]['claim-text']
                                section = {
                                    "id": data['us-patent-application']['claims']['claim'][i]['id'],
                                    "text": [text]
                                }
                                sections.append(section)
                        except:
                            section = {
                                "id": data['us-patent-application']['claims']['claim'][i]['id'],
                                "text": []
                            }
                            sections.append(section)

                # if claim id start with UNKNOWN, then it will be modified to Claim id like CLM-0000001
                else:
                    if type(data['us-patent-application']['claims']['claim'][i]['claim-text']) != list:
                        try:
                            text = data['us-patent-application']['claims']['claim'][i]['claim-text']['text']
                            text = " ".join(text.split())
                            section = {
                                "id": claim_id_format + data['us-patent-application']['claims']['claim'][i]['id'][-2:],
                                "text": [text]
                            }
                            sections.append(section)
                        except TypeError:
                            text = data['us-patent-application']['claims']['claim'][i]['claim-text']
                            text = " ".join(text.split())
                            section = {
                                "id": claim_id_format + data['us-patent-application']['claims']['claim'][i]['id'][-2:],
                                "text": [text]
                            }
                            sections.append(section)
                        except:
                            section = {
                                "id": claim_id_format + data['us-patent-application']['claims']['claim'][i]['id'][-2:],
                                "text": []
                            }
                            sections.append(section)
                    elif type(data['us-patent-application']['claims']['claim'][i]['claim-text']) == list:
                        try:
                            text = data['us-patent-application']['claims']['claim'][i]['claim-text'][0]['text']
                            text = " ".join(text.split())
                            section = {
                                "id": claim_id_format + data['us-patent-application']['claims']['claim'][i]['id'][-2:],
                                "text": [text]
                            }
                            sections.append(section)
                        except TypeError:
                            try:
                                text = data['us-patent-application']['claims']['claim'][i]['claim-text'][-1]['text']
                                text = " ".join(text.split())
                                section = {
                                    "id": claim_id_format + data['us-patent-application']['claims']['claim'][i]['id'][
                                                            -2:],
                                    "text": [text]
                                }
                                sections.append(section)
                            except TypeError:
                                text = data['us-patent-application']['claims']['claim'][i]['claim-text'][0]
                                section = {
                                    "id": claim_id_format + data['us-patent-application']['claims']['claim'][i]['id'][
                                                            -2:],
                                    "text": [text]
                                }
                                sections.append(section)
                        except:
                            section = {
                                "id": claim_id_format + data['us-patent-application']['claims']['claim'][i]['id'][-2:],
                                "text": []
                            }
                            sections.append(section)
        except Exception as e:
            pass
        getjson = {
            'applicationNumber': applicationNumber,
            'date': date,
            'documentType': documentType,
            'sections': sections
        }

        with open(self.cleanJsonPath + "/" + file, 'w') as f:
            json.dump(getjson, f, indent=4)

        # upload clean json file into the GCP bucket
        try:
            self.upload_destination_bucket(file, self.cleanJsonPath + "/" + file, self.destination_bucket_name)
            print(f"{file} is successfully uploaded to bucket")
        except Exception as e:
            print(f"{file} is not uploaded to bucket")

        with open(self.ptf + '/' + "xml_file.txt", 'a') as f:
            f.write(file_name + ".xml\n")

    def old_clm_xml_format_clean_to_json(self, data, file_name, file):
        applicationNumber = \
            int(data['ClaimsDocument']['DocumentHeaderDetails']['ApplicationHeaderDetails'][
                    'ApplicationNumber'])
        date = data['ClaimsDocument']['MailRoomDate']
        documentType = 'CLM'

        # for handle the unknown id to claim id
        claim_id_format = "CLM-00000"
        sections = []
        try:
            for i in range(len(data['ClaimsDocument']['ClaimSet']['ClaimList']['Claim'])):
                if 'ClaimText' in data['ClaimsDocument']['ClaimSet']['ClaimList']['Claim'][i]:
                    if data['ClaimsDocument']['ClaimSet']['ClaimList']['Claim'][i]['id'].split('-')[
                        0] != 'UNKNOWN':
                        if type(data['ClaimsDocument']['ClaimSet']['ClaimList']['Claim'][i][
                                    'ClaimText']) == list:
                            try:
                                text = \
                                    data['ClaimsDocument']['ClaimSet']['ClaimList']['Claim'][i]['ClaimText'][
                                        -1][
                                        'text']
                                text = " ".join(text.split())
                                section = {
                                    "id": data['ClaimsDocument']['ClaimSet']['ClaimList']['Claim'][i]['id'],
                                    "text": [text]
                                }
                                sections.append(section)
                            except:
                                section = {
                                    "id": data['ClaimsDocument']['ClaimSet']['ClaimList']['Claim'][i]['id'],
                                    "text": []
                                }
                                sections.append(section)
                        elif type(data['ClaimsDocument']['ClaimSet']['ClaimList']['Claim'][i][
                                      'ClaimText']) != list:
                            try:
                                text = data['ClaimsDocument']['ClaimSet']['ClaimList']['Claim'][i]['ClaimText'][
                                    'text']
                                text = " ".join(text.split())
                                section = {
                                    "id": data['ClaimsDocument']['ClaimSet']['ClaimList']['Claim'][i]['id'],
                                    "text": [text]
                                }
                                sections.append(section)
                            except:
                                section = {
                                    "id": data['ClaimsDocument']['ClaimSet']['ClaimList']['Claim'][i]['id'],
                                    "text": []
                                }
                                sections.append(section)

                    # if claim id start with UNKNOWN, then it will be modified to Claim id like CLM-0000001
                    else:
                        if type(data['ClaimsDocument']['ClaimSet']['ClaimList']['Claim'][i][
                                    'ClaimText']) == list:
                            try:
                                text = \
                                    data['ClaimsDocument']['ClaimSet']['ClaimList']['Claim'][i]['ClaimText'][
                                        -1][
                                        'text']
                                text = " ".join(text.split())
                                section = {
                                    "id": claim_id_format + data['ClaimsDocument']['ClaimSet']['ClaimList']['Claim'][i][
                                                                'id'][-2:],
                                    "text": [text]
                                }
                                sections.append(section)
                            except KeyError:
                                section = {
                                    "id": claim_id_format + data['ClaimsDocument']['ClaimSet']['ClaimList']['Claim'][i][
                                                                'id'][-2:],
                                    "text": []
                                }
                                sections.append(section)
                            except TypeError:
                                section = {
                                    "id": claim_id_format + data['ClaimsDocument']['ClaimSet']['ClaimList']['Claim'][i][
                                                                'id'][-2:],
                                    "text": []
                                }
                                sections.append(section)
        except Exception as e:
            pass
        getjson = {
            'applicationNumber': applicationNumber,
            'date': date,
            'documentType': documentType,
            'sections': sections
        }
        with open(self.cleanJsonPath + "/" + file, 'w') as f:
            json.dump(getjson, f, indent=4)

        # upload clean json file into the GCP bucket
        try:
            self.upload_destination_bucket(file, self.cleanJsonPath + "/" + file, self.destination_bucket_name)
            print(f"{file} is successfully uploaded to bucket")
        except Exception as e:
            print(f"{file} is not uploaded to bucket")

        with open(self.ptf + '/' + "xml_file.txt", 'a') as f:
            f.write(file_name + ".xml\n")

    def clean_clm_file(self, file, data, file_name):
        if 'ClaimsDocument' in data:
            # this method will be cleaned old CLM type of xml file into json file
            self.old_clm_xml_format_clean_to_json(data, file_name, file)
        elif 'us-patent-application' in data:
            # this method will be cleaned new CLM type of xml file into json file
            self.new_clm_xml_format_clean_to_json(data, file_name, file)
        else:
            print(colored(f"{file} is not a valid type", 'red'))

    def clean_json(self, file, data):
        file_name = file.split('.json')[0]
        data = data.replace("\\t", "")
        data = data.replace("\\n", "")
        data = data.replace("#", "")
        data = data.replace("ns0:", "")
        data = data.replace("ns2:", "")
        data = data.replace("xsi:", "")
        data = json.loads(data)
        if file.endswith('.json'):
            sfile = file.split('-')[-1]
            sfile = sfile.split('.')[0]

            # if file type is SPEC then it will be converting it to SPEC.json
            if sfile == 'SPEC':
                self.clean_spec_file(file, data, file_name)
            # if file type is ABST then it will be converting it to ABST.json
            elif sfile == 'ABST':
                self.clean_abst_file(file, data, file_name)
            # if file type is CLM then it will be converting it to CLM.json
            elif sfile == 'CLM':
                self.clean_clm_file(file, data, file_name)
            else:
                print(f"This {file_name}.xml file Suffix should be CLM, ABST & SPEC format")


def main():
    # this is the main function where we are calling the class to convert json to clean json format
    xml_file = "c:/search-ai-data-landing/"
    XmlToJsonConverter(xml_file)


if __name__ == '__main__':
    main()
