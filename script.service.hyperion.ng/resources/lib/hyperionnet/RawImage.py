# automatically generated by the FlatBuffers compiler, do not modify

# namespace: hyperionnet

import flatbuffers

class RawImage(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAsRawImage(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = RawImage()
        x.Init(buf, n + offset)
        return x

    # RawImage
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # RawImage
    def Data(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(flatbuffers.number_types.Uint8Flags, a + flatbuffers.number_types.UOffsetTFlags.py_type(j * 1))
        return 0

    # RawImage
    def DataAsNumpy(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.GetVectorAsNumpy(flatbuffers.number_types.Uint8Flags, o)
        return 0

    # RawImage
    def DataLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # RawImage
    def Width(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int32Flags, o + self._tab.Pos)
        return -1

    # RawImage
    def Height(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int32Flags, o + self._tab.Pos)
        return -1

def RawImageStart(builder): builder.StartObject(3)
def RawImageAddData(builder, data): builder.PrependUOffsetTRelativeSlot(0, flatbuffers.number_types.UOffsetTFlags.py_type(data), 0)
def RawImageStartDataVector(builder, numElems): return builder.StartVector(1, numElems, 1)
def RawImageAddWidth(builder, width): builder.PrependInt32Slot(1, width, -1)
def RawImageAddHeight(builder, height): builder.PrependInt32Slot(2, height, -1)
def RawImageEnd(builder): return builder.EndObject()
