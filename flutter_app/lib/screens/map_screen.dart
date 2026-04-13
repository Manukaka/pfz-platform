import 'dart:math' as math;
import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:provider/provider.dart';
import '../core/theme.dart';
import '../l10n/strings.dart';
import '../models/pfz_zone.dart';
import '../models/ai_zone.dart';
import '../models/incois_zone.dart';
import '../providers/app_state.dart';
import '../services/map_capture_service.dart';
import '../widgets/data_cards.dart';

class MapScreen extends StatefulWidget {
  const MapScreen({super.key});
  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  final _mapCtrl  = MapController();
  final _mapKey   = GlobalKey();
  PfzZone?    _selectedAlgo;
  AiZone?     _selectedAi;
  IncoisZone? _selectedIncois;
  int  _bottomTab     = 0;
  bool _layerPanelOpen = false;
  bool _soloIncois     = false;  // Show only INCOIS layer
  bool _satelliteMode  = true;   // ESRI satellite vs dark basemap

  @override
  void initState() {
    super.initState();
    MapCaptureService.instance.register(_mapKey);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final state = context.read<AppState>();
      if (state.algoZones.isEmpty && !state.isLoading) state.fetchAll();
    });
  }

  @override
  void dispose() {
    MapCaptureService.instance.unregister();
    super.dispose();
  }

  Color _zoneColor(String level) {
    switch (level) {
      case 'high':   return AppTheme.accent2;
      case 'medium': return AppTheme.warn;
      default:       return AppTheme.danger;
    }
  }

  Color _sstColor(double sst) {
    final t = ((sst - 22.0) / 8.0).clamp(0.0, 1.0);
    return Color.lerp(const Color(0xFF0080FF), const Color(0xFFFF2200), t)!;
  }

  Color _chlColor(double chl) {
    final t = ((chl - 0.1) / 2.9).clamp(0.0, 1.0);
    return Color.lerp(const Color(0xFF607080), const Color(0xFF00FF44), t)!;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.bg,
      body: Column(children: [
        _buildTopBar(),
        Expanded(child: _buildBody()),
        _buildBottomNav(),
      ]),
    );
  }

  Widget _buildTopBar() {
    final state  = context.watch<AppState>();
    final lang   = state.lang;
    final status = state.dataStatus['sources'] as Map<String, dynamic>? ?? {};
    return Container(
      height: 56,
      decoration: const BoxDecoration(
        color: AppTheme.panel,
        border: Border(bottom: BorderSide(color: AppTheme.border, width: 1.5)),
      ),
      child: SafeArea(bottom: false, child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 14),
        child: Row(children: [
          const Text('दर्यासागर',
            style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold,
              color: AppTheme.accent, letterSpacing: 1,
              shadows: [Shadow(color: AppTheme.accent, blurRadius: 10)])),
          const SizedBox(width: 8),
          _ConnDots(status: status),
          const Spacer(),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
            decoration: BoxDecoration(
              color: AppTheme.accent2.withAlpha(30),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: AppTheme.accent2.withAlpha(76)),
            ),
            child: Text(
              '${state.algoZones.length + state.aiZones.length + state.geminiZones.length} ${S.t('pfz', lang)}',
              style: const TextStyle(fontSize: 9, color: AppTheme.accent2, letterSpacing: 1)),
          ),
          const SizedBox(width: 8),
          GestureDetector(
            onTap: () => state.fetchAll(),
            child: state.isLoading
                ? const SizedBox(width: 20, height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2, color: AppTheme.accent))
                : const Icon(Icons.refresh, color: AppTheme.accent, size: 20),
          ),
          const SizedBox(width: 6),
          // Satellite/Dark basemap toggle
          GestureDetector(
            onTap: () => setState(() => _satelliteMode = !_satelliteMode),
            child: Tooltip(message: _satelliteMode ? 'Switch to dark map' : 'Switch to satellite',
              child: Icon(_satelliteMode ? Icons.satellite_alt : Icons.map,
                color: _satelliteMode ? AppTheme.accent : AppTheme.textDim, size: 18)),
          ),
          const SizedBox(width: 6),
          // Solo INCOIS mode toggle
          GestureDetector(
            onTap: () => setState(() { _soloIncois = !_soloIncois; _selectedAlgo = null; _selectedAi = null; }),
            child: Tooltip(message: _soloIncois ? 'Show all layers' : 'INCOIS only',
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: _soloIncois ? AppTheme.warn.withAlpha(40) : Colors.transparent,
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(color: _soloIncois ? AppTheme.warn : Colors.transparent),
                ),
                child: Row(mainAxisSize: MainAxisSize.min, children: [
                  Icon(Icons.waves, color: _soloIncois ? AppTheme.warn : AppTheme.textDim, size: 14),
                  if (_soloIncois) ...[
                    const SizedBox(width: 3),
                    const Text('ONLY', style: TextStyle(fontSize: 8, color: AppTheme.warn, letterSpacing: 1)),
                  ],
                ]),
              )),
          ),
          const SizedBox(width: 6),
          GestureDetector(
            onTap: () { if (mounted) Navigator.pushReplacementNamed(context, '/login'); },
            child: const Icon(Icons.logout, color: AppTheme.textDim, size: 18),
          ),
        ]),
      )),
    );
  }

  Widget _buildBody() {
    switch (_bottomTab) {
      case 0: return _buildMapTab();
      case 1: return _buildForecastTab();
      case 2: return _buildDataTab();
      default: return _buildMapTab();
    }
  }

  Widget _buildMapTab() {
    final state = context.watch<AppState>();
    final lang  = state.lang;
    return Stack(children: [
      RepaintBoundary(
        key: _mapKey,
        child: FlutterMap(
          mapController: _mapCtrl,
          options: const MapOptions(
            initialCenter: LatLng(16.0, 73.0),
            initialZoom: 5.5, minZoom: 4, maxZoom: 15,
          ),
          children: [
            // Basemap: ESRI World Imagery satellite (default) or dark CartoDB
            if (_satelliteMode)
              TileLayer(
                urlTemplate: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                userAgentPackageName: 'com.daryasagar.app',
                tileDisplay: const TileDisplay.fadeIn(),
              )
            else
              TileLayer(
                urlTemplate: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
                subdomains: const ['a', 'b', 'c', 'd'],
                userAgentPackageName: 'com.daryasagar.app',
                tileDisplay: const TileDisplay.fadeIn(),
              ),
            // SST heatmap (hidden in solo INCOIS mode)
            if (!_soloIncois && state.showSst && state.sstGrid.isNotEmpty)
              CircleLayer(circles: state.sstGrid.map((p) {
                final c = _sstColor(p['sst'] ?? 26.0);
                return CircleMarker(point: LatLng(p['lat']!, p['lon']!),
                  useRadiusInMeter: true, radius: 25000,
                  color: c.withAlpha(60), borderColor: c.withAlpha(100), borderStrokeWidth: 0.5);
              }).toList()),
            // CHL heatmap
            if (!_soloIncois && state.showChl && state.chlGrid.isNotEmpty)
              CircleLayer(circles: state.chlGrid.map((p) {
                final c = _chlColor(p['chl'] ?? 0.5);
                return CircleMarker(point: LatLng(p['lat']!, p['lon']!),
                  useRadiusInMeter: true, radius: 25000,
                  color: c.withAlpha(55), borderColor: c.withAlpha(90), borderStrokeWidth: 0.5);
              }).toList()),
            // Algorithmic PFZ — polylines (line format) + center markers
            if (!_soloIncois && state.showAlgo && state.algoZones.isNotEmpty) ...[
              // Render as polylines where lineCoords available
              PolylineLayer(polylines: state.algoZones
                .where((z) => z.lineCoords != null && z.lineCoords!.length >= 2)
                .map((z) {
                  final c = _zoneColor(z.level);
                  return Polyline(
                    points: z.lineCoords!.map((p) => LatLng(p[1], p[0])).toList(),
                    color: c,
                    strokeWidth: 3.0,
                  );
                }).toList()),
              // Fallback circles for zones without line coordinates
              CircleLayer(circles: state.algoZones
                .where((z) => z.lineCoords == null || z.lineCoords!.length < 2)
                .map((z) {
                  final c = _zoneColor(z.level);
                  return CircleMarker(point: LatLng(z.lat, z.lon),
                    useRadiusInMeter: true, radius: 8000,
                    color: c.withAlpha(30), borderColor: c, borderStrokeWidth: 2.0);
                }).toList()),
              MarkerLayer(markers: state.algoZones.map((z) => Marker(
                point: LatLng(z.lat, z.lon), width: 14, height: 14,
                child: GestureDetector(
                  onTap: () => setState(() { _selectedAlgo = z; _selectedAi = null; _selectedIncois = null; }),
                  child: Container(decoration: BoxDecoration(
                    shape: BoxShape.circle, color: _zoneColor(z.level),
                    boxShadow: [BoxShadow(color: _zoneColor(z.level).withAlpha(153), blurRadius: 8)])),
                ),
              )).toList()),
            ],
            // AI Agent PFZ — polylines where available, circles as fallback
            if (!_soloIncois && state.showAi && state.aiZones.isNotEmpty) ...[
              // Polyline outlines for zones with boundary coordinates
              PolylineLayer(polylines: state.aiZones
                .where((z) => z.coordinates != null && z.coordinates!.length >= 2)
                .map((z) => Polyline(
                  points: z.coordinates!.map((c) => LatLng(c[1], c[0])).toList(),
                  color: AppTheme.accent2,
                  strokeWidth: 2.5,
                )).toList()),
              // Fallback circles for zones without polyline data
              CircleLayer(circles: state.aiZones
                .where((z) => z.coordinates == null || z.coordinates!.length < 2)
                .map((z) => CircleMarker(
                  point: LatLng(z.lat, z.lon), useRadiusInMeter: true, radius: 10000,
                  color: AppTheme.accent2.withAlpha(20), borderColor: AppTheme.accent2, borderStrokeWidth: 2,
                )).toList()),
              // Center markers for all AI zones
              MarkerLayer(markers: state.aiZones.map((z) => Marker(
                point: LatLng(z.lat, z.lon), width: 16, height: 16,
                child: GestureDetector(
                  onTap: () => setState(() { _selectedAi = z; _selectedAlgo = null; _selectedIncois = null; }),
                  child: _DiamondMarker(color: AppTheme.accent2),
                ),
              )).toList()),
            ],
            // GEMINI AI PFZ — magenta polylines
            if (!_soloIncois && state.showGemini && state.geminiZones.isNotEmpty) ...[
              PolylineLayer(polylines: state.geminiZones
                .where((z) => z.coordinates != null && z.coordinates!.length >= 2)
                .map((z) => Polyline(
                  points: z.coordinates!.map((c) => LatLng(c[1], c[0])).toList(),
                  color: const Color(0xFFFF00FF),
                  strokeWidth: 2.5,
                )).toList()),
              CircleLayer(circles: state.geminiZones
                .where((z) => z.coordinates == null || z.coordinates!.length < 2)
                .map((z) => CircleMarker(
                  point: LatLng(z.lat, z.lon), useRadiusInMeter: true, radius: 10000,
                  color: const Color(0x30FF00FF), borderColor: const Color(0xFFFF00FF), borderStrokeWidth: 2,
                )).toList()),
              MarkerLayer(markers: state.geminiZones.map((z) => Marker(
                point: LatLng(z.lat, z.lon), width: 16, height: 16,
                child: GestureDetector(
                  onTap: () => setState(() { _selectedAi = z; _selectedAlgo = null; _selectedIncois = null; }),
                  child: _DiamondMarker(color: const Color(0xFFFF00FF)),
                ),
              )).toList()),
            ],
            // INCOIS PFZ — always visible in solo mode, amber stars
            if ((state.showIncois || _soloIncois) && state.incoisZones.isNotEmpty) ...[
              CircleLayer(circles: state.incoisZones.map((z) => CircleMarker(
                point: LatLng(z.lat, z.lon), useRadiusInMeter: true, radius: 12000,
                color: AppTheme.warn.withAlpha(_soloIncois ? 70 : 40),
                borderColor: AppTheme.warn, borderStrokeWidth: _soloIncois ? 3 : 2,
              )).toList()),
              MarkerLayer(markers: state.incoisZones.map((z) => Marker(
                point: LatLng(z.lat, z.lon), width: 18, height: 18,
                child: GestureDetector(
                  onTap: () => setState(() { _selectedIncois = z; _selectedAlgo = null; _selectedAi = null; }),
                  child: Icon(Icons.star, color: AppTheme.warn, size: _soloIncois ? 20 : 16,
                    shadows: [Shadow(color: AppTheme.warn.withAlpha(200), blurRadius: 8)]),
                ),
              )).toList()),
            ],
            // Wind arrows
            if (!_soloIncois && state.showWind && state.windGrid.isNotEmpty)
              MarkerLayer(markers: _buildWindMarkers(state.windGrid)),
          ],
        ),
      ),
      // Layer toggle FAB
      Positioned(bottom: 16, left: 12,
        child: _LayerPanel(open: _layerPanelOpen,
          onToggle: () => setState(() => _layerPanelOpen = !_layerPanelOpen), lang: lang)),
      // Legend
      Positioned(top: 12, right: 12,
        child: _Legend(lang: lang, showAi: state.showAi, showIncois: state.showIncois, showGemini: state.showGemini)),
      // Zone detail cards
      if (_selectedAlgo != null)
        Positioned(bottom: 16, left: 80, right: 16,
          child: _AlgoZoneCard(zone: _selectedAlgo!,
            onClose: () => setState(() => _selectedAlgo = null),
            onPdf: () => Navigator.pushNamed(context, '/pdf'))
          .animate().slideY(begin: 0.3, duration: 300.ms, curve: Curves.easeOut).fadeIn()),
      if (_selectedAi != null)
        Positioned(bottom: 16, left: 80, right: 16,
          child: _AiZoneCard(zone: _selectedAi!,
            onClose: () => setState(() => _selectedAi = null))
          .animate().slideY(begin: 0.3, duration: 300.ms).fadeIn()),
      if (_selectedIncois != null)
        Positioned(bottom: 16, left: 80, right: 16,
          child: _IncoisZoneCard(zone: _selectedIncois!,
            onClose: () => setState(() => _selectedIncois = null))
          .animate().slideY(begin: 0.3, duration: 300.ms).fadeIn()),
    ]);
  }

  List<Marker> _buildWindMarkers(List<Map<String, double>> wind) {
    final step = (wind.length / 80).ceil().clamp(1, 999);
    final markers = <Marker>[];
    for (int i = 0; i < wind.length; i += step) {
      final p = wind[i];
      final speed = p['speed'] ?? 0;
      final dir   = p['dir']   ?? 0;
      if (speed < 1) continue;
      final opacity = (speed / 20).clamp(0.3, 1.0);
      markers.add(Marker(point: LatLng(p['lat']!, p['lon']!), width: 20, height: 20,
        child: Transform.rotate(angle: dir * math.pi / 180,
          child: Icon(Icons.arrow_upward,
            color: Colors.lightBlue.withAlpha((opacity * 200).toInt()), size: 14))));
    }
    return markers;
  }

  Widget _buildForecastTab() {
    final state = context.watch<AppState>();
    final lang  = state.lang;
    return ListView(padding: const EdgeInsets.all(16), children: [
      Row(children: [
        Expanded(child: Text(S.t('forecast_title', lang), style: const TextStyle(
          fontSize: 11, color: AppTheme.accent, letterSpacing: 3, fontWeight: FontWeight.bold))),
        GestureDetector(onTap: () => Navigator.pushNamed(context, '/forecast'),
          child: const Text('EXPAND', style: TextStyle(fontSize: 9, color: AppTheme.accent, letterSpacing: 2))),
      ]),
      const SizedBox(height: 16),
      if (state.forecast.isEmpty)
        Center(child: Text(S.t('no_forecast', lang), style: const TextStyle(color: AppTheme.textDim)))
      else
        for (int i = 0; i < state.forecast.length; i++)
          _ForecastCard(data: state.forecast[i] as Map<String, dynamic>, index: i),
    ]);
  }

  Widget _buildDataTab() {
    final state = context.watch<AppState>();
    final lang  = state.lang;
    return ListView(padding: const EdgeInsets.all(16), children: [
      Text(S.t('ocean_data', lang), style: const TextStyle(
        fontSize: 11, color: AppTheme.accent, letterSpacing: 3, fontWeight: FontWeight.bold)),
      const SizedBox(height: 16),
      DataSummaryCard(title: S.t('sst_grid', lang),
        value: '${state.sstGrid.length} ${S.t('pts', lang)}',
        icon: Icons.thermostat, color: AppTheme.warn, subtitle: S.t('sea_surface_temp', lang)),
      const SizedBox(height: 10),
      DataSummaryCard(title: S.t('chlorophyll', lang),
        value: '${state.chlGrid.length} ${S.t('pts', lang)}',
        icon: Icons.eco, color: AppTheme.accent2, subtitle: S.t('chl_concentration', lang)),
      const SizedBox(height: 10),
      DataSummaryCard(title: S.t('algo_pfz', lang),
        value: '${state.algoZones.length} ${S.t('active', lang)}',
        icon: Icons.location_on, color: AppTheme.accent, subtitle: 'Algorithmic detection'),
      const SizedBox(height: 10),
      DataSummaryCard(title: S.t('ai_pfz', lang),
        value: '${state.aiZones.length} ${S.t('active', lang)}',
        icon: Icons.psychology, color: AppTheme.accent2, subtitle: 'Claude AI agent zones'),
      const SizedBox(height: 10),
      DataSummaryCard(title: S.t('incois_pfz', lang),
        value: '${state.incoisZones.length} ${S.t('active', lang)}',
        icon: Icons.waves, color: AppTheme.warn, subtitle: 'Official INCOIS advisory'),
      const SizedBox(height: 24),
      Text(S.t('all_zones', lang), style: const TextStyle(
        fontSize: 11, color: AppTheme.accent, letterSpacing: 3)),
      const SizedBox(height: 10),
      for (final z in state.algoZones) _ZoneListTile(zone: z),
      const SizedBox(height: 16),
      GestureDetector(
        onTap: () => Navigator.pushNamed(context, '/pdf'),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 14),
          decoration: BoxDecoration(
            color: AppTheme.warn.withAlpha(20), borderRadius: BorderRadius.circular(8),
            border: Border.all(color: AppTheme.warn.withAlpha(80))),
          child: Row(mainAxisAlignment: MainAxisAlignment.center, children: [
            const Icon(Icons.picture_as_pdf, color: AppTheme.warn, size: 18),
            const SizedBox(width: 8),
            Text(S.t('pdf_export', lang), style: const TextStyle(
              color: AppTheme.warn, fontSize: 13, fontWeight: FontWeight.bold)),
          ]))),
    ]);
  }

  Widget _buildBottomNav() {
    final lang   = context.watch<AppState>().lang;
    final labels = [S.t('map', lang), S.t('forecast', lang), S.t('data', lang)];
    const icons  = [Icons.map, Icons.wb_sunny, Icons.bar_chart];
    return Container(
      decoration: const BoxDecoration(color: AppTheme.panel,
        border: Border(top: BorderSide(color: AppTheme.border, width: 1))),
      child: SafeArea(top: false, child: Row(children: [
        for (int i = 0; i < 3; i++)
          Expanded(child: GestureDetector(
            onTap: () => setState(() => _bottomTab = i),
            behavior: HitTestBehavior.opaque,
            child: Padding(padding: const EdgeInsets.symmetric(vertical: 10),
              child: Column(mainAxisSize: MainAxisSize.min, children: [
                Icon(icons[i], color: _bottomTab == i ? AppTheme.accent : AppTheme.textDim, size: 20),
                const SizedBox(height: 3),
                Text(labels[i], style: TextStyle(fontSize: 8, letterSpacing: 1,
                  color: _bottomTab == i ? AppTheme.accent : AppTheme.textDim,
                  fontWeight: _bottomTab == i ? FontWeight.bold : FontWeight.normal)),
              ]))),
          ),
        IconButton(icon: const Icon(Icons.waves, size: 20), color: AppTheme.warn,
          onPressed: () => Navigator.pushNamed(context, '/samudra'), tooltip: 'INCOIS'),
        IconButton(icon: const Icon(Icons.settings, size: 20), color: AppTheme.textDim,
          onPressed: () => Navigator.pushNamed(context, '/settings'), tooltip: 'Settings'),
      ])),
    );
  }
}

