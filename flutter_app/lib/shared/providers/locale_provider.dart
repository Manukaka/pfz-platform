import 'dart:ui';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

final localeProvider = StateNotifierProvider<LocaleNotifier, Locale>((ref) {
  return LocaleNotifier();
});

class LocaleNotifier extends StateNotifier<Locale> {
  static const _key = 'selected_locale';

  LocaleNotifier() : super(const Locale('mr')) {
    _load();
  }

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    final code = prefs.getString(_key);
    if (code != null) state = Locale(code);
  }

  Future<void> setLocale(Locale locale) async {
    state = locale;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_key, locale.languageCode);
  }

  static const supportedLocales = [
    Locale('mr'),
    Locale('gu'),
    Locale('hi'),
    Locale('kok'),
    Locale('kn'),
    Locale('ml'),
    Locale('en'),
  ];

  static const languageNames = {
    'mr': 'मराठी',
    'gu': 'ગુજરાતી',
    'hi': 'हिंदी',
    'kok': 'कोंकणी',
    'kn': 'ಕನ್ನಡ',
    'ml': 'മലയാളം',
    'en': 'English',
  };
}
