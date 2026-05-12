import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../l10n/app_localizations.dart';
import '../../../../shared/providers/locale_provider.dart';

// Keys for notification preferences in SharedPreferences
const _keyCycloneAlerts = 'notif_cyclone_alerts';
const _keyPfzAlerts = 'notif_pfz_alerts';
const _keyWeatherAdvisories = 'notif_weather_advisories';

class NotificationPrefs {
  final bool cycloneAlerts;
  final bool pfzAlerts;
  final bool weatherAdvisories;

  const NotificationPrefs({
    this.cycloneAlerts = true,
    this.pfzAlerts = true,
    this.weatherAdvisories = false,
  });

  NotificationPrefs copyWith({
    bool? cycloneAlerts,
    bool? pfzAlerts,
    bool? weatherAdvisories,
  }) =>
      NotificationPrefs(
        cycloneAlerts: cycloneAlerts ?? this.cycloneAlerts,
        pfzAlerts: pfzAlerts ?? this.pfzAlerts,
        weatherAdvisories: weatherAdvisories ?? this.weatherAdvisories,
      );
}

class NotificationPrefsNotifier extends StateNotifier<NotificationPrefs> {
  NotificationPrefsNotifier() : super(const NotificationPrefs()) {
    _load();
  }

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    state = NotificationPrefs(
      cycloneAlerts: prefs.getBool(_keyCycloneAlerts) ?? true,
      pfzAlerts: prefs.getBool(_keyPfzAlerts) ?? true,
      weatherAdvisories: prefs.getBool(_keyWeatherAdvisories) ?? false,
    );
  }

  Future<void> setCycloneAlerts(bool value) async {
    state = state.copyWith(cycloneAlerts: value);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_keyCycloneAlerts, value);
  }

  Future<void> setPfzAlerts(bool value) async {
    state = state.copyWith(pfzAlerts: value);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_keyPfzAlerts, value);
  }

  Future<void> setWeatherAdvisories(bool value) async {
    state = state.copyWith(weatherAdvisories: value);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_keyWeatherAdvisories, value);
  }
}

final notificationPrefsProvider =
    StateNotifierProvider<NotificationPrefsNotifier, NotificationPrefs>(
  (ref) => NotificationPrefsNotifier(),
);

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final currentLocale = ref.watch(localeProvider);
    final notifPrefs = ref.watch(notificationPrefsProvider);
    final notifNotifier = ref.read(notificationPrefsProvider.notifier);

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.settingsTitle),
        backgroundColor: AppTheme.deepBlue,
        foregroundColor: Colors.white,
      ),
      body: ListView(
        children: [
          _SectionHeader('Preferences'),
          ListTile(
            leading: const Icon(Icons.language_rounded, color: AppTheme.oceanBlue),
            title: Text(l10n.settingsLanguage),
            subtitle: Text(
              LocaleNotifier.languageNames[currentLocale.languageCode] ?? '',
            ),
            trailing: const Icon(Icons.chevron_right_rounded),
            onTap: () => _showLanguagePicker(context, ref),
          ),
          ListTile(
            leading: const Icon(Icons.location_on_rounded, color: AppTheme.oceanBlue),
            title: Text(l10n.settingsRegion),
            subtitle: const Text('Maharashtra'),
            trailing: const Icon(Icons.chevron_right_rounded),
            onTap: () {},
          ),
          const Divider(),
          _SectionHeader('Maps & Data'),
          ListTile(
            leading: const Icon(Icons.map_rounded, color: AppTheme.oceanBlue),
            title: Text(l10n.settingsOfflineMaps),
            subtitle: const Text('Maharashtra downloaded (900 MB)'),
            trailing: const Icon(Icons.chevron_right_rounded),
            onTap: () {},
          ),
          const Divider(),
          _SectionHeader('Account'),
          ListTile(
            leading: const Icon(Icons.person_rounded, color: AppTheme.oceanBlue),
            title: Text(l10n.settingsAccount),
            trailing: const Icon(Icons.chevron_right_rounded),
            onTap: () {},
          ),
          ListTile(
            leading: const Icon(Icons.star_rounded, color: AppTheme.warningAmber),
            title: Text(l10n.settingsSubscription),
            subtitle: const Text('Free Tier'),
            trailing: Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: AppTheme.oceanBlue,
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Text(
                'Upgrade',
                style: TextStyle(color: Colors.white, fontSize: 12),
              ),
            ),
            onTap: () {},
          ),
          const Divider(),
          _SectionHeader('Notifications'),
          SwitchListTile(
            secondary: const Icon(Icons.cyclone_rounded, color: AppTheme.dangerRed),
            title: const Text('Cyclone Alerts'),
            value: notifPrefs.cycloneAlerts,
            onChanged: notifNotifier.setCycloneAlerts,
            activeThumbColor: AppTheme.oceanBlue,
          ),
          SwitchListTile(
            secondary: const Icon(Icons.location_on_rounded, color: AppTheme.safeGreen),
            title: const Text('PFZ Alerts Near Me'),
            value: notifPrefs.pfzAlerts,
            onChanged: notifNotifier.setPfzAlerts,
            activeThumbColor: AppTheme.oceanBlue,
          ),
          SwitchListTile(
            secondary: const Icon(Icons.warning_rounded, color: AppTheme.warningAmber),
            title: const Text('Weather Advisories'),
            value: notifPrefs.weatherAdvisories,
            onChanged: notifNotifier.setWeatherAdvisories,
            activeThumbColor: AppTheme.oceanBlue,
          ),
          const SizedBox(height: 32),
        ],
      ),
    );
  }

  void _showLanguagePicker(BuildContext context, WidgetRef ref) {
    showModalBottomSheet(
      context: context,
      builder: (_) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: LocaleNotifier.supportedLocales.map((locale) {
            final name = LocaleNotifier.languageNames[locale.languageCode]!;
            return ListTile(
              title: Text(name),
              onTap: () {
                ref.read(localeProvider.notifier).setLocale(locale);
                Navigator.pop(context);
              },
            );
          }).toList(),
        ),
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  final String text;
  const _SectionHeader(this.text);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 4),
      child: Text(
        text.toUpperCase(),
        style: TextStyle(
          color: Colors.grey[600],
          fontSize: 12,
          fontWeight: FontWeight.bold,
          letterSpacing: 1,
        ),
      ),
    );
  }
}
