import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../constants/app_constants.dart';
import '../../shared/models/pfz_zone.dart';
import '../../features/home/providers/home_providers.dart';

final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient();
});

class ApiClient {
  late final Dio _dio;

  ApiClient() {
    _dio = Dio(BaseOptions(
      baseUrl: AppConstants.apiBaseUrl,
      connectTimeout: AppConstants.apiTimeout,
      receiveTimeout: AppConstants.apiTimeout,
      headers: {'Content-Type': 'application/json'},
    ));
    _dio.interceptors.add(LogInterceptor(responseBody: false));
  }

  Future<List<PfzZone>> getNearbyZones({
    double? lat,
    double? lon,
    double radiusKm = 100,
  }) async {
    try {
      final response = await _dio.get(
        '/api/v1/pfz/nearby',
        queryParameters: {
          if (lat != null) 'lat': lat,
          if (lon != null) 'lon': lon,
          'radius_km': radiusKm,
        },
      );
      final List<dynamic> data = response.data['zones'] as List;
      return data.map((j) => PfzZone.fromJson(j as Map<String, dynamic>)).toList();
    } on DioException {
      return [];
    }
  }

  Future<SafetyStatus> getSafetyStatus({double? lat, double? lon}) async {
    try {
      final response = await _dio.get(
        '/api/v1/safety/current',
        queryParameters: {
          if (lat != null) 'lat': lat,
          if (lon != null) 'lon': lon,
        },
      );
      return SafetyStatus.fromJson(response.data as Map<String, dynamic>);
    } on DioException {
      return SafetyStatus.defaultSafe;
    }
  }

  Future<Map<String, dynamic>> queryAI(String query, String language) async {
    final response = await _dio.post(
      '/api/v1/ai/query',
      data: {'query': query, 'language': language},
    );
    return response.data as Map<String, dynamic>;
  }

  Future<List<Map<String, dynamic>>> getAlerts({String? state}) async {
    try {
      final response = await _dio.get(
        '/api/v1/alerts',
        queryParameters: {if (state != null) 'state': state},
      );
      return List<Map<String, dynamic>>.from(response.data['alerts'] as List);
    } on DioException {
      return [];
    }
  }

  Future<void> logCatch(Map<String, dynamic> catchData) async {
    await _dio.post('/api/v1/catch', data: catchData);
  }
}
