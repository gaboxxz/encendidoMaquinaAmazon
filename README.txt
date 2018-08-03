-  instalar la ultima version de python (v 3.5  o mayor).
-Instalar en c:\py

- copiar el archivo requirementes.txt a la carpeta de PIP y ejecutar el siguiente comando desde el cmd: (C:\py\Scripts) 

- pip install -r requirements.txt
para levantar la maquina. Carpeta donde estan los archivos(C:\Users\quilate\Desktop\SVN\QUILATE\TestComplete).Comando:

PARA PRENDERLA
python botolaunch.py --key=./key.json --config=./config.json --log=./log.txt

C:\py\python.exe botolaunch.py --key=./key.json --config=./config.json --log=./log.txt


PARA APAGARLA:
python botoStop.py --key=./key.json --id=NUMERO DE INSTANCIA GENERADO EN EL LOG.TXT
C:\py\python.exe botoStop.py --key=./key.json --id=NUMERO DE INSTANCIA GENERADO EN EL LOG.TXT
uir ejecutando aunque no se este monitoreando.

