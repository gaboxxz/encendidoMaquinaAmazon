"""
    Usage:
        botoLaunch.py -h
        botoLaunch.py -v
        botoLaunch.py --key=<key_file> --config=<config_file> --log=<log_dir> 


    Options:
        -h,--help                     : show this help message
        -v, --version                 : show code version

    Arguments:
        --key=<key file>		: Archivo con claves de acceso para AWS 
        --config=<config File>		: Archivo con configuracion de virtual en formato json
        --log=<log file>		: Archivo de log del proceso
"""
from docopt import docopt
import boto3
import botocore
import json
import os
import sys
import time

import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

def create(configdir, keydir,logdir):
	
	#Ec2 instance
	client = init_session_client('ec2',keydir)
	resource = init_session_resource('ec2', keydir)

	#Configuracion fija , ID del volumen del disco del test complete
	discoTest = 'vol-5d1f9b41'
	if client:
		with open(configdir) as configfile:
			config = json.load(configfile)
			#ValidFrom=config['ValidFrom'],
			#ValidUntil=config['ValidUntil'],
			#Crear la instancia
		 	#SecurityGroupIds ='sg-3a2a2158',
			try:
				req = client.request_spot_instances(
					AvailabilityZoneGroup='sa-east-1',
					DryRun=False,
				    SpotPrice=config['SpotPrice'],
				    InstanceCount=config['TargetCapacity'],
				    LaunchSpecification=config['LaunchSpecifications'][0]
					)
				

				srid = req['SpotInstanceRequests'][0]['SpotInstanceRequestId']
				#print(req)
				request_state = client.describe_spot_instance_requests(
				    DryRun=False,
				    SpotInstanceRequestIds=[srid])
				while(request_state['SpotInstanceRequests'][0]['Status']['Code'] != 'fulfilled'):
					print('Esperando a que se complete la solicitud...')
					time.sleep(5)
					request_state = client.describe_spot_instance_requests(
					    DryRun=False,
					    SpotInstanceRequestIds=[srid])

				#ID de la maquina creada
				iid =  request_state['SpotInstanceRequests'][0]['InstanceId']
				#obtener datos de la instancia creada
				instances = client.describe_instances(DryRun=False, InstanceIds=[iid])
				test_instance_attr = instances['Reservations'][0]['Instances'][0]
				
				test_instance = resource.Instance(iid)
				#esperar a que la instancia este ejecutandose
				test_instance.wait_until_running(DryRun=False)
				
				#obtener IP de la instancia
				public_ip = test_instance_attr['PublicIpAddress']

				#Agregar disco TestComplete
				resp_vol = client.attach_volume(DryRun=False,
					VolumeId=discoTest,
					InstanceId=iid,
					Device="xvdf")

				#Guardar Log
				with open(logdir, "w") as logfile:
					logfile.write('REQUEST_ID: ' + srid + '\n')
					logfile.write('INSTANCE_ID: ' + iid + '\n')
					logfile.write('PUBLIC_IP: ' + public_ip + '\n')
					
					#Mail desde donde se envian los mensajes
					fromaddr = "gabrielbori.quilate@gmail.com"
					msg = MIMEMultipart()
					msg['From'] = "Script Inicio Virtual TestComplete"
					msg['To'] = "Testing"
					msg['Subject'] = "NUEVA MAQUINA VIRTUAL PARA TESTCOMPLETE. FECHA: " + datetime.date.today().strftime("%B %d, %Y")
					body = " Request_ID: " + srid + "\n INSTANCE_ID: " + iid + "\n PUBLIC_IP: " + public_ip
					msg.attach(MIMEText(body, 'plain'))
					server = smtplib.SMTP('smtp.gmail.com', 587)
					server.starttls()
					server.login(fromaddr, "") #Clave de la cuenta de envio de mails
					text = msg.as_string()
					server.sendmail(fromaddr, "", text) #Destinatarios. Se pueden agregar tantos como se quiera copiando esta linea y cambiando el mail
					server.sendmail(fromaddr, "", text)
					server.sendmail(fromaddr, "", text)
					server.quit()
	

			except botocore.exceptions.ClientError as e:
				if e.response['Error']['Code'] == 'DryRunOperation':
					print ("Dry Run OK!")
				else:
					print ("Unexpected error: %s" % e)



def main(docopt_args):
	#leer variables ingresadas
	configdir			= docopt_args['--config']
	keydir 				= docopt_args['--key']
	logdir         		= docopt_args['--log']

	#crear maquina virtual segun configuracion
	create(configdir, keydir ,logdir)

if __name__ == "__main__":
  args = docopt(__doc__, version='Version 1.2')
  main(args)