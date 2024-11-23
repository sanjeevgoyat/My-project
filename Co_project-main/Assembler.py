import sys
registers = {"zero":"00000","ra":"00001","sp":"00010","gp":"00011","tp":"00100","t0":"00101","t1":"00110","t2":"00111","s0":"01000","fp":"01000",
            "s1":"01001","a0":"01010","a1":"01011","a2":"01100","a3":"01101","a4":"01110","a5":"01111","a6":"10000","a7":"10001"
            ,"s2":"10010","s3":"10011","s4":"10100","s5":"10101","s6":"10110","s7":"10111","s8":"11000","s9":"11001",
            "s10":"11010","s11":"11011","t3":"11100","t4":"11101","t5":"11110","t6":"11111"}

errorList = []

R_type = ["add","sub","sll","slt","sltu","xor","srl","or","and"]
I_type = ["lw","addi","sltiu","jalr"]
S_type = ["sw"]
B_type = ["beq","bne","blt","bge","bltu","bgeu"]
U_type = ["lui","auipc"]
J_type = ["jal"]

opcode = {"add":"0110011", "sub":"0110011", "sll":"0110011", "slt":"0110011", "sltu":"0110011", "xor":"0110011", "srl":"0110011", "or":"0110011" ,"and":"0110011", "lw":"0000011", "addi":"0010011", "sltiu":"0010011", "jalr":"1100111", "sw":"0100011", "beq":"1100011", "bne":"1100011", "blt":"1100011", "bge":"1100011", "bltu":"1100011", "bgeu":"1100011", "lui":"0110111", "auipc":"0010111", "jal":"1101111" }

funct3 = {"add":"000", "sub":"000", "sll":"001", "slt":"010", "sltu":"011", "xor":"100", "srl":"101", "or":"110", "and":"111", "lw":"010", "addi":"000", "sltiu":"011", "jalr":"000", "sw":"010", "beq":"000", "bne":"001", "blt":"100", "bge":"101", "bltu":"110", "bgeu":"111" }

funct7 = {"add":"0000000", "sub":"0100000", "sll":"0000000", "slt":"0000000", "sltu":"0000000", "xor":"0000000", "srl":"0000000", "or":"0000000" ,"and":"0000000" }

labels = {}

output_list = []

def labeler(mainfile):
    count = 1
    for temp in mainfile:
        templable = temp.split()
        if ":" in templable:
            errorList.append("typo in lable naming")
            break
        if templable and templable[0].endswith(":"): 
            labels[templable[0][:-1]] = count
        count += 1

def errorDetection(line, TOTAL_lines, count, errorlist):
    if line == "beq zero,zero,0\n" and count != TOTAL_lines:
        errorlist.append("virtual halt is being used as the instruction number " + str(count) + " and not at last instruction")
        return 0
    
    symbols = [" ", ":", "(", ",", ")"]
    for symbol in symbols:
        line = " ".join(line.split(symbol))
    list = line.split()

    instruction = list[0]
    if len(list) == 4:
        if instruction in{"add","sub","slt","sltu","xor","sll","srl","or","and"}:
            rd = list[1]
            rs1 = list[2]
            rs2 = list[3]
            if all(r in registers for r in (rd, rs1, rs2)):
                return 1
            else:
                errorlist.append("Invalid register at line no" + str(count))
        elif instruction in{"lw","sw"}:
            rd = list[1]
            imm = list[2]
            rs1 = list[3]
            if ((all(r in registers for r in (rs1,rd))) and int(imm)>=-2048 and int(imm)<=2047):
                return 1
            elif(int(imm)<-2048 and int(imm)>2047):
                errorlist.append("Immediate number not in the range at line no" + str(count))
            else:
                errorlist.append("Invalid register at line no" + str(count))
        elif instruction in{"addi","sltiu","jalr"}:
            rd = list[1]
            rs = list[2]
            imm = list[3]
            if ((all(r in registers for r in (rs,rd))) and int(imm)>=-2048 and int(imm)<=2047):
                return 1
            elif(int(imm)<-2048 and int(imm)>2047):
                errorlist.append("Immediate number not in the range at line no" + str(count))
            else:
                errorlist.append("Invalid register at line no" + str(count))
        elif instruction in{"beq","bne","bge","bgeu","blt","bltu"}:
            rs1 = list[1]
            rs2 = list[2]
            imm = list[3]
            if imm in labels.keys():
                imm = 4*(labels[imm] - count)
            else:
                if "-" in imm:
                    if imm[1:].isdigit():
                        imm = int(imm)
                    else:
                        errorlist.append("Invalid label at line no" + str(count))
                        return
                elif imm.isdigit():
                    imm = int(imm)
                else:
                    errorlist.append("Invalid label at line no" + str(count))
                    return
            if ((all(r in registers for r in (rs1,rs2))) and int(imm)>=-32768 and int(imm)<=32767):
                return 1
            elif(int(imm)<-32768 and int(imm)>32767):
                errorlist.append("Immediate number not in the range at line no" + str(count))
            else:
                errorlist.append("Invalid register at line no" + str(count))
        else:
            errorlist.append("Typo in instruction name on line NO " + str(count))
            return 0
    if(len(list)==3):
        if instruction in{"auipc","lui","jal"}:
            rd = list[1]
            imm = list[2]
            if imm in labels.keys():
                imm = 4*(labels[imm] - count)
            else:
                if "-" in imm:
                    if imm[1:].isdigit():
                        imm = int(imm)
                    else:
                        errorlist.append("Invalid label at line no" + str(count))
                        return
                elif imm.isdigit():
                    imm = int(imm)
                else:
                    errorlist.append("Invalid label at line no" + str(count))
                    return
            if(rd in registers and int(imm)>=-1048576 and int(imm)<=1048575):
                return 1
            elif(int(imm)<-1048576 and int(imm)>1048575):
                errorlist.append("Immediate number not in the range at line no" + str(count))
            else:
                errorlist.append("Invalid register at line no" + str(count))
        else:
            errorlist.append("Typo in instruction name on line NO " + str(count))
            return 0
        
