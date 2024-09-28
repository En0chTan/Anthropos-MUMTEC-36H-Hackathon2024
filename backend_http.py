from flask import Flask, jsonify, request
from flask_cors import CORS
from prompt import prompts
import test
import json
import sys
import os
import re
app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Welcome to the HTTP backend!"

@app.route('/api/optimize', methods=['POST'])
def post_api_data():
    if not request.is_json:
        return jsonify({"error": "Invalid input, expecting JSON"}), 400
    
    data = request.get_json()
    code = data.get("code")
    flags = data.get("flags")
          

    prompt = prompts.REVIEW_PROMPT + prompts.CODE_BEGINS + code + prompts.CODE_ENDS

    # Review the code so that it produces a json output to check if the code can be optimized or not
    options = json.loads(test.AIprompting(prompt))
    used_flags = list()
    for index,each in enumerate(options.values()):
        print(index)
        print(each)
        if index != 0:
            used_flags.append(1 if each == "True" else 0) 
    print(str(used_flags))

    #Turn off program if Not Arduino Code
    if options['Arduino_Code'] == "True":
        pass
    else: 
        return jsonify({"error": "Invalid code"})
        
    if options["optimizeSerial"] == "True":
        code = test.remove_serial_print(code)
        
    if options["optimizeDPA"] == "True":
        add_3_count = False
        if "#define SET_PIN_HIGH(port, pin) (PORT ## port |= (1 << pin))" not in code:
            add_3_count = True
        code_dict = {}
        code_dict = test.find_all_read_write(code)
        if code_dict:
            code = test.Add_DPA_header(code)
            code = test.Read_Write_AI_Optimization(code,code_dict,prompts,add_3_count)
        print(code)
    
    if options["optimizePeriodicTask"] == "True":
        periodic_task_prompt = prompts.PERIODIC_TASK_PROMPT + prompts.CODE_BEGINS + code + prompts.CODE_ENDS
        code = test.AIprompting(periodic_task_prompt)


    if options["optimize_fp_math"] == "True":
        analyze_result = prompts.ANALYZE_FP_MATH +prompts.CODE_BEGINS + prompts.FP_MATH_MACRO  + code + prompts.CODE_ENDS
        analyze_result = test.AIprompting(analyze_result)
        fp_math_prompt = prompts.INT_MATH_PROMPT + analyze_result + prompts.CODE_BEGINS + prompts.FP_MATH_MACRO  + code + prompts.CODE_ENDS
        code = test.AIprompting(fp_math_prompt)
    code = code.split("\n")
    if re.search(r'^\s*```c\s*$',code[0]):
        code.pop(0)
    if re.search(r'^\s*```\s*$',code[-1]):
        code.pop(-1)
    code = "\n".join(code)
    return jsonify({"optimized_code":code, "used_flags":used_flags }), 201

    if code is None:
        return jsonify({"error": "Missing 'code' in request data"}), 400
    return jsonify({"received_code": code, "received_flags": flags}), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

