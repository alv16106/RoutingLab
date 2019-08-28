#Bueno, a empezar
# Requerimientos
# Nodo fuente [texto + @]
# -Nodo destino [texto + @]
# -Saltos (nodos) recorridos [numérico]
# -Distancia [numérico]
# -Listado de nodos[texto]
# -Mensaje [texto]
import slixmpp

recent = []
def flooding():
  
  pass


# def message(self, msg):
#   """ Handler for normal messages """
#   if msg['type'] in ('chat', 'normal'):
#     print(term.magenta(str(msg['from'])+ ' > ') + term.color(55)(msg['body']))

def manage_flooding(msg, boundjid):
  if msg['final_to'] == boundjid.jid:
    if msg['id'] not in recent:
      print("hola")
      recent.append(msg['id'])
  send_flood(msg)
  return 1

# self.send_message(mto=self.current_reciever, mbody=args, msubject='normal message', mfrom=self.boundjid)
# resp = self.Iq()
#     resp['type'] = 'set'
#     resp['from'] = self.boundjid.jid
#     resp['register'] = ' '
#     resp['register']['remove'] = ' '
#     try:
#       await resp.send()
#       print('')
#     except IqError:
#       print(term.bold_red('Error al eliminar cuenta'))
#     except IqTimeout:
#       print(term.bold_red('timeout'))
#       self.disconnect()


 # msg = Iq()
  # msg['type'] = 'message'
  # msg['from'] = boundjid.jid
  # msg['to'] = "hola"
  # msg['final_to'] = "final"
  # print("mandar msg")

def send_flood(msg, boundjid, body, neighbors):
  for x in neighbors:
    print(x)



