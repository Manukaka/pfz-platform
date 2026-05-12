import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';

import '../constants/app_constants.dart';

class LocationData {
  final double lat;
  final double lon;
  final bool isReal;

  const LocationData({
    required this.lat,
    required this.lon,
    required this.isReal,
  });

  static LocationData get fallback => const LocationData(
        lat: AppConstants.defaultLat,
        lon: AppConstants.defaultLon,
        isReal: false,
      );
}

class LocationService {
  Future<LocationData> getCurrentLocation() async {
    try {
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }
      if (permission == LocationPermission.deniedForever ||
          permission == LocationPermission.denied) {
        return LocationData.fallback;
      }

      final position = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.high,
          timeLimit: Duration(seconds: 10),
        ),
      );
      return LocationData(
        lat: position.latitude,
        lon: position.longitude,
        isReal: true,
      );
    } catch (_) {
      return LocationData.fallback;
    }
  }
}

final locationServiceProvider = Provider<LocationService>((ref) {
  return LocationService();
});

final currentLocationProvider = FutureProvider<LocationData>((ref) async {
  final service = ref.read(locationServiceProvider);
  return service.getCurrentLocation();
});
