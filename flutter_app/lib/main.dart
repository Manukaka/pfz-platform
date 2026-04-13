import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'core/theme.dart';
import 'providers/app_state.dart';
import 'screens/splash_screen.dart';
import 'screens/login_screen.dart';
import 'screens/map_screen.dart';
import 'screens/settings_screen.dart';
import 'screens/samudra_screen.dart';
import 'screens/forecast_screen.dart';
import 'screens/pdf_export_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp]);
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.light,
    systemNavigationBarColor: AppTheme.panel,
  ));
  final prefs = await SharedPreferences.getInstance();
  runApp(
    ChangeNotifierProvider(
      create: (_) => AppState(prefs)..startPolling(),
      child: const DaryasagarApp(),
    ),
  );
}

class DaryasagarApp extends StatelessWidget {
  const DaryasagarApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'दर्यासागर',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      routes: {
        '/login':    (_) => const LoginScreen(),
        '/map':      (_) => const MapScreen(),
        '/settings': (_) => const SettingsScreen(),
        '/samudra':  (_) => const SamudraScreen(),
        '/forecast': (_) => const ForecastScreen(),
        '/pdf':      (_) => const PdfExportScreen(),
      },
      home: const SplashScreen(),
    );
  }
}