// ── Connectivity dots ─────────────────────────────────────────────────────────
class _ConnDots extends StatelessWidget {
  final Map<String, dynamic> status;
  const _ConnDots({required this.status});

  Color _color(String key) {
    final s = status[key] as Map<String, dynamic>?;
    if (s == null) return AppTheme.textDim;
    if (s['fetching'] == true) return Colors.lightBlue;
    switch (s['grade']) {
      case 'green':  return AppTheme.accent2;
      case 'orange': return AppTheme.warn;
      default:       return AppTheme.danger;
    }
  }

  @override
  Widget build(BuildContext context) => Row(children: [
    for (final k in ['pfz', 'sst', 'chl', 'wind', 'ai'])
      Padding(padding: const EdgeInsets.only(left: 4),
        child: Tooltip(message: k.toUpperCase(),
          child: Container(width: 6, height: 6,
            decoration: BoxDecoration(shape: BoxShape.circle, color: _color(k))))),
  ]);
}

// ── Layer toggle FAB panel ────────────────────────────────────────────────────
class _LayerPanel extends StatelessWidget {
  final bool open;
  final VoidCallback onToggle;
  final String lang;
  const _LayerPanel({required this.open, required this.onToggle, required this.lang});

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      if (open)
        ClipRRect(
          borderRadius: BorderRadius.circular(12),
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
            child: Container(
          margin: const EdgeInsets.only(bottom: 8),
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: AppTheme.panel.withAlpha(200), borderRadius: BorderRadius.circular(12),
            border: Border.all(color: AppTheme.border)),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(S.t('layers', lang),
              style: const TextStyle(fontSize: 8, color: AppTheme.textDim, letterSpacing: 2)),
            const SizedBox(height: 8),
            _LRow('algo',   S.t('algo_pfz', lang),   AppTheme.accent,    state.showAlgo),
            _LRow('ai',     S.t('ai_pfz', lang),     AppTheme.accent2,   state.showAi),
            _LRow('gemini', 'GEMINI AI',               const Color(0xFFFF00FF), state.showGemini),
            _LRow('incois', S.t('incois_pfz', lang),  AppTheme.warn,      state.showIncois),
            _LRow('tuna',   'TUNA ONLY',              const Color(0xFF00BCD4), state.showTunaOnly),
            _LRow('sst',    S.t('sst_layer', lang),  Colors.deepOrange,  state.showSst),
            _LRow('chl',    S.t('chl_layer', lang),  Colors.green,       state.showChl),
            _LRow('wind',   S.t('wind_layer', lang), Colors.lightBlue,   state.showWind),
          ]),
        ))).animate().fadeIn(duration: 200.ms).slideY(begin: 0.1),
      FloatingActionButton.small(heroTag: 'layers_fab', onPressed: onToggle,
        backgroundColor: AppTheme.panel, elevation: 2,
        child: Icon(open ? Icons.close : Icons.layers,
          color: open ? AppTheme.accent : AppTheme.textDim, size: 20)),
    ]);
  }
}

