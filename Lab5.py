"""
- CS2911 - 011
- Fall 2018
- Lab 5 - HTTP client
- Names:
  - Ashpreet Kaur
  - Noah M. Kennedy

A simple HTTP client
"""
from socket import *
# import the "socket" module -- not using "from socket import *" in order to selectively use items with "socket." prefix
import socket

# import the "regular expressions" module
import re
from typing import Dict, List


def main():
    """
    Tests the client on a variety of resources
    """
    
    # These resource request should result in "Content-Length" data transfer
    get_http_resource('http://msoe.us/taylor/images/taylor.jpg', 'taylor.jpg')

    # this resource request should result in "chunked" data transfer
    get_http_resource('http://msoe.us/taylor/', 'index.html')

    # If you find fun examples of chunked or Content-Length pages, please share them with us!


def get_http_resource(url, file_name):
    """
    Get an HTTP resource from a server
           Parse the URL and call function to actually make the request.

    :param url: full URL of the resource to get
    :param file_name: name of file in which to store the retrieved resource

    (do not modify this function)
    """
    
    # Parse the URL into its component parts using a regular expression.
    url_match = re.search('http://([^/:]*)(:\d*)?(/.*)', url)
    url_match_groups = url_match.groups() if url_match else []
    #    print 'url_match_groups=',url_match_groups
    if len(url_match_groups) == 3:
        host_name = url_match_groups[0]
        host_port = int(url_match_groups[1][1:]) if url_match_groups[1] else 80
        host_resource = url_match_groups[2]
        print('host name = {0}, port = {1}, resource = {2}'.format(host_name, host_port, host_resource))
        status_string = make_http_request(host_name.encode(), host_port, host_resource.encode(), file_name)
        print('get_http_resource: URL="{0}", status="{1}"'.format(url, status_string))
    else:
        print('get_http_resource: URL parse failed, request not sent')


def make_http_request(host: bytes, port: int, resource: bytes, file_name: str) -> int:
    """
    Get an HTTP resource from a server

    :param bytes host: the ASCII domain name or IP address of the server machine (i.e., host) to connect to
    :param int port: port number to connect to on server host
    :param bytes resource: the ASCII path/name of resource to get. This is everything in the URL after the domain name,
           including the first /.
    :param file_name: string (str) containing name of file in which to store the retrieved resource
    :return: the status code
    :return: The status code of the http response.
    """
    
    client_socket = socket.socket(AF_INET, SOCK_STREAM)
    client_socket.connect((host, port))
    client_socket.sendall(b'GET /' + resource + b'/ HTTP/1.1\r\n' + b'Host: ' + host + b'\r\n\r\n')
    
    status = read_status(client_socket)
    header = read_header(client_socket)
    
    message = ""
    if b'Content-Length' in header:
        message = read_content_length(client_socket, int(header[b'Content-Length']))
    else:
        message = read_chunked(client_socket)
    
    write_to_file(message, file_name)
    
    client_socket.close()
    return status


def read_status(tcp_socket: socket) -> int:
    """
    Reads the status line.
    :param tcp_socket: The socket to read the line from.
    :return: The status code.
    :author: Noah Kennedy
    """
    status_bytes = b""
    
    # Read first byte
    new_byte = next_byte(tcp_socket)
    
    # Keep reading bytes until we read a space
    while new_byte != b" ":
        new_byte = next_byte(tcp_socket)
    
    # Read the space
    new_byte = next_byte(tcp_socket)
    
    # Read bytes and add them to status_bytes until we read a space.
    while new_byte != b" ":
        status_bytes += new_byte
        new_byte = next_byte(tcp_socket)
    
    # Two bytes are now used as a buffer so that we can check for "\r\n"
    old_byte = new_byte
    new_byte = next_byte(tcp_socket)
    
    # Read the rest of the status line
    while old_byte != b"\r" or new_byte != b"\n":
        old_byte = new_byte
        new_byte = next_byte(tcp_socket)
    
    return int(status_bytes)


# TODO
def read_header(tcp_socket: socket) -> Dict[bytes, bytes]:
    """
    Reads the headers from an http get request.
    :param tcp_socket: The tcp socket to read bytes from.
    :return: A dictionary whose keys are the http fields and whose values are the associated values
    """
    header: Dict = dict()
    
    reading_buffer = [b'', b'', b'', b'']
    message = b''
    
    reading_buffer[3] = next_byte(tcp_socket)
    
    # Read fields until "\r\n\r\n"
    while reading_buffer[0] != b'\r' or reading_buffer[1] != b'\n' or reading_buffer[2] != b'\r' or reading_buffer[3] != b'\n':
        message += reading_buffer[3]
        
        reading_buffer[0] = reading_buffer[1]
        reading_buffer[1] = reading_buffer[2]
        reading_buffer[2] = reading_buffer[3]
        reading_buffer[3] = next_byte(tcp_socket)
    
    fields = re.compile("\r\n").split(message.decode("utf-8"))
    fields.remove("\r")
    
    for field in fields:
        splitup = re.compile(":").split(field)
        header[splitup[0].encode()] = splitup[1].encode()

    return header


# TODO
def read_content_length(client_socket: socket, content_length: int) -> bytes:
    """
    Reads the body a content-length http message.
    :param client_socket: The socket with the message body.
    :param content_length: The length of the content.
    :return: Returns a string containing the message body.
    :author: Ashpreet Kaur
    """
    # string_headers = headers.decode('utf-8')
    # split_headers = string_headers.split('\r\n')
    # n = 0
    # while 'Content-Length:' not in split_headers[n]:
    #    n = n + 1
    # contentlength = split_headers[n].split(' ')[1]
    # return contentlength
    
    return b''


def read_chunked(tcp_socket: socket) -> bytes:
    """
    Reads a chunked message.
    :param tcp_socket: The TCP Socket to read the message from.
    :return: The chunked contents.
    :author: Noah Kennedy
    """
    last_two = [b'', b'']
    chunk_num = b''
    output = b''
    while not chunk_num == b'0':
        chunk_num = b''
        while not (last_two[0] == b'\r' and last_two[1] == b'\n'):
            chunk_num += last_two[0]
            last_two[0] = last_two[1]
            last_two[1] = next_byte(tcp_socket)
        output += tcp_socket.recv(int(chunk_num, 16))
        tcp_socket.recv(2)
        last_two = [b'', b'']
    return output


def next_byte(data_socket):
    """
    Read the next byte from the socket data_socket.

    Read the next byte from the sender, received over the network.
    If the byte has not yet arrived, this method blocks (waits)
      until the byte arrives.
    If the sender is done sending and is waiting for your response, this method blocks indefinitely.

    :param data_socket: The socket to read from. The data_socket argument should be an open tcp
                        data connection (either a client socket or a server data socket), not a tcp
                        server's listening socket.
    :return: the next byte, as a bytes object with a single byte in it
    """
    return data_socket.recv(1)


def write_to_file(message, file_name):
    """
    This method writes to a file
    @author: Ashpreet kaur
    :param message: is the data or message that we received
    :param file_name: name of file in which to store the retrieved resource
    """
    with open(file_name, 'wb') as file:
        file.write(message)
    file.close()


main()
