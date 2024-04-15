import re

destination = {
    None: 0,
    'M': 1,
    'D': 2,
    'MD': 3, 'DM': 3,
    'A': 4,
    'AM': 5, 'MA': 5,
    'AD': 6, 'DA': 6,
    'ADM': 7, 'AMD': 7,
    'DAM': 7, 'DMA': 7,
    'MAD': 7, 'MDA': 7,
}

jump = {
    None: 0,
    'JGT': 1,
    'JEQ': 2,
    'JGE': 3,
    'JLT': 4,
    'JNE': 5,
    'JLE': 6,
    'JMP': 7,
}

comp1 = {
    '0': 0b0101010,
    '1': 0b0111111,
    '-1': 0b0111010,
    'D': 0b0001100,
    'A': 0b0110000,
    '!D': 0b0001101,
    '!A': 0b0110011,
    '-D': 0b0001111,
    '-A': 0b0110011,
    'D+1': 0b0011111,
    'A+1': 0b0110111,
    'D-1': 0b0001110,
    'A-1': 0b0110010,
    'D+A': 0b0000010,
    'D-A': 0b0010011,
    'A+D': 0b0000010,
    'A-D': 0b0000111,
    'D&A': 0b0000000,
    'D|A': 0b0010101,
    'A|D': 0b0010101,
    'M': 0b1110000,
    '!M': 0b1110001,
    '-M': 0b1110011,
    'M+1': 0b1110111,
    'M-1': 0b1110010,
    'D+M': 0b1000010,
    'M+D': 0b1000010,
    'D-M': 0b1010011,
    'M-D': 0b1000111,
    'D&M': 0b1000000,
    'M&D': 0b1000000,
    'D|M': 0b1010101,
    'M|D': 0b1010101,
}

symbol_table = {
    'SP': 0,
    'LCL': 1,
    'ARG': 2,
    'THIS': 3,
    'THAT': 4,
    'R0': 0,
    'R1': 1,
    'R2': 2,
    'R3': 3,
    'R4': 4,
    'R5': 5,
    'R6': 6,
    'R7': 7,
    'R8': 8,
    'R9': 9,
    'R10': 10,
    'R11': 11,
    'R12': 12,
    'R13': 13,
    'R14': 14,
    'R15': 15,
    'SCREEN': 16384,
    'KBD': 24576,
}
var_addr = 16
instr_addr = 0
lines = []


def citaj_asm(subor, instr_addr, lines):
    print("-----1.cast-----")
    try:
        with open(subor, "r") as f:
            for line in f:
                line = line.strip()  # Odstránime bielé znaky zo začiatku a konca riadku

                comment_r = re.compile(
                    r'/.*$')  # / je zaciatok reg. vyrazu,.* je akykol. pocet akyc. znakov,$ je koniec riadka
                source_code_instr = comment_r.sub("//", line)  # nahradi // za line
                source_code_instr = re.sub('/', '', source_code_instr)
                line = source_code_instr

                if not line:  # Ak je riadok prázdny, preskočíme ho
                    continue

                # Hladanie navestia
                if source_code_instr[0] == "(":  # Ak je to navestie
                    record_found = False
                    for key in symbol_table.items():  # Hladanie a porovnavanie zaznamu v tabulke s riadkom assemblera
                        if source_code_instr[1:-1] == key[0]:
                            record_found = True
                            if source_code_instr[0:] == "(" + key[0] + ")":  # hladanie duplicitneho labelu
                                raise Exception("Nastala chyba, bol najdeny duplicitny LABEL!")

                    if not record_found:  # Ak sa nenasiel zaznam v tabulke, tak sa prida
                        symbol_table.update({
                            source_code_instr[1:-1]: instr_addr,
                        })
                else:  # Ak aktualny riadok nie je navestie, tak...
                    instr_addr += 1  # Inkrementacia adresy instukcie
                    lines.append(source_code_instr.strip())  # Pridanie aktualneho riadku do zoznamu pre dalsi krok


    except FileNotFoundError:
        print(f"Súbor '{subor}' nebol nájdený.")

    return lines


def citaj_asm1(var_addr, lines):
    print("-----2.cast-----")
    for i, line in enumerate(lines):
        source_code_instr = re.sub(r'\s+', '', line)
        # print(source_code_instr)
        if source_code_instr[0] == "@":  # Ak ideme vyberat adresu, tak...
            # print(source_code_instr)
            found_in_table = False  # Predpoklame ze je vyber pamete je nenajdeny v tabulke
            for key in symbol_table.items():
                if source_code_instr[1:] == key[0]:
                    found_in_table = True
            if not found_in_table:  # Ak je vyber pamete nenajdeny v tabulke, tak
                je_cislo = bool(re.match(r"^\d+$", source_code_instr[1:]))  # Overenie ci je to celociselne cislo
                # print(source_code_instr[1:])
                if je_cislo:
                    pass
                else:  # Ak to nie je celociselne cislo, tak pridaj klucive slovo : a adresu v pamati do tabulky
                    symbol_table.update({
                        source_code_instr[1:]: var_addr,
                    })
                    var_addr += 1  # Zvacsi adresu volnej pamate o jedna
        if source_code_instr[0] == "(":  # Ak je to navestie, odstran cely riadok
            del lines[i]
    return lines