class _LRow extends StatelessWidget {
  final String keyName, label;
  final Color color;
  final bool  value;
  const _LRow(this.keyName, this.label, this.color, this.value);

  @override
  Widget build(BuildContext context) => GestureDetector(
    onTap: () => context.read<AppState>().toggle(keyName),
    child: Padding(padding: const EdgeInsets.symmetric(vertical: 5),
      child: Row(mainAxisSize: MainAxisSize.min, children: [
        Container(width: 8, height: 8, decoration: BoxDecoration(shape: BoxShape.circle,
          color: value ? color : AppTheme.textDim.withAlpha(100))),
        const SizedBox(width: 8),
        SizedBox(width: 110, child: Text(label, style: TextStyle(fontSize: 11,
          color: value ? AppTheme.textPrimary : AppTheme.textDim))),
        Icon(value ? Icons.check_box : Icons.check_box_outline_blank,
          color: value ? color : AppTheme.textDim, size: 14),
      ])),
  );
}

// ── Legend ────────────────────────────────────────────────────────────────────
class _Legend extends StatelessWidget {
  final String lang;
  final bool showAi, showIncois, showGemini;
  const _Legend({required this.lang, required this.showAi, required this.showIncois, required this.showGemini});

  @override
  Widget build(BuildContext context) => ClipRRect(
    borderRadius: BorderRadius.circular(10),
    child: BackdropFilter(
      filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
      child: Container(
    padding: const EdgeInsets.all(10),
    decoration: BoxDecoration(color: AppTheme.panel.withAlpha(200),
      borderRadius: BorderRadius.circular(10), border: Border.all(color: AppTheme.border)),
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(S.t('pfz_zones', lang),
        style: const TextStyle(fontSize: 8, color: AppTheme.textDim, letterSpacing: 1.5)),
      const SizedBox(height: 6),
      for (final e in [
        [S.t('high', lang), AppTheme.accent2],
        [S.t('med',  lang), AppTheme.warn],
        [S.t('low',  lang), AppTheme.danger],
      ])
        Padding(padding: const EdgeInsets.only(bottom: 3), child: Row(children: [
          Container(width: 8, height: 8, decoration: BoxDecoration(shape: BoxShape.circle, color: e[1] as Color)),
          const SizedBox(width: 5),
          Text(e[0] as String, style: const TextStyle(fontSize: 9, color: AppTheme.textPrimary)),
        ])),
      const Padding(padding: EdgeInsets.symmetric(vertical: 4), child: Divider(color: AppTheme.border, height: 1)),
      _LType(color: AppTheme.accent,  icon: Icons.circle,  label: 'ALGO'),
      if (showAi)     _LType(color: AppTheme.accent2, icon: Icons.diamond, label: 'CLAUDE AI'),
      if (showGemini) _LType(color: const Color(0xFFFF00FF), icon: Icons.diamond, label: 'GEMINI AI'),
      if (showIncois) _LType(color: AppTheme.warn,    icon: Icons.star,    label: 'INCOIS'),
    ]),
  )));
}

