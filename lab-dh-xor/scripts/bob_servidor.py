#!/usr/bin/env python3
"""Servidor didáctico: DH pequeño y XOR de un byte; no usar en producción."""
import socket

P = 251
G = 6
PUERTO = 5000


def aplicar_xor(datos_bytes, llave_k):
    resultado = []
    for byte in datos_bytes:
        resultado.append(byte ^ llave_k)
    return bytes(resultado)


def main():
    b = int(input("Introduce tu número secreto (b), de 2 a 250: "))
    if not 2 <= b <= 250:
        raise ValueError("b debe estar entre 2 y 250")
    B = pow(G, b, P)
    print(f"[Local Bob] b = {b} | B = {B}", flush=True)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("0.0.0.0", PUERTO))
        s.listen(1)
        print(f"[*] Esperando conexión de Alice en el puerto {PUERTO}...", flush=True)
        conn, addr = s.accept()
        with conn:
            conn.settimeout(120)
            print(f"[*] Conexión desde {addr[0]}", flush=True)
            # Una línea delimita la clave; TCP puede fragmentar los datos.
            with conn.makefile("rb") as entrada:
                linea = entrada.readline(32)
                if not linea.endswith(b"\n"):
                    raise ValueError("Clave pública sin delimitador")
                A = int(linea)
                if not 1 <= A < P:
                    raise ValueError("Clave pública fuera de rango")
                print(f"[Red Pública] Recibida A = {A}", flush=True)
                conn.sendall(f"{B}\n".encode("ascii"))
                print(f"[Red Pública] Enviada B = {B}", flush=True)
                K = pow(A, b, P)
                print(f"[Local Bob] K = {K}; no se transmite", flush=True)
                # El cliente cierra su dirección de envío al terminar el mensaje.
                mensaje_cifrado = entrada.read()
            print(f"[Cifrado Hex] {mensaje_cifrado.hex(' ').upper()}", flush=True)
            mensaje = aplicar_xor(mensaje_cifrado, K).decode("utf-8")
            print(f"[Mensaje recuperado] {mensaje}", flush=True)


if __name__ == "__main__":
    main()
