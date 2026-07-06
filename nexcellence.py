import nexcellence
import nihonium
import common

bytecode = [
    nexcellence.OpCode.PUSH, nihonium.String("test.txt"),
    nexcellence.OpCode.PUSH, common.FileMode.APP,
    nexcellence.OpCode.OPEN, common.StreamType.FILE,
    nexcellence.OpCode.STORE, 180,
    nexcellence.OpCode.LOAD, 180,
    nexcellence.OpCode.PUSH, nihonium.String("davenavarro"),
    nexcellence.OpCode.PRINT,
    nexcellence.OpCode.LOAD, 180,
    nexcellence.OpCode.CLOSE,
    nexcellence.OpCode.HALT
]

bytecode2 = [
    nexcellence.OpCode.PUSH, nihonium.String("test.txt"),
    nexcellence.OpCode.PUSH, common.FileMode.READ,
    nexcellence.OpCode.OPEN, common.StreamType.FILE,
    nexcellence.OpCode.STORE, 43,
    nexcellence.OpCode.PUSH, 1,

    nexcellence.OpCode.LOAD, 43,
    nexcellence.OpCode.READ,

    nexcellence.OpCode.PRINT
]

vm = nexcellence.VM(nexcellence.parse(bytecode2))
vm.run()

