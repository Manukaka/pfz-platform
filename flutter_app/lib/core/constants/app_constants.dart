class AppConstants {
  // Environment
  static const String environment = String.fromEnvironment(
    'ENV',
    defaultValue: 'development',
  );

  // Supabase
  static const String supabaseUrl = String.fromEnvironment(
    'SUPABASE_URL',
    defaultValue: 'https://your-project.supabase.co',
  );
  static const String supabaseAnonKey = String.fromEnvironment(
    'SUPABASE_ANON_KEY',
    defaultValue: '',
  );

  // Backend API
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000',
  );
  static const String wsBaseUrl = String.fromEnvironment(
    'WS_BASE_URL',
    defaultValue: 'ws://localhost:8000',
  );

  // Mapbox
  static const String mapboxAccessToken = String.fromEnvironment(
    'MAPBOX_ACCESS_TOKEN',
    defaultValue: '',
  );

  // Sentry
  static const String sentryDsn = String.fromEnvironment(
    'SENTRY_DSN',
    defaultValue: '',
  );

  // App config
  static const Duration wsReconnectDelay = Duration(seconds: 5);
  static const Duration apiTimeout = Duration(seconds: 30);
  static const int maxAiQueriesPerDayFree = 10;

  // Supported states
  static const List<String> westCoastStates = [
    'gujarat',
    'maharashtra',
    'goa',
    'karnataka',
    'kerala',
  ];

  // Map defaults
  static const double defaultLat = 15.0;
  static const double defaultLon = 73.5;
  static const double defaultZoom = 6.0;
}
