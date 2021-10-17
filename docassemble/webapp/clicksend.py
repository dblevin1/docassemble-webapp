import clicksend_client
from clicksend_client import FaxMessage
from clicksend_client.rest import ApiException
import codecs
import json

def send_fax(fax_number, the_file, config, country=None):
    if (hasattr(the_file, 'extension') and the_file.extension == 'pdf') or (hasattr(the_file, 'mimetype') and the_file.mimetype == 'application/pdf'):
        use_url = True
    else:
        use_url = False
    the_file.url_for(temporary=True, seconds=600)
    configuration = clicksend_client.Configuration()
    configuration.username = config['api username']
    configuration.password = config['api key']
    api_instance = clicksend_client.FAXApi(clicksend_client.ApiClient(configuration))
    fax_message_list = [FaxMessage(source="sdk", to=fax_number, _from=config['number'], country=country or config['country'], from_email=config['from email'])];
    if use_url:
        file_url = the_file.url_for(temporary=True, seconds=600)
    else:
        upload_file = clicksend_client.UploadFile(content=codecs.encode(the_file.slurp(auto_decode=False), 'base64'));
        try:
            api_response = api_instance.uploads_post(upload_file, 'fax')
        except ApiException as e:
            raise Exception("Exception when calling UploadApi->uploads_post: %s\n" % e)
        try:
            response = json.loads(api_response)
        except:
            raise Exception("Exception when calling UploadApi->uploads_post: response not JSON: " + api_response)
        if response.get('http_code', 0) != 200:
            raise Exception("Exception when calling UploadApi->uploads_post: response code not 200: " + api_response)
        if '_url' not in response:
            raise Exception("Exception when calling UploadApi->uploads_post: url not returned " + api_response)
        file_url = response['_url']
    fax_message = clicksend_client.FaxMessageCollection(file_url=file_url, messages=fax_message_list)
    try:
        api_response = api_instance.fax_send_post(fax_message)
    except ApiException as e:
        raise Exception("Exception when calling FAXApi->fax_send_post: %s\n" % e)
    try:
        response = json.loads(api_response)
    except:
        raise Exception("Exception when calling FAXApi->fax_send_post: response not JSON: " + api_response)
    if response.get('http_code', 0) != 200:
        raise Exception("Exception when calling FAXApi->fax_send_post: response code not 200: " + api_response)
    try:
        message_id = response['data']['messages'][0]['message_id']
    except:
        raise Exception("Exception when calling FAXApi->fax_send_post: message_id not in response" + api_response)
    return response['data']['messages'][0]
