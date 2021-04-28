# Importaciones de  librerías
import io
import ftplib
from picamera import PiCamera
import picamera.array
import time
import cv2
import datetime as dt


class Detector(object):
    def __init__(self):
        """ Constructor de la clase Detector"""
        self.fondo = None

    # Devuelve True cuando detecta movimiento
    def detectaMovimiento(self):

        self.resultado = False 

        for frame in camara.capture_continuous(camara.rawCapture, format="bgr", use_video_port=True):
            
            imagen = frame.array # Obtenemos el array en formato NumPy
            ### SUBSTRACCIÓN DE FONDO - técnica para detectar movimiento ###
            
            ## 1- Conversión a escala de grises y eliminación de ruido ##
            gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY) # Convertimos a escala de grises

            gris = cv2.GaussianBlur(gris, (21, 21), 0) # Aplicamos suavizado para eliminar ruido
            
            # Establecemos fondo como el primer frame obtenido
            if self.fondo is None:
                self.fondo = gris

            ## 2- Operación de substracción entre el primer y el segundo plano ##
            resta = cv2.absdiff(self.fondo, gris) # Calculo de la diferencia entre el fondo y el frame actual
            
            
            ## 3- Aplicar un umbral a la imagen resultado de la resta ##
            umbral = cv2.threshold(resta, 25, 255, cv2.THRESH_BINARY)[1] # Aplicamos un umbral
            umbral = cv2.dilate(umbral, None, iterations=2) # Dilatamos el umbral para tapar agujeros
            
            
            ## 4- Detección de contornos o Blob ##
            contornosimg = umbral.copy() # Copiamos el umbral para detectar los contornos

            # Buscamos contorno en la imagen
            contornos, hierarchy = cv2.findContours(contornosimg,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) 

            # Recorremos todos los contornos encontrados
            for c in contornos:

                # Eliminamos los contornos más pequeños
                if cv2.contourArea(c) < 500:
                    continue

                resultado = True

            # Reseteamos el archivo raw para la siguiente captura
            camara.rawCapture.truncate(0)
            return resultado

class HerramientaFTP(object):
    def __init__(self, ftp_servidor, ftp_usuario, ftp_clave, ftp_raiz, fichero_raiz):
        """Constructor de clase HerramientaFTP"""
        self.ftp_servidor = ftp_servidor # Dirección del servidor
        self.ftp_usuario = ftp_usuario # Usuario del Servidor
        self.ftp_clave = ftp_clave # Contaseña
        self.ftp_raiz = ftp_raiz # Directorío ftp 
        self.fichero_raiz = fichero_raiz # Directorio local
        self.servidor = None 
        self. fichero = None
    
    # Establece conexión con el servidor FTP
    def conectaServidor(self):
        try:
            # Instanciamos el servidor enviando cómo parámetro la dirección, el usuario y la contraseña
            self.servidor = ftplib.FTP(self.ftp_servidor, self.ftp_usuario, self.ftp_clave)
            print('Conexión con servidor FTP establecida.')
        except:
            print('No se ha podido conectar al servidor ' + self.ftp_servidor + '.')

    # Desconecta del servidor FTP y cierra el fichero
    def desconectaServidor(self):
        if  self.fichero is not None:
            self.fichero.close()

        if self.servidor is not None:
            self.servidor.quit()
            print('Desconexión del servidor FTP.')
 
    # Sube el archivo indicado al servidor FTP
    def subeArchivo(self, fichero_destino):
        self.conectaServidor()
        try:
            fichero_origen = self.fichero_raiz + fichero_destino
            self.fichero = open(fichero_origen, 'rb') # Abrimos el archivo que queremos subir
            self.servidor.cwd(self.ftp_raiz) # Establecemos la ruta donde se subirá el archivo
            # Iniciamos la transferencia del archivo desde el cliente al servidor
            self.servidor.storbinary('STOR ' + fichero_destino, self.fichero)
            print('Archivo subido al servidor satisfactoriamente.')
            self.desconectaServidor()

        except:
            print('No se ha podido encontrar el fichero ' + fichero_origen + '.')

class Camara(PiCamera):
        def __init__(self, resolution = (640, 480) , framerate = 32):
                """Constructor de clase camara"""
        
                # Invocamos el constructor de PiCamera
                PiCamera.__init__(self)

                self.resolution = resolution
                self.framerate = framerate
                self.rawCapture = picamera.array.PiRGBArray(self, size=(640, 480))
                self.grabando = False # Bandera para controlar si se está grabando un movimiento o no
                
                time.sleep(0.5) # Tiempo de espera para que la cámara arranque

        def isGrabando(self):
                """ Devuelve el valor de grabando"""
                return self.grabando

        def setGrabando(self, grabando):
                """ Asigna un estado a la bandera grabando"""
                self.grabando = grabando

        def escribeVideo(self, stream, nombreVideo):
                """ Guarda el vídeo obtenido en el disco"""

                # Encuentra el primer frame del stream
                for frame in stream.frames:
                    if frame.frame_type == picamera.PiVideoFrameType.sps_header:
                        stream.seek(frame.position) # Localiza el stream en dicho frame
                        break
                # Escribe en el disco el stream
                with io.open(nombreVideo, 'wb') as output:
                        output.write(stream.read())
                        print('Guardo el Stream en un archivo.')
                        stream.clear()
                        print('Reseteo el stream.')
            

# Datos FTP y Local
ftp_servidor = '192.168.1.134' 
ftp_usuario = 'PiCamera' 
ftp_clave = 'SubeteArchivo' 
ftp_raiz = '/home/PiCamera/ftp' 
fichero_raiz = '/home/pi/PiCamera/' 

camara = Camara() # Instancio la Cámara     
detector = Detector() # Instancio el Detector de movimiento
ftp = HerramientaFTP(ftp_servidor, ftp_usuario,ftp_clave, ftp_raiz, fichero_raiz) # Instancio el la Herramienta FTP

stream = picamera.PiCameraCircularIO(camara, size=None, seconds=10) # Iniciamos el stream
camara.start_recording(stream, format='h264') # Iniciamos la grabación, enviandole el stream
inicio = time.time() # Tomamos referencia de la hora de inicio

nombreVideo = None # Nombre con el que se guardará el vídeo

try:
    while True:
        print('Movimiento -> '+str(detector.detectaMovimiento()) + '.')
        # Compruebo si se est detectando algún movimiento
        if detector.detectaMovimiento():
            # Si no hay una grabación en curso, le doy inicio a una
            if not camara.isGrabando():
                print('Empiezo a grabar.')
                camara.setGrabando(True)
                nombreVideo = dt.datetime.now().strftime('%Y%m%d_%H%M%S.h264')

            # Si hay una grabación en curso, añado un segundo a la grabación
            else:
                print('Espero un segundo.')
                camara.wait_recording(1)

        # Si no se detecta ningún movimiento
        else:
            # Si hay una grabación en curso, paro la grabación, la guardo y la subo.
            if camara.isGrabando():
                print('Paro la grabación.')
                camara.setGrabando(False)
                camara.escribeVideo(stream, fichero_raiz + nombreVideo)
                ftp.subeArchivo(nombreVideo)
                inicio = time.time() # Reinicio la referencia del contador
                continue


            contador = time.time()
            if (contador - inicio) > 10:
                inicio = time.time() # Reinicio la referencia del contador
                stream.clear()
                print('Reseteo el stream.')
finally:
    camara.stop_recording()
    camara.close()
    