import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../l10n/app_localizations.dart';
import '../../providers/home_providers.dart';

class OceanParamsRow extends ConsumerWidget {
  const OceanParamsRow({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final safetyAsync = ref.watch(safetyStatusProvider);

    return safetyAsync.when(
      data: (safety) => _buildRow(
        context,
        l10n,
        wave: '${safety.waveHeight.toStringAsFixed(1)} m',
        wind: '${safety.windSpeed.toStringAsFixed(0)} km/h',
        sst: '${safety.sst.toStringAsFixed(1)}°C',
      ),
      loading: () => _buildRow(context, l10n,
          wave: '...', wind: '...', sst: '...'),
      error: (_, __) => _buildRow(context, l10n,
          wave: '--', wind: '--', sst: '--'),
    );
  }

  Widget _buildRow(
    BuildContext context,
    AppLocalizations l10n, {
    required String wave,
    required String wind,
    required String sst,
  }) {
    return Row(
      children: [
        _ParamCard(
          icon: Icons.waves_rounded,
          label: l10n.waveHeight,
          value: wave,
          color: AppTheme.oceanBlue,
        ),
        const SizedBox(width: 8),
        _ParamCard(
          icon: Icons.air_rounded,
          label: l10n.windSpeed,
          value: wind,
          color: AppTheme.seafoam,
        ),
        const SizedBox(width: 8),
        _ParamCard(
          icon: Icons.thermostat_rounded,
          label: 'SST',
          value: sst,
          color: AppTheme.coral,
        ),
      ],
    );
  }
}

class _ParamCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;

  const _ParamCard({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.08),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: color.withValues(alpha: 0.2)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: color, size: 20),
            const SizedBox(height: 4),
            Text(
              value,
              style: TextStyle(
                color: color,
                fontWeight: FontWeight.bold,
                fontSize: 15,
              ),
            ),
            Text(
              label,
              style: const TextStyle(color: Colors.grey, fontSize: 10),
            ),
          ],
        ),
      ),
    );
  }
}
