import boto3
import os
import setting
from time import sleep
import requests
import re

# AWS requests config
my_bucket_name = 'mytestset'
# To use Transcribe service, you must use aws s3 to store audio files!
# s3 client
s3_client = boto3.resource(
    's3',
    aws_access_key_id=setting.AWSAccessKeyId,
    aws_secret_access_key=setting.AWSSecretKey)
testset = s3_client.Bucket(my_bucket_name)
# ASR client
asr_client = boto3.client('transcribe', region_name='us-east-2',
                          aws_access_key_id=setting.AWSAccessKeyId,
                          aws_secret_access_key=setting.AWSSecretKey)
# loop through the files in s3
for file in testset.objects.all():
    file_name = file.key
    file_uri = 's3://' + my_bucket_name + '/' + file_name
    print(file_name)
    # Start a transciption job
    if(re.search(r"-w\.wav$", file_name) != None):  # I just wanna use some files
        try:
            asr_client.start_transcription_job(
                TranscriptionJobName=file_name,
                Media={'MediaFileUri': file_uri},
                MediaFormat='wav',
                LanguageCode='fa-IR')
            # See if the job is done
            while True:
                response = asr_client.get_transcription_job(
                    TranscriptionJobName=file_name)
                status = response['TranscriptionJob']['TranscriptionJobStatus']
                if status == 'COMPLETED':
                    sharable_url = response['TranscriptionJob']['Transcript']['TranscriptFileUri']
                    output = requests.get(sharable_url)
                    open('output/'+file_name+'.txt',
                         'wb').write(output.content)
                    break
                elif status == 'FAILED':
                    print('failed and skiped')
                    break
                else:
                    print(file_name)
                    print(status)
                sleep(15)
        except Exception as e:
            print(e)
            pass
