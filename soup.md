## global variables
    memory list: each index stores 1 byte of data (initialized to 255  =0xFF); binary
    register list: 32 list (initialized to 0); decimal
    pc counter : counts current instruction

## helper functions
    #function: print final output 
        prints out final register values

    #function: read instr file 
    
    #function: read data file

    #function: convert binary to hexadecimal

    #function: decimal to binary string

    #function: to twos complement


## disassembling functions: adjust PC counter accordingly

    #function: r disassemble
        #instr = add, sub, xor, or, sll, srl, sra, slt

    #function: i disassemble
        #instr = addi, xori, ori, slli, srli, srai, slti, lw, jalr
        #lw --> Load a word (lw) from 0x20000000 : stdin으로 숫자 받아서 rd에 저장
        #jalr --> PC counter + imm value

    #function: s disassemble
        #instr = sw
        #Store a word (sw) to 0x20000000: Print the ascii character corresponds to the stored data the console

    #function: u disassemble
        #instr = auipc, lui
        #lui add extra 12bits at the end (just add them when inputting in registers)

    #function: sb disassemble
        #instr = beq, bne, blt, bge
        #adjust PC counter accordingly (PC counter + imm value)

    #function: j disassemble
        #instr = jal
        #adjust PC counter accordingly (PC counter + imm value)

## main:
    take in arguments (2, 3)
    initialize register list to 0 and memory list to 255 (0xFF) (does memory list not contain any initial values?)

    - PC counter tracks varible starts from 0; used as binary file index

    while n > 0: (n = number of instructions)
        read binary instruction

        disassemble binary instruction & modify registers/memory as needed in the functions
        - lui, auipc, lw, sw --> modifies memory
            - sw: print(chr(value_8bit),end='') prints the ascii chars
            - lw: Wait for the user to enter a number though the console (stdin) (decimal int) --> loaded to rd
        - rest only modifies registers
        - imm value = returned when each instruction is disassembled
    
        if instruction doesn't exist:
            return error message
        
        n--;

    print final register values

#instructions that are needed:
◼ add, sub, addi 
◼ xor, or, and, xori, ori, andi 
◼ slli, srli, srai, sll, srl, sra 
◼ slti, slt
◼ auipc, lui
◼ jal, jalr
◼ beq, bne, blt, bge
◼ lw, sw
