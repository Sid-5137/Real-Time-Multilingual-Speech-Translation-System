import 'dart:io';

import 'package:flutter/material.dart';
import 'package:just_audio/just_audio.dart';
import 'package:path_provider/path_provider.dart';
import 'package:record/record.dart';
import 'package:path/path.dart' as path;

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late AudioRecorder _audioRecorder;
  late AudioPlayer _audioPlayer;
  bool isRecording = false;
  bool isPlaying = false;
  String? recordedPath;

  @override
  void initState() {
    super.initState();
    _audioRecorder = AudioRecorder();
    _audioPlayer = AudioPlayer();
  }

  @override
  void dispose() {
    _audioRecorder.dispose();
    _audioPlayer.dispose();
    super.dispose();
  }

  Future<void> _toggleRecording() async {
    if (isRecording) {
      await _stopRecording();
    } else {
      await _startRecording();
    }
  }

  Future<void> _stopRecording() async {
    String? savedFilePath = await _audioRecorder.stop();
    if (savedFilePath != null) {
      print('Saved file at $savedFilePath');
      setState(() {
        recordedPath = savedFilePath;
        isRecording = false;
      });
    } else {
      print('Error saving file');
    }
  }

  Future<void> _startRecording() async {
    if (await _audioRecorder.hasPermission()) {
      final Directory directory = await getApplicationDocumentsDirectory();
      final filePath = path.join(directory.path, 'voice_link_recoding.wav');
      await _audioRecorder.start(const RecordConfig(), path: filePath);
      setState(() {
        isRecording = true;
        recordedPath = null;
      });
    }
  }

  Future<void> _playAudio() async {
    if (_audioPlayer.playing) {
      await _audioPlayer.stop();
      setState(() {
        isPlaying = false;
      });
    } else {
      await _audioPlayer.setFilePath(recordedPath!);
      await _audioPlayer.play();
      setState(() {
        isPlaying = true;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Voice link'),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () async {
          await _toggleRecording();
        },
        child: Icon(
          isRecording ? Icons.stop : Icons.mic,
        ),
      ),
      body: _getBody(),
    );
  }

  Widget _getBody() {
    return SafeArea(
      child: SizedBox(
        width: MediaQuery.sizeOf(context).width,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            if (recordedPath != null)
              MaterialButton(
                onPressed: () async {
                  await _playAudio();
                },
                color: Theme.of(context).colorScheme.primary,
                child: Text(
                  isPlaying ? 'Stop playing' : 'Start playing',
                  style: const TextStyle(
                    color: Colors.white,
                  ),
                ),
              ),
            if (recordedPath == null) const Text('No recording found'),
          ],
        ),
      ),
    );
  }
}
