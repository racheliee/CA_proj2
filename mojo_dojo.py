import sys

#helper functions ========================================================================
#read instr file
def read_instr_file(file_path):
    binary = []

    with open(file_path, 'rb') as binary_file:
        while True:
            line = binary_file.read(4) #read 4 bytes each 
            if not line:
                break
            decimal_value = int.from_bytes(line, byteorder='little', signed = False) #convert to decimal
            binary_value = format(decimal_value, '032b') # convert back to binary (big endian)
            binary.append(binary_value) #add the binary into the binary_data
    return binary

#read data file 
def read_data_file(file_path):
    binary = {}
    dict_key = 268435456 #0x10000000
    with open(file_path, 'rb') as binary_file:
        while True:
            line = binary_file.read(4) #read 4 byte each
            if not line:
                break
            decimal_value = int.from_bytes(line, byteorder='little', signed = False) #convert to decimal
            binary_value = format(decimal_value, '032b') # convert back to binary (big endian)
            # append 1 byte at a time
            index = 0 
            
            while (index < 32):
                binary[dict_key]= binary_value[index:index+8]
                index += 8
                dict_key += 1

    #filling in the rest with 0xFF
    while(dict_key <= 268500991):
        binary[dict_key] = "11111111"
        dict_key += 1

    return binary

#converts decimal to 32 bit binary string
def convert_to_bin(decimal):
    s = bin(decimal & int("1"*32, 2))[2:]
    return ("{0:0>%s}" % (32)).format(s)

#converts signed binary string to decimal
def to_twos_comp(binary_str, bits):
    val = int(binary_str, 2)
    if (val & (1 << (bits - 1))) != 0: # if sign bit is = 1
        val = val - (1 << bits)        # compute negative value
    return val 

#CHECK IF THIS PRINTS OUT NEGTIAVE VALUES CORRECTLY
#prints final value of the registers in hexadecimal
def print_final_registers(register):
    for i in range(len(register)):
        print("x" + str(i) + ": 0x" + format((register[i] & ((1 << 32)-1)), "08x")) #prints register value in hex padded to match 8 digits

#instruction disassembly =================================================================
#R Format
def r_format_disassemble(binary_instr):
    funct7 = binary_instr[:7]
    funct3 = binary_instr[17:20]
    rs1 = int(binary_instr[12:17], 2)
    rs2 = int(binary_instr[7:12], 2)
    rd = int(binary_instr[20:25], 2)
    opcode = binary_instr[25:]

    global register
    global pc_counter

    binary_rs2 = convert_to_bin(register[rs2])
    if opcode == '0110011':
        if funct7 == '0000000':
            if funct3 == '000': #add
                register[rd] = register[rs1] + register[rs2]
                print("add x{}, x{}, x{}".format(rd, rs1, rs2))
            elif funct3 == '001': #sll 
                #shift using only lower 5 bits
                register[rd] = register[rs1] << int(convert_to_bin(register[rs2])[-5:], 2)
                print("sll x{}, x{}, x{}".format(rd, rs1, rs2))
            elif funct3 == '010': #slt 
                #test case 3 seems to be the opposite
                #test case 3 works with register[rs1] > register[rs2]
                register[rd] = 1 if register[rs1] < register[rs2] else 0
                print("slt x{}, x{}, x{}".format(rd, rs1, rs2))
            elif funct3 == '100': #xor
                register[rd] = register[rs1] ^ register[rs2]
                print("xor x{}, x{}, x{}".format(rd, rs1, rs2))
            elif funct3 == '101': #srl
                if register[rs1] >= 0:
                    register[rd] = register[rs1] >> int(binary_rs2[-5:], 2)
                else:
                    register[rd] = (register[rs1]+ 0x100000000) >> int(binary_rs2[-5:], 2)
                print("srl x{}, x{}, x{}".format(rd, rs1, rs2))
            elif funct3 == '110': #or
                register[rd] = register[rs1] | register[rs2]
                print("or x{}, x{}, x{}".format(rd, rs1, rs2))
            elif funct3 == '111': #and
                register[rd] = register[rs1] & register[rs2]
                print("and x{}, x{}, x{}".format(rd, rs1, rs2))
        elif funct7 == '0100000':
            if funct3 == '000': #sub
                register[rd] = register[rs1] - register[rs2]
                print("sub x{}, x{}, x{}".format(rd, rs1, rs2))
            if funct3 == '101': #sra
                register[rd] = register[rs1] >> int(binary_rs2[-5:], 2)
                print("sra x{}, x{}, x{}".format(rd, rs1, rs2))
    
    pc_counter += 1
    return 

