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
    get_http_resource('http://msoe.us/taylor/', 'index.html')

    # this resource request should result in "chunked" data transfer
    get_http_resource('http://msoe.us/taylor/images/taylor.jpg', 'taylor.jpg')

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


def make_http_request(host, port, resource, file_name):
    """
    Get an HTTP resource from a server

    :param bytes host: the ASCII domain name or IP address of the server machine (i.e., host) to connect to
    :param int port: port number to connect to on server host
    :param bytes resource: the ASCII path/name of resource to get. This is everything in the URL after the domain name,
           including the first /.
    :param file_name: string (str) containing name of file in which to store the retrieved resource
    :return: the status code
    :rtype: int
    """

    client_socket = socket.socket(AF_INET, SOCK_STREAM)
    client_socket.connect((host, port))
    client_socket.sendall(b'GET /' + resource + b'/ HTTP/1.1\r\n' + b'Host: ' + host + b'\r\n\r\n')

    status = read_status(client_socket)
    header = read_header(client_socket)

    message = ""
    if "content_length" in header:
        message = read_content_length(client_socket, header["content_length"])
    else:
        message = read_chunked(client_socket)

    write_to_file(message, file_name)

    client_socket.close()
    return status


def read_status(tcp_socket: socket) -> int:
    output = b""
    last_byte = next_byte(tcp_socket)

    while last_byte != b" ":
        last_byte = next_byte(tcp_socket)

    last_byte = next_byte(tcp_socket)

    while last_byte != b" ":
        output += last_byte
        last_byte = next_byte(tcp_socket)

    return int(output)


# TODO
def read_header(tcp_socket: socket) -> Dict:
    output: Dict = []

    while

    current_item = b""

    last_byte = next_byte(tcp_socket)

    while last_byte != ":"
        current_item += last_byte
        last_byte = next_byte(tcp_socket)


# TODO
def read_content_length(tcp_socket: socket, content_length: int) -> str:


def read_chunked(tcp_socket: socket):
    """
    Reads a chunked message.
    :author: Noah Kennedy
    :param tcp_socket: The TCP Socket to read the message from.
    :return: The chunked contents.
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
