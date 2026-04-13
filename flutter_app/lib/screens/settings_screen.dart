import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/theme.dart';
import '../core/constants.dart';
import '../l10n/strings.dart';
import '../providers/app_state.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();
    final lang  = state.lang;

    return Scaffold(
      backgroundColor: AppTheme.bg,
      body: Column(children: [
        _TopBar(title: S.t('settings_title', lang)),
        Expanded(child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // ── Language ──────────────────────────────────────────────────
            _SectionHeader(S.t('language', lang)),
            _LanguagePicker(lang: lang, onChanged: (l) => state.setLang(l)),
            const SizedBox(height: 20),

            // ── Map Layers ────────────────────────────────────────────────
            _SectionHeader(S.t('map_layers', lang)),
            _LayerRow(label: S.t('algo_pfz', lang),  color: AppTheme.accent,  value: state.showAlgo,   onToggle: () => state.toggle('algo')),
            _LayerRow(label: S.t('ai_pfz', lang),    color: AppTheme.accent2, value: state.showAi,     onToggle: () => state.toggle('ai')),
            _LayerRow(label: S.t('incois_pfz', lang),color: AppTheme.warn,    value: state.showIncois, onToggle: () => state.toggle('incois')),
            _LayerRow(label: S.t('sst_layer', lang), color: Colors.deepOrange,value: state.showSst,    onToggle: () => state.toggle('sst')),
            _LayerRow(label: S.t('chl_layer', lang), color: Colors.green,     value: state.showChl,    onToggle: () => state.toggle('chl')),
            _LayerRow(label: S.t('wind_layer', lang),color: Colors.lightBlue, value: state.showWind,   onToggle: () => state.toggle('wind')),
            const SizedBox(height: 20),

            // ── Data Freshness ────────────────────────────────────────────
            _SectionHeader(S.t('data_freshness', lang)),
            _DataStatusSection(status: state.dataStatus, lang: lang),
            const SizedBox(height: 20),

            // ── Auto-Refresh ──────────────────────────────────────────────
            _SectionHeader(S.t('auto_refresh', lang)),
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: AppTheme.panel,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: AppTheme.border),
              ),
              child: Row(children: [
                const Icon(Icons.sync, color: AppTheme.accent2, size: 18),
                const SizedBox(width: 10),
                Expanded(child: Text(S.t('refresh_info', lang),
                  style: const TextStyle(fontSize: 12, color: AppTheme.textDim, height: 1.5))),
              ]),
            ),
            const SizedBox(height: 20),

            // ── About ─────────────────────────────────────────────────────
            _SectionHeader(S.t('about', lang)),
            _InfoRow(S.t('version', lang), '1.0.0+1'),
            _InfoRow(S.t('backend', lang), kBaseUrl),
          ],
        )),
      ]),
    );
  }
}

class _TopBar extends StatelessWidget {
  final String title;
  const _TopBar({required this.title});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 56,
      decoration: const BoxDecoration(
        color: AppTheme.panel,
        border: Border(bottom: BorderSide(color: AppTheme.border, width: 1.5)),
      ),
      child: SafeArea(
        bottom: false,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14),
          child: Row(children: [
            GestureDetector(
              onTap: () => Navigator.of(context).pop(),
              child: const Icon(Icons.arrow_back_ios, color: AppTheme.accent, size: 18),
            ),
            const SizedBox(width: 12),
            Text(title, style: const TextStyle(
              fontSize: 14, fontWeight: FontWeight.bold,
              color: AppTheme.textPrimary, letterSpacing: 2)),
          ]),
        ),
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  final String text;
  const _SectionHeader(this.text);

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 10),
    child: Text(text, style: const TextStyle(
      fontSize: 10, color: AppTheme.accent, letterSpacing: 3, fontWeight: FontWeight.bold)),
  );
}

