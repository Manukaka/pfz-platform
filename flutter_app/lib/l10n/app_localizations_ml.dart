// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Malayalam (`ml`).
class AppLocalizationsMl extends AppLocalizations {
  AppLocalizationsMl([String locale = 'ml']) : super(locale);

  @override
  String get appName => 'ദര്യാസാഗർ';

  @override
  String get navHome => 'ഹോം';

  @override
  String get navMap => 'മാപ്പ്';

  @override
  String get navSamudra => 'സമുദ്രം';

  @override
  String get navAi => 'AI സഹായം';

  @override
  String get navCatch => 'മത്സ്യം';

  @override
  String get navAlerts => 'മുന്നറിയിപ്പ്';

  @override
  String get navSpecies => 'ഇനങ്ങൾ';

  @override
  String get navSettings => 'ക്രമീകരണം';

  @override
  String get splashTagline =>
      'പശ്ചിമ തീരത്തെ മത്സ്യത്തൊഴിലാളികൾക്ക് തത്സമയ കടൽ വിവരങ്ങൾ';

  @override
  String get selectLanguage => 'നിങ്ങളുടെ ഭാഷ തിരഞ്ഞെടുക്കുക';

  @override
  String get homeTitle => 'ദര്യാസാഗർ';

  @override
  String get homePfzNearYou => 'നിങ്ങൾക്ക് അടുത്തുള്ള PFZ മേഖലകൾ';

  @override
  String get homeTopSpots => 'ഇന്നത്തെ മികച്ച സ്ഥലങ്ങൾ';

  @override
  String get homeSafetyStatus => 'സുരക്ഷ നില';

  @override
  String get homeSafe => 'മത്സ്യബന്ധനം സുരക്ഷിതം';

  @override
  String get homeWarning => 'ജാഗ്രത പാലിക്കുക';

  @override
  String get homeDanger => 'കടലിൽ പോകരുത്';

  @override
  String get mapTitle => 'തത്സമയ മാപ്പ്';

  @override
  String get mapLayers => 'മാപ്പ് പാളികൾ';

  @override
  String get mapPfzZones => 'PFZ മേഖലകൾ';

  @override
  String get mapWindParticles => 'കാറ്റ് കണങ്ങൾ';

  @override
  String get mapOceanCurrents => 'കടൽ ഒഴുക്കുകൾ';

  @override
  String get mapSstHeatmap => 'SST ഹീറ്റ്മാപ്പ്';

  @override
  String get mapChlorophyll => 'ക്ലോറോഫിൽ';

  @override
  String get mapCycloneTracks => 'ചുഴലിക്കാറ്റ് പാത';

  @override
  String get mapShippingLanes => 'കപ്പൽ പാത';

  @override
  String get mapMpa => 'സംരക്ഷിത മേഖലകൾ';

  @override
  String get samudraTitle => 'INCOIS സമുദ്രം';

  @override
  String get aiTitle => 'AI സഹായകൻ';

  @override
  String get aiPlaceholder =>
      'മത്സ്യബന്ധന മേഖല, കാലാവസ്ഥ, മത്സ്യം ഇനം ചോദിക്കൂ...';

  @override
  String get aiVoiceHint => 'സംസാരിക്കാൻ മൈക്ക് അമർത്തുക';

  @override
  String get catchTitle => 'മത്സ്യ രേഖ';

  @override
  String get catchAddEntry => 'മത്സ്യം രേഖപ്പെടുത്തുക';

  @override
  String get catchSpecies => 'മത്സ്യത്തിന്റെ പേര്';

  @override
  String get catchQuantityKg => 'അളവ് (കിലോ)';

  @override
  String get catchLocation => 'സ്ഥലം';

  @override
  String get alertsTitle => 'മുന്നറിയിപ്പുകൾ';

  @override
  String get alertsCyclone => 'ചുഴലിക്കാറ്റ് മുന്നറിയിപ്പ്';

  @override
  String get alertsWeather => 'കാലാവസ്ഥ ഉപദേശം';

  @override
  String get alertsPfz => 'പുതിയ PFZ മുന്നറിയിപ്പ്';

  @override
  String get speciesTitle => 'മത്സ്യ ഇനങ്ങൾ';

  @override
  String get settingsTitle => 'ക്രമീകരണം';

  @override
  String get settingsLanguage => 'ഭാഷ';

  @override
  String get settingsRegion => 'ഗൃഹ മേഖല';

  @override
  String get settingsOfflineMaps => 'ഓഫ്‌ലൈൻ മാപ്പുകൾ';

  @override
  String get settingsNotifications => 'അറിയിപ്പുകൾ';

  @override
  String get settingsAccount => 'അക്കൗണ്ട്';

  @override
  String get settingsSubscription => 'സബ്‌സ്‌ക്രിപ്‌ഷൻ';

  @override
  String get premiumFeature => 'പ്രീമിയം ഫീച്ചർ';

  @override
  String get upgradeToProMessage =>
      'പരിധിയില്ലാത്ത AI ചോദ്യങ്ങൾക്കും തത്സമയ അലേർട്ടുകൾക്കും Pro-ലേക്ക് അപ്‌ഗ്രേഡ് ചെയ്യൂ';

  @override
  String get upgradePro => 'Pro-ലേക്ക് അപ്‌ഗ്രേഡ്';

  @override
  String get confidenceScore => 'വിശ്വാസ്യത';

  @override
  String get lastUpdated => 'അപ്‌ഡേറ്റ്';

  @override
  String kmFromYou(double km) {
    final intl.NumberFormat kmNumberFormat = intl.NumberFormat.decimalPattern(
      localeName,
    );
    final String kmString = kmNumberFormat.format(km);

    return '$kmString കിലോമീറ്റർ അകലെ';
  }

  @override
  String get expectedCatch => 'പ്രതീക്ഷിത മത്സ്യം';

  @override
  String get speciesLikely => 'കിട്ടാൻ സാധ്യത';

  @override
  String get safetyGreen => 'പച്ച - സുരക്ഷിതം';

  @override
  String get safetyYellow => 'മഞ്ഞ - ജാഗ്രത';

  @override
  String get safetyRed => 'ചുവപ്പ് - അപകടം';

  @override
  String get safetyBlack => 'കറുപ്പ് - പോകരുത്';

  @override
  String get waveHeight => 'തിരമാല ഉയരം';

  @override
  String get windSpeed => 'കാറ്റ് വേഗം';

  @override
  String get currentStrength => 'കടൽ ഒഴുക്ക്';

  @override
  String get noInternetOfflineMode => 'ഓഫ്‌ലൈൻ - കാഷ്ഡ് ഡേറ്റ ഉപയോഗിക്കുന്നു';

  @override
  String get retry => 'വീണ്ടും ശ്രമിക്കുക';

  @override
  String get loading => 'ലോഡ് ചെയ്യുന്നു...';

  @override
  String get error => 'എന്തോ തെറ്റ് സംഭവിച്ചു';

  @override
  String get permissionLocation =>
      'PFZ മേഖല കാണിക്കാൻ ലൊക്കേഷൻ അനുമതി ആവശ്യമാണ്';

  @override
  String get grantPermission => 'അനുമതി നൽകുക';
}
