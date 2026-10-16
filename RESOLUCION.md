# PE 89.2 — Resolución

MF0489 — Técnicas criptográficas, intercambio de claves y certificados digitales.

Práctica realizada el 16 de octubre de 2026. Los valores pequeños de Diffie–Hellman y el cifrado XOR se utilizan únicamente con fines didácticos.

## Bloque 1 — Selección de técnicas criptográficas

### Ejercicio 1

| Necesidad | Técnica seleccionada | Justificación |
|---|---|---|
| Proteger un gran volumen de información con una clave secreta ya compartida | Cifrado simétrico | Es eficiente para grandes volúmenes y utiliza la clave que ya comparten emisor y receptor. En un sistema real conviene un modo autenticado, como AES-GCM. |
| Proteger un secreto destinado a un receptor sin clave compartida previa | Cifrado asimétrico | Permite cifrar con la clave pública auténtica del receptor; solo su clave privada debe permitir recuperar el secreto. Se suele combinar con cifrado simétrico en esquemas híbridos. |
| Detectar modificaciones de un archivo | Función hash | Se calcula una huella y se compara con una referencia fiable. Un cambio altera normalmente la huella. Para resistir a un atacante que pueda sustituir archivo y huella, hace falta autenticar la referencia. |
| Comprobar identidad de un servidor web | Certificado digital | Vincula la identidad con una clave pública mediante una firma de una CA. Se validan confianza, vigencia y nombre, y TLS exige demostrar posesión de la privada. |
| Acordar una clave compartida sobre una red insegura | Intercambio Diffie–Hellman | Permite calcular un secreto común intercambiando valores públicos sin enviar directamente el secreto. Requiere autenticación para resistir intermediarios. |
| Demostrar firma de una entidad y detectar modificaciones posteriores | Firma digital | La privada firma y la pública verifica integridad y uso de la clave de firma. La atribución a la entidad requiere una vinculación fiable de identidad y clave. |

### Ejercicio 2

**1. Configuración seleccionada: B.** Combina certificado RSA-2048, SHA-256 y TLS 1.3. Entre las tres propuestas ofrece algoritmos y protocolo adecuados para una comunicación actual, siempre que se implementen correctamente y se valide el certificado. Un certificado RSA en TLS 1.3 autentica; no implica usar transporte de claves RSA.

**2. Configuraciones rechazadas.** A usa RSA-1024, con margen insuficiente para una configuración moderna; SHA-1, inadecuado para firmas por sus colisiones conocidas; y TLS 1.0, deprecado. C usa MD5, con colisiones conocidas; HTTP sin TLS, que deja la comunicación expuesta a escucha y alteración; y envía la clave secreta directamente dentro del mensaje, por lo que un observador podría obtenerla.

**3. Cifrado frente a hash.** El cifrado busca confidencialidad y permite recuperar el original mediante la clave adecuada. Un hash genera una huella que se recalcula y compara; no se descifra. Un hash solo no acredita el origen ni protege la confidencialidad.

**4. Certificado en TLS.** Contribuye a autenticar al servidor al vincular identidad y clave pública mediante una CA confiable. La validación de la cadena, vigencia y nombre, junto con la prueba de posesión de la privada, ayuda a impedir suplantaciones. El conjunto de TLS aporta confidencialidad e integridad al tráfico. El certificado por sí solo no cifra toda la comunicación ni garantiza que el sitio sea honesto.

## Bloque 2 — Diffie–Hellman y XOR

### Ejercicio 1: entorno

Se entrega `lab-dh-xor/docker-compose.yml` con python:3.11-slim, servicios y contenedores alice y bob, hostnames respectivos, directorio /app, volumen ./scripts:/app, tty y stdin_open habilitados y sleep infinity para mantenerlos activos. Red red-cripto con internal: true, subred 172.28.0.0/16, Alice 172.28.0.20 y Bob 172.28.0.10. No se publican puertos en el anfitrión.

