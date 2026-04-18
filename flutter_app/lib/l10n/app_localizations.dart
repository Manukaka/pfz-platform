import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_en.dart';
import 'app_localizations_gu.dart';
import 'app_localizations_hi.dart';
import 'app_localizations_kn.dart';
import 'app_localizations_kok.dart';
import 'app_localizations_ml.dart';
import 'app_localizations_mr.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'l10n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
    : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
        delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
      ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('en'),
    Locale('gu'),
    Locale('hi'),
    Locale('kn'),
    Locale('kok'),
    Locale('ml'),
    Locale('mr'),
  ];

  /// No description provided for @appName.
  ///
  /// In en, this message translates to:
  /// **'DaryaSagar'**
  String get appName;

  /// No description provided for @navHome.
  ///
  /// In en, this message translates to:
  /// **'Home'**
  String get navHome;

  /// No description provided for @navMap.
  ///
  /// In en, this message translates to:
  /// **'Map'**
  String get navMap;

  /// No description provided for @navSamudra.
  ///
  /// In en, this message translates to:
  /// **'Samudra'**
  String get navSamudra;

  /// No description provided for @navAi.
  ///
  /// In en, this message translates to:
  /// **'AI Help'**
  String get navAi;

  /// No description provided for @navCatch.
  ///
  /// In en, this message translates to:
  /// **'Catch'**
  String get navCatch;

  /// No description provided for @navAlerts.
  ///
  /// In en, this message translates to:
  /// **'Alerts'**
  String get navAlerts;

  /// No description provided for @navSpecies.
  ///
  /// In en, this message translates to:
  /// **'Species'**
  String get navSpecies;

  /// No description provided for @navSettings.
  ///
  /// In en, this message translates to:
  /// **'Settings'**
  String get navSettings;

  /// No description provided for @splashTagline.
  ///
  /// In en, this message translates to:
  /// **'Real-time ocean intelligence for West Coast fishermen'**
  String get splashTagline;

  /// No description provided for @selectLanguage.
  ///
  /// In en, this message translates to:
  /// **'Select Your Language'**
  String get selectLanguage;

  /// No description provided for @homeTitle.
  ///
  /// In en, this message translates to:
  /// **'DaryaSagar'**
  String get homeTitle;

  /// No description provided for @homePfzNearYou.
  ///
  /// In en, this message translates to:
  /// **'PFZ Zones Near You'**
  String get homePfzNearYou;

  /// No description provided for @homeTopSpots.
  ///
  /// In en, this message translates to:
  /// **'Today\'s Top Spots'**
  String get homeTopSpots;

  /// No description provided for @homeSafetyStatus.
  ///
  /// In en, this message translates to:
  /// **'Safety Status'**
  String get homeSafetyStatus;

  /// No description provided for @homeSafe.
  ///
  /// In en, this message translates to:
  /// **'Safe to fish'**
  String get homeSafe;

  /// No description provided for @homeWarning.
  ///
  /// In en, this message translates to:
  /// **'Exercise caution'**
  String get homeWarning;

  /// No description provided for @homeDanger.
  ///
  /// In en, this message translates to:
  /// **'Do not venture out'**
  String get homeDanger;

  /// No description provided for @mapTitle.
  ///
  /// In en, this message translates to:
  /// **'Live Map'**
  String get mapTitle;

  /// No description provided for @mapLayers.
  ///
  /// In en, this message translates to:
  /// **'Map Layers'**
  String get mapLayers;

  /// No description provided for @mapPfzZones.
  ///
  /// In en, this message translates to:
  /// **'PFZ Zones'**
  String get mapPfzZones;

  /// No description provided for @mapWindParticles.
  ///
  /// In en, this message translates to:
  /// **'Wind Particles'**
  String get mapWindParticles;

  /// No description provided for @mapOceanCurrents.
  ///
  /// In en, this message translates to:
  /// **'Ocean Currents'**
  String get mapOceanCurrents;

  /// No description provided for @mapSstHeatmap.
  ///
  /// In en, this message translates to:
  /// **'SST Heatmap'**
  String get mapSstHeatmap;

  /// No description provided for @mapChlorophyll.
  ///
  /// In en, this message translates to:
  /// **'Chlorophyll'**
  String get mapChlorophyll;

  /// No description provided for @mapCycloneTracks.
  ///
  /// In en, this message translates to:
  /// **'Cyclone Tracks'**
  String get mapCycloneTracks;

  /// No description provided for @mapShippingLanes.
  ///
  /// In en, this message translates to:
  /// **'Shipping Lanes'**
  String get mapShippingLanes;

  /// No description provided for @mapMpa.
  ///
  /// In en, this message translates to:
  /// **'Protected Areas'**
  String get mapMpa;

  /// No description provided for @samudraTitle.
  ///
  /// In en, this message translates to:
  /// **'INCOIS Samudra'**
  String get samudraTitle;

  /// No description provided for @aiTitle.
  ///
  /// In en, this message translates to:
  /// **'AI Assistant'**
  String get aiTitle;

  /// No description provided for @aiPlaceholder.
  ///
  /// In en, this message translates to:
  /// **'Ask about fishing zones, weather, species...'**
  String get aiPlaceholder;

  /// No description provided for @aiVoiceHint.
  ///
  /// In en, this message translates to:
  /// **'Tap mic to speak'**
  String get aiVoiceHint;

  /// No description provided for @catchTitle.
  ///
  /// In en, this message translates to:
  /// **'Catch Logger'**
  String get catchTitle;

  /// No description provided for @catchAddEntry.
  ///
  /// In en, this message translates to:
  /// **'Log Catch'**
  String get catchAddEntry;

  /// No description provided for @catchSpecies.
  ///
  /// In en, this message translates to:
  /// **'Species'**
  String get catchSpecies;

  /// No description provided for @catchQuantityKg.
  ///
  /// In en, this message translates to:
  /// **'Quantity (kg)'**
  String get catchQuantityKg;

  /// No description provided for @catchLocation.
  ///
  /// In en, this message translates to:
  /// **'Location'**
  String get catchLocation;

  /// No description provided for @alertsTitle.
  ///
  /// In en, this message translates to:
  /// **'Alerts'**
  String get alertsTitle;

  /// No description provided for @alertsCyclone.
  ///
  /// In en, this message translates to:
  /// **'Cyclone Warning'**
  String get alertsCyclone;

  /// No description provided for @alertsWeather.
  ///
  /// In en, this message translates to:
  /// **'Weather Advisory'**
  String get alertsWeather;

  /// No description provided for @alertsPfz.
  ///
  /// In en, this message translates to:
  /// **'New PFZ Alert'**
  String get alertsPfz;

  /// No description provided for @speciesTitle.
  ///
  /// In en, this message translates to:
  /// **'Fish Species'**
  String get speciesTitle;

  /// No description provided for @settingsTitle.
  ///
  /// In en, this message translates to:
  /// **'Settings'**
  String get settingsTitle;

  /// No description provided for @settingsLanguage.
  ///
  /// In en, this message translates to:
  /// **'Language'**
  String get settingsLanguage;

  /// No description provided for @settingsRegion.
  ///
  /// In en, this message translates to:
  /// **'Home Region'**
  String get settingsRegion;

  /// No description provided for @settingsOfflineMaps.
  ///
  /// In en, this message translates to:
  /// **'Offline Maps'**
  String get settingsOfflineMaps;

  /// No description provided for @settingsNotifications.
  ///
  /// In en, this message translates to:
  /// **'Notifications'**
  String get settingsNotifications;

  /// No description provided for @settingsAccount.
  ///
  /// In en, this message translates to:
  /// **'Account'**
  String get settingsAccount;

  /// No description provided for @settingsSubscription.
  ///
  /// In en, this message translates to:
  /// **'Subscription'**
  String get settingsSubscription;

  /// No description provided for @premiumFeature.
  ///
  /// In en, this message translates to:
  /// **'Premium Feature'**
  String get premiumFeature;

  /// No description provided for @upgradeToProMessage.
  ///
  /// In en, this message translates to:
  /// **'Upgrade to Pro for unlimited AI queries and real-time alerts'**
  String get upgradeToProMessage;

  /// No description provided for @upgradePro.
  ///
  /// In en, this message translates to:
  /// **'Upgrade to Pro'**
  String get upgradePro;

  /// No description provided for @confidenceScore.
  ///
  /// In en, this message translates to:
  /// **'Confidence'**
  String get confidenceScore;

  /// No description provided for @lastUpdated.
  ///
  /// In en, this message translates to:
  /// **'Updated'**
  String get lastUpdated;

  /// No description provided for @kmFromYou.
  ///
  /// In en, this message translates to:
  /// **'{km} km from you'**
  String kmFromYou(double km);

  /// No description provided for @expectedCatch.
  ///
  /// In en, this message translates to:
  /// **'Expected catch'**
  String get expectedCatch;

  /// No description provided for @speciesLikely.
  ///
  /// In en, this message translates to:
  /// **'Species likely'**
  String get speciesLikely;

  /// No description provided for @safetyGreen.
  ///
  /// In en, this message translates to:
  /// **'Green - Safe'**
  String get safetyGreen;

  /// No description provided for @safetyYellow.
  ///
  /// In en, this message translates to:
  /// **'Yellow - Caution'**
  String get safetyYellow;

  /// No description provided for @safetyRed.
  ///
  /// In en, this message translates to:
  /// **'Red - Danger'**
  String get safetyRed;

  /// No description provided for @safetyBlack.
  ///
  /// In en, this message translates to:
  /// **'Black - Do Not Go'**
  String get safetyBlack;

  /// No description provided for @waveHeight.
  ///
  /// In en, this message translates to:
  /// **'Wave Height'**
  String get waveHeight;

  /// No description provided for @windSpeed.
  ///
  /// In en, this message translates to:
  /// **'Wind Speed'**
  String get windSpeed;

  /// No description provided for @currentStrength.
  ///
  /// In en, this message translates to:
  /// **'Current'**
  String get currentStrength;

  /// No description provided for @noInternetOfflineMode.
  ///
  /// In en, this message translates to:
  /// **'Offline mode - using cached data'**
  String get noInternetOfflineMode;

  /// No description provided for @retry.
  ///
  /// In en, this message translates to:
  /// **'Retry'**
  String get retry;

  /// No description provided for @loading.
  ///
  /// In en, this message translates to:
  /// **'Loading...'**
  String get loading;

  /// No description provided for @error.
  ///
  /// In en, this message translates to:
  /// **'Something went wrong'**
  String get error;

  /// No description provided for @permissionLocation.
  ///
  /// In en, this message translates to:
  /// **'Location access needed to show PFZ zones near you'**
  String get permissionLocation;

  /// No description provided for @grantPermission.
  ///
  /// In en, this message translates to:
  /// **'Grant Permission'**
  String get grantPermission;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) => <String>[
    'en',
    'gu',
    'hi',
    'kn',
    'kok',
    'ml',
    'mr',
  ].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'en':
      return AppLocalizationsEn();
    case 'gu':
      return AppLocalizationsGu();
    case 'hi':
      return AppLocalizationsHi();
    case 'kn':
      return AppLocalizationsKn();
    case 'kok':
      return AppLocalizationsKok();
    case 'ml':
      return AppLocalizationsMl();
    case 'mr':
      return AppLocalizationsMr();
  }

  throw FlutterError(
    'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.',
  );
}