#I Format
def i_format_disassemble(binary_instr):
    funct3 = binary_instr[17:20]
    immediate = to_twos_comp(binary_instr[:12], len(binary_instr[:12]))
    rs1 = int(binary_instr[12:17], 2)
    rd = int(binary_instr[20:25], 2)
    opcode = binary_instr[25:]

    global register
    global data_file   
    global pc_counter

    if opcode == '0000011' and funct3 == '010': #lw
        if rs1 == 536870912: #0x20000000 saves user input
            register[rd] = input()
        else:
            index = register[rs1] + immediate #index of the data_file
            register[rd] = to_twos_comp(data_file[index] + data_file[index+1] + data_file[index+2] + data_file[index+3], 32)
        print("lw x{}, {}(x{})".format(rd, immediate, rs1))
        pc_counter += 1
    elif opcode == '0010011':
        if funct3 == '000': #addi
            register[rd] = register[rs1] + immediate
            print("addi x{} x{} {}".format(rd, rs1, immediate))
        elif funct3 == '010': #slti
            register[rd] = 1 if register[rs1] < immediate else 0
            print("slti x{} x{} {}".format(rd, rs1, immediate))
        elif funct3 == '100': #xori
            register[rd] = register[rs1] ^ immediate
            print("xori x{} x{} {}".format(rd, rs1, immediate))
        elif funct3 == '110': #ori
            register[rd] = register[rs1] | immediate
            print("ori x{} x{} {}".format(rd, rs1, immediate))
        elif funct3 == '111': #andi
            register[rd] = register[rs1] & immediate
            print("andi x{} x{} {}".format(rd, rs1, immediate))

        shamt = int(binary_instr[7:12], 2) #rs2 location
        binary_shamt = convert_to_bin(shamt)
        if binary_instr[:7] == '0000000':
            if funct3 == '001': #slli
                register[rd] = register[rs1] << int(binary_shamt[-5:], 2)
                print("slli x{}, x{}, {}".format(rd, rs1, int(binary_shamt[-5:], 2)))
            if funct3 == '101': #srli
                if register[rs1] >= 0:
                    register[rd] = register[rs1] >> int(binary_shamt[-5:], 2)
                else:
                    register[rd] = (register[rs1]+ 0x100000000) >> int(binary_shamt[-5:], 2)
                print("srli x{}, x{}, {}".format(rd, rs1, shamt))
        if binary_instr[:7] == '0100000': 
            if funct3 == '101': #srai
                register[rd] = register[rs1] >> int(binary_shamt[-5:], 2)
            print("srai x{}, x{}, {}".format(rd, rs1, shamt))
        
        pc_counter += 1
    elif opcode == '1100111' and funct3 == '000': #jalr 
        #R[rd] = PC + 4
        #PC = (R[rs1] + SignExt(imm12)) & (~1) for alignment purposes
        register[rd] = (pc_counter + 1)*4
        pc_counter = (int(register[rs1]/4) + int(immediate/4)) #
        print("jalr x{}, x{}, {}".format(rd, rs1, immediate))
    
    return

#S Format
def s_format_disassemble(binary_instr):
    rs2 = int(binary_instr[7:12], 2)
    rs1 = int(binary_instr[12:17], 2)
    immediate = to_twos_comp(binary_instr[:7] + binary_instr[20:25], len(binary_instr[:7] + binary_instr[20:25]))

    global register
    global data_file   
    global pc_counter

    index = register[rs1] + immediate
    value = convert_to_bin(register[rs2])
    if binary_instr[17:20] == '010': #sw; binary_instr[17:20] = funct3
        #store word to data_file 
        i = 0
        while (i < 32):
            data_file[index] = value[i:i+8]
            index += 1
            i += 8
        print("sw x{}, {}(x{})".format(rs2, immediate, rs1))
        
    pc_counter += 1
    return 

