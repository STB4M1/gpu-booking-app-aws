import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

import 'screens/booking_page.dart';
import 'screens/login_page.dart';
import 'screens/register_page.dart';
import 'theme/material_theme.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await dotenv.load();
  runApp(const BookingApp());
}

class BookingApp extends StatelessWidget {
  const BookingApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'GPU予約アプリ',
      debugShowCheckedModeBanner: false,
      theme: customTheme,
      initialRoute: '/',
      routes: _appRoutes,
    );
  }

  Map<String, WidgetBuilder> get _appRoutes => {
        '/': (context) => const LoginPage(),
        '/booking': (context) => const BookingPage(),
        '/register': (context) => const RegisterPage(),
      };
}
