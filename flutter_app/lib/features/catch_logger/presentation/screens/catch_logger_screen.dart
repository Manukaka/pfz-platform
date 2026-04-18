import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../l10n/app_localizations.dart';

class CatchLoggerScreen extends ConsumerStatefulWidget {
  const CatchLoggerScreen({super.key});

  @override
  ConsumerState<CatchLoggerScreen> createState() => _CatchLoggerScreenState();
}

class _CatchLoggerScreenState extends ConsumerState<CatchLoggerScreen> {
  final _formKey = GlobalKey<FormState>();
  final _speciesController = TextEditingController();
  final _quantityController = TextEditingController();
  final List<Map<String, dynamic>> _entries = [];
  bool _saving = false;

  @override
  void dispose() {
    _speciesController.dispose();
    _quantityController.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _saving = true);

    final entry = {
      'id': const Uuid().v4(),
      'species': _speciesController.text,
      'quantity_kg': double.tryParse(_quantityController.text) ?? 0,
      'timestamp': DateTime.now().toIso8601String(),
      'lat': 15.0,
      'lon': 73.5,
    };

    try {
      await ref.read(apiClientProvider).logCatch(entry);
      setState(() {
        _entries.insert(0, entry);
        _speciesController.clear();
        _quantityController.clear();
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Catch logged!'), backgroundColor: AppTheme.safeGreen),
        );
      }
    } catch (_) {
      setState(() => _entries.insert(0, entry));
    } finally {
      setState(() => _saving = false);
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
                          if (double.tryParse(v) == null) return 'Enter valid number';
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
                                child: CircularProgressIndicator(strokeWidth: 2),
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
                ? Center(
                    child: Text(
                      'No catches logged yet',
                      style: const TextStyle(color: Colors.grey),
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    itemCount: _entries.length,
                    itemBuilder: (context, index) {
                      final e = _entries[index];
                      return Card(
                        child: ListTile(
                          leading: const Icon(Icons.set_meal_rounded, color: AppTheme.oceanBlue),
                          title: Text(e['species'] as String),
                          subtitle: Text(
                            '${e['quantity_kg']} kg • ${e['timestamp'].toString().substring(0, 10)}',
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
