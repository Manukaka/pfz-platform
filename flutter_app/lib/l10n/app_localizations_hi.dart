// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Hindi (`hi`).
class AppLocalizationsHi extends AppLocalizations {
  AppLocalizationsHi([String locale = 'hi']) : super(locale);

  @override
  String get appName => 'दर्यासागर';

  @override
  String get navHome => 'होम';

  @override
  String get navMap => 'नक्शा';

  @override
  String get navSamudra => 'समुद्र';

  @override
  String get navAi => 'AI मदद';

  @override
  String get navCatch => 'पकड़';

  @override
  String get navAlerts => 'चेतावनी';

  @override
  String get navSpecies => 'मछली';

  @override
  String get navSettings => 'सेटिंग';

  @override
  String get splashTagline =>
      'पश्चिमी तट के मछुआरों के लिए रीयल-टाइम समुद्री जानकारी';

  @override
  String get selectLanguage => 'अपनी भाषा चुनें';

  @override
  String get homeTitle => 'दर्यासागर';

  @override
  String get homePfzNearYou => 'आपके पास PFZ क्षेत्र';

  @override
  String get homeTopSpots => 'आज के सर्वश्रेष्ठ स्थान';

  @override
  String get homeSafetyStatus => 'सुरक्षा स्थिति';

  @override
  String get homeSafe => 'मछली पकड़ना सुरक्षित है';

  @override
  String get homeWarning => 'सावधानी बरतें';

  @override
  String get homeDanger => 'समुद्र में न जाएं';

  @override
  String get mapTitle => 'लाइव नक्शा';

  @override
  String get mapLayers => 'नक्शा परतें';

  @override
  String get mapPfzZones => 'PFZ क्षेत्र';

  @override
  String get mapWindParticles => 'हवा के कण';

  @override
  String get mapOceanCurrents => 'समुद्री धाराएं';

  @override
  String get mapSstHeatmap => 'SST हीटमैप';

  @override
  String get mapChlorophyll => 'क्लोरोफिल';

  @override
  String get mapCycloneTracks => 'चक्रवात मार्ग';

  @override
  String get mapShippingLanes => 'जहाज मार्ग';

  @override
  String get mapMpa => 'संरक्षित क्षेत्र';

  @override
  String get samudraTitle => 'INCOIS समुद्र';

  @override
  String get aiTitle => 'AI सहायक';

  @override
  String get aiPlaceholder =>
      'मछली क्षेत्र, मौसम, प्रजाति के बारे में पूछें...';

  @override
  String get aiVoiceHint => 'बोलने के लिए माइक दबाएं';

  @override
  String get catchTitle => 'पकड़ लॉग';

  @override
  String get catchAddEntry => 'पकड़ दर्ज करें';

  @override
  String get catchSpecies => 'मछली का नाम';

  @override
  String get catchQuantityKg => 'मात्रा (किग्रा)';

  @override
  String get catchLocation => 'स्थान';

  @override
  String get alertsTitle => 'चेतावनियां';

  @override
  String get alertsCyclone => 'चक्रवात चेतावनी';

  @override
  String get alertsWeather => 'मौसम सलाह';

  @override
  String get alertsPfz => 'नई PFZ चेतावनी';

  @override
  String get speciesTitle => 'मछली प्रजातियां';

  @override
  String get settingsTitle => 'सेटिंग';

  @override
  String get settingsLanguage => 'भाषा';

  @override
  String get settingsRegion => 'गृह क्षेत्र';

  @override
  String get settingsOfflineMaps => 'ऑफलाइन नक्शे';

  @override
  String get settingsNotifications => 'सूचनाएं';

  @override
  String get settingsAccount => 'खाता';

  @override
  String get settingsSubscription => 'सदस्यता';

  @override
  String get premiumFeature => 'प्रीमियम सुविधा';

  @override
  String get upgradeToProMessage =>
      'असीमित AI प्रश्न और रीयल-टाइम अलर्ट के लिए Pro में अपग्रेड करें';

  @override
  String get upgradePro => 'Pro में अपग्रेड करें';

  @override
  String get confidenceScore => 'विश्वसनीयता';

  @override
  String get lastUpdated => 'अपडेट';

  @override
  String kmFromYou(double km) {
    final intl.NumberFormat kmNumberFormat = intl.NumberFormat.decimalPattern(
      localeName,
    );
    final String kmString = kmNumberFormat.format(km);

    return '$kmString किमी दूर';
  }

  @override
  String get expectedCatch => 'अपेक्षित पकड़';

  @override
  String get speciesLikely => 'मिलने की संभावना';

  @override
  String get safetyGreen => 'हरा - सुरक्षित';

  @override
  String get safetyYellow => 'पीला - सावधान';

  @override
  String get safetyRed => 'लाल - खतरा';

  @override
  String get safetyBlack => 'काला - न जाएं';

  @override
  String get waveHeight => 'लहरों की ऊंचाई';

  @override
  String get windSpeed => 'हवा की गति';

  @override
  String get currentStrength => 'समुद्री धारा';

  @override
  String get noInternetOfflineMode => 'ऑफलाइन मोड - कैश डेटा उपयोग हो रहा है';

  @override
  String get retry => 'फिर कोशिश करें';

  @override
  String get loading => 'लोड हो रहा है...';

  @override
  String get error => 'कुछ गलत हो गया';

  @override
  String get permissionLocation =>
      'आपके पास PFZ क्षेत्र दिखाने के लिए स्थान अनुमति चाहिए';

  @override
  String get grantPermission => 'अनुमति दें';
}
