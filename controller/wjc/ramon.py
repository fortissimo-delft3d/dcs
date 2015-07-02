import io
import os
import requests
import subprocess
import zipfile
from logging.config import dictConfig, logging

logging_config = {
                'version': 1,
                'disable_existing_loggers': False,
                'formatters': {
                    'standard': {'format': '[ILM]-%(asctime)s[%(levelname)s](%(name)s):%(message)s',
                                 'datefmt': '%Y-%m-%d %H:%M:%S'},
                    'logstash': {'format': '[ILM]-[%(levelname)s] %(message)s'}
                },
                'handlers': {
                    'fh': {'class': 'logging.StreamHandler',
                           'formatter': 'standard',
                           'level': 'debug',
                           'stream': 'ext://sys.stdout'},
                    'ls': {'class': 'logstash.TCPLogstashHandler',
                           'formatter': 'logstash',
                           'level': 'info',
                           'host': [elk],
                           'port': 9300,
                           'version': 1}
                },
                'loggers': {
                    '': {'handlers': ['fh', 'ls'],
                         'level': 'DEBUG',
                         'propagate': True}
                }
            }
dictConfig(logging_config)

try:
    # go get our stuff
    logging.info('downloading')
    r = requests.post('http://[wjc]/jobs/[uuid]/state/downloading')
    r = requests.get('http://[store]/[uuid].zip')
    if r.status_code != 200:
        raise Exception('could not download [uuid].zip')
    with open('./[uuid].zip', 'wb') as f:
        f.write(r.content)
    # unzip the file
    r = requests.post('http://[wjc]/jobs/[uuid]/state/extracting')
    with zipfile.ZipFile('[uuid].zip') as zf:
        zf.extractall()
    # start the 'run' script
    r = requests.post('http://[wjc]/jobs/[uuid]/state/running')
    output_filename = 'output.log'
    error_filename = 'output.log'
    # mwahahaha, buffer outputs and write them to loggers during execution (non blocking)
    with io.open(output_filename, 'wb') as output_writer, io.open(output_filename, 'rb', 1) as output_reader, \
            io.open(error_filename, 'wb') as error_writer, io.open(error_filename, 'rb', 1) as error_reader:
        process = subprocess.Popen('./run', shell=True, stdout=output_writer, stderr=error_writer)
        while process.poll() is None:
            output_line = output_reader.read()
            error_line = error_reader.read()
            if output_line is not None and len(output_line) > 0:
                logging.info(output_line)
            if error_line is not None and len(error_line) > 0:
                logging.error(error_line)
        process.wait()
        output_line = output_reader.read()
        if output_line is not None and len(output_line) > 0:
            logging.info(output_line)
        error_line = error_reader.read()
        if error_line is not None and len(error_line) > 0:
            logging.error(error_line)
    # zip the results
    r = requests.post('http://[wjc]/jobs/[uuid]/state/compressing')
    os.remove('./[uuid].zip')
    with zipfile.ZipFile('[uuid].zip', mode='w') as zf:
        for root, dirs, files in os.walk('.'):
            for file in files:
                zf.write(os.path.join(root, file))
    # upload the results
    r = requests.post('http://[wjc]/jobs/[uuid]/state/uploading')
    # remove old file on store
    r = requests.delete('http://[store]/[uuid].zip')
    with open('./[uuid].zip', 'rb') as data:
        headers = {'Content-Type': 'application/octet-stream'}
        r = requests.post('http://[store]/[uuid].zip', data=data, headers=headers)
        if r.status_code != 200:
            raise Exception('could not upload results')
    # finished
    r = requests.post('http://[wjc]/jobs/[uuid]/state/finished')
    logging.info('job [uuid] done')
except Exception:
    logging.exception('Failed to complete work')
    r = requests.post('http://[wjc]/jobs/[uuid]/state/failed')
