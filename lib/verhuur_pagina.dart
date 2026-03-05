import 'package:flutter/material.dart';
import 'widgets/car_card.dart';


// Uses the same CarCard widget from main.dart
class VerhuurPagina extends StatelessWidget {
  const VerhuurPagina({super.key});

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
              SizedBox(height: 16),
              CarCard(
                imagePath: 'assets/rolled_royce.png',
                name: 'Rolled Royce',
              ),
              SizedBox(height: 16),
              CarCard(
                imagePath: 'assets/porsche9_11.png',
                name: 'Porsche 9/11',
              ),
            ],
          ),
        ),
      ],
    );
  }
}
