// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appName => 'DaryaSagar';

  @override
  String get navHome => 'Home';

  @override
  String get navMap => 'Map';

  @override
  String get navSamudra => 'Samudra';

  @override
  String get navAi => 'AI Help';

  @override
  String get navCatch => 'Catch';

  @override
  String get navAlerts => 'Alerts';

  @override
  String get navSpecies => 'Species';

  @override
  String get navSettings => 'Settings';

  @override
  String get splashTagline =>
      'Real-time ocean intelligence for West Coast fishermen';

  @override
  String get selectLanguage => 'Select Your Language';

  @override
  String get homeTitle => 'DaryaSagar';

  @override
  String get homePfzNearYou => 'PFZ Zones Near You';

  @override
  String get homeTopSpots => 'Today\'s Top Spots';

  @override
  String get homeSafetyStatus => 'Safety Status';

  @override
  String get homeSafe => 'Safe to fish';

  @override
  String get homeWarning => 'Exercise caution';

  @override
  String get homeDanger => 'Do not venture out';

  @override
  String get mapTitle => 'Live Map';

  @override
  String get mapLayers => 'Map Layers';

  @override
  String get mapPfzZones => 'PFZ Zones';

  @override
  String get mapWindParticles => 'Wind Particles';

  @override
  String get mapOceanCurrents => 'Ocean Currents';

  @override
  String get mapSstHeatmap => 'SST Heatmap';

  @override
  String get mapChlorophyll => 'Chlorophyll';

  @override
  String get mapCycloneTracks => 'Cyclone Tracks';

  @override
  String get mapShippingLanes => 'Shipping Lanes';

  @override
  String get mapMpa => 'Protected Areas';

  @override
  String get samudraTitle => 'INCOIS Samudra';

  @override
  String get aiTitle => 'AI Assistant';

  @override
  String get aiPlaceholder => 'Ask about fishing zones, weather, species...';

  @override
  String get aiVoiceHint => 'Tap mic to speak';

  @override
  String get catchTitle => 'Catch Logger';

  @override
  String get catchAddEntry => 'Log Catch';

  @override
  String get catchSpecies => 'Species';

  @override
  String get catchQuantityKg => 'Quantity (kg)';

  @override
  String get catchLocation => 'Location';

  @override
  String get alertsTitle => 'Alerts';

  @override
  String get alertsCyclone => 'Cyclone Warning';

  @override
  String get alertsWeather => 'Weather Advisory';

  @override
  String get alertsPfz => 'New PFZ Alert';

  @override
  String get speciesTitle => 'Fish Species';

  @override
  String get settingsTitle => 'Settings';

  @override
  String get settingsLanguage => 'Language';

  @override
  String get settingsRegion => 'Home Region';

  @override
  String get settingsOfflineMaps => 'Offline Maps';

  @override
  String get settingsNotifications => 'Notifications';

  @override
  String get settingsAccount => 'Account';

  @override
  String get settingsSubscription => 'Subscription';

  @override
  String get premiumFeature => 'Premium Feature';

  @override
  String get upgradeToProMessage =>
      'Upgrade to Pro for unlimited AI queries and real-time alerts';

  @override
  String get upgradePro => 'Upgrade to Pro';

  @override
  String get confidenceScore => 'Confidence';

  @override
  String get lastUpdated => 'Updated';

  @override
  String kmFromYou(double km) {
    final intl.NumberFormat kmNumberFormat = intl.NumberFormat.decimalPattern(
      localeName,
    );
    final String kmString = kmNumberFormat.format(km);

    return '$kmString km from you';
  }

  @override
  String get expectedCatch => 'Expected catch';

  @override
  String get speciesLikely => 'Species likely';

  @override
  String get safetyGreen => 'Green - Safe';

  @override
  String get safetyYellow => 'Yellow - Caution';

  @override
  String get safetyRed => 'Red - Danger';

  @override
  String get safetyBlack => 'Black - Do Not Go';

  @override
  String get waveHeight => 'Wave Height';

  @override
  String get windSpeed => 'Wind Speed';

  @override
  String get currentStrength => 'Current';

  @override
  String get noInternetOfflineMode => 'Offline mode - using cached data';

  @override
  String get retry => 'Retry';

  @override
  String get loading => 'Loading...';

  @override
  String get error => 'Something went wrong';

  @override
  String get permissionLocation =>
      'Location access needed to show PFZ zones near you';

  @override
  String get grantPermission => 'Grant Permission';
}
