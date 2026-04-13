const fs = require('fs');

const imports = `import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:provider/provider.dart';
import 'package:screenshot/screenshot.dart';
import '../core/theme.dart';
import '../l10n/strings.dart';
import '../models/pfz_zone.dart';
import '../models/ai_zone.dart';
import '../models/incois_zone.dart';
import '../providers/app_state.dart';
import '../widgets/data_cards.dart';
`;

// Read original file to keep structure reference
const original = fs.readFileSync('lib/screens/map_screen.dart', 'utf8');
console.log('Original lines:', original.split('\n').length);

// Check if already updated
if (original.includes("package:provider")) {
  console.log('Already updated!');
  process.exit(0);
}

// Write updated imports to top of file (prepend)
// Strategy: replace original imports block with new imports
const newContent = original
  .replace(
    `import 'package:flutter/material.dart';`,
    imports
  )
  // Add provider usage
  .replace(
    `  bool _refreshing = false;
  int _bottomTab = 0;
  List<PfzZone> _zones = [];
  List<dynamic> _forecast = [];
  List<dynamic> _sstGrid = [];
  List<dynamic> _chlGrid = [];

  @override
  void initState() {
    super.initState();
    _fetchAll();
  }

  Future<void> _fetchAll() async {
      if (mounted) setState(() => _refreshing = true);
    try {
      final results = await Future.wait([
        ApiService.instance.fetchPfzZones().onError((_, __) => <PfzZone>[]),
        ApiService.instance.fetchForecast().onError((_, __) => <dynamic>[]),
        ApiService.instance.fetchSstGrid().onError((_, __) => <Map<String,double>>[]),
        ApiService.instance.fetchChlGrid().onError((_, __) => <Map<String,double>>[]),
      ]).timeout(const Duration(seconds: 30), onTimeout: () => [[], [], [], []]);
      if (mounted) {
        setState(() {
          if (results.length == 4) {
            _zones    = results[0] as List<PfzZone>;
            _forecast = results[1];
            _sstGrid  = results[2];
            _chlGrid  = results[3];
          }
        });
      }
    } catch (e) {
      if (mounted) {
        // If 401, token expired → go to login
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Could not load data. Check connection.'),
              backgroundColor: AppTheme.danger));
      }
    } finally {
      if (mounted) setState(() => _refreshing = false);
    }
  }

  Future<void> _refresh() => _fetchAll();`,
    `  final _screenshotCtrl = ScreenshotController();
  bool _layerPanelOpen = false;
  int _bottomTab = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final state = context.read<AppState>();
      if (state.algoZones.isEmpty && !state.isLoading) state.fetchAll();
    });
  }`
  );

fs.writeFileSync('lib/screens/map_screen.dart', newContent, 'utf8');
console.log('Imports updated. Lines now:', newContent.split('\n').length);
console.log('Has provider:', newContent.includes('package:provider'));
