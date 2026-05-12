import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import 'package:mapbox_maps_flutter/mapbox_maps_flutter.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../../../../core/constants/app_constants.dart';

class PfzRealtimeLayer extends StatefulWidget {
  final MapboxMap map;
  const PfzRealtimeLayer({super.key, required this.map});

  @override
  State<PfzRealtimeLayer> createState() => _PfzRealtimeLayerState();
}

class _PfzRealtimeLayerState extends State<PfzRealtimeLayer> {
  WebSocketChannel? _channel;
  StreamSubscription? _sub;
  bool _connected = false;

  @override
  void initState() {
    super.initState();
    _connect();
    _addMapLayers();
  }

  Future<void> _addMapLayers() async {
    await _ensureSource();

    // Add PFZ fill layer
    try {
      await widget.map.style.addLayer(FillLayer(
        id: 'pfz-fill',
        sourceId: 'pfz-source',
        fillColor: Colors.cyan.withValues(alpha: 0.3).toARGB32(),
        fillOpacity: 0.5,
      ));
    } catch (_) {}

    // Add PFZ outline layer
    try {
      await widget.map.style.addLayer(LineLayer(
        id: 'pfz-outline',
        sourceId: 'pfz-source',
        lineColor: Colors.cyan.toARGB32(),
        lineWidth: 2.0,
      ));
    } catch (_) {}
    await _loadInitialZones();
  }

  Future<void> _ensureSource() async {
    try {
      await widget.map.style.getSource('pfz-source');
    } catch (_) {
      await widget.map.style.addSource(GeoJsonSource(
        id: 'pfz-source',
        data: jsonEncode({
          'type': 'FeatureCollection',
          'features': [],
        }),
      ));
    }
  }

  void _connect() {
    try {
      _channel = WebSocketChannel.connect(
        Uri.parse('${AppConstants.wsBaseUrl}/ws/pfz'),
      );
      setState(() => _connected = true);

      _sub = _channel!.stream.listen(
        _onMessage,
        onDone: () {
          setState(() => _connected = false);
          Future.delayed(AppConstants.wsReconnectDelay, _connect);
        },
        onError: (_) {
          setState(() => _connected = false);
          Future.delayed(AppConstants.wsReconnectDelay, _connect);
        },
      );
    } catch (_) {
      Future.delayed(AppConstants.wsReconnectDelay, _connect);
    }
  }

  void _onMessage(dynamic data) {
    try {
      final json = jsonDecode(data as String) as Map<String, dynamic>;
      if (json['type'] == 'pfz_update') {
        _updatePfzLayer(json['zones'] as List);
      }
    } catch (_) {}
  }

  Future<void> _updatePfzLayer(List zones) async {
    final features = zones.map((z) => {
      'type': 'Feature',
      'geometry': {
        'type': 'Polygon',
        'coordinates': [z['polygon']],
      },
      'properties': {
        'confidence': z['confidence'],
        'state': z['state'],
        'species': z['top_species'],
      },
    }).toList();

    await _setFeatureCollection(features);
  }

  Future<void> _loadInitialZones() async {
    try {
      final response = await Dio().get('${AppConstants.apiBaseUrl}/api/v1/pfz/geojson');
      final data = response.data;
      if (data is Map<String, dynamic>) {
        final features = data['features'];
        if (features is List) {
          await _setFeatureCollection(features);
        }
      }
    } catch (_) {}
  }

  Future<void> _setFeatureCollection(List features) async {
    final geojson = jsonEncode({
      'type': 'FeatureCollection',
      'features': features,
    });

    try {
      final source = await widget.map.style.getSource('pfz-source') as GeoJsonSource;
      source.updateGeoJSON(geojson);
    } catch (_) {}
  }

  @override
  void dispose() {
    _sub?.cancel();
    _channel?.sink.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!_connected) {
      return Positioned(
        bottom: 20,
        left: 12,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
          decoration: BoxDecoration(
            color: Colors.orange.withValues(alpha: 0.9),
            borderRadius: BorderRadius.circular(8),
          ),
          child: const Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.wifi_off_rounded, color: Colors.white, size: 14),
              SizedBox(width: 4),
              Text('Offline', style: TextStyle(color: Colors.white, fontSize: 12)),
            ],
          ),
        ),
      );
    }
    return const Positioned(
      bottom: 20,
      left: 12,
      child: SizedBox.shrink(),
    );
  }
}
