import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../shared/models/pfz_zone.dart';
import '../../../core/network/api_client.dart';

final nearbyPfzZonesProvider = FutureProvider<List<PfzZone>>((ref) async {
  final client = ref.read(apiClientProvider);
  return client.getNearbyZones();
});

final safetyStatusProvider = FutureProvider<SafetyStatus>((ref) async {
  final client = ref.read(apiClientProvider);
  return client.getSafetyStatus();
});

class SafetyStatus {
  final int score;
  final String color;
  final String message;
  final double waveHeight;
  final double windSpeed;
  final double currentStrength;
  final double sst;

  const SafetyStatus({
    required this.score,
    required this.color,
    required this.message,
    required this.waveHeight,
    required this.windSpeed,
    required this.currentStrength,
    this.sst = 29.0,
  });

  factory SafetyStatus.fromJson(Map<String, dynamic> json) {
    return SafetyStatus(
      score: json['score'] as int,
      color: json['color'] as String,
      message: json['message'] as String,
      waveHeight: (json['wave_height'] as num).toDouble(),
      windSpeed: (json['wind_speed'] as num).toDouble(),
      currentStrength: (json['current_strength'] as num).toDouble(),
      sst: (json['sst'] as num?)?.toDouble() ?? 29.0,
    );
  }

  static SafetyStatus get defaultSafe => const SafetyStatus(
        score: 15,
        color: 'green',
        message: 'Safe conditions',
        waveHeight: 0.8,
        windSpeed: 12.0,
        currentStrength: 0.4,
        sst: 29.0,
      );
}
