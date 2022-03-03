from cProfile import run
from urllib import response
import boto3, json
import subprocess
import requests
from botocore.exceptions import NoCredentialsError

ACCESS_KEY = 'AKIAWR447HNMAXDEWL7O'
SECRET_KEY = '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'
sqs = boto3.client("sqs")
request_queue_url = 'https://sqs.us-east-1.amazonaws.com/547230687929/Request_Queue'
response_queue_url = 'https://sqs.us-east-1.amazonaws.com/547230687929/Response_Queue'

def send_message(file, output):

    message = {
        "File": file,
        "Output": output}
    response = sqs.send_message(
        QueueUrl=response_queue_url,
        MessageBody=json.dumps(message)
    )
    print(response)

def receive_message():
    response = sqs.receive_message(
        QueueUrl=request_queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10,
    )

    print(f"Number of messages received: {len(response.get('Messages', []))}")

    for message in response.get("Messages", []):
        message_body = message["Body"]
        print(f"Message body: {message_body}")
        print(f"Receipt Handle: {message['ReceiptHandle']}")
        delete_message(message['ReceiptHandle'])

    if len(response.get('Messages', [])) > 0 :
        return True, "test_00.jpg"
    
    else: 
        return False, ""

def delete_message(receipt_handle):
    response = sqs.delete_message(
        QueueUrl=request_queue_url,
        ReceiptHandle=receipt_handle,
    )
    print(response)

def ping_webserver():
    resp = requests.post('dummy.website.com/ping')
    return resp

# def save_to_s3():
#     return

def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)

    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

def upload_result(bucket_name,file_name,txt_data):
    session = boto3.Session(
        aws_access_key_id='AKIAWR447HNMAXDEWL7O',
        aws_secret_access_key='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'
    )
    s3 = session.resource('s3')

    object = s3.Object(bucket_name, file_name)

    result = object.put(Body=txt_data)

    res = result.get('ResponseMetadata')

if __name__ == "__main__":
    run_flag = False
    while(run_flag == False):
        run_flag, image_name = receive_message()
        image_file = "img/" + image_name

        if run_flag:
            bashCommand = "python3 face_recognition.py " + image_file
            process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            output = output.decode("utf-8")
            output = output[:len(output)-1]
            
            send_message(file=image_name[:len(image_name) - 4], output=output)
            uploaded = upload_to_aws(r'C:\Users\Dell\Desktop\cloud computing\face_images_100\test_00.jpg',
                                     'ccinputimages', 'Test_00')
            upload_result1 = upload_result('recognitionresults', 'test_00', 'Paul')
