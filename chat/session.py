from slixmpp import ClientXMPP
from slixmpp.exceptions import IqError, IqTimeout
from slixmpp.xmlstream.asyncio import asyncio
from threading import Thread
from chat.menu import menu
from utils import getNeighbours
import pickle
import logging
import sys
import uuid
import blessed

# Start the blessed terminal used for UI
term = blessed.Terminal()

class Session(ClientXMPP):

  def __init__(self, jid, password, relations, algorithm, name):
    ClientXMPP.__init__(self, jid, password)
    """ Add all event handlers, nickname and
    start reciever in alumnchat """
    self.add_event_handler("session_start", self.session_start)
    self.add_event_handler("message", self.message)
    self.room = 'alumnos'
    self.current_reciever = 'alumchat.xyz'
    self.auto_subscribe = True
    self.relations = relations
    self.algorithm = algorithm
    self.neighbours = getNeighbours(relations, name)
    # Functions sent as arguments to main menu
    functions = {
      'dc': self.dc_and_exit,
      'list': self.get_contacts,
      'add': self.add_contact,
      'rm': self.delete_account,
      'send_message': self.message_sender,
      'jc': self.join_conversation,
      'find': self.start_algorithm
    }
    self.menuInstance = Thread(target = menu, args = (functions,))
    self.add_event_handler("register", self.register)

  def session_start(self, event):
    """ Handler for successful connection,
    start the menu thread """
    self.send_presence()
    self.get_roster()
    self.menuInstance.start()
  
  def start_algorithm(self, args):
    """ Where the magic happens, start sending hellos to neighbours
    and hope for the best """
    pass
    
  def dc_and_exit(self, args):
    """ Disconect from server and exit the 
    program
    BUG: For some reason after using blessed's
    fullscreeen sys.exit() doesn't exit the program correctly """
    self.disconnect(wait=2.0)
    sys.exit()
    sys.exit()

  def message_error(self, msg):
    """ Error messages """
    print(term.bold_red('ha ocurrido un error'))
    print(msg)
  
  def message(self, msg):
    """ Handler for normal messages """
    if msg['type'] in ('chat', 'normal'):
      print(term.magenta(str(msg['from'])+ ' > ') + term.color(55)(msg['body']))

  def add_contact(self, contact):
    """ Add contact to contact list
    TODO: Currently no handling of error when adding user """
    self.send_presence_subscription(pto=contact)
    print(term.bold_green(contact + ' es ahora tu contacto'))
  
  def get_contacts(self, args):
    """ Print all contacts on contact list """
    print(term.magenta('Users in your contact list: '))
    for jid in self.roster[self.jid]:
      print(term.cyan(jid))

  def join_conversation(self, args):
    """ Method used to change the guy we are currently speaking to
    returns an error in case that user is not in our contacts list """
    if args in self.roster[self.jid]:
      self.current_reciever = args
    else:
      print(term.bold_red('ERROR: Usuario no en la lista de contactos'))

  def message_sender(self, args):
    """ Send normal message
    TODO: Make it alternate between muc and normal given the conversation context """
    self.send_message(mto=self.current_reciever, mbody=args, msubject='normal message', mfrom=self.boundjid)
     
  def delete_account(self, args):
    """ Helper function to delete account """
    asyncio.run(self.delete_account_send())

  async def delete_account_send(self):
    # Manual build of delete account iq
    resp = self.Iq()
    resp['type'] = 'set'
    resp['from'] = self.boundjid.jid
    resp['register'] = ' '
    resp['register']['remove'] = ' '
    try:
      await resp.send()
      print('')
    except IqError:
      print(term.bold_red('Error al eliminar cuenta'))
    except IqTimeout:
      print(term.bold_red('timeout'))
      self.disconnect()

  async def register(self, iq):
    """ Register function, calls itself every time.
    If your accont already exists it does nothing, if
    it is new, it registers you
    TODO: Find way to skip this function if your account
    already exists """
    resp = self.Iq()
    resp['type'] = 'set'
    resp['register']['username'] = self.boundjid.user
    resp['register']['password'] = self.password
    try:
      await resp.send()
      logging.info("Account created for %s!" % self.boundjid)
    except IqError as e:
      logging.error("Could not register account: %s" %e.iq['error']['text'])
    except IqTimeout:
      logging.error("No response from server.")
      self.disconnect()
    