def prekladC1(lines):
    code = []
    print("-----3.cast-----")
    for i, line in enumerate(lines):
        inTable = False
        source_code_instr = re.sub(r'\s+', '', line)
        # print(source_code_instr)
        if source_code_instr[0] == "@":  # Ak je to vyber adresy, tak...
            for key in symbol_table.items():
                if source_code_instr[1:] == key[0]:  # zhoda (slova) adresy s tabulkou
                    inTable = True
                    length = len("{0:b}".format(key[1]))  # Nacitanie hodnoty z tabulky
                    addbits = 16 - length  # Dopocitanie dlzky kolko bitov sa ma pridat
                    bits = "{0:b}".format(key[1])
                    padded_binary_string = '0' * addbits + bits
                    # print(padded_binary_string)
                    code.append(padded_binary_string)
            if inTable == False:  # Nie je v tabulke, vyber adresy pomocou cisla
                length = len("{0:b}".format(int(source_code_instr[1:])))
                addbits = 16 - length
                bits = "{0:b}".format(int(source_code_instr[1:]))
                padded_binary_string = '0' * addbits + bits
                code.append(padded_binary_string)
            # print("pridana instrukcia: "+padded_binary_string)

        if source_code_instr[0] != "@":  # Ak instukcia nie je vyber adresy
            padded_binary_string = '1' * 3  # Skladanie instrukcie, prve 3 bity zprava su 1

            # lengthOfInstruction = len(source_code_instr)-1
            # print("dlzka riadku je: "+str (len(source_code_instr)))

            comp_temp = ""  # Bude obsahovat Assembler kod na riadku
            for i in source_code_instr:  # Sluzi na urcenie source code instrukcie na danom riadku
                if i == ";":  # Ak sa najde bodkociarka, tak...
                    break  # Vyhod z cyklu
                if i == "=":  # Ak sa najde rovna sa, tak...
                    comp_temp = ""  # Nastav na prazdnu comp_temp
                    i = ""  # Vynuluj dany charakter precitany z "source_code_instr"
                comp_temp = comp_temp + i

            # print("comptemp " + compTemp + " ")
            # print(instruction)
            comp_size = 7  # Pocet bitov v instrukcii casti comp_code
            padded_binary_string_after_comp = ""
            for cmpKey, cmpValue in comp1.items():
                if cmpKey == comp_temp:
                    ax = len(str("{0:b}".format(cmpValue)))
                    padded_binary_string_after_comp = '0' * (comp_size - ax) + str("{0:b}".format(cmpValue))
                    # print("cmpValue: "+padded_binary_string_after_comp)
            if len(padded_binary_string_after_comp) < comp_size:
                padded_binary_string_after_comp = "0000000"

            dest_temp = ""
            # lengthOfInstruction = len(source_code_instr)-1
            has_destination = False
            for i in source_code_instr:
                if i == "=":
                    has_destination = True

            for i in source_code_instr:
                if i != "=" and has_destination:
                    dest_temp = dest_temp + i
                else:
                    break

            # print("destTemp: "+destTemp)

            dest_size = 3  # Pocet bitov v instrukcii casti dest_size
            padded_binary_string_after_destination = ""
            for destKey, destValue in destination.items():
                if destKey == dest_temp:
                    ax = len(str("{0:b}".format(destValue)))
                    padded_binary_string_after_destination = '0' * (dest_size - ax) + str("{0:b}".format(destValue))
            if len(padded_binary_string_after_destination) < dest_size:
                padded_binary_string_after_destination = "000"

            cond_tempc = ""  # Bude obsahovat podmienku
            next_is_condition = False
            # lengthOfInstruction = len(source_code_instr)-1
            for i in source_code_instr:
                if next_is_condition:
                    cond_tempc = cond_tempc + i
                if i != ";":
                    pass
                elif i == ";":  # Ak je dany charakter bodkociarka, tak...
                    next_is_condition = True  # True znamena -> Dalsi nacitany "char" bude zaciatok instrukcie
            # print("jmpTemp: "+jmpTemp)

            jmp_size = 3  # Pocet bitov v instrukcii casti jmp_size
            padded_binary_string_after_jmp = ""
            for jmpKey, jmpValue in jump.items():
                if jmpKey == cond_tempc:
                    ax = len(str("{0:b}".format(jmpValue)))
                    padded_binary_string_after_jmp = '0' * (jmp_size - ax) + str("{0:b}".format(jmpValue))
                    # print("jmpValue: " + padded_binary_string_after_jmp)
            if len(padded_binary_string_after_jmp) < jmp_size:
                padded_binary_string_after_jmp = "000"
            # Vysledne skladanie instukcie
            c_instruction = padded_binary_string + padded_binary_string_after_comp + padded_binary_string_after_destination + padded_binary_string_after_jmp
            # Pridanie instrukcie do zoznamu
            code.append(c_instruction)

    return code

# Volanie metod
obsah = citaj_asm("PongL.asm", instr_addr, lines)
obsah1 = citaj_asm1(var_addr, obsah)
obsah2 = prekladC1(obsah)

print("XXXX_zaciatok_vypisu_instrukcii_XXXXX")
for fin in obsah2:
    print(fin)
    pass
with open("vystupny_subor.hack", "w") as f:
    for fin in obsah2:
        f.write(str(fin) + "\n")
