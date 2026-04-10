import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../core/theme.dart';
import '../models/pfz_zone.dart';
import '../services/api_service.dart';
import '../widgets/data_cards.dart';

class MapScreen extends StatefulWidget {
  final List<PfzZone> pfzZones;
  final List<dynamic> sstGrid;
  final List<dynamic> chlGrid;
  final List<dynamic> forecast;

  const MapScreen({
    super.key,
    required this.pfzZones,
    required this.sstGrid,
    required this.chlGrid,
    required this.forecast,
  });

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  final _mapCtrl = MapController();
  PfzZone? _selectedZone;
  bool _refreshing = false;
  int _bottomTab = 0;
  List<PfzZone> _zones = [];

  @override
  void initState() {
    super.initState();
    _zones = widget.pfzZones;
  }

  Future<void> _refresh() async {
    setState(() => _refreshing = true);
    try {
      final zones = await ApiService.instance.fetchPfzZones();
      setState(() { _zones = zones; });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Failed to refresh data'), backgroundColor: AppTheme.danger)
        );
      }
    } finally {
      if (mounted) setState(() => _refreshing = false);
    }
  }

  Color _zoneColor(String level) {
    switch (level) {
      case 'high':   return AppTheme.accent2;
      case 'medium': return AppTheme.warn;
      default:       return AppTheme.danger;
    }
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
    return Container(
      height: 56,
      decoration: const BoxDecoration(
        color: AppTheme.panel,
        border: Border(bottom: BorderSide(color: AppTheme.border, width: 1.5)),
      ),
      child: SafeArea(
        bottom: false,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14),
          child: Row(children: [
            // Live indicator
            Container(
              width: 8, height: 8,
              decoration: const BoxDecoration(
                shape: BoxShape.circle, color: AppTheme.accent2,
              ),
            ).animate(onPlay: (c) => c.repeat())
             .scaleXY(end: 1.4, duration: 800.ms).then().scaleXY(end: 1.0, duration: 800.ms),
            const SizedBox(width: 8),
            const Text('दर्यासागर',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold,
                color: AppTheme.accent, letterSpacing: 1,
                shadows: [Shadow(color: AppTheme.accent, blurRadius: 10)]),
            ),
            const SizedBox(width: 4),
            const Text('LIVE', style: TextStyle(fontSize: 8, color: AppTheme.accent2, letterSpacing: 2)),
            const Spacer(),
            // PFZ count badge
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
              decoration: BoxDecoration(
                color: AppTheme.accent2.withAlpha(30),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: AppTheme.accent2.withAlpha(76)),
              ),
              child: Text('${_zones.length} PFZ',
                style: const TextStyle(fontSize: 9, color: AppTheme.accent2, letterSpacing: 1)),
            ),
            const SizedBox(width: 8),
            // Refresh
            GestureDetector(
              onTap: _refresh,
              child: _refreshing
                  ? const SizedBox(width: 20, height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2, color: AppTheme.accent))
                  : const Icon(Icons.refresh, color: AppTheme.accent, size: 20),
            ),
            const SizedBox(width: 8),
            // Logout
            GestureDetector(
              onTap: () async {
                await ApiService.instance.logout();
                if (mounted) Navigator.pushReplacementNamed(context, '/login');
              },
              child: const Icon(Icons.logout, color: AppTheme.textDim, size: 18),
            ),
          ]),
        ),
      ),
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
    return Stack(children: [
      // Map
      FlutterMap(
        mapController: _mapCtrl,
        options: const MapOptions(
          initialCenter: LatLng(16.5, 73.5),
          initialZoom: 6.5,
          minZoom: 4,
          maxZoom: 15,
          backgroundColor: AppTheme.bg,
        ),
        children: [
          // Ocean tile layer
          TileLayer(
            urlTemplate: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            subdomains: const ['a', 'b', 'c'],
            tileDisplay: const TileDisplay.fadeIn(),
            tileBuilder: (context, child, tile) {
              // Dark ocean filter
              return ColorFiltered(
                colorFilter: const ColorFilter.matrix([
                  -0.3, 0, 0, 0, 20,
                   0, -0.1, 0, 0, 10,
                   0, 0, 0.5, 0, 30,
                   0, 0, 0, 1, 0,
                ]),
                child: child,
              );
            },
          ),
          // PFZ zones as circles
          CircleLayer(
            circles: _zones.map((z) {
              final c = _zoneColor(z.level);
              return CircleMarker(
                point: LatLng(z.lat, z.lon),
                useRadiusInMeter: true,
                radius: 8000,
                color: c.withAlpha(76),
                borderColor: c,
                borderStrokeWidth: 2,
              );
            }).toList(),
          ),
          // Tap markers on top
          MarkerLayer(
            markers: _zones.map((z) => Marker(
              point: LatLng(z.lat, z.lon),
              width: 16, height: 16,
              child: GestureDetector(
                onTap: () => setState(() => _selectedZone = z),
                child: Container(
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: _zoneColor(z.level),
                    boxShadow: [BoxShadow(color: _zoneColor(z.level).withAlpha(153), blurRadius: 8)],
                  ),
                ),
              ),
            )).toList(),
          ),
        ],
      ),

      // Selected zone panel
      if (_selectedZone != null)
        Positioned(
          bottom: 16, left: 16, right: 16,
          child: _ZoneCard(zone: _selectedZone!, onClose: () => setState(() => _selectedZone = null)),
        ).animate().slideY(begin: 0.3, duration: 300.ms, curve: Curves.easeOut).fadeIn(),

      // Legend
      Positioned(
        top: 12, right: 12,
        child: Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: AppTheme.panel.withAlpha(230),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: AppTheme.border),
          ),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const Text('PFZ ZONES', style: TextStyle(fontSize: 8, color: AppTheme.textDim, letterSpacing: 2)),
            const SizedBox(height: 6),
            for (final e in [['HIGH', AppTheme.accent2], ['MED', AppTheme.warn], ['LOW', AppTheme.danger]])
              Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Row(children: [
                  Container(width: 10, height: 10, decoration: BoxDecoration(
                    shape: BoxShape.circle, color: e[1] as Color)),
                  const SizedBox(width: 6),
                  Text(e[0] as String, style: const TextStyle(fontSize: 10, color: AppTheme.textPrimary)),
                ]),
              ),
          ]),
        ),
      ),
    ]);
  }

  Widget _buildForecastTab() {
    final forecast = widget.forecast;
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const Text('6-DAY FORECAST', style: TextStyle(
          fontSize: 11, color: AppTheme.accent, letterSpacing: 3, fontWeight: FontWeight.bold)),
        const SizedBox(height: 16),
        if (forecast.isEmpty)
          const Center(child: Text('No forecast data available',
            style: TextStyle(color: AppTheme.textDim)))
        else
          for (int i = 0; i < forecast.length; i++)
            _ForecastCard(data: forecast[i] as Map<String, dynamic>, index: i),
      ],
    );
  }

  Widget _buildDataTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const Text('OCEAN DATA', style: TextStyle(
          fontSize: 11, color: AppTheme.accent, letterSpacing: 3, fontWeight: FontWeight.bold)),
        const SizedBox(height: 16),
        DataSummaryCard(
          title: 'SST GRID',
          value: '${widget.sstGrid.length} pts',
          icon: Icons.thermostat,
          color: AppTheme.warn,
          subtitle: 'Sea Surface Temperature',
        ),
        const SizedBox(height: 10),
        DataSummaryCard(
          title: 'CHLOROPHYLL',
          value: '${widget.chlGrid.length} pts',
          icon: Icons.eco,
          color: AppTheme.accent2,
          subtitle: 'CHL Concentration Grid',
        ),
        const SizedBox(height: 10),
        DataSummaryCard(
          title: 'PFZ ZONES',
          value: '${_zones.length} active',
          icon: Icons.location_on,
          color: AppTheme.accent,
          subtitle: 'Potential Fishing Zones',
        ),
        const SizedBox(height: 24),
        const Text('ALL ZONES', style: TextStyle(
          fontSize: 11, color: AppTheme.accent, letterSpacing: 3)),
        const SizedBox(height: 10),
        for (final z in _zones) _ZoneListTile(zone: z),
      ],
    );
  }

  Widget _buildBottomNav() {
    return Container(
      decoration: const BoxDecoration(
        color: AppTheme.panel,
        border: Border(top: BorderSide(color: AppTheme.border, width: 1)),
      ),
      child: SafeArea(
        top: false,
        child: Row(children: [
          for (int i = 0; i < 3; i++)
            Expanded(child: GestureDetector(
              onTap: () => setState(() => _bottomTab = i),
              behavior: HitTestBehavior.opaque,
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 10),
                child: Column(mainAxisSize: MainAxisSize.min, children: [
                  Icon(
                    [Icons.map, Icons.wb_sunny, Icons.bar_chart][i],
                    color: _bottomTab == i ? AppTheme.accent : AppTheme.textDim,
                    size: 20,
                  ),
                  const SizedBox(height: 3),
                  Text(
                    ['MAP', 'FORECAST', 'DATA'][i],
                    style: TextStyle(
                      fontSize: 8, letterSpacing: 1,
                      color: _bottomTab == i ? AppTheme.accent : AppTheme.textDim,
                      fontWeight: _bottomTab == i ? FontWeight.bold : FontWeight.normal,
                    ),
                  ),
                ]),
              ),
            )),
        ]),
      ),
    );
  }
}

