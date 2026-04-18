import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/theme/app_theme.dart';
import '../../../../l10n/app_localizations.dart';
import '../../../../shared/models/pfz_zone.dart';
import '../../providers/home_providers.dart';
import '../widgets/pfz_zone_card.dart';
import '../widgets/safety_status_widget.dart';
import '../widgets/quick_ai_widget.dart';
import '../widgets/ocean_params_row.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final nearbyZones = ref.watch(nearbyPfzZonesProvider);
    final safety = ref.watch(safetyStatusProvider);

    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.surface,
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            expandedHeight: 120,
            pinned: true,
            flexibleSpace: FlexibleSpaceBar(
              title: Text(
                l10n.homeTitle,
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
              background: Container(
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    colors: [AppTheme.deepBlue, AppTheme.oceanBlue],
                  ),
                ),
              ),
            ),
            actions: [
              IconButton(
                icon: const Icon(Icons.notifications_outlined, color: Colors.white),
                onPressed: () => context.go('/alerts'),
              ),
              IconButton(
                icon: const Icon(Icons.settings_outlined, color: Colors.white),
                onPressed: () => context.go('/settings'),
              ),
            ],
          ),
          SliverPadding(
            padding: const EdgeInsets.all(16),
            sliver: SliverList(
              delegate: SliverChildListDelegate([
                // Safety status
                safety.when(
                  data: (s) => SafetyStatusWidget(status: s),
                  loading: () => const _SafetyShimmer(),
                  error: (e, _) => const SizedBox.shrink(),
                ),
                const SizedBox(height: 16),

                // Ocean params
                const OceanParamsRow(),
                const SizedBox(height: 20),

                // Quick AI
                const QuickAiWidget(),
                const SizedBox(height: 20),

                // Nearby PFZ zones
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      l10n.homePfzNearYou,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    TextButton(
                      onPressed: () => context.go('/map'),
                      child: const Text('View Map'),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                nearbyZones.when(
                  data: (zones) => zones.isEmpty
                      ? _EmptyZonesCard(l10n: l10n)
                      : Column(
                          children: zones
                              .take(3)
                              .map((z) => PfzZoneCard(zone: z))
                              .toList(),
                        ),
                  loading: () => const _ZonesShimmer(),
                  error: (e, _) => _ErrorCard(message: l10n.error),
                ),
              ]),
            ),
          ),
        ],
      ),
    );
  }
}

class _SafetyShimmer extends StatelessWidget {
  const _SafetyShimmer();
  @override
  Widget build(BuildContext context) => Container(
        height: 80,
        decoration: BoxDecoration(
          color: Colors.grey[200],
          borderRadius: BorderRadius.circular(12),
        ),
      );
}

class _ZonesShimmer extends StatelessWidget {
  const _ZonesShimmer();
  @override
  Widget build(BuildContext context) => Column(
        children: List.generate(
          3,
          (_) => Container(
            height: 100,
            margin: const EdgeInsets.only(bottom: 12),
            decoration: BoxDecoration(
              color: Colors.grey[200],
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        ),
      );
}

class _EmptyZonesCard extends StatelessWidget {
  final AppLocalizations l10n;
  const _EmptyZonesCard({required this.l10n});
  @override
  Widget build(BuildContext context) => Card(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            children: [
              const Icon(Icons.waves_rounded, size: 48, color: Colors.grey),
              const SizedBox(height: 12),
              Text(
                'No PFZ zones nearby right now',
                style: Theme.of(context).textTheme.bodyLarge,
              ),
            ],
          ),
        ),
      );
}

class _ErrorCard extends StatelessWidget {
  final String message;
  const _ErrorCard({required this.message});
  @override
  Widget build(BuildContext context) => Card(
        color: Colors.red[50],
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Text(message, style: const TextStyle(color: Colors.red)),
        ),
      );
}
