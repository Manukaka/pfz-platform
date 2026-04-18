import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../l10n/app_localizations.dart';

class AlertsScreen extends ConsumerWidget {
  const AlertsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final alertsFuture = ref.watch(alertsProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.alertsTitle),
        backgroundColor: AppTheme.deepBlue,
        foregroundColor: Colors.white,
      ),
      body: alertsFuture.when(
        data: (alerts) => alerts.isEmpty
            ? const _EmptyAlerts()
            : ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: alerts.length,
                itemBuilder: (context, index) => _AlertCard(alert: alerts[index]),
              ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
      ),
    );
  }
}

final alertsProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  return ref.read(apiClientProvider).getAlerts();
});

class _AlertCard extends StatelessWidget {
  final Map<String, dynamic> alert;
  const _AlertCard({required this.alert});

  @override
  Widget build(BuildContext context) {
    final type = alert['type'] as String? ?? 'info';
    final color = _getColor(type);
    final icon = _getIcon(type);

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(icon, color: color),
        ),
        title: Text(
          alert['title'] as String? ?? 'Alert',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text(alert['message'] as String? ?? ''),
        trailing: Text(
          alert['time'] as String? ?? '',
          style: const TextStyle(color: Colors.grey, fontSize: 11),
        ),
      ),
    );
  }

  Color _getColor(String type) {
    switch (type) {
      case 'cyclone': return AppTheme.dangerRed;
      case 'warning': return AppTheme.warningAmber;
      case 'pfz': return AppTheme.safeGreen;
      default: return AppTheme.oceanBlue;
    }
  }

  IconData _getIcon(String type) {
    switch (type) {
      case 'cyclone': return Icons.cyclone_rounded;
      case 'warning': return Icons.warning_rounded;
      case 'pfz': return Icons.location_on_rounded;
      default: return Icons.info_outline_rounded;
    }
  }
}

class _EmptyAlerts extends StatelessWidget {
  const _EmptyAlerts();

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.notifications_none_rounded, size: 64, color: Colors.grey),
          SizedBox(height: 16),
          Text('No active alerts', style: TextStyle(color: Colors.grey)),
        ],
      ),
    );
  }
}