class _ZoneCard extends StatelessWidget {
  final PfzZone zone;
  final VoidCallback onClose;
  const _ZoneCard({required this.zone, required this.onClose});

  Color get _color {
    switch (zone.level) {
      case 'high': return AppTheme.accent2;
      case 'medium': return AppTheme.warn;
      default: return AppTheme.danger;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.panel,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: _color.withAlpha(128), width: 1.5),
        boxShadow: [BoxShadow(color: _color.withAlpha(51), blurRadius: 20)],
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: _color.withAlpha(51),
              borderRadius: BorderRadius.circular(6),
              border: Border.all(color: _color.withAlpha(128)),
            ),
            child: Text('PFZ: ${zone.level.toUpperCase()}',
              style: TextStyle(fontSize: 11, color: _color, fontWeight: FontWeight.bold, letterSpacing: 1)),
          ),
          const Spacer(),
          GestureDetector(
            onTap: onClose,
            child: const Icon(Icons.close, color: AppTheme.textDim, size: 18),
          ),
        ]),
        const SizedBox(height: 12),
        Row(children: [
          if (zone.fishEn != null && zone.fishEn!.isNotEmpty) ...[
            const Icon(Icons.set_meal, color: AppTheme.accent, size: 14),
            const SizedBox(width: 6),
            Text(zone.fishEn!, style: const TextStyle(fontSize: 13, color: AppTheme.textPrimary)),
          ],
          if (zone.fishMr != null && zone.fishMr!.isNotEmpty) ...[
            const SizedBox(width: 8),
            Text('(${zone.fishMr!})', style: const TextStyle(fontSize: 11, color: AppTheme.textDim)),
          ],
        ]),
        const SizedBox(height: 10),
        Row(children: [
          _Stat('CONF', zone.confidenceScore != null ? '${zone.confidenceScore}%' : '--', _color),
          const SizedBox(width: 16),
          _Stat('SST', zone.sst != null ? '${zone.sst!.toStringAsFixed(1)}°C' : '--', AppTheme.warn),
          const SizedBox(width: 16),
          _Stat('CHL', zone.chlorophyll != null ? zone.chlorophyll!.toStringAsFixed(3) : '--', AppTheme.accent2),
          if (zone.depthM != null) ...[
            const SizedBox(width: 16),
            _Stat('DEPTH', '${zone.depthM!.toInt()}m', AppTheme.accent),
          ],
        ]),
        if (zone.bestTime != null && zone.bestTime!.isNotEmpty) ...[
          const SizedBox(height: 10),
          Row(children: [
            const Icon(Icons.access_time, color: AppTheme.textDim, size: 13),
            const SizedBox(width: 6),
            Text('Best: ${zone.bestTime!}',
              style: const TextStyle(fontSize: 11, color: AppTheme.textDim)),
          ]),
        ],
      ]),
    );
  }
}

