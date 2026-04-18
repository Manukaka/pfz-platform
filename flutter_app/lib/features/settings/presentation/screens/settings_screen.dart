import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../l10n/app_localizations.dart';
import '../../../../shared/providers/locale_provider.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final currentLocale = ref.watch(localeProvider);

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
            value: true,
            onChanged: (_) {},
            activeColor: AppTheme.oceanBlue,
          ),
          SwitchListTile(
            secondary: const Icon(Icons.location_on_rounded, color: AppTheme.safeGreen),
            title: const Text('PFZ Alerts Near Me'),
            value: true,
            onChanged: (_) {},
            activeColor: AppTheme.oceanBlue,
          ),
          SwitchListTile(
            secondary: const Icon(Icons.warning_rounded, color: AppTheme.warningAmber),
            title: const Text('Weather Advisories'),
            value: false,
            onChanged: (_) {},
            activeColor: AppTheme.oceanBlue,
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
