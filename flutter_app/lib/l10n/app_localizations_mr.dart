// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Marathi (`mr`).
class AppLocalizationsMr extends AppLocalizations {
  AppLocalizationsMr([String locale = 'mr']) : super(locale);

  @override
  String get appName => 'दर्यासागर';

  @override
  String get navHome => 'मुख्यपृष्ठ';

  @override
  String get navMap => 'नकाशा';

  @override
  String get navSamudra => 'समुद्र';

  @override
  String get navAi => 'AI मदत';

  @override
  String get navCatch => 'मासेमारी';

  @override
  String get navAlerts => 'सूचना';

  @override
  String get navSpecies => 'मासे';

  @override
  String get navSettings => 'सेटिंग';

  @override
  String get splashTagline =>
      'पश्चिम किनाऱ्यावरील मच्छीमारांसाठी रियल-टाइम सागरी माहिती';

  @override
  String get selectLanguage => 'तुमची भाषा निवडा';

  @override
  String get homeTitle => 'दर्यासागर';

  @override
  String get homePfzNearYou => 'तुमच्या जवळचे PFZ क्षेत्र';

  @override
  String get homeTopSpots => 'आजचे सर्वोत्तम ठिकाणे';

  @override
  String get homeSafetyStatus => 'सुरक्षा स्थिती';

  @override
  String get homeSafe => 'मासेमारी सुरक्षित आहे';

  @override
  String get homeWarning => 'सावधगिरी बाळगा';

  @override
  String get homeDanger => 'समुद्रात जाऊ नका';

  @override
  String get mapTitle => 'लाइव्ह नकाशा';

  @override
  String get mapLayers => 'नकाशा स्तर';

  @override
  String get mapPfzZones => 'PFZ क्षेत्रे';

  @override
  String get mapWindParticles => 'वाऱ्याचे कण';

  @override
  String get mapOceanCurrents => 'सागरी प्रवाह';

  @override
  String get mapSstHeatmap => 'SST उष्णता नकाशा';

  @override
  String get mapChlorophyll => 'क्लोरोफिल';

  @override
  String get mapCycloneTracks => 'चक्रीवादळ मार्ग';

  @override
  String get mapShippingLanes => 'जहाज मार्ग';

  @override
  String get mapMpa => 'संरक्षित क्षेत्रे';

  @override
  String get samudraTitle => 'INCOIS समुद्र';

  @override
  String get aiTitle => 'AI सहाय्यक';

  @override
  String get aiPlaceholder => 'मासेमारी क्षेत्र, हवामान, माशांबद्दल विचारा...';

  @override
  String get aiVoiceHint => 'बोलण्यासाठी मायक्रोफोन दाबा';

  @override
  String get catchTitle => 'पकड नोंद';

  @override
  String get catchAddEntry => 'पकड नोंदवा';

  @override
  String get catchSpecies => 'माशाचे नाव';

  @override
  String get catchQuantityKg => 'प्रमाण (किलो)';

  @override
  String get catchLocation => 'ठिकाण';

  @override
  String get alertsTitle => 'सूचना';

  @override
  String get alertsCyclone => 'चक्रीवादळ इशारा';

  @override
  String get alertsWeather => 'हवामान सूचना';

  @override
  String get alertsPfz => 'नवीन PFZ सूचना';

  @override
  String get speciesTitle => 'मत्स्य प्रजाती';

  @override
  String get settingsTitle => 'सेटिंग';

  @override
  String get settingsLanguage => 'भाषा';

  @override
  String get settingsRegion => 'गृह प्रदेश';

  @override
  String get settingsOfflineMaps => 'ऑफलाइन नकाशे';

  @override
  String get settingsNotifications => 'सूचना';

  @override
  String get settingsAccount => 'खाते';

  @override
  String get settingsSubscription => 'सदस्यता';

  @override
  String get premiumFeature => 'प्रीमियम वैशिष्ट्य';

  @override
  String get upgradeToProMessage =>
      'असीमित AI प्रश्न आणि रियल-टाइम सूचनांसाठी Pro मध्ये अपग्रेड करा';

  @override
  String get upgradePro => 'Pro मध्ये अपग्रेड करा';

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

    return '$kmString किमी दूर';
  }

  @override
  String get expectedCatch => 'अपेक्षित पकड';

  @override
  String get speciesLikely => 'मिळण्याची शक्यता';

  @override
  String get safetyGreen => 'हिरवा - सुरक्षित';

  @override
  String get safetyYellow => 'पिवळा - सावधान';

  @override
  String get safetyRed => 'लाल - धोका';

  @override
  String get safetyBlack => 'काळा - जाऊ नका';

  @override
  String get waveHeight => 'लाटांची उंची';

  @override
  String get windSpeed => 'वाऱ्याचा वेग';

  @override
  String get currentStrength => 'समुद्री प्रवाह';

  @override
  String get noInternetOfflineMode => 'ऑफलाइन मोड - कॅश केलेला डेटा वापरत आहे';

  @override
  String get retry => 'पुन्हा प्रयत्न करा';

  @override
  String get loading => 'लोड होत आहे...';

  @override
  String get error => 'काहीतरी चुकले';

  @override
  String get permissionLocation =>
      'तुमच्या जवळचे PFZ क्षेत्र दाखवण्यासाठी स्थान परवानगी आवश्यक आहे';

  @override
  String get grantPermission => 'परवानगी द्या';
}
