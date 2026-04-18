class PfzZone {
  final String id;
  final String state;
  final double confidence;
  final String source;
  final List<List<double>> polygon;
  final double centerLat;
  final double centerLon;
  final Map<String, double> speciesProbability;
  final double sst;
  final double chlorophyll;
  final DateTime validFrom;
  final DateTime validUntil;
  final double distanceFromShoreKm;
  final String safetyStatus;
  final double? distanceFromUserKm;

  const PfzZone({
    required this.id,
    required this.state,
    required this.confidence,
    required this.source,
    required this.polygon,
    required this.centerLat,
    required this.centerLon,
    required this.speciesProbability,
    required this.sst,
    required this.chlorophyll,
    required this.validFrom,
    required this.validUntil,
    required this.distanceFromShoreKm,
    required this.safetyStatus,
    this.distanceFromUserKm,
  });

  factory PfzZone.fromJson(Map<String, dynamic> json) {
    return PfzZone(
      id: json['zone_id'] as String,
      state: json['state'] as String,
      confidence: (json['confidence'] as num).toDouble(),
      source: json['source'] as String,
      polygon: (json['polygon'] as List)
          .map((p) => (p as List).map((v) => (v as num).toDouble()).toList())
          .toList(),
      centerLat: (json['center'][1] as num).toDouble(),
      centerLon: (json['center'][0] as num).toDouble(),
      speciesProbability: Map<String, double>.from(
        (json['species_probability'] as Map).map(
          (k, v) => MapEntry(k as String, (v as num).toDouble()),
        ),
      ),
      sst: (json['environmental_factors']['sst'] as num).toDouble(),
      chlorophyll: (json['environmental_factors']['chlorophyll'] as num).toDouble(),
      validFrom: DateTime.parse(json['valid_from'] as String),
      validUntil: DateTime.parse(json['valid_until'] as String),
      distanceFromShoreKm: (json['distance_from_shore_km'] as num).toDouble(),
      safetyStatus: json['safety_status'] as String,
      distanceFromUserKm: json['distance_from_user_km'] != null
          ? (json['distance_from_user_km'] as num).toDouble()
          : null,
    );
  }

  String get topSpecies {
    if (speciesProbability.isEmpty) return '';
    return speciesProbability.entries
        .reduce((a, b) => a.value > b.value ? a : b)
        .key;
  }

  bool get isValid => DateTime.now().isBefore(validUntil);
}
