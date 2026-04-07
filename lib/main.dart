import 'package:flutter/material.dart';
import 'account_pagina.dart';
import 'verhuur_pagina.dart';
import 'widgets/car_card.dart';
import 'login.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  bool _isDarkMode = true;
  bool _isLoggedIn = false;
  String _userEmail = "";

  /// 🔥 GLOBAL PREFERENCE
  String _preferredCarType = "Any";

  void toggleTheme(bool value) {
    setState(() {
      _isDarkMode = value;
    });
  }

  void login(String email) {
    setState(() {
      _isLoggedIn = true;
      _userEmail = email;
    });
  }

  void logout() {
    setState(() {
      _isLoggedIn = false;
      _userEmail = "";
    });
  }

  void setPreferredCarType(String type) {
    setState(() {
      _preferredCarType = type;
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      themeMode: _isDarkMode ? ThemeMode.dark : ThemeMode.light,
      theme: ThemeData.light(useMaterial3: true),
      darkTheme: ThemeData.dark(useMaterial3: true),
      home: MyHomePage(
        isDarkMode: _isDarkMode,
        isLoggedIn: _isLoggedIn,
        userEmail: _userEmail,
        onThemeChanged: toggleTheme,
        onLogin: login,
        onLogout: logout,
        preferredCarType: _preferredCarType,
        onCarTypeChanged: setPreferredCarType,
      ),
    );
  }
}

class MyHomePage extends StatefulWidget {
  final bool isDarkMode;
  final bool isLoggedIn;
  final String userEmail;
  final Function(bool) onThemeChanged;
  final Function(String) onLogin;
  final VoidCallback onLogout;

  final String preferredCarType;
  final Function(String) onCarTypeChanged;

  const MyHomePage({
    super.key,
    required this.isDarkMode,
    required this.isLoggedIn,
    required this.userEmail,
    required this.onThemeChanged,
    required this.onLogin,
    required this.onLogout,
    required this.preferredCarType,
    required this.onCarTypeChanged,
  });

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  final PageController _controller = PageController(initialPage: 1);
  int _pageIndex = 1;

  String getTitle() {
    if (_pageIndex == 0) return "Account";
    if (_pageIndex == 1) return "Uitgelicht";
    return "Verhuur";
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(getTitle()),
        centerTitle: true,
      ),
      body: PageView(
        controller: _controller,
        onPageChanged: (i) => setState(() => _pageIndex = i),
        children: [
          AccountPagina(
            isDarkMode: widget.isDarkMode,
            isLoggedIn: widget.isLoggedIn,
            userEmail: widget.userEmail,
            onThemeChanged: widget.onThemeChanged,
            onLogout: widget.onLogout,
            onLogin: widget.onLogin,
            preferredCarType: widget.preferredCarType,
            onCarTypeChanged: widget.onCarTypeChanged,
          ),
          UitgelichtPagina(
            preferredCarType: widget.preferredCarType,
          ),
          const VerhuurPagina(),
        ],
      ),
    );
  }
}

/// 🔥 UITGELICHT (CONNECTED TO SETTINGS)
class UitgelichtPagina extends StatelessWidget {
  final String preferredCarType;

  const UitgelichtPagina({
    super.key,
    required this.preferredCarType,
  });

  @override
  Widget build(BuildContext context) {
    final cars = [
      {
        "name": "Renault Twingo",
        "image": "assets/ford_unfocus.png",
        "type": "Any",
        "price": 30,
        "category": "A"
      },
      {
        "name": "Kia Picanto",
        "image": "assets/dodge_rammed.png",
        "type": "Any",
        "price": 35,
        "category": "A"
      },
      {
        "name": "Volkswagen Polo",
        "image": "assets/tesla_model_tree.png",
        "type": "SUV",
        "price": 60,
        "category": "B"
      },
    ];

    final filteredCars = cars.where((car) {
      if (preferredCarType != "Any" &&
          car["type"] != preferredCarType) {
        return false;
      }
      return true;
    }).toList();

    return ListView(
      padding: const EdgeInsets.all(16),
      children: filteredCars.map((car) {
        return Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: CarCard(
            imagePath: car["image"] as String,
            name: "${car["name"]} (€${car["price"]}/day)",
          ),
        );
      }).toList(),
    );
  }
}