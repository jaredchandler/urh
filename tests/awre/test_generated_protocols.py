from tests.awre.AWRETestCase import AWRETestCase
from tests.awre.AWRExperiments import AWRExperiments
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


class TestGeneratedProtocols(AWRETestCase):
    def __check_addresses(self, messages, format_finder, known_participant_addresses):


        for msg_type, indices in format_finder.existing_message_types.items():
            for i in indices:
                messages[i].message_type = msg_type

        participants = list(set(m.participant for m in messages))
        for p in participants:
            p.address_hex = ""
        AutoAssigner.auto_assign_participant_addresses(messages, participants)

        for i in range(len(participants)):
            self.assertIn(participants[i].address_hex,
                          list(map(util.convert_numbers_to_hex_string, known_participant_addresses.values())),
                          msg=" [ " + " ".join(p.address_hex for p in participants) + " ]")

    def test_without_preamble(self):
        alice = Participant("Alice", address_hex="24")
        broadcast = Participant("Broadcast", address_hex="ff")

        mb = MessageTypeBuilder("data")
        mb.add_label(FieldType.Function.SYNC, 16)
        mb.add_label(FieldType.Function.LENGTH, 8)
        mb.add_label(FieldType.Function.SRC_ADDRESS, 8)
        mb.add_label(FieldType.Function.SEQUENCE_NUMBER, 8)
        protocol, expected_labels = AWRExperiments.get_protocol(1,num_messages=5,num_broken_messages=0,silent=True)
        print("protocol")
        for m in protocol.messages:
          print("\t",str(m.plain_bits))
        print("expected_labels")
        for l in expected_labels:
          print("\t"+str(l))
        pg = ProtocolGenerator([mb.message_type],
                               syncs_by_mt={mb.message_type: "0x8e88"},
                               preambles_by_mt={mb.message_type: "10" * 8},
                               participants=[alice, broadcast])

        for i in range(300):
            data_bits = 16 if i % 2 == 0 else 32
            source = pg.participants[i % 2]
            destination = pg.participants[(i + 1) % 2]
            pg.generate_message(data="1010" * (data_bits // 4), source=source, destination=destination)
            print("i",i)

        #self.save_protocol("without_preamble", pg)
        mtx = MessageType("foo")

        for m in pg.messages:
          print("".join([str(b) for b in m.plain_bits]))

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

        for m in pg.messages:
          print(bits2bytes("".join([str(b) for b in m.plain_bits])))
        

        for m in hx.split("\n"):
          print("\t",m,bytes2bits(bits2bytes(bytes2bits(m))))
        
        def awreinfer(hx):
            msgs = bytes2awreinput(hx)
            ff = FormatFinder(msgs)
            ff.run()
            mt = ff.message_types[0]
            for t in mt:
                print("\ttype",t)

        msgs = bytes2awreinput(hx)
        for m in msgs:
          print("x",str(m.plain_bits))
        #self.clear_message_types(pg.messages)
        ff = FormatFinder(msgs)
        #ff.known_participant_addresses.clear()

        ff.run()
        #self.assertEqual(len(ff.message_types), 1)

        mt = ff.message_types[0]
        for t in mt:
          print("type",t)
        
        
        data = """01ff
        02ffee
        01ff
        03ffeedd"""
        awreinfer(data)
