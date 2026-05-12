import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:retry/retry.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../constants/app_constants.dart';
import '../../shared/models/pfz_zone.dart';
import '../../features/home/providers/home_providers.dart';

final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient();
});

// Retry 3 times with exponential backoff; only retry on network/timeout errors.
const _retry = RetryOptions(maxAttempts: 3);

bool _isRetryable(Exception e) =>
    e is DioException &&
    e.type != DioExceptionType.badResponse &&
    e.type != DioExceptionType.cancel;

class ApiClient {
  late final Dio _dio;

  ApiClient() {
    _dio = Dio(BaseOptions(
      baseUrl: AppConstants.apiBaseUrl,
      connectTimeout: AppConstants.apiTimeout,
      receiveTimeout: AppConstants.apiTimeout,
      headers: {'Content-Type': 'application/json'},
    ));
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        final token = Supabase.instance.client.auth.currentSession?.accessToken;
        if (token != null && token.isNotEmpty) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
    ));
    _dio.interceptors.add(LogInterceptor(responseBody: false));
  }

  Future<List<PfzZone>> getNearbyZones({
    double? lat,
    double? lon,
    double radiusKm = 100,
  }) async {
    try {
      final response = await _retry.retry(
        () => _dio.get(
          '/api/v1/pfz/nearby',
          queryParameters: _queryParameters({
            'lat': lat,
            'lon': lon,
            'radius_km': radiusKm,
          }),
        ),
        retryIf: _isRetryable,
      );
      final List<dynamic> data = response.data['zones'] as List;
      return data.map((j) => PfzZone.fromJson(j as Map<String, dynamic>)).toList();
    } on DioException {
      return [];
    }
  }

  Future<SafetyStatus> getSafetyStatus({double? lat, double? lon}) async {
    try {
      final response = await _retry.retry(
        () => _dio.get(
          '/api/v1/safety/current',
          queryParameters: _queryParameters({'lat': lat, 'lon': lon}),
        ),
        retryIf: _isRetryable,
      );
      return SafetyStatus.fromJson(response.data as Map<String, dynamic>);
    } on DioException {
      return SafetyStatus.defaultSafe;
    }
  }

  Future<Map<String, dynamic>> queryAI(String query, String language) async {
    // AI queries are not retried — each attempt costs tokens.
    final response = await _dio.post(
      '/api/v1/ai/query',
      data: {'query': query, 'language': language},
    );
    return response.data as Map<String, dynamic>;
  }

  Future<List<Map<String, dynamic>>> getAlerts({String? state}) async {
    try {
      final response = await _retry.retry(
        () => _dio.get(
          '/api/v1/alerts',
          queryParameters: _queryParameters({'state': state}),
        ),
        retryIf: _isRetryable,
      );
      return List<Map<String, dynamic>>.from(response.data['alerts'] as List);
    } on DioException {
      return [];
    }
  }

  Future<void> logCatch(Map<String, dynamic> catchData) async {
    await _retry.retry(
      () => _dio.post('/api/v1/catch', data: catchData),
      retryIf: _isRetryable,
    );
  }

  Map<String, dynamic> _queryParameters(Map<String, Object?> values) {
    return {
      for (final entry in values.entries)
        if (entry.value != null) entry.key: entry.value,
    };
  }
}
