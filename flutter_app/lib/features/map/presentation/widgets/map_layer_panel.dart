import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../l10n/app_localizations.dart';

final mapLayersProvider = StateProvider<Set<String>>((ref) => {
  'pfz_zones',
  'wind_particles',
  'sst_heatmap',
});

class MapLayerPanel extends ConsumerWidget {
  final VoidCallback onClose;
  const MapLayerPanel({super.key, required this.onClose});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final activeLayers = ref.watch(mapLayersProvider);

    final layers = [
      ('pfz_zones', Icons.location_on_rounded, l10n.mapPfzZones),
      ('wind_particles', Icons.air_rounded, l10n.mapWindParticles),
      ('ocean_currents', Icons.water_rounded, l10n.mapOceanCurrents),
      ('sst_heatmap', Icons.thermostat_rounded, l10n.mapSstHeatmap),
      ('chlorophyll', Icons.eco_rounded, l10n.mapChlorophyll),
      ('cyclone_tracks', Icons.cyclone_rounded, l10n.mapCycloneTracks),
      ('shipping_lanes', Icons.directions_boat_rounded, l10n.mapShippingLanes),
      ('mpa', Icons.shield_rounded, l10n.mapMpa),
    ];

    return Container(
      width: 220,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.black87,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                l10n.mapLayers,
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 13,
                ),
              ),
              const Spacer(),
              GestureDetector(
                onTap: onClose,
                child: const Icon(Icons.close, color: Colors.white60, size: 18),
              ),
            ],
          ),
          const SizedBox(height: 8),
          ...layers.map((layer) => _LayerToggle(
                id: layer.$1,
                icon: layer.$2,
                label: layer.$3,
                active: activeLayers.contains(layer.$1),
                onToggle: (val) {
                  final current = ref.read(mapLayersProvider);
                  if (val) {
                    ref.read(mapLayersProvider.notifier).state = {...current, layer.$1};
                  } else {
                    ref.read(mapLayersProvider.notifier).state =
                        current.where((l) => l != layer.$1).toSet();
                  }
                },
              )),
        ],
      ),
    );
  }
}

class _LayerToggle extends StatelessWidget {
  final String id;
  final IconData icon;
  final String label;
  final bool active;
  final ValueChanged<bool> onToggle;

  const _LayerToggle({
    required this.id,
    required this.icon,
    required this.label,
    required this.active,
    required this.onToggle,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          Icon(icon, color: active ? Colors.cyan : Colors.white38, size: 16),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              label,
              style: TextStyle(
                color: active ? Colors.white : Colors.white54,
                fontSize: 12,
              ),
            ),
          ),
          Switch(
            value: active,
            onChanged: onToggle,
            materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
            activeThumbColor: Colors.cyan,
          ),
        ],
      ),
    );
  }
}
