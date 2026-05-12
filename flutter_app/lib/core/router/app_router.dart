import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../features/splash/presentation/screens/splash_screen.dart';
import '../../features/splash/presentation/screens/language_select_screen.dart';
import '../../features/home/presentation/screens/home_screen.dart';
import '../../features/map/presentation/screens/map_screen.dart';
import '../../features/samudra/presentation/screens/samudra_screen.dart';
import '../../features/ai_assistant/presentation/screens/ai_assistant_screen.dart';
import '../../features/species/presentation/screens/species_screen.dart';
import '../../features/catch_logger/presentation/screens/catch_logger_screen.dart';
import '../../features/alerts/presentation/screens/alerts_screen.dart';
import '../../features/insights/presentation/screens/insights_screen.dart';
import '../../features/settings/presentation/screens/settings_screen.dart';
import '../shell/main_shell.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/splash',
    routes: [
      GoRoute(
        path: '/splash',
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: '/language-select',
        builder: (context, state) => const LanguageSelectScreen(),
      ),
      ShellRoute(
        builder: (context, state, child) => MainShell(child: child),
        routes: [
          GoRoute(
            path: '/home',
            builder: (context, state) => const HomeScreen(),
          ),
          GoRoute(
            path: '/map',
            builder: (context, state) => const MapScreen(),
          ),
          GoRoute(
            path: '/samudra',
            builder: (context, state) => const SamudraScreen(),
          ),
          GoRoute(
            path: '/ai',
            builder: (context, state) => const AiAssistantScreen(),
          ),
          GoRoute(
            path: '/species',
            builder: (context, state) => const SpeciesScreen(),
          ),
          GoRoute(
            path: '/catch',
            builder: (context, state) => const CatchLoggerScreen(),
          ),
          GoRoute(
            path: '/alerts',
            builder: (context, state) => const AlertsScreen(),
          ),
          GoRoute(
            path: '/insights',
            builder: (context, state) => const InsightsScreen(),
          ),
          GoRoute(
            path: '/settings',
            builder: (context, state) => const SettingsScreen(),
          ),
        ],
      ),
    ],
  );
});