class _Stat extends StatelessWidget {
  final String label;
  final String value;
  final Color color;
  const _Stat(this.label, this.value, this.color);

  @override
  Widget build(BuildContext context) => Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
    Text(label, style: const TextStyle(fontSize: 8, color: AppTheme.textDim, letterSpacing: 1)),
    const SizedBox(height: 2),
    Text(value, style: TextStyle(fontSize: 13, color: color, fontWeight: FontWeight.bold)),
  ]);
}

class _ZoneListTile extends StatelessWidget {
  final PfzZone zone;
  const _ZoneListTile({required this.zone});

  Color get _color {
    switch (zone.level) {
      case 'high': return AppTheme.accent2;
      case 'medium': return AppTheme.warn;
      default: return AppTheme.danger;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppTheme.panel,
        borderRadius: BorderRadius.circular(8),
        border: Border(left: BorderSide(color: _color, width: 3)),
      ),
      child: Row(children: [
        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(zone.fishEn ?? 'Unknown Species',
            style: const TextStyle(fontSize: 13, color: AppTheme.textPrimary, fontWeight: FontWeight.bold)),
          const SizedBox(height: 3),
          Text('${zone.lat.toStringAsFixed(4)}°N, ${zone.lon.toStringAsFixed(4)}°E',
            style: const TextStyle(fontSize: 10, color: AppTheme.textDim)),
        ])),
        Column(crossAxisAlignment: CrossAxisAlignment.end, children: [
          Text(zone.level.toUpperCase(),
            style: TextStyle(fontSize: 10, color: _color, fontWeight: FontWeight.bold, letterSpacing: 1)),
          if (zone.confidenceScore != null)
            Text('${zone.confidenceScore}%', style: const TextStyle(fontSize: 11, color: AppTheme.textDim)),
        ]),
      ]),
    );
  }
}

