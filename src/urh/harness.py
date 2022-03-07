from urh.awre import AutoAssigner
from urh.awre.FormatFinder import FormatFinder
from urh.awre.MessageTypeBuilder import MessageTypeBuilder
from urh.awre.Preprocessor import Preprocessor
from urh.awre.ProtocolGenerator import ProtocolGenerator
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.Participant import Participant
from urh.signalprocessing.Message import Message
from urh.signalprocessing.MessageType import MessageType
from urh.util import util


f=open("/content/tc1.txt")
hx = f.read().strip()
f.close()


bs = [bytes.fromhex(l) for l in hx.split("\n")]

# Convert hex string to awre style bitstring
# Puts most significant bit first
def bytes2bits(data_):
    data = bytes.fromhex(data_)
    def access_bit(data, num):
        base = int(num // 8)
        shift = int(num % 8)
        return (data[base] >> shift) & 0x1
    bits = []
    for i in range(0,len(data)*8,8):
        bit_chunk =  [access_bit(data,i) for i in range(i,i+8)][::-1]
        bits+=bit_chunk
    return "".join([str(v) for v in bits])
    return [access_bit(data,i) for i in range(len(data)*8)]


# Convert AWRE Style bits to hex string
# assumes most significant bit of byte comes first
# Input text string of 010101010's 
# Output hex String
def bits2bytes(a_):
    a = [int(v) for v in a_]
    if len(a) % 8 != 0:
        a =    [0] * (8 - (len(a) % 8)) + a # adding in extra 0 values to make a multiple of 8 bits
    s = ''.join(str(x) for x in a)[::-1] # reverses and joins all bits
    #print("s",s)
    returnInts = []
    for i in range(0,len(s),8):
        #print("\t",i,"\t",s[i:i+8])
        returnInts.append(int(s[i:i+8][::-1],2)) # goes 8 bits at a time to save as ints
    return bytes(returnInts[::-1]).hex()

# Convert raw hex messages into bit array format awre expects
def bytes2awreinput(data):
  # Split string into messages
  msgs = data.split("\n")
  #Turn into bitstrings
  bits_messages = [[int(v) for v in bytes2bits(m.strip())] for m in msgs]
  mtx = MessageType("foo")
  msgs = [Message(m,0,mtx) for m in bits_messages]
  return msgs

#for m in pg.messages:
#  print(bits2bytes("".join([str(b) for b in m.plain_bits])))


#for m in hx.split("\n"):
#  print("\t",m,bytes2bits(bits2bytes(bytes2bits(m))))

def awreinfer(hx):
    print("Input")
    print(hx)
    print("Infers")
    msgs = bytes2awreinput(hx)
    ff = FormatFinder(msgs)
    ff.run()
    mt = ff.message_types[0]
    for t in mt:
        print("\ttype",t.name,t.start,t.end,"(",t,")")
    print("")

data = """01ff
02ffee
01ff
03ffeedd"""
awreinfer(data)

awreinfer(hx)
