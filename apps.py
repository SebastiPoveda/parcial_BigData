import requests
import datetime
import boto3
import json
import csv
import os
from bs4 import BeautifulSoup


def download_data(url):
    response = requests.get(url)
    return response


def f():
    url = ('https://pisos.mitula.com/searchRE/nivel2-Madrid/'
           'nivel1-Madrid/tipo-Casa/q-Madrid')
    bucket = 'landing-casas-pineda-poveda'

    response = requests.get(url)
    html_url = response.content

    s3 = boto3.resource('s3')
    dt = datetime.date.today()
    file_name = dt.strftime("%Y-%m-%d") + ".html"

    s3.Bucket(bucket).put_object(Key=file_name, Body=html_url)

    return {
        'statusCode': 200,
        'body': 'Contenido guardado - ' + file_name
    }


def g():
    s3 = boto3.client('s3')
    dt = datetime.date.today()
    bucket = 'landing-casas-pineda-poveda'
    bucket_destino = 'casas-final-pineda-poveda'

    source_file_name = dt.strftime("%Y-%m-%d") + ".html"
    csv_file_name = f'{dt}.csv'

    try:
        s3.download_file(bucket, source_file_name, source_file_name)

        html_doc = read_file(source_file_name)

        soup = BeautifulSoup(html_doc, 'html.parser')
        div_tag_script = soup.find('script', type='application/ld+json')
        json_text = div_tag_script.string.strip()
        json_file = json.loads(json_text)

        with open('/tmp/' + csv_file_name, 'w', newline='') as csvfile:
            fields = ["date", "name",
                      "numberOfBedrooms", "numberOfBathroomsTotal",
                      "address.addressRegion", "address.addressLocality",
                      "address.addressCountry.name", "floorSize.value",
                      "floorSize.unitCode"]
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()

            for item in json_file['about']:
                row = {
                    "date":
                        datetime.date.today().strftime("%Y-%m-%d"),
                    "name":
                        item.get('name', ''),
                    "numberOfBedrooms":
                        item.get('numberOfBedrooms', ''),
                    "numberOfBathroomsTotal":
                        item.get('numberOfBathroomsTotal', ''),
                    "address.addressRegion":
                        item.get('address', {}).get('addressRegion', ''),
                    "address.addressLocality":
                        item.get('address', {}).get('addressLocality', ''),
                    "address.addressCountry.name":
                        item.get('address', {}).get('addressCountry',
                                                    {}).get('name', ''),
                    "floorSize.value":
                        item.get('floorSize', {}).get('value', {}),
                    "floorSize.unitCode":
                        item.get('floorSize', {}).get('unitCode', {})
                }
                writer.writerow(row)

        with open('/tmp/' + csv_file_name, 'rb') as csvfile:
            s3.upload_fileobj(csvfile, bucket_destino, f'{dt}.csv')

        os.remove(source_file_name)
        os.remove('/tmp/' + csv_file_name)

    except Exception as e:
        # Handle the exception
        print("Ocurrió un error", e)

    return {
        'statusCode': 200,
        'body': 'Contenido guardado - ' + csv_file_name
    }


def read_file(source_file_name):
    with open(source_file_name, 'r') as f:
        html_doc = f.read()
    return html_doc