class _LType extends StatelessWidget {
  final Color color;
  final IconData icon;
  final String label;
  const _LType({required this.color, required this.icon, required this.label});

  @override
  Widget build(BuildContext context) => Padding(padding: const EdgeInsets.only(bottom: 3),
    child: Row(children: [
      Icon(icon, color: color, size: 9), const SizedBox(width: 4),
      Text(label, style: const TextStyle(fontSize: 8, color: AppTheme.textDim, letterSpacing: 1)),
    ]));
}

// ── Diamond marker for AI zones ───────────────────────────────────────────────
class _DiamondMarker extends StatelessWidget {
  final Color color;
  const _DiamondMarker({required this.color});

  @override
  Widget build(BuildContext context) => Transform.rotate(angle: math.pi / 4,
    child: Container(width: 10, height: 10,
      decoration: BoxDecoration(color: color,
        border: Border.all(color: Colors.white, width: 1),
        boxShadow: [BoxShadow(color: color.withAlpha(153), blurRadius: 6)])));
}

// ── Zone detail cards ─────────────────────────────────────────────────────────
class _AlgoZoneCard extends StatelessWidget {
  final PfzZone zone;
  final VoidCallback onClose, onPdf;
  const _AlgoZoneCard({required this.zone, required this.onClose, required this.onPdf});

