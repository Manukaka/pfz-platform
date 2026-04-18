// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Konkani (`kok`).
class AppLocalizationsKok extends AppLocalizations {
  AppLocalizationsKok([String locale = 'kok']) : super(locale);

  @override
  String get appName => 'दर्यासागर';

  @override
  String get navHome => 'मुखपान';

  @override
  String get navMap => 'नकाशो';

  @override
  String get navSamudra => 'दर्यो';

  @override
  String get navAi => 'AI मदत';

  @override
  String get navCatch => 'मासो';

  @override
  String get navAlerts => 'इशारो';

  @override
  String get navSpecies => 'माशांचे प्रकार';

  @override
  String get navSettings => 'सेटिंग';

  @override
  String get splashTagline =>
      'पश्चिम किनाऱ्यावरील कोळ्यांखातीर रियल-टायम दर्यादखल माहिती';

  @override
  String get selectLanguage => 'तुमची भास निवडात';

  @override
  String get homeTitle => 'दर्यासागर';

  @override
  String get homePfzNearYou => 'तुमच्या लागीं PFZ क्षेत्र';

  @override
  String get homeTopSpots => 'आजचीं सगळ्यांत बरीं जागां';

  @override
  String get homeSafetyStatus => 'सुरक्षा परिस्थिती';

  @override
  String get homeSafe => 'मासेमारी सुरक्षित आसा';

  @override
  String get homeWarning => 'सावधगिरी घेयात';

  @override
  String get homeDanger => 'दर्यांत वचनाकात';

  @override
  String get mapTitle => 'लाइव्ह नकाशो';

  @override
  String get mapLayers => 'नकाशाचे स्तर';

  @override
  String get mapPfzZones => 'PFZ क्षेत्र';

  @override
  String get mapWindParticles => 'वाऱ्याचे कण';

  @override
  String get mapOceanCurrents => 'दर्यादखल प्रवाह';

  @override
  String get mapSstHeatmap => 'SST उश्णताय नकाशो';

  @override
  String get mapChlorophyll => 'क्लोरोफिल';

  @override
  String get mapCycloneTracks => 'वादळाचो मार्ग';

  @override
  String get mapShippingLanes => 'जहाज मार्ग';

  @override
  String get mapMpa => 'संरक्षित क्षेत्र';

  @override
  String get samudraTitle => 'INCOIS दर्यो';

  @override
  String get aiTitle => 'AI सहाय्यक';

  @override
  String get aiPlaceholder =>
      'मासेमारी क्षेत्र, हवामान, माशां विशीं विचारात...';

  @override
  String get aiVoiceHint => 'उलोवपाखातीर माइक दाबात';

  @override
  String get catchTitle => 'मास पकड नोंद';

  @override
  String get catchAddEntry => 'पकड नोंदयात';

  @override
  String get catchSpecies => 'माशाचें नाव';

  @override
  String get catchQuantityKg => 'प्रमाण (किलो)';

  @override
  String get catchLocation => 'जागो';

  @override
  String get alertsTitle => 'इशारे';

  @override
  String get alertsCyclone => 'वादळाचो इशारो';

  @override
  String get alertsWeather => 'हवामान सुचोवणी';

  @override
  String get alertsPfz => 'नवो PFZ इशारो';

  @override
  String get speciesTitle => 'माशांचे प्रकार';

  @override
  String get settingsTitle => 'सेटिंग';

  @override
  String get settingsLanguage => 'भास';

  @override
  String get settingsRegion => 'घराचो प्रदेश';

  @override
  String get settingsOfflineMaps => 'ऑफलाइन नकाशे';

  @override
  String get settingsNotifications => 'सुचोवण्यो';

  @override
  String get settingsAccount => 'खातें';

  @override
  String get settingsSubscription => 'वर्गणी';

  @override
  String get premiumFeature => 'प्रीमियम सोय';

  @override
  String get upgradeToProMessage =>
      'अमर्यादित AI प्रस्न आनी रियल-टायम इशाऱ्यांखातीर Pro कडेन अपग्रेड करात';

  @override
  String get upgradePro => 'Pro कडेन अपग्रेड';

  @override
  String get confidenceScore => 'विश्वासार्हता';

  @override
  String get lastUpdated => 'अपडेट';

  @override
  String kmFromYou(double km) {
    final intl.NumberFormat kmNumberFormat = intl.NumberFormat.decimalPattern(
      localeName,
    );
    final String kmString = kmNumberFormat.format(km);

    return '$kmString किमी लांय';
  }

  @override
  String get expectedCatch => 'अपेक्षित पकड';

  @override
  String get speciesLikely => 'मेळ्पाची शक्यताय';

  @override
  String get safetyGreen => 'हिरवें - सुरक्षित';

  @override
  String get safetyYellow => 'पिवळें - सावध';

  @override
  String get safetyRed => 'तांबडें - धोको';

  @override
  String get safetyBlack => 'काळें - वचनाकात';

  @override
  String get waveHeight => 'लाटांची उंचाय';

  @override
  String get windSpeed => 'वाऱ्याचो वेग';

  @override
  String get currentStrength => 'दर्यादखल प्रवाह';

  @override
  String get noInternetOfflineMode => 'ऑफलाइन मोड - कॅश केलेलो डेटा वापरताय';

  @override
  String get retry => 'परत प्रयत्न करात';

  @override
  String get loading => 'लोड जाता...';

  @override
  String get error => 'कितेंतरी चुकलें';

  @override
  String get permissionLocation => 'PFZ क्षेत्र दाखोवपाखातीर स्थान परवानगी जाय';

  @override
  String get grantPermission => 'परवानगी दियात';
}
