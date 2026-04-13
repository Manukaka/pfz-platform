class IncoisZone {
  final double lat;
  final double lon;
  final String? date;
  final String source;
  final String? region;
  final String? description;

  const IncoisZone({
    required this.lat,
    required this.lon,
    this.date,
    this.source = 'incois',
    this.region,
    this.description,
  });

  factory IncoisZone.fromJson(Map<String, dynamic> j) => IncoisZone(
    lat: (j['lat'] ?? j['center_lat'] ?? j['latitude'] ?? 0).toDouble(),
    lon: (j['lon'] ?? j['lng'] ?? j['center_lon'] ?? j['center_lng'] ?? j['longitude'] ?? 0).toDouble(),
    date: j['date'] ?? j['advisory_date'],
    source: j['source'] ?? 'incois',
    region: j['region'] ?? j['area'],
    description: j['description'] ?? j['remarks'],
  );
}
