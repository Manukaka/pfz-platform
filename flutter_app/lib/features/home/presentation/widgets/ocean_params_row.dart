import 'package:flutter/material.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../l10n/app_localizations.dart';

class OceanParamsRow extends StatelessWidget {
  const OceanParamsRow({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Row(
      children: [
        _ParamCard(
          icon: Icons.waves_rounded,
          label: l10n.waveHeight,
          value: '1.2 m',
          color: AppTheme.oceanBlue,
        ),
        const SizedBox(width: 8),
        _ParamCard(
          icon: Icons.air_rounded,
          label: l10n.windSpeed,
          value: '18 km/h',
          color: AppTheme.seafoam,
        ),
        const SizedBox(width: 8),
        _ParamCard(
          icon: Icons.thermostat_rounded,
          label: 'SST',
          value: '28.4°C',
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
          color: color.withOpacity(0.08),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: color.withOpacity(0.2)),
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
