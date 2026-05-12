import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:uuid/uuid.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/services/location_service.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../l10n/app_localizations.dart';

const _catchBoxName = 'catch_logs';
const _syncedKey = 'synced';

// Opens (or reuses) the Hive box for catch logs.
Future<Box> _openCatchBox() => Hive.openBox(_catchBoxName);

class CatchLoggerScreen extends ConsumerStatefulWidget {
  const CatchLoggerScreen({super.key});

  @override
  ConsumerState<CatchLoggerScreen> createState() => _CatchLoggerScreenState();
}

class _CatchLoggerScreenState extends ConsumerState<CatchLoggerScreen> {
  final _formKey = GlobalKey<FormState>();
  final _speciesController = TextEditingController();
  final _quantityController = TextEditingController();
  List<Map<String, dynamic>> _entries = [];
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    _loadFromHive();
  }

  Future<void> _loadFromHive() async {
    final box = await _openCatchBox();
    final loaded = box.values
        .cast<Map>()
        .map((e) => Map<String, dynamic>.from(e))
        .toList()
      ..sort((a, b) =>
          (b['timestamp'] as String).compareTo(a['timestamp'] as String));
    if (mounted) setState(() => _entries = loaded);
    // Flush any unsynced entries from previous sessions
    _syncPending(box);
  }

  Future<void> _syncPending(Box box) async {
    final client = ref.read(apiClientProvider);
    for (final key in box.keys.toList()) {
      final raw = box.get(key);
      if (raw == null) continue;
      final entry = Map<String, dynamic>.from(raw as Map);
      if (entry[_syncedKey] == true) continue;
      try {
        final payload = Map<String, dynamic>.from(entry)..remove(_syncedKey);
        await client.logCatch(payload);
        await box.put(key, {...entry, _syncedKey: true});
        if (mounted) {
          setState(() {
            final idx = _entries.indexWhere((e) => e['id'] == entry['id']);
            if (idx != -1) _entries[idx] = {...entry, _syncedKey: true};
          });
        }
      } catch (_) {
        // Will retry next session or when user taps save again
      }
    }
  }

  @override
  void dispose() {
    _speciesController.dispose();
    _quantityController.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _saving = true);

    final location = await ref.read(locationServiceProvider).getCurrentLocation();
    final entry = {
      'id': const Uuid().v4(),
      'species': _speciesController.text.trim(),
      'quantity_kg': double.tryParse(_quantityController.text) ?? 0.0,
      'timestamp': DateTime.now().toIso8601String(),
      'lat': location.lat,
      'lon': location.lon,
      _syncedKey: false,
    };

    // Persist locally first (offline-first)
    final box = await _openCatchBox();
    await box.put(entry['id'], entry);
    setState(() {
      _entries.insert(0, entry);
      _speciesController.clear();
      _quantityController.clear();
    });

    // Attempt immediate sync
    try {
      final payload = Map<String, dynamic>.from(entry)..remove(_syncedKey);
      await ref.read(apiClientProvider).logCatch(payload);
      final synced = {...entry, _syncedKey: true};
      await box.put(entry['id'], synced);
      if (mounted) {
        setState(() => _entries[0] = synced);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Catch logged!'),
            backgroundColor: AppTheme.safeGreen,
          ),
        );
      }
    } catch (_) {
      // Saved locally; will sync next time
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Saved locally — will sync when online'),
            backgroundColor: AppTheme.warningAmber,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.catchTitle),
        backgroundColor: AppTheme.deepBlue,
        foregroundColor: Colors.white,
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      TextFormField(
                        controller: _speciesController,
                        decoration: InputDecoration(
                          labelText: l10n.catchSpecies,
                          prefixIcon: const Icon(Icons.set_meal_rounded),
                          border: const OutlineInputBorder(),
                        ),
                        validator: (v) => v!.isEmpty ? 'Required' : null,
                      ),
                      const SizedBox(height: 12),
                      TextFormField(
                        controller: _quantityController,
                        keyboardType: TextInputType.number,
                        decoration: InputDecoration(
                          labelText: l10n.catchQuantityKg,
                          prefixIcon: const Icon(Icons.scale_rounded),
                          border: const OutlineInputBorder(),
                        ),
                        validator: (v) {
                          if (v!.isEmpty) return 'Required';
                          if (double.tryParse(v) == null) {
                            return 'Enter valid number';
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton.icon(
                        onPressed: _saving ? null : _save,
                        icon: _saving
                            ? const SizedBox(
                                width: 18,
                                height: 18,
                                child: CircularProgressIndicator(
                                    strokeWidth: 2),
                              )
                            : const Icon(Icons.add_rounded),
                        label: Text(l10n.catchAddEntry),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppTheme.oceanBlue,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 14),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
          Expanded(
            child: _entries.isEmpty
                ? const Center(
                    child: Text(
                      'No catches logged yet',
                      style: TextStyle(color: Colors.grey),
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    itemCount: _entries.length,
                    itemBuilder: (context, index) {
                      final e = _entries[index];
                      final isSynced = e[_syncedKey] == true;
                      return Card(
                        child: ListTile(
                          leading: const Icon(Icons.set_meal_rounded,
                              color: AppTheme.oceanBlue),
                          title: Text(e['species'] as String),
                          subtitle: Text(
                            '${e['quantity_kg']} kg • '
                            '${(e['timestamp'] as String).substring(0, 10)}',
                          ),
                          trailing: Icon(
                            isSynced
                                ? Icons.cloud_done_rounded
                                : Icons.cloud_upload_rounded,
                            color: isSynced
                                ? AppTheme.safeGreen
                                : AppTheme.warningAmber,
                            size: 18,
                          ),
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}
