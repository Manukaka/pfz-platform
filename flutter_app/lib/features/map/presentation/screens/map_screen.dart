import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mapbox_maps_flutter/mapbox_maps_flutter.dart';

import '../../../../core/constants/app_constants.dart';
import '../../../../l10n/app_localizations.dart';
import '../widgets/map_layer_panel.dart';
import '../widgets/pfz_realtime_layer.dart';

class MapScreen extends ConsumerStatefulWidget {
  const MapScreen({super.key});

  @override
  ConsumerState<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends ConsumerState<MapScreen> {
  MapboxMap? _mapboxMap;
  bool _layerPanelOpen = false;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    return Scaffold(
      body: Stack(
        children: [
          MapWidget(
            key: const ValueKey('mainMap'),
            onMapCreated: _onMapCreated,
            cameraOptions: CameraOptions(
              center: Point(
                coordinates: Position(
                  AppConstants.defaultLon,
                  AppConstants.defaultLat,
                ),
              ),
              zoom: AppConstants.defaultZoom,
            ),
            styleUri: MapboxStyles.DARK,
          ),

          // Top bar
          Positioned(
            top: MediaQuery.of(context).padding.top + 8,
            left: 12,
            right: 12,
            child: Row(
              children: [
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    decoration: BoxDecoration(
                      color: Colors.black87,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      l10n.mapTitle,
                      style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                _MapButton(
                  icon: Icons.layers_rounded,
                  onTap: () => setState(() => _layerPanelOpen = !_layerPanelOpen),
                ),
              ],
            ),
          ),

          // PFZ real-time layer overlay
          if (_mapboxMap != null)
            PfzRealtimeLayer(map: _mapboxMap!),

          // Layer panel
          if (_layerPanelOpen)
            Positioned(
              top: MediaQuery.of(context).padding.top + 70,
              right: 12,
              child: MapLayerPanel(
                onClose: () => setState(() => _layerPanelOpen = false),
              ),
            ),

          // Zoom controls
          Positioned(
            right: 12,
            bottom: 80,
            child: Column(
              children: [
                _MapButton(
                  icon: Icons.add_rounded,
                  onTap: () => _zoom(1),
                ),
                const SizedBox(height: 8),
                _MapButton(
                  icon: Icons.remove_rounded,
                  onTap: () => _zoom(-1),
                ),
                const SizedBox(height: 8),
                _MapButton(
                  icon: Icons.my_location_rounded,
                  onTap: _goToMyLocation,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _onMapCreated(MapboxMap map) {
    setState(() => _mapboxMap = map);
  }

  Future<void> _zoom(double delta) async {
    final camera = await _mapboxMap?.getCameraState();
    if (camera != null) {
      _mapboxMap?.setCamera(CameraOptions(zoom: camera.zoom + delta));
    }
  }

  Future<void> _goToMyLocation() async {
    // TODO: get actual GPS location
    _mapboxMap?.setCamera(CameraOptions(
      center: Point(
        coordinates: Position(AppConstants.defaultLon, AppConstants.defaultLat),
      ),
      zoom: 9.0,
    ));
  }
}

class _MapButton extends StatelessWidget {
  final IconData icon;
  final VoidCallback onTap;
  const _MapButton({required this.icon, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 44,
        height: 44,
        decoration: BoxDecoration(
          color: Colors.black87,
          borderRadius: BorderRadius.circular(10),
        ),
        child: Icon(icon, color: Colors.white, size: 22),
      ),
    );
  }
}
