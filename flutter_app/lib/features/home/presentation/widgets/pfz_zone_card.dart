import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../../shared/models/pfz_zone.dart';
import '../../../../l10n/app_localizations.dart';
import '../../../../core/theme/app_theme.dart';

class PfzZoneCard extends StatelessWidget {
  final PfzZone zone;
  const PfzZoneCard({super.key, required this.zone});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final confidencePct = (zone.confidence * 100).toStringAsFixed(0);

    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => context.go('/map'),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            children: [
              Container(
                width: 50,
                height: 50,
                decoration: BoxDecoration(
                  color: AppTheme.oceanBlue.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(
                  Icons.location_on_rounded,
                  color: AppTheme.oceanBlue,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      zone.state.toUpperCase(),
                      style: Theme.of(context).textTheme.labelSmall?.copyWith(
                        color: AppTheme.oceanBlue,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      zone.topSpecies,
                      style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    if (zone.distanceFromUserKm != null)
                      Text(
                        l10n.kmFromYou(zone.distanceFromUserKm!),
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.grey,
                        ),
                      ),
                  ],
                ),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: AppTheme.safeGreen.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      '$confidencePct%',
                      style: const TextStyle(
                        color: AppTheme.safeGreen,
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'SST ${zone.sst.toStringAsFixed(1)}°C',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Colors.grey,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
