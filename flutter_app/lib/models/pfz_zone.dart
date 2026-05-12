class PfzZone {
  final double lat;
  final double lon;
  final double? sst;
  final double? chlorophyll;
  final int? confidenceScore;
  final String? fishEn;
  final String? fishMr;
  final String level; // high / medium / low
  final String? bestTime;
  final double? depthM;
  /// Line coordinates from GeoJSON LineString geometry [[lon,lat], ...]
  final List<List<double>>? lineCoords;

  PfzZone({
    required this.lat,
    required this.lon,
    this.sst,
    this.chlorophyll,
    this.confidenceScore,
    this.fishEn,
    this.fishMr,
    required this.level,
    this.bestTime,
    this.depthM,
    this.lineCoords,
  });

  /// Parse from GeoJSON feature: pass both feature['properties'] and feature['geometry']
  factory PfzZone.fromGeoJson(Map<String, dynamic> props, Map<String, dynamic>? geometry) {
    final score = (props['confidence_score'] as num?)?.toInt();
    final level = score == null ? 'medium'
                : score >= 70 ? 'high'
                : score >= 50 ? 'medium' : 'low';

    List<List<double>>? lineCoords;
    if (geometry != null && geometry['coordinates'] is List) {
      try {
        final rawCoords = geometry['coordinates'] as List;
        if (rawCoords.isNotEmpty && rawCoords[0] is List) {
          lineCoords = rawCoords.map((c) {
            final pair = c as List;
            return [(pair[0] as num).toDouble(), (pair[1] as num).toDouble()];
          }).toList();
        }
      } catch (_) {}
    }

    return PfzZone(
      lat: (props['center_lat'] as num).toDouble(),
      lon: (props['center_lon'] as num?)?.toDouble() ??
           (props['center_lng'] as num?)?.toDouble() ?? 0,
      sst: (props['sst'] as num?)?.toDouble(),
      chlorophyll: (props['chlorophyll'] as num?)?.toDouble() ??
                   (props['chl'] as num?)?.toDouble(),
      confidenceScore: score,
      fishEn: props['fish_en'] as String?,
      fishMr: props['fish_mr'] as String?,
      level: level,
      bestTime: props['best_fishing_time'] as String?,
      depthM: (props['depth_m'] as num?)?.toDouble(),
      lineCoords: lineCoords,
    );
  }

  factory PfzZone.fromJson(Map<String, dynamic> props) => PfzZone.fromGeoJson(props, null);
}
