import os
import json
from prompt import prompts
from groq import Groq
import re
import sys
turnOffSerial = True
optimizeDPA = True
optimizePeriodicTask = True
optimize_fp_math = True

def remove_serial_print(code):
    pattern = r'^[^\/"]*Serial\.(?:print|println)\([^\)]*\);\s*$'
    new_code = list()
    for line in code.split('\n'):
        new_line = line
        matches = re.search(pattern,line)
        if matches:
            new_line = "//"+matches.group()
        new_code.append(new_line)
    code = '\n'.join(new_code)
    return code

def find_all_read_write(code):
    pattern = r'^[^\/"]*digital(Read|Write)\([^)]*\);\s*$'
    code_dict = dict()
    for line_index,line in enumerate(code.split('\n')):
        matches = re.search(pattern,line)
        if matches:
            code_dict[str(line_index)] = dict()
            code_dict[str(line_index)]["Original"] = matches.group()
    return code_dict
    
def Add_DPA_header(code):
    DPA_header = """#define SET_PIN_HIGH(port, pin) (PORT ## port |= (1 << pin))\n#define SET_PIN_LOW(port, pin)((PORT ## port) &= ~(1 << (pin)))\n#define PIN_READ(port, pin) (PIN ## port & (1 << pin))\n"""
    if "#define SET_PIN_HIGH(port, pin) (PORT ## port |= (1 << pin))" not in code:
        code = DPA_header + code
    return code
         
def AIprompting(prompt,token="llama-3.1-70b-versatile"):
    client = Groq(
        api_key="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",
    )
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user", "content": prompt,
            }
        ],
        model=token,
        temperature=0
    )

    return chat_completion.choices[0].message.content
    
def Read_Write_AI_Optimization(code,code_dict,PROMPT,add_3_count):
    DPA_header = """#define SET_PIN_HIGH(port, pin) (PORT ## port |= (1 << pin))\n#define SET_PIN_LOW(port, pin)((PORT ## port) &= ~(1 << (pin)))\n#define PIN_READ(port, pin) (PIN ## port & (1 << pin))\n"""
    prompt = PROMPT.DRDW_optimization_prompt + DPA_header
    for each in code.split("\n"):
        if "#define " in each:
            if not "#define SET_PIN_HIGH(port, pin)" in code and not "#define SET_PIN_LOW(port, pin)" in code and not "#define PIN_READ" in code:
                prompt += each
                prompt += "\n"
    for each in code_dict:
        prompt += "\n"
        prompt += code_dict[each]["Original"]
    results = AIprompting(prompt,"llama3-70b-8192")

    start_flag = False
    count = 0
    keys = list(code_dict.keys())
    Modified_list = list()
    count_end = len(keys)
    for each in results.split("\n"):
        if start_flag == False:
            if "+++" in each:
                start_flag = True
        elif start_flag == True:
            if each != '':
                print(repr(each))
                Modified_list.append(each)
                count = count+1
                if count == count_end:
                    break
    count = 0
    key_list_index = 0
    code = code.split("\n")
    if add_3_count == True:
        for index,each in enumerate(keys):
            keys[index] = str(int(each) + 3) 
    for each in code:
        if str(count) == keys[key_list_index]:
            space_count = len(each) - len(each.lstrip(' '))
            tab_count = len(each) - len(each.lstrip('\t'))
            code[count] = tab_count*'\t' + space_count*' ' + Modified_list[key_list_index]
            key_list_index += 1
            if key_list_index == count_end:
                break
        count += 1
    code = "\n".join(code)
    return code
       
 
