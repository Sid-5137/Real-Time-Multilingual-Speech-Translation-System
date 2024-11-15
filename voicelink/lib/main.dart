import 'package:flutter/material.dart';
import 'package:voicelink/home.dart';
import 'package:voicelink/home_chrome.dart';

void main() {
  runApp(const VoiceLink());
}

class VoiceLink extends StatelessWidget {
  const VoiceLink({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Voice link',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const FileUploadPage(),
    );
  }
}