Comandos de arranque y comprobación:

```bash
cd ~/PE89.2/lab-dh-xor
sudo docker compose config
sudo docker compose up -d
sudo docker compose ps
sudo docker network inspect red-cripto
```

### Ejercicios 2 y 3: implementación

Los scripts completos están en `lab-dh-xor/scripts/`. Para cada pública se utiliza `pow(G, privada, P)`; para la compartida, `pow(publica_recibida, privada, P)`. XOR recorre los bytes y aplica `byte ^ K`. Alice codifica UTF-8 antes de cifrar y Bob decodifica UTF-8 después de descifrar.

Se utilizan P=251, G=6 y puerto 5000. Bob escucha dentro del contenedor en 0.0.0.0:5000 y Alice se conecta a 172.28.0.10:5000. La red de Docker permanece interna. La pública se delimita por salto de línea y el mensaje por fin de envío, para manejar correctamente el flujo TCP.

Terminal de Bob:

```bash
sudo docker compose exec bob python bob_servidor.py
```

Introducir b=11. En otra terminal:

```bash
sudo docker compose exec alice python alice_cliente.py
```

Introducir a=7 y mensaje Hola Bob. No iniciar Alice antes de que Bob esté escuchando.

### Ejercicio 4: tabla de comprobación

| Elemento | Valor del ejemplo reproducible |
|---|---|
| Privada de Alice, a | 7 |
| Pública de Alice, A | 71 |
| Privada de Bob, b | 11 |
| Pública de Bob, B | 150 |
| K calculada por Alice | 158 |
| K calculada por Bob | 158 |
| Mensaje original | Hola Bob |
| Cifrado hexadecimal | D6 F1 F2 FF BE DC F1 FC |
| Mensaje recuperado | Hola Bob |

Cálculos: A = 6^7 mod 251 = 71; B = 6^11 mod 251 = 150; K de Alice = 150^7 mod 251 = 158; K de Bob = 71^11 mod 251 = 158. Aquí `^` expresa potencia en notación matemática; en Python se usa pow, porque el operador ^ de Python es XOR.

La primera letra, H, vale 72 en UTF-8. 72 XOR 158 = 214, que se representa D6 en hexadecimal. 214 XOR 158 = 72 recupera H. La misma propiedad se aplica a cada byte.

**Qué atraviesa la red:** A, B y bytes cifrados. Las privadas a y b no se transmiten; K se calcula en ambos extremos y tampoco se transmite directamente. Las impresiones locales de claves son evidencias didácticas. DH sin autenticar permite un intermediario, el grupo diminuto admite búsqueda exhaustiva y XOR de clave repetida de un byte no ofrece seguridad real ni integridad. El sistema es exclusivamente educativo.

## Bloque 3 — Certificado digital

Se usan exactamente los dos certificados públicos enlazados por Ironhack en el repositorio faguilar-ironhack/assets, commit 724f6531058847752f800ef15042241b809815cd.

### Ejercicio 1: ficha del certificado

| Elemento | Valor obtenido del certificado |
|---|---|
| Sujeto | C=ES, O=CETI Formacion, OU=PE 89.2, CN=servidor.pe89.local |
| Nombre común, CN | servidor.pe89.local |
| Organización | CETI Formacion |
| Emisor | C=ES, O=CETI Formacion, OU=Laboratorio de Criptografia, CN=CETI Lab Root CA 2026 |
| Número de serie | 2300585473 en decimal; 89202601 en hexadecimal |
| Inicio | 16 de octubre de 2026, 06:21:14 UTC |
| Caducidad | 16 de octubre de 2027, 06:21:14 UTC |
| Algoritmo de clave pública | rsaEncryption, RSA |
| Tamaño de clave pública | 2048 bits |
| Algoritmo de firma | sha256WithRSAEncryption |
| Huella SHA-256 | C2:6C:98:F6:63:81:45:0C:04:9A:BA:29:72:B7:FB:CD:24:DB:54:31:27:95:E5:CB:BC:F0:06:82:56:1E:D7:14 |
| SAN | DNS:servidor.pe89.local; DNS:www.servidor.pe89.local; IP Address:172.28.0.30 |
| Key Usage, crítica | Digital Signature, Key Encipherment |
| Extended Key Usage | TLS Web Server Authentication |
| ¿Puede actuar como CA? | No; Basic Constraints, crítica, contiene CA:FALSE |