class _LanguagePicker extends StatelessWidget {
  final String lang;
  final ValueChanged<String> onChanged;
  const _LanguagePicker({required this.lang, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    return Row(children: [
      for (final opt in [('en', 'English'), ('mr', 'मराठी'), ('hi', 'हिंदी')])
        Expanded(child: Padding(
          padding: const EdgeInsets.only(right: 8),
          child: GestureDetector(
            onTap: () => onChanged(opt.$1),
            child: Container(
              padding: const EdgeInsets.symmetric(vertical: 12),
              decoration: BoxDecoration(
                color: lang == opt.$1 ? AppTheme.accent.withAlpha(30) : AppTheme.panel,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: lang == opt.$1 ? AppTheme.accent : AppTheme.border,
                  width: lang == opt.$1 ? 2 : 1,
                ),
              ),
              child: Column(children: [
                Text(opt.$2, style: TextStyle(
                  fontSize: 13, fontWeight: FontWeight.bold,
                  color: lang == opt.$1 ? AppTheme.accent : AppTheme.textDim)),
                Text(opt.$1.toUpperCase(), style: const TextStyle(fontSize: 8, color: AppTheme.textDim, letterSpacing: 2)),
              ]),
            ),
          ),
        )),
    ]);
  }
}

class _LayerRow extends StatelessWidget {
  final String label;
  final Color color;
  final bool value;
  final VoidCallback onToggle;
  const _LayerRow({required this.label, required this.color, required this.value, required this.onToggle});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 6),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: AppTheme.panel,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: value ? color.withAlpha(80) : AppTheme.border),
      ),
      child: Row(children: [
        Container(width: 10, height: 10,
          decoration: BoxDecoration(shape: BoxShape.circle, color: color)),
        const SizedBox(width: 12),
        Expanded(child: Text(label,
          style: TextStyle(fontSize: 13, color: value ? AppTheme.textPrimary : AppTheme.textDim))),
        Switch(
          value: value,
          onChanged: (_) => onToggle(),
          activeColor: color,
          trackColor: WidgetStateProperty.all(AppTheme.panel),
        ),
      ]),
    );
  }
}

class _DataStatusSection extends StatelessWidget {
  final Map<String, dynamic> status;
  final String lang;
  const _DataStatusSection({required this.status, required this.lang});

  @override
  Widget build(BuildContext context) {
    if (status.isEmpty) {
      return Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(color: AppTheme.panel, borderRadius: BorderRadius.circular(8)),
        child: const Text('Loading...', style: TextStyle(color: AppTheme.textDim, fontSize: 12)),
      );
    }
    final sources = status['sources'] as Map<String, dynamic>? ?? {};
    return Column(children: [
      for (final entry in sources.entries)
        _SourceRow(key: ValueKey(entry.key), sourceKey: entry.key, data: entry.value as Map<String, dynamic>),
    ]);
  }
}

class _SourceRow extends StatelessWidget {
  final String sourceKey;
  final Map<String, dynamic> data;
  const _SourceRow({super.key, required this.sourceKey, required this.data});

  Color get _gradeColor {
    switch (data['grade']) {
      case 'green':  return AppTheme.accent2;
      case 'orange': return AppTheme.warn;
      default:       return AppTheme.danger;
    }
  }

  @override
  Widget build(BuildContext context) {
    final ageLabel = data['age_label'] ?? data['status'] ?? '--';
    final fetching = data['fetching'] == true;
    return Container(
      margin: const EdgeInsets.only(bottom: 6),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: AppTheme.panel, borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppTheme.border),
      ),
      child: Row(children: [
        Container(width: 8, height: 8,
          decoration: BoxDecoration(shape: BoxShape.circle,
            color: fetching ? Colors.lightBlue : _gradeColor)),
        const SizedBox(width: 10),
        Expanded(child: Text(sourceKey.toUpperCase(),
          style: const TextStyle(fontSize: 11, color: AppTheme.textPrimary, letterSpacing: 1))),
        Text(fetching ? 'Fetching...' : ageLabel,
          style: TextStyle(fontSize: 10,
            color: fetching ? Colors.lightBlue : AppTheme.textDim)),
      ]),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final String label;
  final String value;
  const _InfoRow(this.label, this.value);

  @override
  Widget build(BuildContext context) => Container(
    margin: const EdgeInsets.only(bottom: 6),
    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
    decoration: BoxDecoration(color: AppTheme.panel, borderRadius: BorderRadius.circular(8),
      border: Border.all(color: AppTheme.border)),
    child: Row(children: [
      Text(label, style: const TextStyle(fontSize: 12, color: AppTheme.textDim)),
      const Spacer(),
      Flexible(child: Text(value, style: const TextStyle(fontSize: 11, color: AppTheme.textPrimary),
        textAlign: TextAlign.right, overflow: TextOverflow.ellipsis)),
    ]),
  );
}