  Color get _color => zone.level == 'high' ? AppTheme.accent2
      : zone.level == 'medium' ? AppTheme.warn : AppTheme.danger;

  @override
  Widget build(BuildContext context) => ClipRRect(
    borderRadius: BorderRadius.circular(14),
    child: BackdropFilter(
      filter: ImageFilter.blur(sigmaX: 12, sigmaY: 12),
      child: Container(
    padding: const EdgeInsets.all(14),
    decoration: BoxDecoration(color: AppTheme.panel.withAlpha(200), borderRadius: BorderRadius.circular(14),
      border: Border.all(color: _color.withAlpha(128), width: 1.5),
      boxShadow: [BoxShadow(color: _color.withAlpha(51), blurRadius: 16)]),
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Row(children: [
        Container(padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
          decoration: BoxDecoration(color: _color.withAlpha(40), borderRadius: BorderRadius.circular(6),
            border: Border.all(color: _color.withAlpha(100))),
          child: Text('ALGO · ${zone.level.toUpperCase()}',
            style: TextStyle(fontSize: 10, color: _color, fontWeight: FontWeight.bold))),
        const Spacer(),
        GestureDetector(onTap: onPdf,
          child: const Icon(Icons.picture_as_pdf, color: AppTheme.warn, size: 16)),
        const SizedBox(width: 8),
        GestureDetector(onTap: onClose,
          child: const Icon(Icons.close, color: AppTheme.textDim, size: 16)),
      ]),
      if (zone.fishEn != null) ...[
        const SizedBox(height: 8),
        Row(children: [
          const Icon(Icons.set_meal, color: AppTheme.accent, size: 13), const SizedBox(width: 6),
          Text(zone.fishEn!, style: const TextStyle(fontSize: 13, color: AppTheme.textPrimary)),
          if (zone.fishMr != null) ...[const SizedBox(width: 6),
            Text('(${zone.fishMr!})', style: const TextStyle(fontSize: 11, color: AppTheme.textDim))],
        ]),
      ],
      const SizedBox(height: 8),
      Row(children: [
        _Stat('CONF', zone.confidenceScore != null ? '${zone.confidenceScore}%' : '--', _color),
        const SizedBox(width: 14),
        _Stat('SST', zone.sst != null ? '${zone.sst!.toStringAsFixed(1)}°C' : '--', AppTheme.warn),
        const SizedBox(width: 14),
        _Stat('CHL', zone.chlorophyll != null ? zone.chlorophyll!.toStringAsFixed(3) : '--', AppTheme.accent2),
        if (zone.depthM != null) ...[const SizedBox(width: 14),
          _Stat('DEPTH', '${zone.depthM!.toInt()}m', AppTheme.accent)],
      ]),
      const SizedBox(height: 6),
      Text('${zone.lat.toStringAsFixed(4)}°N, ${zone.lon.toStringAsFixed(4)}°E',
        style: const TextStyle(fontSize: 10, color: AppTheme.textDim)),
    ]),
  )));
}