class _ForecastCard extends StatelessWidget {
  final Map<String, dynamic> data;
  final int index;
  const _ForecastCard({required this.data, required this.index});

  @override
  Widget build(BuildContext context) {
    final date = data['date'] ?? data['day'] ?? 'Day ${index + 1}';
    final sst  = data['sst']?.toString();
    final wind = data['wind_speed']?.toString() ?? data['wind']?.toString();
    final wave = data['wave_height']?.toString() ?? data['wave']?.toString();
    final fish = (data['fish_score'] ?? data['score'])?.toString();

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppTheme.panel,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: AppTheme.border),
      ),
      child: Row(children: [
        Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('$date', style: const TextStyle(fontSize: 11, color: AppTheme.accent, letterSpacing: 1)),
          const SizedBox(height: 6),
          Row(children: [
            if (sst != null) _Tag('SST $sst°C', AppTheme.warn),
            if (wind != null) ...[const SizedBox(width: 8), _Tag('WIND $wind kt', AppTheme.accent)],
            if (wave != null) ...[const SizedBox(width: 8), _Tag('WAVE ${wave}m', AppTheme.accent2)],
          ]),
        ]),
        const Spacer(),
        if (fish != null)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
            decoration: BoxDecoration(
              color: AppTheme.accent2.withAlpha(30),
              borderRadius: BorderRadius.circular(6),
              border: Border.all(color: AppTheme.accent2.withAlpha(76)),
            ),
            child: Text(fish, style: const TextStyle(fontSize: 14, color: AppTheme.accent2, fontWeight: FontWeight.bold)),
          ),
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
    decoration: BoxDecoration(
      color: color.withAlpha(30), borderRadius: BorderRadius.circular(4),
    ),
    child: Text(label, style: TextStyle(fontSize: 9, color: color, letterSpacing: 0.5)),
  );
}
