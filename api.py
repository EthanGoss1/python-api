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

        #If the use case people want an actual grade:
        tally=len(body)
        correct_amt = 0
        
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
            if output_of_program.strip() == expected_output_text:
                correct_amt+=1
            else:
                failures.append(input)
        if tally!=0:    
            grade=correct_amt/tally #Calculates the grade as a decimal percentage if needed
        else:
            grade=0
        
        if failures != []:
            response_obj['failures'] = failures

        response_obj['grade'] = grade

        print(response_obj)
            
    return Response(json.dumps(response_obj), mimetype='application/json', status=200)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6589, debug=True)