class _AiZoneCard extends StatelessWidget {
  final AiZone zone;
  final VoidCallback onClose;
  const _AiZoneCard({required this.zone, required this.onClose});

  @override
  Widget build(BuildContext context) => ClipRRect(
    borderRadius: BorderRadius.circular(14),
    child: BackdropFilter(
      filter: ImageFilter.blur(sigmaX: 12, sigmaY: 12),
      child: Container(
    padding: const EdgeInsets.all(14),
    decoration: BoxDecoration(color: AppTheme.panel.withAlpha(200), borderRadius: BorderRadius.circular(14),
      border: Border.all(color: AppTheme.accent2.withAlpha(128), width: 1.5),
      boxShadow: [BoxShadow(color: AppTheme.accent2.withAlpha(40), blurRadius: 16)]),
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Row(children: [
        Container(padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
          decoration: BoxDecoration(color: AppTheme.accent2.withAlpha(30), borderRadius: BorderRadius.circular(6)),
          child: Text('AI AGENT · ${zone.level.toUpperCase()}',
            style: const TextStyle(fontSize: 10, color: AppTheme.accent2, fontWeight: FontWeight.bold))),
        const Spacer(),
        if (zone.region != null) Text(zone.region!, style: const TextStyle(fontSize: 9, color: AppTheme.textDim)),
        const SizedBox(width: 8),
        GestureDetector(onTap: onClose, child: const Icon(Icons.close, color: AppTheme.textDim, size: 16)),
      ]),
      if (zone.fishEn != null) ...[
        const SizedBox(height: 8),
        Row(children: [const Icon(Icons.set_meal, color: AppTheme.accent2, size: 13), const SizedBox(width: 6),
          Text(zone.fishEn!, style: const TextStyle(fontSize: 13, color: AppTheme.textPrimary))]),
      ],
      const SizedBox(height: 8),
      Row(children: [
        if (zone.confidence != null) _Stat('CONF', '${zone.confidence}%', AppTheme.accent2),
        if (zone.sst != null) ...[const SizedBox(width: 14),
          _Stat('SST', '${zone.sst!.toStringAsFixed(1)}°C', AppTheme.warn)],
        if (zone.chl != null) ...[const SizedBox(width: 14),
          _Stat('CHL', zone.chl!.toStringAsFixed(3), Colors.green)],
      ]),
      const SizedBox(height: 6),
      Text('${zone.lat.toStringAsFixed(4)}°N, ${zone.lon.toStringAsFixed(4)}°E',
        style: const TextStyle(fontSize: 10, color: AppTheme.textDim)),
    ]),
  )));
}

