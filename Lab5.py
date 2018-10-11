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
    client_socket.sendall(b'GET / HTTP/1.1\r\n' + b'Host: ' + host + b'\r\n\r\n')
    header = read_headers(client_socket)
    
    relevant_headers = get_contentlenght_chunked(header)
    
    contents = read_contents(relevant_headers, client_socket)
    
    client_socket.close()
    status = status_index(header)
    write_to_file(contents, file_name)
    
    return status


def read_contents(length, socket):
    """
    This method will decide either the response will be read
    as content-length or chunked data.
    :author:
    :param length: The content-length or chunk
    :param socket: The data socket
    :return: Either the body of content-length or chunk
    """
    if length == 'chunked':
        return read_chunked(socket)
    else:
        return read_body(length, socket)


def status_index(header):
    """
    //todo - helped method
    Return the status index from http header
    :author:
    :param header: The header of the response
    :return: result2 the status index of http request
    """
    info = header.decode('utf-8')
    result = info.split(' ')
    result2 = result[1]
    return result2


def read_chunked(tcp_socket):
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
        while not (last_two[0] == b'\r' and last_two[1] == b'n'):
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


def read_headers(socket):
    """
    This method reads the headers

    :author: Ashpreet kaur
    :param socket: is the socket to read from.
    :return: The header
    """
    header = b''
    while True:
        if b'\r\n\r\n' in header:
            break
        header += next_byte(socket)
    return header.split(b'\r\n\r\n')[0]


def get_contentlenght_chunked(header):
    """
    //todo - helped to change the if statement and remove arrays
    :param header:
    :return:
    """
    # #changes byte header to string and splits the line
    # split_headers = header.decode('utf-8').split('\r\n')
    # #goes to the fourth lines of the header which could be either chuncked or content length
    # content_length = split_headers[4].split(' ')[1]
    # #i used array where [1] is either chunck or content length
    # chunked = split_headers[3].split(' ')[1]
    # #stored the array in respense variable which is being called by the main
    # response = [content_length, chunked]
    
    split_headers = header.decode('utf-8').split('\r\n')
    content_length = split_headers[4].split(' ')[1]
    if content_length == " chunked":
        return content_length
    else:
        return int(content_length)


def read_body(length, socket):
    """
    //todo - helped
    :param length:
    :param socket:
    :return:
    """
    data = b''
    for i in range(0, length):
        data += next_byte(socket)
    return data


def write_to_file(message, file_name):
    """
    This method saves to a file
    
    @author: Ashpreet kaur
    :param message: is the data or message that we received
    :param file_name: name of file in which to store the retrieved resource
    """
    with open(file_name, 'wb') as file:
        file.write(message)
    file.close()


main()
