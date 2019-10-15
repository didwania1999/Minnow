# automatically generated by the FlatBuffers compiler, do not modify

# namespace: motor

import flatbuffers

class command(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAscommand(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = command()
        x.Init(buf, n + offset)
        return x

    # command
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # command
    def Time(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Float64Flags, o + self._tab.Pos)
        return 0.0

    # command
    def Motor1Command(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Float32Flags, o + self._tab.Pos)
        return 0.0

    # command
    def Motor2Command(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Float32Flags, o + self._tab.Pos)
        return 0.0

    # command
    def Motor3Command(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Float32Flags, o + self._tab.Pos)
        return 0.0

def commandStart(builder): builder.StartObject(4)
def commandAddTime(builder, time): builder.PrependFloat64Slot(0, time, 0.0)
def commandAddMotor1Command(builder, motor1Command): builder.PrependFloat32Slot(1, motor1Command, 0.0)
def commandAddMotor2Command(builder, motor2Command): builder.PrependFloat32Slot(2, motor2Command, 0.0)
def commandAddMotor3Command(builder, motor3Command): builder.PrependFloat32Slot(3, motor3Command, 0.0)
def commandEnd(builder): return builder.EndObject()
