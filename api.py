from flask import Flask, jsonify, request, Response
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
    if 'cppfile' not in request.files:
        return Response('Missing .cpp file', status=400, mimetype='text/plain')

    cpp_file = request.files['cppfile']

    body = json.loads(request.form.get('json_body', '{}'))

    response_obj = {
        "out": ''
    }
    print('Grading...')
    print(body)

    with tempfile.TemporaryDirectory() as tempdir:
        cpp_path = os.path.join(tempdir, 'program.cpp')
        exe_path = os.path.join(tempdir, 'program.exe')

        # input_file.save(input_path)
        cpp_file.save(cpp_path)

        compile_process = subprocess.run(['g++', cpp_path, '-o', exe_path], capture_output=True, text=True)
        if compile_process.returncode != 0:
            return Response(f'Compilation failed: {compile_process.stderr}', status=400, mimetype='text/plain')
        
        print('compiled')

        for input in body:
            input_text = body[input]
            print(input)
            print(input_text)
            process = subprocess.run([exe_path],
                                  input=input,
                                  text=True,
                                  capture_output=True)
            
            print(f'process code: {process.returncode}')

            if process.returncode != 0:
                return Response(f'Execution failed: {process.stderr}', 
                              status=400, mimetype='text/plain')
            print('finished executing for input')
            response_obj = {
                "out": process.stdout
            }
    return Response(json.dumps(response_obj), mimetype='application/json', status=200)

    # return f'<h2>Grading...</h2><br/><p></p>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6589, debug=True)