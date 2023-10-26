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

#read data file (saved in binary little endian)
def read_data_file(file_path):
    binary = []

    with open(file_path, 'rb') as binary_file:
        while True:
            line = binary_file.read(1) #read 1 byte each
            if not line:
                break
            binary.append(line)
    return binary

#converts decimal to binary string
def convert_to_bin(decimal):
    return format(decimal, '032b') #binary string value returned

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

    if opcode == '0110011':
        if funct7 == '0000000':
            if funct3 == '000': #add
                register[rd] = register[rs1] + register[rs2]
            elif funct3 == '001': #sll 
                #shift using only lower 5 bits
                register[rd] = register[rs1] * pow(2, int(convert_to_bin(register[rs2])[-5:], 2))  
            elif funct3 == '010': #slt 
                register[rd] = 1 if register[rs1] < register[rs2] else 0
            elif funct3 == '100': #xor
                register[rd] = register[rs1] ^ register[rs2]
            elif funct3 == '101': #srl
                if register[rs1] >= 0:
                    register[rd] = register[rs1] >> register[rs2]
                else:
                    register[rd] = (register[rs1]+ 0x100000000) >> register[rs2]
            elif funct3 == '110': #or
                register[rd] = register[rs1] | register[rs2]
            elif funct3 == '111': #and
                register[rd] = register[rs1] & register[rs2]
        elif funct7 == '0100000':
            if funct3 == '000': #sub
                register[rd] = register[rs1] - register[rs2]
            if funct3 == '101': #sra
                register[rd] = register[rs1] >> register[rs2]
    
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
            index = register[rs1] + immediate
            register[rd] = to_twos_comp(data_file[index+3] + data_file[index+2] + data_file[index+1] + data_file[index], 32)
            #OUT OF BOUNDS check
        pc_counter += 1
    elif opcode == '0010011':
        if funct3 == '000': #addi
            register[rd] = register[rs1] + immediate
        elif funct3 == '010': #slti
            register[rd] = 1 if register[rs1] < immediate else 0
        elif funct3 == '100': #xori
            register[rd] = register[rs1] ^ immediate
        elif funct3 == '110': #ori
            register[rd] = register[rs1] | immediate
        elif funct3 == '111': #andi
            register[rd] = register[rs1] & immediate

        shamt = int(binary_instr[7:12]) #rs2 location
        if binary_instr[:7] == '0000000':
            if funct3 == '001': #slli
                register[rd] = register[rs1] * pow(2, int(convert_to_bin(shamt)[-5:], 2))  
            if funct3 == '101': #srli
                if register[rs1] >= 0:
                    register[rd] = register[rs1] >> shamt
                else:
                    register[rd] = (register[rs1]+ 0x100000000) >> shamt
        if binary_instr[:7] == '0100000': 
            if funct3 == '101': #srai
                register[rd] = register[rs1] >> shamt
        
        pc_counter += 1
    elif opcode == '1100111' and funct3 == '000': #jalr 
        #R[rd] = PC + 4
        #PC = (R[rs1] + SignExt(imm12)) & (~1) for alignment purposes
        register[rd] = pc_counter + 1
        pc_counter = (register[rs1] + immediate/4) & (~1) #check up on the divide by 4
    

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
    if binary_instr[17:20] == '010': #sw; binary_instr[17:20] = funct3
        value = convert_to_bin(register[rs2])
        temp = len(value);
        #store word to data_file in little endian
        while (temp > 0):
            data_file[index] = value[temp-8:temp]
            index += 1
            temp -= 8
        
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
    global data_file   
    global pc_counter

    if funct3 == '000': #beq
        instruction = 'beq'
    elif funct3 == '001': #bne
        instruction = 'bne'
    elif funct3 == '100': #blt
        instruction = 'blt'
    elif funct3 == '101': #bge
        instruction = 'bge'

    pc_counter += 1

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
        pc_counter += 1
    elif opcode == '0010111': #auipc
        assembly = 'auipc x' + str(rd) + ', ' + str(immediate)

    
    return 

#main ====================================================================================

#taking in the arguments
instr_file = read_instr_file(sys.argv[1]) #takes in the instruction binary file as first input
second_arg = sys.argv[2] #takes in the second argument

#takes in number of instructions to run and initializes binary data file
if(len(sys.argv) == 3):
    n = int(second_arg)
    data_file = ["11111111"] * 65536 #initialized to 0xFF; binary values
else:
    data_file = read_data_file(second_arg) 
    n = sys.argv[3] 
    
register = [0] * 32 #registers initialized to 0; decimal values

pc_counter = 0 #points to the current instruction being read in the instr_file

#loop until n instructions are executed
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