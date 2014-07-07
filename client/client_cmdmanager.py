#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cmd
import socket
import struct
import json


DAEMON_HOST = 'localhost'
DAEMON_PORT = 50001


class CommandParser(cmd.Cmd):
    """
    Command line interpreter
    Parse user input
    """

    # Override attribute in cmd.Cmd
    prompt = '(PyBox)>>> '

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def _send_to_daemon(self, message=None):
        """
        it sends user input command to the daemon server
        """
        if not message:
            raise

        data_packet = json.dumps(message)
        try:
            # send the command to daemon
            data_packet_size = struct.pack('!i', len(data_packet))
            self.sock.sendall(data_packet_size)
            self.sock.sendall(data_packet)

            # receive the information message from daemon
            response_size = self.sock.recv(struct.calcsize('!i'))
            if len(response_size) == struct.calcsize('!i'):
                response_size = int(struct.unpack('!i', response_size)[0])
                response_packet = ''
                remaining_size = response_size
                while len(response_packet) < response_size:
                    response_buffer = self.sock.recv(remaining_size)
                    remaining_size -= len(response_buffer)
                    response_packet = ''.join([response_packet, response_buffer])

                response = json.loads(response_packet)

                print response['message']

                # to improve testing
                return response['message']
            else:
                raise Exception('Error: lost connection with daemon')

        except socket.error as ex:
            # log exception message
            print 'Socket Error: ', ex

    def preloop(self):
        self.sock.connect((DAEMON_HOST, DAEMON_PORT))

    def postloop(self):
        self.sock.close()

    def do_quit(self, line):
        """Exit Command"""
        return True

    def do_EOF(self, line):
        return True

    def do_reguser(self, line):
        """ Create new user
            Usage: reguser <username> <password>
        """

        try:
            user, password = line.split()
        except ValueError:
            print 'usage: newUser <username> <password>'
        else:
            message = {'reguser': (user, password)}
            print message
            self._send_to_daemon(message)

    def do_shutdown(self, line):
        message = {'shutdown': ()}
        self._send_to_daemon(message)


if __name__ == '__main__':
    CommandParser().cmdloop()
