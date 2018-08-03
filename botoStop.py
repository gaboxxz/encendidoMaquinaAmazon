"""
    Usage:
        botoStop.py -h
        botoStop.py -v
        botoStop.py --key=<key_file> --id=<instance_id> 


    Options:
        -h,--help                     : show this help message
        -v, --version                 : show code version

    Arguments:
        --key=<key file>		: Archivo con claves de acceso para AWS 
        --id=<instance_id>		: ID de la isntancia en amazon a parar(buscar en el log de botoLaunch)
"""
from docopt import docopt
import boto3
import botocore
import json
import os
import sys
import time

def init_session_client(resource,configdir):
	#access key y secret key hay que cargarlas desde un archivo
	#NO deben estar hardcodeadas!!
	with open(configdir, 'r') as f:
		y = json.load(f)

		client = boto3.client(resource,
			aws_access_key_id = y['Access_Key_ID'],
			aws_secret_access_key = y['Secret_Access_Key'],
			region_name = y['Region_Name'])
	return client


def init_session_resource(resource,configdir):
	#access key y secret key hay que cargarlas desde un archivo
	#NO deben estar hardcodeadas!!
	with open(configdir, 'r') as f:
		y = json.load(f)

		resource = boto3.resource(resource,
			aws_access_key_id = y['Access_Key_ID'],
			aws_secret_access_key = y['Secret_Access_Key'],
			region_name = y['Region_Name'])
	return resource


def terminate(iid, keydir):
	resource = init_session_resource('ec2', keydir)
	
	discoTest = 'vol-5d1f9b41'
	if resource:
		test_instance = resource.Instance(iid)

		#Desmontar disco TestComplete
		try:
			test_instance.detach_volume(DryRun=False,
				VolumeId=discoTest,
				Device="xvdf",
				Force=False)
		except botocore.exceptions.ClientError as e:
			if e.response['Error']['Code'] == 'DryRunOperation':
				print ("Dry Run OK!")
			else:
				print ("Unexpected error: %s" % e)

		#Parar Ejecucion Maquina virtual
		try:
			test_instance.terminate(DryRun=False)
		except botocore.exceptions.ClientError as e:
			if e.response['Error']['Code'] == 'DryRunOperation':
				print ("Dry Run OK!")
			else:
				print ("Unexpected error: %s" % e)




def main(docopt_args):
	#leer variables ingresadas
	iid					= docopt_args['--id']
	keydir 				= docopt_args['--key']


	#crear maquina virtual segun configuracion
	terminate(iid, keydir)

if __name__ == "__main__":
  args = docopt(__doc__, version='Version 1.2')
  main(args)