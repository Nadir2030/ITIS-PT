import struct

MAX_MESSAGE_SIZE = 10 * 1024 * 1024


def recv_exact(sock, size):
    data = b""

    while len(data) < size:
        chunk = sock.recv(size - len(data))

        if chunk == b"":
            raise ConnectionError("Соединение закрыто")

        data += chunk

    return data


def send_message(sock, command, payload):
    command_bytes = command.encode("utf-8")

    if len(command_bytes) != 4:
        raise ValueError("Команда должна занимать 4 байта")

    if len(payload) > MAX_MESSAGE_SIZE:
        raise ValueError("Сообщение слишком большое")

    header = command_bytes + struct.pack("!I", len(payload))

    sock.sendall(header + payload)


def recv_message(sock):
    command_bytes = recv_exact(sock, 4)
    length_bytes = recv_exact(sock, 4)

    command = command_bytes.decode("utf-8")
    length = struct.unpack("!I", length_bytes)[0]

    if length > MAX_MESSAGE_SIZE:
        raise ValueError("Сообщение слишком большое")

    payload = recv_exact(sock, length)

    return command, payload