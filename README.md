# Detector de Movimiento

Código desarrollado en python para una Raspberry Pi 3 con una PiCamera conectada.
Al ejecutar el programa, la cárama comienza a captar todo lo que tiene delante.
Procesa las imagenes captadas para analizarlas y detectar movimiento mediante el método de sustracción de fondo.
Si detecta movimiento graba un vídeo incluyendo, hasta un máximo de 10 segundos previos al movimiento y la duración completa del movimiento.
Una vez se haya grabado el vídeo del movimiento, lo sube a un servidor FTP.

Caracteristicas:
- Desarrollado completamente en Python 3.
- Libreria utilizada -> OpenCv 4.5.1
- Depende de un servidor FTP externo
