import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../l10n/app_localizations.dart';

class SpeciesScreen extends ConsumerWidget {
  const SpeciesScreen({super.key});

  static const _speciesData = [
    _Species('Bangda (Mackerel)', 'Rastrelliger kanagurta', Icons.set_meal, AppTheme.oceanBlue,
      'SST: 26-30°C | Depth: 20-200m', 'Maharashtra, Goa, Karnataka'),
    _Species('Pomfret', 'Pampus argenteus', Icons.set_meal, AppTheme.seafoam,
      'SST: 24-28°C | Depth: 10-100m', 'Gujarat, Maharashtra'),
    _Species('Sardine (Mathi)', 'Sardinella longiceps', Icons.set_meal, AppTheme.safeGreen,
      'SST: 27-30°C | Depth: 5-80m', 'Kerala, Karnataka'),
    _Species('Bombay Duck', 'Harpadon nehereus', Icons.set_meal, AppTheme.warningAmber,
      'SST: 26-29°C | Muddy bottom', 'Gujarat, Maharashtra'),
    _Species('Seer Fish (Surmai)', 'Scomberomorus commerson', Icons.set_meal, AppTheme.coral,
      'SST: 25-29°C | Open sea', 'All states'),
    _Species('Indian Prawn', 'Penaeus indicus', Icons.set_meal, Colors.pink,
      'Estuaries, 1-50m depth', 'All states'),
    _Species('Tuna (Choora)', 'Thunnus albacares', Icons.set_meal, Colors.deepPurple,
      'Offshore, deep water', 'Kerala offshore'),
    _Species('Hilsa (Palva)', 'Tenualosa ilisha', Icons.set_meal, Colors.teal,
      'Migratory, estuary-sea', 'Gujarat, Maharashtra'),
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.speciesTitle),
        backgroundColor: AppTheme.deepBlue,
        foregroundColor: Colors.white,
      ),
      body: ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: _speciesData.length,
        separatorBuilder: (_, __) => const SizedBox(height: 8),
        itemBuilder: (context, index) {
          final s = _speciesData[index];
          return Card(
            child: ListTile(
              contentPadding: const EdgeInsets.all(12),
              leading: Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: s.color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(s.icon, color: s.color),
              ),
              title: Text(
                s.name,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(s.scientific,
                      style: const TextStyle(
                          fontStyle: FontStyle.italic, fontSize: 11, color: Colors.grey)),
                  const SizedBox(height: 2),
                  Text(s.habitat, style: const TextStyle(fontSize: 12)),
                  Text('Found: ${s.states}',
                      style: const TextStyle(fontSize: 11, color: AppTheme.oceanBlue)),
                ],
              ),
              isThreeLine: true,
            ),
          );
        },
      ),
    );
  }
}

class _Species {
  final String name;
  final String scientific;
  final IconData icon;
  final Color color;
  final String habitat;
  final String states;
  const _Species(this.name, this.scientific, this.icon, this.color, this.habitat, this.states);
}
