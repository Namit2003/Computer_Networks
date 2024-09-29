import socket
import re

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(("www.example.com", 80))

sock.send(b"GET / HTTP/1.1\r\nHost:www.example.com\r\nConnection: close\r\n\r\n")

response = b""
while True:
    chunk = sock.recv(4096)
    if len(chunk) == 0:
        break
    response = response + chunk

res = response.decode()
sock.close()

# print(res)

status_line = res.split('\n')[0]
status_code = status_line.split(' ')[1]

if status_code == '200':
    print("Status Code: 200 OK")

    with open('index.html','w', encoding='utf-8') as f:
        f.write(res)

    with open('index.html', 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Find the index of the line containing '<!doctype html>'
    index = -1
    for i, line in enumerate(lines):
        if '<!doctype html>' in line.lower():
            index = i
            break

    # If '<!doctype html>' is found, delete everything before that line
    if index != -1:
        lines = lines[index:]

        # Write the updated content back to the file
        with open('index.html', 'w', encoding='utf-8') as file:
            file.writelines(lines)
    else:
        print("'<!doctype html>' not found in the file.")

elif status_code == '301':
    print("Status Code: 301 Moved Permanently")

elif status_code == '404':
    print("Status Code: 404 Not Found")

else:
    print(f"Status Code: {status_code}")
