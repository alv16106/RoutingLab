from slixmpp import ClientXMPP
from slixmpp.exceptions import IqError, IqTimeout
from slixmpp.xmlstream.asyncio import asyncio
from threading import Thread
from chat.menu import menu
from utils import getNeighbours, getAlgorithm, generateLSP
from graph import Graph, shortest_path
import pickle
import logging
import sys
import uuid
import blessed
import algorithms.flooding as f
import json

# Start the blessed terminal used for UI
term = blessed.Terminal()

mem = {
      "emisor": "R",
      "weight": 100,
      "nodes": "none",
      "msg": "msg"
    }

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
    self.algorithm_name = algorithm
    self.algorithm = getAlgorithm(algorithm)
    self.serial = 1
    self.neighbours = getNeighbours(relations, name)
    self.graph = Graph()
    self.name = name
    self.lsps = {}
    # Functions sent as arguments to main menu
    functions = {
      'dc': self.dc_and_exit,
      'list': self.get_contacts,
      'add': self.add_contact,
      'rm': self.delete_account,
      'send_message': self.message_sender,
      'jc': self.join_conversation,
      'find': self.start_algorithm,
      'd' : self.direct_message
    }
    self.menuInstance = Thread(target = menu, args = (functions,))
    self.add_event_handler("register", self.register)

  def session_start(self, event):
    """ Handler for successful connection,
    start the menu thread """
    self.send_presence()
    self.get_roster()

    #Start the graph by adding ourselves and our neighbours
    self.graph.addNode(self.name)
    for node in self.neighbours:
      self.graph.addNode(node)
      self.graph.addEdge(self.name, node, self.neighbours[node])
    self.start_algorithm({})
    self.menuInstance.start()
  
  def start_algorithm(self, args):
    """ Where the magic happens, start sending hellos to neighbours
    and hope for the best """
    if self.algorithm_name in ('lsr', 'dvr'):
      self.send_to_neighbours(generateLSP(self.name, self.neighbours, self.serial), "start")
      self.serial += 1
    
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
      if msg['subject'] in ('flood'):
        jmsg = msg['body']
        og_msg = json.loads(jmsg)
        if og_msg["final_to"] == self.boundjid.jid.split("/")[0]:
          if og_msg["og_from"] == mem["emisor"] and og_msg["msg"] == mem["msg"]:
            if int(og_msg["weight"]) < mem["weight"]:
              mem["weight"] = og_msg["weight"]
              mem["nodes"] = og_msg["node_list"]
          else:
            print(mem["weight"])
            print(mem["nodes"])
            print(term.cyan(og_msg["og_from"] +": "+og_msg['msg']))
            mem["weight"] = og_msg["weight"]
            mem["nodes"] = og_msg["node_list"]
            mem["emisor"] = og_msg["og_from"]
            mem["msg"] = og_msg['msg']
            return 0
        elif og_msg["hops"] != 0:
          self.resend(og_msg, msg['from'])
      elif msg['subject'] in ('start', 'resend'):
        resend_message = self.algorithm(self, msg)
        self.send_to_neighbours(resend_message, "resend") if resend_message else None
      elif msg['subject'] in ('lsr_message'):
        body = json.loads(msg['body'])
        path = body['path']
        print(path)
        if path[-1] == self.name:
          print(term.magenta(str(msg['from'])+ ' > ') + term.color(55)(body['msg']))
        else:
          next_hop = path.index(self.name) + 1
          self.send_message(mto = 'g1_'+path[next_hop]+"@alumchat.xyz", mbody = msg['body'], msubject = 'lsr_message', mfrom = self.boundjid)
      else:
        print(term.magenta(str(msg['from'])+ ' > ') + term.color(55)(msg['body']))
      
  def send_to_neighbours(self, message, subject):
    for neighbour in self.neighbours:
      self.send_message(mto = 'g1_'+neighbour+"@alumchat.xyz", mbody = generateLSP(self.name, self.neighbours, self.serial), msubject = subject, mfrom = self.boundjid)
      self.send_message(mto = 'g1_'+neighbour+"@alumchat.xyz", mbody = message, msubject = subject, mfrom = self.boundjid)

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

  def direct_message(self, args):
    content = input('Mensaje?  ')
    if self.algorithm == "flooding":
      body = {
          "og_from": str(self.boundjid),
          "final_to": 'g1_'+args+"@alumchat.xyz",
          "hops": 3,
          "distance": 0,
          "node_list": self.boundjid.jid,
          "msg": content,
          "weight": 0,
        }
      #Send Direct Message
      for x in self.neighbours:
        body["weight"] = self.neighbours[x]
        jbody = json.dumps(body)
        self.send_message(mto = 'g1_'+x+"@alumchat.xyz", mbody = jbody, msubject = 'flood', mfrom = self.boundjid)
    elif self.algorithm_name == 'lsr':
      path = shortest_path(self.graph, self.name, args.upper())
      body = {
        'from': self.name,
        'to': 'g1_'+args+"@alumchat.xyz",
        'path': path[1],
        'distance': path[0],
        'msg': content
      }
      self.send_message(mto = 'g1_'+path[1][1]+"@alumchat.xyz", mbody = json.dumps(body), msubject = 'lsr_message', mfrom = self.boundjid)
    else:
      self.send_message(mto = 'g1_'+args+"@alumchat.xyz", mbody = content, msubject = 'normal chat', mfrom = self.boundjid)

  def resend(self, og, sender):
    body = {
      "og_from": og["og_from"],
      "final_to": og["final_to"],
      "hops": og["hops"] - 1,
      "distance": og["distance"] + 1,
      "node_list": og["node_list"] + self.boundjid.jid,
      "msg": og["msg"],
      "weight": og["weight"]
    }
    for x in self.neighbours:
      if 'g1_'+x.lower()+"@alumchat.xyz" != str(sender).split("/")[0]:
        body["weight"] = body["weight"] + self.neighbours[x]
        jbody = json.dumps(body)
        self.send_message(mto = 'g1_'+x+"@alumchat.xyz", mbody = jbody, msubject = 'flood', mfrom = self.boundjid)

     
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