def deci_to_bin(decimal_num, num_bits):
    decimal_num = int(decimal_num)
    if decimal_num < 0:
        positive_decimal = abs(decimal_num)
        binary_str = bin(positive_decimal)[2:]
        padded_binary_str = binary_str.zfill(num_bits)
        inverted_bits = ''.join('1' if bit == '0' else '0' for bit in padded_binary_str)
        inverted_bits = bin(int(inverted_bits, 2) + 1)[2:]
        return inverted_bits.zfill(num_bits)
    else:
        binary_str = bin(int(decimal_num))[2:]
        return binary_str.zfill(num_bits)

def assembler(instruction_list):
    current_line = 1

    for instruction in instruction_list:
        symbols = [" ", ":", "(", ",", ")"]
        for symbol in symbols:
            instruction = " ".join(instruction.split(symbol))
        ins = instruction.split() 

        if ins[0] in R_type:
            string = ""
            string += funct7[ins[0]]
            string += registers[ins[3]]
            string += registers[ins[2]]
            string += funct3[ins[0]]
            string += registers[ins[1]]
            string += opcode[ins[0]]

            output_list.append(string)
        
        elif ins[0] in I_type:
            if ins[0] == "lw":
                imm = deci_to_bin(ins[2],12)
                string = ""
                string+= imm
                string += registers[ins[3]]
                string += funct3[ins[0]]
                string += registers[ins[1]]
                string += opcode[ins[0]]

            else:
                imm = deci_to_bin(ins[3],12)
                string = ""
                string+= imm
                string += registers[ins[2]]
                string += funct3[ins[0]]
                string += registers[ins[1]]
                string += opcode[ins[0]]

            output_list.append(string)
        
        elif ins[0] in S_type:
            string = ""
            imm = deci_to_bin(ins[2],12)
            string += imm[0:7]
            string += registers[ins[1]]
            string += registers[ins[3]]
            string += funct3[ins[0]]
            string += imm[7:]
            string += opcode[ins[0]]

            output_list.append(string)

        elif ins[0] in B_type:
            imm = ins[3]
            if imm in labels.keys():
                imm =  4*(labels[imm] - current_line)

            imm = deci_to_bin(imm,16)
            string = ""
            string += imm[3] + imm[5:11]
            string += registers[ins[2]]
            string += registers[ins[1]]
            string += funct3[ins[0]]
            string += imm[11:15] + imm[4]
            string += opcode[ins[0]]

            output_list.append(string)

        elif ins[0] in U_type:
            if(int(ins[2])>0):
                imm = deci_to_bin(ins[2],32)
            else:
                imm = deci_to_bin(ins[2],33)
            string = ""
            string += imm[0:20]
            string += registers[ins[1]]
            string += opcode[ins[0]]

            output_list.append(string)

        elif ins[0] in J_type:
            imm = ins[2]
            if imm in labels.keys():
                imm =  4*(labels[imm] - current_line)
            print(imm)
            imm = deci_to_bin(imm, 21)         
            imm_formatted = imm[0] + imm[10:20] + imm[-11] + imm[1:9]
            string = ""  
            string += imm_formatted
            string += registers[ins[1]]  
            string += opcode[ins[0]]  

            output_list.append(string)

        current_line += 1
        

def main():
    inp = sys.argv[1]
    out = sys.argv[2]
    F = open("inp", "r")
    mainfile = []
    for line in F:
        if line != "" and line != "\n":
            mainfile.append(line)

    F.close()

    flag = 1

    labeler(mainfile)
    
    for instruction in mainfile:
        symbols = [" ", ":", "(", ",", ")"]
        for symbol in symbols:
            instruction = " ".join(instruction.split(symbol))
        ins = instruction.split()

        mlabel = ins[0]
        if mlabel in labels.keys():
            mainfile[labels[mlabel]-1] = mainfile[labels[mlabel]-1].replace(mlabel + ": " , "")

    OUT = open("out", "w")
    counter = 1
    if len(mainfile) <= 128:
        for line in mainfile:
            if counter > 128:
                break
            else:
                if len(errorList) > 0:
                    break
                elif "beq zero,zero,0" in mainfile or "beq zero,zero,0\n" in mainfile:
                    flag = errorDetection(line, len(mainfile), counter, errorList)
                    counter += 1
                    if len(errorList) > 0:
                        break

                else:
                    errorList.append("virtual halt is missing")
                    break

        if len(errorList) > 0:
            OUT.write(errorList[0])
            OUT.write("\n")
        else:
            assembler(mainfile)
            for i in output_list:
                OUT.write(i)
                OUT.write("\n")
    else:
        print("NO OF INSTRUCTIONS EXCEED 128")
    OUT.close()


if __name__ == "__main__":
    main()