Comandos de consulta:

```bash
openssl x509 -in certificado_servidor_PE89_2.crt -text -noout
openssl x509 -in certificado_servidor_PE89_2.crt -noout -subject -issuer -serial -dates
openssl x509 -in certificado_servidor_PE89_2.crt -noout -fingerprint -sha256
```

### Ejercicio 2: interpretación

**1. Tipo de certificado.** Es un certificado de servidor. Lo indican CA:FALSE y Extended Key Usage: TLS Web Server Authentication. Key Usage permite firma digital y cifrado de claves, sin Certificate Sign.

**2. Identidad del servidor.** SAN contiene los nombres DNS y la dirección IP admitidos. CN también presenta servidor.pe89.local; la verificación moderna del nombre se basa en SAN. La firma de la CA vincula esos datos con la clave pública, siempre que se valide contra una CA de confianza. La IP 172.28.0.30 del certificado no es la dirección de Bob.

**3. Qué puede distribuirse.** Todo el certificado puede distribuirse públicamente: clave pública, identidad, extensiones y firma. También puede distribuirse el certificado público de la CA.

**4. Clave privada.** No está incluida. El certificado contiene la pública del servidor, no su privada ni la privada de la CA.

**5. Robo de la privada.** Un atacante podría intentar suplantar al servidor y demostrar posesión de su clave si consigue atraer o redirigir conexiones. Hay que revocar y reemplazar el certificado y el par de claves comprometido. El robo no descifra automáticamente sesiones anteriores que usaran secreto hacia adelante, por ejemplo TLS 1.3 con intercambio efímero.

### Ejercicio 3: verificación

Desde la carpeta certificados:

```bash
openssl verify -CAfile CA_laboratorio_PE89_2.crt certificado_servidor_PE89_2.crt
```

Salida obtenida:

```text
certificado_servidor_PE89_2.crt: OK
```

El resultado indica validación satisfactoria frente a la CA indicada, con las comprobaciones aplicables de OpenSSL. No instala confianza global ni demuestra que un navegador confíe en la CA del laboratorio. El comando básico no verifica por sí solo el nombre del servidor, su disponibilidad ni el estado de revocación mediante una consulta en línea.

Comprobación adicional de finalidad y nombre:

```bash
openssl verify -CAfile CA_laboratorio_PE89_2.crt -purpose sslserver -verify_hostname servidor.pe89.local certificado_servidor_PE89_2.crt
```

Los comandos y sus salidas se encuentran en el directorio `evidencias/`.

## Fuentes

- Enunciado y rúbrica de PE 89.2: portal de Ironhack, MF0489 Semana 2, consultado el 16 de octubre de 2026.
- [Certificado original del servidor](https://github.com/faguilar-ironhack/assets/blob/724f6531058847752f800ef15042241b809815cd/mf0489/certificados/certificado_servidor_PE89_2.crt).
- [Certificado público de la CA](https://github.com/faguilar-ironhack/assets/blob/724f6531058847752f800ef15042241b809815cd/mf0489/certificados/CA_laboratorio_PE89_2.crt).
- [Python 3.11: pow](https://docs.python.org/3.11/library/functions.html#pow).
- [OpenSSL: verify](https://docs.openssl.org/3.0/man1/openssl-verify/).
- [TLS 1.3, RFC 8446](https://www.rfc-editor.org/rfc/rfc8446).
- [Deprecación de TLS 1.0 y 1.1, RFC 8996](https://www.rfc-editor.org/rfc/rfc8996).
