class AiZone {
  final double lat;
  final double lon;
  final String level;
  final String? fishEn;
  final String? fishMr;
  final String? fishHi;
  final int? confidence;
  final String? region;
  final double? sst;
  final double? chl;
  final String? bestTime;
  final String? depthRange;
  final String? reasoning;
  final String? windRisk;
  // Polygon boundary vertices as [lon, lat] pairs
  final List<List<double>>? coordinates;

  const AiZone({
    required this.lat,
    required this.lon,
    required this.level,
    this.fishEn,
    this.fishMr,
    this.fishHi,
    this.confidence,
    this.region,
    this.sst,
    this.chl,
    this.bestTime,
    this.depthRange,
    this.reasoning,
    this.windRisk,
    this.coordinates,
  });

  factory AiZone.fromJson(Map<String, dynamic> j) {
    // Parse fish species from structured array (Claude agent format)
    String? fishEn, fishMr, fishHi;
    final species = j['fish_species'] as List<dynamic>?;
    if (species != null && species.isNotEmpty) {
      final first = species[0] as Map<String, dynamic>;
      fishEn = first['name_en'] as String?;
      fishMr = first['name_mr'] as String?;
      fishHi = first['name_hi'] as String?;
    } else {
      // Fallback for older/simple format
      fishEn = j['fish_en'] as String? ?? j['primary_species'] as String? ?? j['fish'] as String?;
      fishMr = j['fish_mr'] as String?;
      fishHi = j['fish_hi'] as String?;
    }

    // Parse confidence: Claude returns 0.0-1.0 float → convert to 0-100 int
    int? confidence;
    final rawConf = j['confidence'];
    if (rawConf != null) {
      final f = (rawConf as num).toDouble();
      confidence = f <= 1.0 ? (f * 100).toInt() : f.toInt();
    }

    // Parse polygon coordinates [[lon, lat], ...]
    List<List<double>>? coordinates;
    final rawCoords = j['coordinates'] as List<dynamic>?;
    if (rawCoords != null && rawCoords.length >= 3) {
      try {
        coordinates = rawCoords.map((c) {
          final pair = c as List<dynamic>;
          return [
            (pair[0] as num).toDouble(),
            (pair[1] as num).toDouble(),
          ];
        }).toList();
      } catch (_) {}
    }

    return AiZone(
      lat: (j['center_lat'] ?? j['lat'] ?? j['latitude'] ?? 0).toDouble(),
      lon: (j['center_lon'] ?? j['center_lng'] ?? j['lon'] ?? j['lng'] ?? j['longitude'] ?? 0).toDouble(),
      level: (j['type'] ?? j['confidence_level'] ?? j['level'] ?? 'medium') as String,
      fishEn: fishEn,
      fishMr: fishMr,
      fishHi: fishHi,
      confidence: confidence,
      region: j['region'] as String?,
      sst: j['sst'] != null ? (j['sst'] as num).toDouble() : null,
      chl: (j['chl'] ?? j['chlorophyll']) != null
          ? ((j['chl'] ?? j['chlorophyll']) as num).toDouble()
          : null,
      bestTime: j['best_fishing_time'] as String? ?? j['best_time'] as String? ?? j['optimal_time'] as String?,
      depthRange: j['depth_range'] as String?,
      reasoning: j['reasoning'] as String?,
      windRisk: j['wind_risk'] as String?,
      coordinates: coordinates,
    );
  }
}
