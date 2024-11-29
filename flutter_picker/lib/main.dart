import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:file_selector/file_selector.dart';
import 'package:http_parser/http_parser.dart';

void main() {
  runApp(const MyApp());
}

Future<XFile?> selectFile({List<String> allowedFileTypes = const []}) async {
  final XFile? file = await openFile(
    acceptedTypeGroups: [
      XTypeGroup(
        extensions: allowedFileTypes,
      ),
    ],
  );
  return file;
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'File Upload Example',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const MyHomePage(),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key});

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  final bool _disabled = false;
  bool _selectedFiles = false;
  String? filePath;
  XFile? selectedFile;

  Future<void> _processFiles(List<XFile> files) async {
    for (final XFile file in files) {
      debugPrint('File: ${file.name} (MIME type: ${file.mimeType})');

      // Get bytes from the file
      final Uint8List bytes = await file.readAsBytes();

      // Create a multipart request
      var request = http.MultipartRequest(
          'POST', Uri.parse('http://192.168.1.177:6589/grade'));  
      request.files.add(http.MultipartFile.fromBytes('cppfile', bytes,
          filename: file.name,
          contentType: MediaType('application', 'octet-stream')));

      //below is the example of sending test object with multiline string for this problem: https://open.kattis.com/problems/bigtruck
      //here is the solution for the problem: https://github.com/JonSteinn/Kattis-Solutions/blob/master/src/Big%20Truck/C%2B%2B/main.cpp
      //
      //I understand that you might not have capability for multiline strings directly but you can just include escape characters like \n
      //and program will still run correctly 
      //so we map test input to expected output, please feel free to tag me on discord and ask me to explain if you have any questions

      //last note, use "json_body" as key for the body of the request and "cppfile" as key for the file because these names areused to access the data on server side

      Map<String, String> inputBody = {
        '''6
1 1 2 3 1 0
7
1 2 2
2 3 3
3 6 4
1 4 4
4 3 2
4 5 3
5 6 2
''': '''9 5''',
'2\n5 5\n0': 'impossible',
      };

      request.fields["json_body"] = jsonEncode(inputBody);
      // Send the request
      var response = await request.send();

      // Read the response
      final responseString = await response.stream.bytesToString();

      if (response.statusCode == 200) {
        debugPrint('File uploaded successfully');
        debugPrint(responseString);

        // Decode the JSON response
        final jsonResponse = jsonDecode(responseString);
        final formattedJson =
            const JsonEncoder.withIndent('  ').convert(jsonResponse);
        print('JSON Response: \n$formattedJson');
      } else {
        debugPrint('File upload failed with status: ${response.statusCode}');
        debugPrint(responseString);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    XFile? response;
    return Scaffold(
      appBar: AppBar(
        title: const Text('File Upload Example'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            TextField(
              controller: TextEditingController(text: filePath),
              decoration: const InputDecoration(
                labelText: 'Selected File',
                border: OutlineInputBorder(),
              ),
              readOnly: true,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _disabled ? null : () async => {
                response = await selectFile(allowedFileTypes: ['cpp']),
                setState(() {
                  _selectedFiles = true;
                  filePath = response!.name;
                  selectedFile = response;
                })
              },
              child: const Text('Select File'),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _selectedFiles
                  ? () async => _processFiles([selectedFile!])
                  : null,
              child: const Text('Send File'),
            ),
          ],
        ),
      ),
    );
  }
}


class InputOutputFileRow extends StatefulWidget {
  String? inputFilePath;
  String? outputFilePath;

  InputOutputFileRow({
    super.key,
  });

  @override
  State<InputOutputFileRow> createState() => _InputOutputFileRowState();
}

class _InputOutputFileRowState extends State<InputOutputFileRow> {
  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: TextField(
            controller: TextEditingController(text: widget.inputFilePath),
            decoration: const InputDecoration(
              labelText: "Select Input File",
              border: OutlineInputBorder(),
            ),
            readOnly: true,
          ),
        ),
        const SizedBox(width: 16),
        ElevatedButton(
          onPressed: () async {
            final XFile? response = await selectFile(allowedFileTypes: ['cpp']);
            setState(() {
              widget.inputFilePath = response!.name;
            });
          },
          child: const Text('Select File'),
        ),
      ],
    );
  }
}