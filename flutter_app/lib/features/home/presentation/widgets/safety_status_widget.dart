import 'package:flutter/material.dart';
import '../../../../core/theme/app_theme.dart';
import '../../providers/home_providers.dart';
import '../../../../l10n/app_localizations.dart';

class SafetyStatusWidget extends StatelessWidget {
  final SafetyStatus status;
  const SafetyStatusWidget({super.key, required this.status});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final color = _getColor(status.color);
    final label = _getLabel(status.color, l10n);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(color: color, shape: BoxShape.circle),
            child: Icon(_getIcon(status.color), color: Colors.white, size: 24),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  l10n.homeSafetyStatus,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.grey[600],
                  ),
                ),
                Text(
                  label,
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    color: color,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          Text(
            '${status.score}',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
              color: color,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Color _getColor(String colorStr) {
    switch (colorStr) {
      case 'green': return AppTheme.safeGreen;
      case 'yellow': return AppTheme.warningAmber;
      case 'red': return AppTheme.dangerRed;
      case 'black': return Colors.black;
      default: return AppTheme.safeGreen;
    }
  }

  IconData _getIcon(String colorStr) {
    switch (colorStr) {
      case 'green': return Icons.check_circle_outline;
      case 'yellow': return Icons.warning_amber_outlined;
      case 'red': return Icons.dangerous_outlined;
      case 'black': return Icons.block_outlined;
      default: return Icons.check_circle_outline;
    }
  }

  String _getLabel(String colorStr, AppLocalizations l10n) {
    switch (colorStr) {
      case 'green': return l10n.safetyGreen;
      case 'yellow': return l10n.safetyYellow;
      case 'red': return l10n.safetyRed;
      case 'black': return l10n.safetyBlack;
      default: return l10n.safetyGreen;
    }
  }
}
