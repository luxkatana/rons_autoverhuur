import 'package:flutter/material.dart';
import 'verhuur_pagina.dart';
import 'widgets/car_card.dart'; // ✅ now actively used

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title:
      'Uitgelicht Cars',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(useMaterial3: true),
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
  final PageController _controller = PageController();
  int _pageIndex = 0;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF2E2E2E),

      // ✅ NAVBAR
      appBar: AppBar(
        backgroundColor: const Color(0xFF5A5656),
        elevation: 0,

        leading: Padding(
          padding: const EdgeInsets.all(8.0),
          child: Image.asset(
            'assets/rra.png',
            fit: BoxFit.contain,
          ),
        ),

        title: Text(
          _pageIndex == 0 ? 'Uitgelicht' : 'Verhuur',
          style: const TextStyle(color: Colors.white),
        ),
        centerTitle: true,
      ),

      // ✅ SWIPE BETWEEN PAGES
      body: PageView(
        controller: _controller,
        onPageChanged: (i) => setState(() => _pageIndex = i),
        children: const [
          UitgelichtPagina(),
          VerhuurPagina(),
        ],
      ),
    );
  }
}

// ✅ UITGELICHT PAGE
class UitgelichtPagina extends StatelessWidget {
  const UitgelichtPagina({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const SizedBox(height: 16),
        Expanded(
          child: ListView(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            children: const [
              CarCard(
                imagePath: 'assets/ford_unfocus.png',
                name: 'Ford Unfocus',
              ),
              SizedBox(height: 16),
              CarCard(
                imagePath: 'assets/tesla_model_tree.png',
                name: 'Tesla Model Tree',
              ),
              SizedBox(height: 16),
              CarCard(
                imagePath: 'assets/dodge_rammed.png',
                name: 'Dodge Rammed',
              ),
            ],
          ),
        ),
      ],
    );
  }
}
