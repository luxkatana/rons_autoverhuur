import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:google_mlkit_text_recognition/google_mlkit_text_recognition.dart';

class LoginPage extends StatefulWidget {
  final Function(String email) onLogin;

  const LoginPage({super.key, required this.onLogin});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();

  bool _obscurePassword = true;

  File? idImage;
  String extractedText = "";

  /// 🔐 SHOW ADMIN BUTTON
  bool _showAdminButton = false;

  /// 🔐 MULTI-TOUCH STATE
  int _activePointers = 0;
  bool _twoFingerHold = false;
  Timer? _holdTimer;
  double _totalMoveX = 0;

  bool isValidEmail(String email) {
    final emailRegex =
    RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$');
    return emailRegex.hasMatch(email);
  }

  /// 📅 Extract dates
  List<DateTime> extractDates(String text) {
    final matches = RegExp(r'(\d{2})[-/\.](\d{2})[-/\.](\d{4})')
        .allMatches(text);

    List<DateTime> dates = [];

    for (var m in matches) {
      try {
        dates.add(DateTime(
          int.parse(m.group(3)!),
          int.parse(m.group(2)!),
          int.parse(m.group(1)!),
        ));
      } catch (_) {}
    }
    return dates;
  }

  /// 🔍 Validate licence
  bool isValidDrivingLicence(String text) {
    text = text.toUpperCase();

    final hasKeyword = [
      "DRIVING",
      "LICENCE",
      "LICENSE",
      "RIJBEWIJS",
      "PERMIS",
      "FUHRERSCHEIN",
      "LICENCIA"
    ].any((k) => text.contains(k));

    final hasName =
        text.contains("NAME") ||
            text.contains("NAAM") ||
            text.contains("NOM");

    final hasNumber =
    RegExp(r'\d{6,}').hasMatch(text);

    final dates = extractDates(text);
    final hasDates = dates.length >= 2;

    bool expired = false;
    if (dates.isNotEmpty) {
      dates.sort((a, b) => a.compareTo(b));
      if (dates.last.isBefore(DateTime.now())) {
        expired = true;
      }
    }

    return hasKeyword &&
        hasName &&
        hasNumber &&
        hasDates &&
        !expired &&
        text.length > 100;
  }

  /// 📷 Scan
  Future<bool> scanLicenceAndValidate() async {
    try {
      final picker = ImagePicker();
      final picked =
      await picker.pickImage(source: ImageSource.camera);

      if (picked == null) return false;

      setState(() => idImage = File(picked.path));

      final inputImage = InputImage.fromFile(idImage!);
      final textRecognizer =
      TextRecognizer(script: TextRecognitionScript.latin);

      final result =
      await textRecognizer.processImage(inputImage);

      textRecognizer.close();

      extractedText =
          result.blocks.map((b) => b.text).join(' ');

      final valid =
      isValidDrivingLicence(extractedText);

      if (!valid) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
              content: Text("Invalid or expired licence")),
        );
        return false;
      }

      return true;
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Scan error: $e")),
      );
      return false;
    }
  }

  /// 🔐 LOGIN
  Future<void> _login() async {
    if (!_formKey.currentState!.validate()) return;

    final ok = await scanLicenceAndValidate();
    if (!ok) return;

    widget.onLogin(_emailController.text.trim());
    Navigator.pop(context);
  }

  /// 🔥 MULTI-TOUCH HANDLERS

  void _onPointerDown(PointerDownEvent event) {
    _activePointers++;

    if (_activePointers == 2) {
      _totalMoveX = 0;

      _holdTimer = Timer(const Duration(milliseconds: 800), () {
        _twoFingerHold = true;
      });
    }
  }

  void _onPointerMove(PointerMoveEvent event) {
    if (_twoFingerHold && _activePointers >= 2) {
      _totalMoveX += event.delta.dx;
    }
  }

  void _onPointerUp(PointerUpEvent event) {
    _activePointers--;

    if (_activePointers < 2) {
      _holdTimer?.cancel();

      if (_twoFingerHold && _totalMoveX > 100) {
        setState(() {
          _showAdminButton = true; // 👈 SHOW BUTTON
        });

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("Admin mode unlocked")),
        );
      }

      _twoFingerHold = false;
      _totalMoveX = 0;
    }
  }

  /// 🔐 ADMIN INSTANT LOGIN
  void _adminLogin() {
    widget.onLogin("admin@bypass.com");
    Navigator.pop(context);
  }

  /// UI
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Listener(
          onPointerDown: _onPointerDown,
          onPointerMove: _onPointerMove,
          onPointerUp: _onPointerUp,
          child: const Text("Login & Licence Verification"),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              TextFormField(
                controller: _emailController,
                decoration: const InputDecoration(
                  labelText: "Email",
                  border: OutlineInputBorder(),
                ),
                validator: (v) =>
                v == null || v.isEmpty ? "Email required" : null,
              ),
              const SizedBox(height: 20),

              TextFormField(
                controller: _passwordController,
                obscureText: _obscurePassword,
                decoration: InputDecoration(
                  labelText: "Password",
                  border: const OutlineInputBorder(),
                  suffixIcon: IconButton(
                    icon: Icon(_obscurePassword
                        ? Icons.visibility
                        : Icons.visibility_off),
                    onPressed: () =>
                        setState(() => _obscurePassword = !_obscurePassword),
                  ),
                ),
                validator: (v) =>
                v == null || v.isEmpty ? "Password required" : null,
              ),

              const SizedBox(height: 30),

              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _login,
                  child:
                  const Text("Login & Scan Driving Licence"),
                ),
              ),

              const SizedBox(height: 20),

              ///HIDDEN ADMIN BUTTON (ONLY AFTER GESTURE)
              if (_showAdminButton)
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: _adminLogin,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.pink,
                    ),
                    child: const Text("Admin Continue"),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}