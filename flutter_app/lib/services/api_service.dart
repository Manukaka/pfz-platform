import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../core/constants.dart';
import '../models/pfz_zone.dart';

class ApiService {
  static ApiService? _instance;
  static ApiService get instance => _instance ??= ApiService._();
  ApiService._();

  String? _token;

  String? get token => _token;
  bool get isLoggedIn => _token != null;

  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('samudra_token');
  }

  Map<String, String> get _authHeaders => {
    'Authorization': 'Bearer $_token',
    'Content-Type': 'application/json',
  };

  // ── AUTH ─────────────────────────────────────────────────────────────────
  Future<Map<String, dynamic>> login(String username, String password) async {
    final r = await http.post(
      Uri.parse(kApiLogin),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'username': username, 'password': password}),
    ).timeout(const Duration(seconds: 15));

    if (r.statusCode == 200) {
      final data = jsonDecode(r.body) as Map<String, dynamic>;
      _token = data['token'] as String;
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('samudra_token', _token!);
      await prefs.setString('samudra_role', (data['user']?['role'] ?? '') as String);
      return data;
    }
    throw Exception('Invalid credentials');
  }

  Future<Map<String, dynamic>> checkSession() async {
    if (_token == null) throw Exception('Not logged in');
    final r = await http.get(
      Uri.parse(kApiSession),
      headers: _authHeaders,
    ).timeout(const Duration(seconds: 12));
    if (r.statusCode == 200) return jsonDecode(r.body) as Map<String, dynamic>;
    throw Exception('Session expired');
  }

  Future<void> logout() async {
    _token = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('samudra_token');
    await prefs.remove('samudra_role');
  }

  // ── PFZ DATA ──────────────────────────────────────────────────────────────
  Future<List<PfzZone>> fetchPfzZones() async {
    final r = await http.get(
      Uri.parse('$kApiPfzLive?_t=${DateTime.now().millisecondsSinceEpoch}'),
      headers: _token != null ? _authHeaders : {},
    ).timeout(const Duration(seconds: 20));

    if (r.statusCode == 200) {
      final geojson = jsonDecode(r.body) as Map<String, dynamic>;
      final features = (geojson['features'] as List?) ?? [];
      final zones = <PfzZone>[];
      for (final f in features) {
        final props = f['properties'] as Map<String, dynamic>;
        final lat = props['center_lat'];
        final lon = props['center_lon'] ?? props['center_lng'];
        if (lat == null || lon == null) continue;
        zones.add(PfzZone.fromJson(props));
      }
      return zones;
    }
    throw Exception('Failed to load PFZ data');
  }

  // ── SST GRID ──────────────────────────────────────────────────────────────
  Future<List<Map<String, double>>> fetchSstGrid() async {
    final r = await http.get(Uri.parse(kApiSstData))
        .timeout(const Duration(seconds: 20));
    if (r.statusCode == 200) {
      final data = jsonDecode(r.body) as Map<String, dynamic>;
      final points = (data['points'] as List?) ?? [];
      return points.map((p) => {
        'lat': (p['lat'] as num).toDouble(),
        'lon': (p['lon'] as num).toDouble(),
        'sst': (p['sst'] as num).toDouble(),
      }).toList();
    }
    return [];
  }

  // ── CHL GRID ──────────────────────────────────────────────────────────────
  Future<List<Map<String, double>>> fetchChlGrid() async {
    final r = await http.get(Uri.parse(kApiChlData))
        .timeout(const Duration(seconds: 20));
    if (r.statusCode == 200) {
      final data = jsonDecode(r.body) as Map<String, dynamic>;
      final points = (data['points'] as List?) ?? [];
      return points.map((p) => {
        'lat': (p['lat'] as num).toDouble(),
        'lon': (p['lon'] as num).toDouble(),
        'chl': (p['chl'] as num).toDouble(),
      }).toList();
    }
    return [];
  }

  // ── 6-DAY FORECAST ────────────────────────────────────────────────────────
  Future<List<dynamic>> fetchForecast() async {
    final r = await http.get(
      Uri.parse('$kApiForecast?_t=${DateTime.now().millisecondsSinceEpoch}'),
    ).timeout(const Duration(seconds: 15));
    if (r.statusCode == 200) {
      final data = jsonDecode(r.body);
      return (data is List) ? data : (data['forecast'] as List? ?? []);
    }
    return [];
  }

  // ── INCOIS ALERTS ─────────────────────────────────────────────────────────
  Future<Map<String, dynamic>> fetchIncois() async {
    final r = await http.get(
      Uri.parse('$kApiIncois?_t=${DateTime.now().millisecondsSinceEpoch}'),
    ).timeout(const Duration(seconds: 15));
    if (r.statusCode == 200) return jsonDecode(r.body) as Map<String, dynamic>;
    return {};
  }
}
