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
    nexcellence.OpCode.OPEN, common.StreamType.FILE, "test.txt", common.FileMode.WRITE,
    nexcellence.OpCode.READ, 3,

    nexcellence.OpCode.PRINT, 1
]

vm = nexcellence.VM(nexcellence.parse(bytecode2))
vm.run()

