// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Gujarati (`gu`).
class AppLocalizationsGu extends AppLocalizations {
  AppLocalizationsGu([String locale = 'gu']) : super(locale);

  @override
  String get appName => 'દરિયાસાગર';

  @override
  String get navHome => 'હોમ';

  @override
  String get navMap => 'નકશો';

  @override
  String get navSamudra => 'સમુદ્ર';

  @override
  String get navAi => 'AI મદદ';

  @override
  String get navCatch => 'પકડ';

  @override
  String get navAlerts => 'ચેતવણી';

  @override
  String get navSpecies => 'માછली';

  @override
  String get navSettings => 'સેટિંગ';

  @override
  String get splashTagline =>
      'પશ્ચિમ કિનારે માછીમારો માટે રીઅલ-ટાઈમ સમુદ્ री માહિતી';

  @override
  String get selectLanguage => 'તમારી ભાષા પસંદ કરો';

  @override
  String get homeTitle => 'દરિયાસાગર';

  @override
  String get homePfzNearYou => 'તમારી નજીકના PFZ વિસ્તારો';

  @override
  String get homeTopSpots => 'આજના શ્રેષ્ઠ સ્થળો';

  @override
  String get homeSafetyStatus => 'સુરક્ષા સ્થિતિ';

  @override
  String get homeSafe => 'માછીમારી સુરક્ષિત છે';

  @override
  String get homeWarning => 'સાવધ રહો';

  @override
  String get homeDanger => 'સમુદ્રમાં ન જાઓ';

  @override
  String get mapTitle => 'લાઈવ નકશો';

  @override
  String get mapLayers => 'નકશો સ્તરો';

  @override
  String get mapPfzZones => 'PFZ વિસ્તારો';

  @override
  String get mapWindParticles => 'પવન કણો';

  @override
  String get mapOceanCurrents => 'સમુદ્ री પ્રવાહ';

  @override
  String get mapSstHeatmap => 'SST હીટમેપ';

  @override
  String get mapChlorophyll => 'ક્લોરોફિલ';

  @override
  String get mapCycloneTracks => 'ચક્રવાત માર્ગ';

  @override
  String get mapShippingLanes => 'જહાજ માર્ગ';

  @override
  String get mapMpa => 'સંરક્ષિત વિસ્તારો';

  @override
  String get samudraTitle => 'INCOIS સમુદ્ர';

  @override
  String get aiTitle => 'AI સહાયક';

  @override
  String get aiPlaceholder => 'માછીમારી વિસ્તાર, હવામાન, માછલી વિશે પૂછો...';

  @override
  String get aiVoiceHint => 'બોલવા માટે માઈક દબાવો';

  @override
  String get catchTitle => 'પકડ નોંધ';

  @override
  String get catchAddEntry => 'પકડ નોંધો';

  @override
  String get catchSpecies => 'માછલીનું નામ';

  @override
  String get catchQuantityKg => 'જથ્થો (કિગ્રા)';

  @override
  String get catchLocation => 'સ્થળ';

  @override
  String get alertsTitle => 'ચેતવણી';

  @override
  String get alertsCyclone => 'ચક્રવાત ચેતવણી';

  @override
  String get alertsWeather => 'હવામાન સૂચના';

  @override
  String get alertsPfz => 'નવી PFZ ચેતવણી';

  @override
  String get speciesTitle => 'માછ્ ли પ્રજાતિ';

  @override
  String get settingsTitle => 'સેટિંગ';

  @override
  String get settingsLanguage => 'ભાષા';

  @override
  String get settingsRegion => 'ઘરનો વિસ્તાર';

  @override
  String get settingsOfflineMaps => 'ઓફ્ ‍लाઈन નકશા';

  @override
  String get settingsNotifications => 'સૂચના';

  @override
  String get settingsAccount => 'ખાતું';

  @override
  String get settingsSubscription => 'સભ્યપદ';

  @override
  String get premiumFeature => 'પ્રીમિયम સુविधा';

  @override
  String get upgradeToProMessage =>
      'અમर्यादित AI પ્રшнો અने real-time ચेتवणी маटे Pro маं upgrade करो';

  @override
  String get upgradePro => 'Pro маं Upgrade करो';

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

    return '$kmString किмी दूर';
  }

  @override
  String get expectedCatch => 'अपेक्षित पकड';

  @override
  String get speciesLikely => 'मळवानी शक्यता';

  @override
  String get safetyGreen => 'लीलो - सुरक्षित';

  @override
  String get safetyYellow => 'पीळो - सावधान';

  @override
  String get safetyRed => 'लाल - खतरो';

  @override
  String get safetyBlack => 'काळो - न जाओ';

  @override
  String get waveHeight => 'मोजांनी ऊंचाई';

  @override
  String get windSpeed => 'पवननी गति';

  @override
  String get currentStrength => 'समुद्री प्रवाह';

  @override
  String get noInternetOfflineMode => 'ऑफलाइन मोड - कैश डेटा वपराय छे';

  @override
  String get retry => 'फरी प्रयत्न करो';

  @override
  String get loading => 'लोड थाय छे...';

  @override
  String get error => 'कंईक गडबड थई';

  @override
  String get permissionLocation => 'PFZ क्षेत्र देखाडवा स्थान परवानगी जोईए';

  @override
  String get grantPermission => 'परवानगी आपो';
}
