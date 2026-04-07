import 'package:flutter/material.dart';
import 'login.dart';

class AccountPagina extends StatefulWidget {
  final bool isDarkMode;
  final bool isLoggedIn;
  final String userEmail;
  final Function(bool) onThemeChanged;
  final VoidCallback onLogout;
  final Function(String) onLogin;

  final String preferredCarType;
  final Function(String) onCarTypeChanged;

  const AccountPagina({
    super.key,
    required this.isDarkMode,
    required this.isLoggedIn,
    required this.userEmail,
    required this.onThemeChanged,
    required this.onLogout,
    required this.onLogin,
    required this.preferredCarType,
    required this.onCarTypeChanged,
  });

  @override
  State<AccountPagina> createState() => _AccountPaginaState();
}

class _AccountPaginaState extends State<AccountPagina> {
  bool notificationsEnabled = true;

  @override
  Widget build(BuildContext context) {
    /// 🔒 NOT LOGGED IN
    if (!widget.isLoggedIn) {
      return Center(
        child: ElevatedButton(
          child: const Text("Login"),
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => LoginPage(onLogin: widget.onLogin),
              ),
            );
          },
        ),
      );
    }

    /// ✅ LOGGED IN UI
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [

          /// 👤 ACCOUNT
          const Text(
            "Account",
            style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 10),

          Card(
            child: ListTile(
              leading: const Icon(Icons.person),
              title: Text(widget.userEmail),
              subtitle: const Text("Logged in user"),
            ),
          ),

          const SizedBox(height: 20),

          /// 🎨 APPEARANCE
          const Text(
            "Appearance",
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),

          SwitchListTile(
            title: const Text("Dark Mode"),
            value: widget.isDarkMode,
            onChanged: widget.onThemeChanged,
          ),

          const SizedBox(height: 20),

          /// 🔔 NOTIFICATIONS
          const Text(
            "Notifications",
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),

          SwitchListTile(
            title: const Text("Enable notifications"),
            value: notificationsEnabled,
            onChanged: (val) {
              setState(() {
                notificationsEnabled = val;
              });
            },
          ),

          const SizedBox(height: 20),

          /// 🚗 RENTAL PREFERENCES (IMPORTANT PART)
          const Text(
            "Rental Preferences",
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),

          const SizedBox(height: 10),

          DropdownButtonFormField<String>(
            value: widget.preferredCarType,
            decoration: const InputDecoration(
              labelText: "Preferred car type",
              border: OutlineInputBorder(),
            ),
            items: const [
              DropdownMenuItem(value: "Any", child: Text("Any")),
              DropdownMenuItem(value: "SUV", child: Text("SUV")),
              DropdownMenuItem(value: "Electric", child: Text("Electric")),
            ],
            onChanged: (val) {
              widget.onCarTypeChanged(val!);
            },
          ),

          const SizedBox(height: 20),

          /// 💳 PAYMENT (placeholder)
          const Text(
            "Payment",
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),

          Card(
            child: ListTile(
              leading: const Icon(Icons.credit_card),
              title: const Text("Add payment method"),
              trailing: const Icon(Icons.arrow_forward_ios),
              onTap: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text("Coming soon")),
                );
              },
            ),
          ),

          const SizedBox(height: 20),

          /// 🔒 SECURITY
          const Text(
            "Security",
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),

          Card(
            child: ListTile(
              leading: const Icon(Icons.lock),
              title: const Text("Change password"),
              trailing: const Icon(Icons.arrow_forward_ios),
              onTap: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text("Coming soon")),
                );
              },
            ),
          ),

          const SizedBox(height: 30),

          /// LOGOUT
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: widget.onLogout,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.black,
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
              child: const Text("Logout"),
            ),
          ),
        ],
      ),
    );
  }
}