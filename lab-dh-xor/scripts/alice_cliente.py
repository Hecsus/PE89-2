#!/usr/bin/env python3
"""Cliente didáctico: intercambia solo la clave pública y el mensaje XOR."""
import socket

P = 251
G = 6
IP_BOB = "172.28.0.10"
PUERTO = 5000


def aplicar_xor(datos_bytes, llave_k):
    resultado = []
    for byte in datos_bytes:
        resultado.append(byte ^ llave_k)
    return bytes(resultado)


def main():
    a = int(input("Introduce tu número secreto (a), de 2 a 250: "))
    if not 2 <= a <= 250:
        raise ValueError("a debe estar entre 2 y 250")
    A = pow(G, a, P)
    print(f"[Local Alice] a = {a} | A = {A}", flush=True)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(120)
        print(f"[*] Conectando con Bob ({IP_BOB}:{PUERTO})...", flush=True)
        s.connect((IP_BOB, PUERTO))
        s.sendall(f"{A}\n".encode("ascii"))
        with s.makefile("rb") as entrada:
            linea = entrada.readline(32)
            if not linea.endswith(b"\n"):
                raise ValueError("Clave pública sin delimitador")
            B = int(linea)
            if not 1 <= B < P:
                raise ValueError("Clave pública fuera de rango")
        print(f"[Red Pública] Enviada A = {A} | Recibida B = {B}", flush=True)
        K = pow(B, a, P)
        print(f"[Local Alice] K = {K}; no se transmite", flush=True)
        mensaje = input("Escribe el mensaje para Bob: ")
        print(f"[Mensaje original] {mensaje}", flush=True)
        bytes_cifrados = aplicar_xor(mensaje.encode("utf-8"), K)
        print(f"[Cifrado Hex] {bytes_cifrados.hex(' ').upper()}", flush=True)
        s.sendall(bytes_cifrados)
        s.shutdown(socket.SHUT_WR)
        print("[+] Mensaje enviado", flush=True)


if __name__ == "__main__":
    main()
