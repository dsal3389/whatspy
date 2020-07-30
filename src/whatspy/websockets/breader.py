import struct
import io


class BytesTags:
    LIST_EMPTY      = 0
    STREAM_END      = 2
    DICTIONARY_0    = 236
    DICTIONARY_1    = 237
    DICTIONARY_2    = 238
    DICTIONARY_3    = 239
    LIST_8          = 248
    LIST_16         = 249
    JID_PAIR        = 250
    HEX_8           = 251
    BINARY_8        = 252
    BINARY_20       = 253
    BINARY_32       = 254
    NIBBLE_8        = 255
    SINGLE_BYTE_MAX = 256
    PACKED_MAX      = 254


class ByteReader:
    """
    getting bytes that recved from the whatsapp websocket
    and start decoding them
    """
    
    def __init__(self, bytes):
        self._bytes = bytes
        self.stream = io.BytesIO(self._bytes)
        self.stream.seek(1, io.SEEK_CUR) # skip tag

    def read_node(self):
        list_size = self.size
        description_tag = self.read_next_byte()

        if description_tag == BytesTags.STREAM_END:
            raise ValueError('unexpected stream end')

        # need to implement

    def read_byte(self, position):
        return ord(chr(self._bytes[position]))

    def read_next_byte(self):
        return self.stream.seek(1, io.SEEK_CUR)

    def read_int_16(self): # need to implements
        pass

    @property
    def tag(self):
        return self.read_byte(0)

    @property
    def size(self):
        list_tags = {
            BytesTags.LIST_EMPTY: lambda : None,
            BytesTags.LIST_8 : self.read_next_byte,
            BytesTags.LIST_16: self.read_int_16
        }
        callback = list_tags.get(self.tag, None)

        if not callable(callback):
            raise ValueError('unexpected tag for list size (%s)' %self.tag)
        return callback()


