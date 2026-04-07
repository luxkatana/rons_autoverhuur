import 'package:flutter/material.dart';
import 'widgets/car_card.dart';

class VerhuurPagina extends StatefulWidget {
  const VerhuurPagina({super.key});

  @override
  State<VerhuurPagina> createState() => _VerhuurPaginaState();
}

class _VerhuurPaginaState extends State<VerhuurPagina> {
  double maxPrice = 100;
  String selectedCategory = "Any";

  @override
  Widget build(BuildContext context) {
    final cars = [
      {
        "name": "Renault Twingo",
        "image": "assets/ford_unfocus.png",
        "price": 30,
        "category": "A",
      },
      {
        "name": "Kia Picanto",
        "image": "assets/dodge_rammed.png",
        "price": 35,
        "category": "A",
      },
      {
        "name": "Volkswagen Polo",
        "image": "assets/tesla_model_tree.png",
        "price": 60,
        "category": "B",
      },
      {
        "name": "Rolled Royce",
        "image": "assets/rolled_royce.png",
        "price": 150,
        "category": "B",
      },
    ];

    final filteredCars = cars.where((car) {
      if (car["price"] as int > maxPrice) return false;

      if (selectedCategory != "Any" &&
          car["category"] != selectedCategory) {
        return false;
      }

      return true;
    }).toList();

    return Column(
      children: [
        /// 🔥 FILTERS
        Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              /// 💰 PRICE
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text("Max price: €${maxPrice.toInt()}"),
                  Slider(
                    value: maxPrice,
                    min: 10,
                    max: 200,
                    divisions: 19,
                    onChanged: (value) {
                      setState(() {
                        maxPrice = value;
                      });
                    },
                  ),
                ],
              ),

              const SizedBox(height: 10),

              /// 🚗 CATEGORY
              DropdownButtonFormField<String>(
                value: selectedCategory,
                decoration: const InputDecoration(
                  labelText: "Category",
                  border: OutlineInputBorder(),
                ),
                items: const [
                  DropdownMenuItem(value: "Any", child: Text("Any")),
                  DropdownMenuItem(value: "A", child: Text("Category A")),
                  DropdownMenuItem(value: "B", child: Text("Category B")),
                ],
                onChanged: (val) {
                  setState(() {
                    selectedCategory = val!;
                  });
                },
              ),
            ],
          ),
        ),

        /// 🚗 LIST
        Expanded(
          child: ListView(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            children: filteredCars.map((car) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 16),
                child: CarCard(
                  imagePath: car["image"] as String,
                  name:
                  "${car["name"]} (€${car["price"]}/day)",
                ),
              );
            }).toList(),
          ),
        ),
      ],
    );
  }
}