#SB Format
def sb_format_disassemble(binary_instr):
    funct3 = binary_instr[17:20]
    rs2 = int(binary_instr[7:12], 2)
    rs1 = int(binary_instr[12:17], 2)
    immediate = binary_instr[:1] + binary_instr[24:25] + binary_instr[1:7]+ binary_instr[20:24] + "0"
    immediate = to_twos_comp(immediate, len(immediate))

    global register 
    global pc_counter

    if funct3 == '000': #beq
        if(register[rs1] == register[rs2]):
            pc_counter += int(immediate/4)
        else:
            pc_counter += 1
        print("beq x{}, x{}, {}".format(rs1, rs2, immediate))
    elif funct3 == '001': #bne
        print("before " + str(pc_counter))
        if(register[rs1] != register[rs2]):
            pc_counter += int(immediate/4)
        else:
            pc_counter += 1
        print("bne x{}, x{}, {}".format(rs1, rs2, immediate))
        print("after " + str(pc_counter))
    elif funct3 == '100': #blt
        if(register[rs1]< register[rs2]):
            pc_counter += int(immediate/4)
        else:
            pc_counter += 1
        print("blt x{}, x{}, {}".format(rs1, rs2, immediate))
    elif funct3 == '101': #bge
        if(register[rs1] >= register[rs2]):
            pc_counter += int(immediate/4)
        else:
            pc_counter += 1
        print("bge x{}, x{}, {}".format(rs1, rs2, immediate))

    return 

#UJ Format
def uj_format_disassemble(binary_instr):
    rd = int(binary_instr[20:25], 2)    
    immediate = binary_instr[0] + binary_instr[12:20] + binary_instr[11] + binary_instr[1:11] + "0"
    immediate = to_twos_comp(immediate, len(immediate))

    global register
    global data_file   
    global pc_counter

    #jal rd, imm
    #R[rd] = PC + 4
    #PC = PC + SignExt(imm20 << 1)
    register[rd] = (pc_counter + 1)* 4
    pc_counter += int(immediate/4)
    print("jal x{}, {}".format(rd, immediate))

    return 

#U Format
def u_format_disassemble(binary_instr):
    rd = int(binary_instr[20:25], 2)
    immediate = binary_instr[:20] + '000000000000'
    immediate = to_twos_comp(immediate, len(immediate))
    opcode = binary_instr[25:]
    
    global register
    global pc_counter

    if opcode == '0110111': #lui
        register[rd] = immediate 
        print("lui x{}, {}".format(rd, immediate))
        pc_counter += 1
    elif opcode == '0010111': #auipc
        #auipc rd, D[31:12]+D[11] addi rd, rd, D[11:0]
        #Load absolute address where D = symbol – pc
        print("auipc x{}, {}".format(rd, immediate))

    return 

#main ====================================================================================

#taking in the arguments
instr_file = read_instr_file(sys.argv[1]) #takes in the instruction binary file as first input
second_arg = sys.argv[2] #takes in the second argument

#takes in number of instructions to run and initializes binary data file
if(len(sys.argv) == 3):
    n = int(second_arg)
    i = 268435456 #0x10000000
    data_file = {} #dictionary; keys are in decimal
    while (i <= 268500991): #0x1000FFFF
        data_file[i] = "11111111" #initialized to 0xFF
        i += 1
else:
    data_file = read_data_file(second_arg) 
    n = int(sys.argv[3])

register = [0] * 32 #registers initialized to 0; decimal values

pc_counter = 0 #points to the current instruction being read in the instr_file

#loop until n instructions are executed and there are instructions left to be read
while (n > 0):
    n -= 1
    if(pc_counter >= len(instr_file)): #if the pc_counter is trying to read more instructions than there are, break
        break
    binary_instr = instr_file[pc_counter] #binary instruction being read at the moment
    opcode = binary_instr[25:]

    if opcode == "0110011": # r-format disassemble
        r_format_disassemble(binary_instr) 
    if opcode == "0000011" or opcode == "0010011" or opcode == "1100111":  # i-format diassemble
        assembly_code = i_format_disassemble(binary_instr)
    if opcode == "0100011": # s-format disassemble
        assembly_code = s_format_disassemble(binary_instr)
    if opcode == "1100011": # sb-format disassemble
        assembly_code = sb_format_disassemble(binary_instr)
    if opcode == "1101111": # uj-format disassemble
        assembly_code = uj_format_disassemble(binary_instr)
    if opcode == "0110111" or opcode == "0010111": # u-format disassemble
        assembly_code = u_format_disassemble(binary_instr)    
   
    register[0] = 0 #since x0 = 0 always

print_final_registers(register); #print final output