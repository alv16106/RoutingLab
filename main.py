import logging
import blessed
from getpass import getpass
from argparse import ArgumentParser

from chat.session import Session
from chat.menu import menu
from utils import getAlgorithm

term = blessed.Terminal()

if __name__ == '__main__':
  # Start the fullscreen mode, clearing the terminal
  with term.fullscreen():
    parser = ArgumentParser()
    # add arguments to parser
    parser.add_argument("-j", "--jid", dest="jid", help="JID to use")
    parser.add_argument("-p", "--password", dest="password", help="password to use")
    parser.add_argument("-a", "--algorithm", dest="alg", help="algorithm to use")
    args = parser.parse_args()

    #If not arguments were passed, ask for them
    if args.jid is None:
      args.jid = input("Username: ")
    if args.password is None:
      args.password = getpass("Password: ")
    if args.alg is None:
      args.alg = input("Algorithm: ")

    # Select algorithm to use
    algorithm = getAlgorithm(args.alg)
      
    """ Start an instance of our session manager and register
    all plugins necessary """
    xmpp = Session(args.jid, args.password)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0004') # Data forms
    xmpp.register_plugin('xep_0060') # PubSub
    xmpp.register_plugin('xep_0047') # In-band Bytestreams
    xmpp.register_plugin('xep_0066') # Out-of-band Data
    xmpp.register_plugin('xep_0199') # Ping
    xmpp.register_plugin('xep_0045')
    xmpp.register_plugin('xep_0065', {
      'auto_accept': True
    }) # SOCKS5 Bytestreams
    xmpp.register_plugin('xep_0077') # In-band Registration
    xmpp['xep_0077'].force_registration = True

    # Setup logging.
    logging.basicConfig(level=logging.ERROR, format='%(levelname)-8s %(message)s')

    xmpp.connect()
    xmpp.process()