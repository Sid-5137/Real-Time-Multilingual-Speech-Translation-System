import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:html' as html;
import 'dart:convert';

class FileUploadPage extends StatefulWidget {
  const FileUploadPage({super.key});

  @override
  _FileUploadPageState createState() => _FileUploadPageState();
}

class _FileUploadPageState extends State<FileUploadPage> {
  html.File? selectedFile;
  String responseMessage = "";
  String translatedText = "";
  String outputFilename = "";
  bool isUploading = false;
  bool isFetching = false;

  void selectFile() {
    final html.FileUploadInputElement uploadInput = html.FileUploadInputElement();
    uploadInput.accept = 'audio/*';
    uploadInput.click();

    uploadInput.onChange.listen((e) {
      final files = uploadInput.files;
      if (files!.isNotEmpty) {
        setState(() {
          selectedFile = files.first;
          responseMessage = "";
          translatedText = "";
          outputFilename = "";
        });
      }
    });
  }

  Future<void> sendFileToFastAPI() async {
    if (selectedFile == null) {
      setState(() {
        responseMessage = "Please select a file first.";
      });
      return;
    }

    setState(() {
      isUploading = true;
    });

    final reader = html.FileReader();
    reader.readAsArrayBuffer(selectedFile!);
    await reader.onLoadEnd.first;

    if (reader.result != null) {
      final Uint8List fileBytes = reader.result as Uint8List;
      final url = Uri.parse("http://localhost:8000/upload/");
      final request = http.MultipartRequest("POST", url)
        ..files.add(http.MultipartFile.fromBytes(
          'file',
          fileBytes,
          filename: selectedFile!.name,
        ));

      try {
        final response = await request.send();
        final responseBody = await response.stream.bytesToString();
        setState(() {
          isUploading = false;
        });

        if (response.statusCode == 200) {
          final jsonResponse = json.decode(responseBody);
          setState(() {
            responseMessage = jsonResponse['message'] ?? "File uploaded successfully.";
            translatedText = jsonResponse['translated_text'] ?? "No translated text.";
            outputFilename = jsonResponse['output_file'] ?? "";
          });
        } else {
          setState(() {
            responseMessage = "File upload failed with status: ${response.statusCode}";
          });
        }
      } catch (e) {
        setState(() {
          isUploading = false;
          responseMessage = "File upload failed with error: $e";
        });
      }
    }
  }

  void playSelectedAudio() {
    if (selectedFile != null) {
      final reader = html.FileReader();
      reader.readAsDataUrl(selectedFile!);
      reader.onLoadEnd.listen((event) {
        final audioElement = html.AudioElement()..src = reader.result as String;
        audioElement.controls = true;
        audioElement.autoplay = true;
        // html.document.body!.append(audioElement);
      });
    }
  }

  Future<void> playOutputAudio() async {
    if (outputFilename.isNotEmpty) {
      setState(() {
        isFetching = true;
      });
      
      final url = Uri.parse(outputFilename);
      // html.document.body!.querySelectorAll("audio").forEach((element) => element.remove());
      try {
        final response = await http.get(url);
        if (response.statusCode == 200) {
          final blob = html.Blob([response.bodyBytes], 'audio/wav');
          final blobUrl = html.Url.createObjectUrlFromBlob(blob);
          final audioElement = html.AudioElement()..src = blobUrl;
          audioElement.controls = true;
          audioElement.autoplay = true;
          // html.document.body!.append(audioElement);
        } else {
          setState(() {
            responseMessage = "Failed to fetch audio file from server.";
          });
        }
      } catch (e) {
        setState(() {
          responseMessage = "Error playing audio file: $e";
        });
      } finally {
        setState(() {
          isFetching = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text("Audio File Upload"),
        backgroundColor: Colors.teal,
        elevation: 0,
        centerTitle: true,
      ),
      body: Center(
        child: Container(
          padding: const EdgeInsets.all(24.0),
          constraints: const BoxConstraints(maxWidth: 500),
          child: Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            elevation: 6,
            child: Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    "Upload and Translate Audio",
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Colors.teal[800],
                    ),
                  ),
                  const SizedBox(height: 20),
                  OutlinedButton.icon(
                    onPressed: selectFile,
                    icon: Icon(Icons.file_upload, color: Colors.teal[700]),
                    label: const Text("Select Audio File"),
                    style: OutlinedButton.styleFrom(
                      side: BorderSide(color: Colors.teal),
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                  ),
                  const SizedBox(height: 20),
                  ElevatedButton.icon(
                    onPressed: isUploading ? null : sendFileToFastAPI,
                    icon: isUploading
                        ? const SizedBox(
                            height: 24,
                            width: 24,
                            child: CircularProgressIndicator(
                              color: Colors.white,
                              strokeWidth: 2,
                            ),
                          )
                        : Icon(Icons.cloud_upload, color: Colors.white),
                    label: const Text("Upload File"),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.teal,
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                  ),
                  const SizedBox(height: 10),
                  if (selectedFile != null)
                    Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: Column(
                        children: [
                          Text(
                            "Selected File: ${selectedFile!.name}",
                            style: TextStyle(color: Colors.grey[700]),
                          ),
                          ElevatedButton.icon(
                            onPressed: playSelectedAudio,
                            icon: Icon(Icons.play_circle_filled, color: Colors.white),
                            label: const Text("Play Selected Audio"),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.green,
                              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                            ),
                          ),
                        ],
                      ),
                    ),
                  const SizedBox(height: 10),
                  if (responseMessage.isNotEmpty)
                    Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: Text(
                        responseMessage,
                        style: TextStyle(color: Colors.teal[700], fontWeight: FontWeight.w600, fontSize: 16),
                        textAlign: TextAlign.center,
                      ),
                    ),
                  if (translatedText.isNotEmpty)
                    Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: Text(
                        "Translated Text: $translatedText",
                        style: TextStyle(color: Colors.deepOrange, fontSize: 16, fontStyle: FontStyle.italic),
                        textAlign: TextAlign.center,
                      ),
                    ),
                  if (outputFilename.isNotEmpty)
                    Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: Column(
                        children: [
                          Text(
                            "Output Audio",
                            style: TextStyle(color: Colors.teal[800], fontSize: 16, fontWeight: FontWeight.bold),
                          ),
                          ElevatedButton.icon(
                            onPressed: isFetching ? null : playOutputAudio,
                            icon: isFetching
                                ? const SizedBox(
                                    height: 24,
                                    width: 24,
                                    child: CircularProgressIndicator(
                                      color: Colors.white,
                                      strokeWidth: 2,
                                    ),
                                  )
                                : Icon(Icons.play_circle, color: Colors.white),
                            label: const Text("Play Output Audio"),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.orange,
                              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                            ),
                          ),
                        ],
                      ),
                    ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