class _IncoisZoneCard extends StatelessWidget {
  final IncoisZone zone;
  final VoidCallback onClose;
  const _IncoisZoneCard({required this.zone, required this.onClose});

  @override
  Widget build(BuildContext context) => ClipRRect(
    borderRadius: BorderRadius.circular(14),
    child: BackdropFilter(
      filter: ImageFilter.blur(sigmaX: 12, sigmaY: 12),
      child: Container(
    padding: const EdgeInsets.all(14),
    decoration: BoxDecoration(color: AppTheme.panel.withAlpha(200), borderRadius: BorderRadius.circular(14),
      border: Border.all(color: AppTheme.warn.withAlpha(128), width: 1.5),
      boxShadow: [BoxShadow(color: AppTheme.warn.withAlpha(40), blurRadius: 16)]),
    child: Row(children: [
      const Icon(Icons.waves, color: AppTheme.warn, size: 20), const SizedBox(width: 12),
      Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('INCOIS SAMUDRA', style: TextStyle(fontSize: 10, color: AppTheme.warn,
          fontWeight: FontWeight.bold, letterSpacing: 1)),
        const SizedBox(height: 4),
        Text('${zone.lat.toStringAsFixed(4)}°N, ${zone.lon.toStringAsFixed(4)}°E',
          style: const TextStyle(fontSize: 12, color: AppTheme.textPrimary)),
        if (zone.region != null) Text(zone.region!, style: const TextStyle(fontSize: 10, color: AppTheme.textDim)),
        if (zone.date != null) Text('Date: ${zone.date}', style: const TextStyle(fontSize: 9, color: AppTheme.textDim)),
      ])),
      GestureDetector(onTap: onClose, child: const Icon(Icons.close, color: AppTheme.textDim, size: 16)),
    ]),
  )));
}

