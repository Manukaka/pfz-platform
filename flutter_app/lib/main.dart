import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'core/theme.dart';
import 'screens/splash_screen.dart';
import 'screens/login_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp]);
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.light,
    systemNavigationBarColor: AppTheme.panel,
  ));
  runApp(const DaryasagarApp());
}

class DaryasagarApp extends StatelessWidget {
  const DaryasagarApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '?????????',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      routes: {
        '/splash': (_) => const SplashScreen(),
        '/login':  (_) => const LoginScreen(),
      },
      home: const SplashScreen(),
    );
  }
}
