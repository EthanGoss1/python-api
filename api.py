from flask import Flask, request, Response
from flask_cors import CORS
import tempfile
import os
import subprocess
import json


app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return '<h1>Flask Grader API</h1>'

@app.route('/grade', methods=['POST'])
def grade():
    # whoever is calling this API should send a .cpp file with name 'cppfile', see flutter code for example
    if 'cppfile' not in request.files:
        return Response('Missing .cpp file', status=400, mimetype='text/plain')

    cpp_file = request.files['cppfile']

    #we also expect a json body with inputs:outputs to the program where each entry is a test case, see flutter code for example


    body = json.loads(request.form.get('json_body', '{}'))

    response_obj = {
    }
    failures = []
    with tempfile.TemporaryDirectory() as tempdir:
        cpp_path = os.path.join(tempdir, 'program.cpp')
        exe_path = os.path.join(tempdir, 'program.exe')

        # input_file.save(input_path)
        cpp_file.save(cpp_path)
        compile_process = subprocess.run(['g++', cpp_path, '-o', exe_path], capture_output=True, text=True)
        if compile_process.returncode != 0:
            return Response(f'Compilation failed: {compile_process.stderr}', status=400, mimetype='text/plain')

        
        for input in body:
            expected_output_text = body[input]
            process = subprocess.run([exe_path],
                                  input=input,
                                  text=True,
                                  capture_output=True)
            
            output_of_program = process.stdout            
            if process.returncode != 0:
                return Response(f'Execution failed: {process.stderr}', 
                              status=400, mimetype='text/plain')
            #Allows for error reporting/what happened where
            if output_of_program.strip() != expected_output_text:
                failure = {
                    'input': input,
                    'expected_output': expected_output_text,
                    'output': output_of_program.strip()
                }
                failures.append(failure)
        if failures != []:
            response_obj['failures'] = failures

        #Separated grading logic into another function
        response_obj['grade'] = grading_logic(len(body), failures)

        print(response_obj)
            
    return Response(json.dumps(response_obj), mimetype='application/json', status=200)

def grading_logic(length, failures):
    #If the failures list is empty, return perfect score
    if(failures !=[]):
        correct = length - len(failures)
        #If you got none correct, return 0
        if correct==0:
            return 0.0
        else:
            #Everything in between
            gradePercent = correct/length
            return gradePercent
    else:
        return 1.0
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6589, debug=True)