// ── Shared stat ───────────────────────────────────────────────────────────────
class _Stat extends StatelessWidget {
  final String label, value;
  final Color  color;
  const _Stat(this.label, this.value, this.color);

  @override
  Widget build(BuildContext context) => Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
    Text(label, style: const TextStyle(fontSize: 8, color: AppTheme.textDim, letterSpacing: 1)),
    const SizedBox(height: 2),
    Text(value, style: TextStyle(fontSize: 13, color: color, fontWeight: FontWeight.bold)),
  ]);
}

// ── Zone list tile ────────────────────────────────────────────────────────────
class _ZoneListTile extends StatelessWidget {
  final PfzZone zone;
  const _ZoneListTile({required this.zone});

  Color get _color => zone.level == 'high' ? AppTheme.accent2
      : zone.level == 'medium' ? AppTheme.warn : AppTheme.danger;

  @override
  Widget build(BuildContext context) => Container(
    margin: const EdgeInsets.only(bottom: 8), padding: const EdgeInsets.all(12),
    decoration: BoxDecoration(color: AppTheme.panel, borderRadius: BorderRadius.circular(8),
      border: Border(left: BorderSide(color: _color, width: 3))),
    child: Row(children: [
      Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(zone.fishEn ?? 'Unknown Species', style: const TextStyle(
          fontSize: 13, color: AppTheme.textPrimary, fontWeight: FontWeight.bold)),
        const SizedBox(height: 3),
        Text('${zone.lat.toStringAsFixed(4)}°N, ${zone.lon.toStringAsFixed(4)}°E',
          style: const TextStyle(fontSize: 10, color: AppTheme.textDim)),
      ])),
      Column(crossAxisAlignment: CrossAxisAlignment.end, children: [
        Text(zone.level.toUpperCase(), style: TextStyle(
          fontSize: 10, color: _color, fontWeight: FontWeight.bold, letterSpacing: 1)),
        if (zone.confidenceScore != null)
          Text('${zone.confidenceScore}%', style: const TextStyle(fontSize: 11, color: AppTheme.textDim)),
      ]),
    ]),
  );
}

// ── Forecast card ─────────────────────────────────────────────────────────────
class _ForecastCard extends StatelessWidget {
  final Map<String, dynamic> data;
  final int index;
  const _ForecastCard({required this.data, required this.index});

  @override
  Widget build(BuildContext context) {
    final date = data['date'] ?? data['day'] ?? 'Day ${index + 1}';
    final sst  = data['sst']?.toString();
    final wind = (data['wind_speed'] ?? data['wind'])?.toString();
    final wave = (data['wave_height'] ?? data['wave'])?.toString();
    final fish = (data['fish_score'] ?? data['score'])?.toString();
    return Container(
      margin: const EdgeInsets.only(bottom: 10), padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(color: AppTheme.panel, borderRadius: BorderRadius.circular(10),
        border: Border.all(color: AppTheme.border)),
      child: Row(children: [
        Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('$date', style: const TextStyle(fontSize: 11, color: AppTheme.accent, letterSpacing: 1)),
          const SizedBox(height: 6),
          Row(children: [
            if (sst  != null) _Tag('SST ${sst}°C', AppTheme.warn),
            if (wind != null) ...[const SizedBox(width: 8), _Tag('WIND $wind kt', AppTheme.accent)],
            if (wave != null) ...[const SizedBox(width: 8), _Tag('WAVE ${wave}m', AppTheme.accent2)],
          ]),
        ]),
        const Spacer(),
        if (fish != null) Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
          decoration: BoxDecoration(color: AppTheme.accent2.withAlpha(30), borderRadius: BorderRadius.circular(6),
            border: Border.all(color: AppTheme.accent2.withAlpha(76))),
          child: Text(fish, style: const TextStyle(
            fontSize: 14, color: AppTheme.accent2, fontWeight: FontWeight.bold))),
      ]),
    ).animate().fadeIn(delay: Duration(milliseconds: index * 80)).slideX(begin: 0.1);
  }
}

class _Tag extends StatelessWidget {
  final String label;
  final Color color;
  const _Tag(this.label, this.color);

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
    decoration: BoxDecoration(color: color.withAlpha(30), borderRadius: BorderRadius.circular(4)),
    child: Text(label, style: TextStyle(fontSize: 9, color: color)));
}
