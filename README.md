# PE 89.2 — Criptografía y certificados digitales

Práctica de MF0489 sobre selección de técnicas criptográficas, intercambio de claves Diffie–Hellman, cifrado XOR y análisis de certificados con OpenSSL.

## Contenido

- [Resolución](RESOLUCION.md): respuestas de los tres bloques y resultados.
- `lab-dh-xor/docker-compose.yml`: configuración del entorno.
- `lab-dh-xor/scripts/`: servidor Bob y cliente Alice.
- `certificados/`: certificados públicos proporcionados para la práctica.
- `evidencias/`: configuración, salidas y comprobaciones.

## Ejecución

Requisitos: Docker con Compose y OpenSSL. La ejecución se ha comprobado en Kali Linux.

Desde `lab-dh-xor`, iniciar los contenedores y ejecutar Bob:

```bash
cd lab-dh-xor
sudo docker compose up -d
sudo docker compose ps
sudo docker compose exec bob python bob_servidor.py
```

Introducir `11` como clave privada de Bob. En otra terminal, desde `lab-dh-xor`, ejecutar Alice:

```bash
sudo docker compose exec alice python alice_cliente.py
```

Introducir `7` como clave privada de Alice y `Hola Bob` como mensaje.

| Dato | Resultado |
|---|---|
| Pública de Alice | 71 |
| Pública de Bob | 150 |
| Clave compartida en ambos extremos | 158 |
| Mensaje cifrado, hexadecimal | D6 F1 F2 FF BE DC F1 FC |
| Mensaje recuperado por Bob | Hola Bob |

La red interna `red-cripto` utiliza la subred `172.28.0.0/16`. Bob tiene la IP `172.28.0.10` y Alice `172.28.0.20`. Los contenedores usan `python:3.11-slim` y comparten la carpeta de scripts mediante un volumen.

## Verificación del certificado

Desde la raíz del repositorio:

```bash
cd certificados
openssl x509 -in certificado_servidor_PE89_2.crt -text -noout
openssl x509 -in certificado_servidor_PE89_2.crt -noout -fingerprint -sha256
openssl verify -CAfile CA_laboratorio_PE89_2.crt certificado_servidor_PE89_2.crt
```

Resultado:

```text
certificado_servidor_PE89_2.crt: OK
```

Los certificados proceden del [material del curso](https://github.com/faguilar-ironhack/assets/tree/724f6531058847752f800ef15042241b809815cd/mf0489/certificados).

El intercambio con parámetros pequeños y el XOR de un byte son demostraciones educativas; no son apropiados para proteger datos reales.
