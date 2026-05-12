import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../core/constants.dart';
import '../models/pfz_zone.dart';
import '../models/ai_zone.dart';
import '../models/incois_zone.dart';

class ApiService {
  static ApiService? _instance;
  static ApiService get instance => _instance ??= ApiService._();
  ApiService._();

  String? _token;
  String? _savedUsername;
  String? _savedPassword;
  String? get token => _token;
  String? get savedUsername => _savedUsername;
  String? get savedPassword => _savedPassword;
  bool get isLoggedIn => _token != null;

  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    _token          = prefs.getString('samudra_token');
    _savedUsername  = prefs.getString('samudra_username');
    _savedPassword  = prefs.getString('samudra_password');
  }

  Map<String, String> get _authHeaders => {
    'Authorization': 'Bearer $_token',
    'Content-Type': 'application/json',
  };

  Future<Map<String, dynamic>> login(String username, String password) async {
    try {
      final r = await http.post(
        Uri.parse(kApiLogin),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'username': username, 'password': password}),
      ).timeout(const Duration(seconds: 60)); // 60s for Render cold-start
      if (r.statusCode == 200) {
        final data = jsonDecode(r.body) as Map<String, dynamic>;
        _token = data['token'] as String;
        _savedUsername = username;
        _savedPassword = password;
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('samudra_token',    _token!);
        await prefs.setString('samudra_username', username);
        await prefs.setString('samudra_password', password);
        await prefs.setString('samudra_role', (data['user']?['role'] ?? '') as String);
        return data;
      }
      if (r.statusCode == 401) throw Exception('auth:Invalid credentials');
      throw Exception('server:Server error (${r.statusCode})');
    } on Exception {
      rethrow;
    } catch (_) {
      throw Exception('network:Server offline — check connection');
    }
  }

  /// Checks session with the server.
  /// Returns true  → session valid.
  /// Returns false → network/server error (offline) — caller should proceed with cached data.
  /// Throws        → 401 or explicit auth failure — caller must re-login.
  Future<bool> checkSessionSafe() async {
    if (_token == null) throw Exception('Not logged in');
    try {
      final r = await http.get(Uri.parse(kApiSession), headers: _authHeaders)
          .timeout(const Duration(seconds: 12));
      if (r.statusCode == 200) return true;
      if (r.statusCode == 401) throw Exception('Session expired');
      return false; // 5xx or other → treat as server-side issue, allow offline
    } catch (e) {
      final msg = e.toString();
      if (msg.contains('Session expired') || msg.contains('401')) rethrow;
      return false; // network error / timeout → offline mode
    }
  }

  /// Clears only the session token. Keeps saved username/password for offline re-login.
  Future<void> logout() async {
    _token = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('samudra_token');
    await prefs.remove('samudra_role');
    // intentionally keep samudra_username and samudra_password for offline re-login
  }

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
        final geometry = f['geometry'] as Map<String, dynamic>?;
        final lat = props['center_lat'];
        final lon = props['center_lon'] ?? props['center_lng'];
        if (lat == null || lon == null) continue;
        zones.add(PfzZone.fromGeoJson(props, geometry));
      }
      return zones;
    }
    throw Exception('Failed to load PFZ data');
  }

  Future<List<Map<String, double>>> fetchSstGrid() async {
    final r = await http.get(Uri.parse(kApiSstData)).timeout(const Duration(seconds: 20));
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

  Future<List<Map<String, double>>> fetchChlGrid() async {
    final r = await http.get(Uri.parse(kApiChlData)).timeout(const Duration(seconds: 20));
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

  Future<List<Map<String, double>>> fetchWindGrid() async {
    final r = await http.get(
      Uri.parse('$kApiWindLive?_t=${DateTime.now().millisecondsSinceEpoch}'),
    ).timeout(const Duration(seconds: 20));
    if (r.statusCode == 200) {
      final data = jsonDecode(r.body) as Map<String, dynamic>;
      final points = (data['points'] as List?) ?? (data['data'] as List?) ?? [];
      final result = <Map<String, double>>[];
      for (final p in points) {
        try {
          result.add({
            'lat':   (p['lat'] as num).toDouble(),
            'lon':   (p['lon'] as num).toDouble(),
            'speed': ((p['speed'] ?? p['wind_speed'] ?? 0) as num).toDouble(),
            'dir':   ((p['dir'] ?? p['direction'] ?? 0) as num).toDouble(),
          });
        } catch (_) {}
      }
      return result;
    }
    return [];
  }

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

  Future<List<IncoisZone>> fetchIncoisZones() async {
    final r = await http.get(
      Uri.parse('$kApiIncois?_t=${DateTime.now().millisecondsSinceEpoch}'),
    ).timeout(const Duration(seconds: 15));
    if (r.statusCode != 200) return [];
    final body = jsonDecode(r.body);
    final zones = <IncoisZone>[];
    if (body is Map && body['features'] != null) {
      for (final f in (body['features'] as List)) {
        final props = (f['properties'] ?? {}) as Map<String, dynamic>;
        final lat = props['center_lat'] ?? props['lat'] ?? props['latitude'];
        final lon = props['center_lon'] ?? props['center_lng'] ?? props['lon'] ?? props['longitude'];
        if (lat == null || lon == null) continue;
        zones.add(IncoisZone.fromJson({...props, 'lat': lat, 'lon': lon}));
      }
    } else if (body is List) {
      for (final item in body) {
        try { zones.add(IncoisZone.fromJson(item as Map<String, dynamic>)); } catch (_) {}
      }
    } else if (body is Map && body['zones'] != null) {
      for (final item in (body['zones'] as List)) {
        try { zones.add(IncoisZone.fromJson(item as Map<String, dynamic>)); } catch (_) {}
      }
    }
    return zones;
  }

  Future<List<AiZone>> fetchAiZones() async {
    try {
      final r = await http.post(
        Uri.parse(kApiAgentsClaude),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({}),
      ).timeout(const Duration(seconds: 45));
      if (r.statusCode != 200) return [];
      final body = jsonDecode(r.body);
      // Backend wraps response: {"status": "success", "data": {"zones": [...]}}
      // Unwrap data envelope if present
      final data = (body is Map && body['data'] != null) ? body['data'] : body;
      final List rawZones = data is List
          ? data
          : (data['zones'] ?? data['pfz_zones'] ?? data['hotspots'] ?? []) as List;
      final zones = <AiZone>[];
      for (final item in rawZones) {
        try {
          final m = item as Map<String, dynamic>;
          final lat = m['center_lat'] ?? m['lat'] ?? m['latitude'];
          final lon = m['center_lon'] ?? m['center_lng'] ?? m['lon'] ?? m['lng'] ?? m['longitude'];
          if (lat == null || lon == null) continue;
          zones.add(AiZone.fromJson({...m, 'lat': lat, 'lon': lon}));
        } catch (_) {}
      }
      return zones;
    } catch (_) {
      return [];
    }
  }

  Future<List<AiZone>> fetchGeminiZones() async {
    try {
      final r = await http.post(
        Uri.parse(kApiAgentsGemini),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({}),
      ).timeout(const Duration(seconds: 45));
      if (r.statusCode != 200) return [];
      final body = jsonDecode(r.body);
      final data = (body is Map && body['data'] != null) ? body['data'] : body;
      final List rawZones = data is List
          ? data
          : (data['zones'] ?? data['pfz_zones'] ?? data['hotspots'] ?? []) as List;
      final zones = <AiZone>[];
      for (final item in rawZones) {
        try {
          final m = item as Map<String, dynamic>;
          final lat = m['center_lat'] ?? m['lat'] ?? m['latitude'];
          final lon = m['center_lon'] ?? m['center_lng'] ?? m['lon'] ?? m['lng'] ?? m['longitude'];
          if (lat == null || lon == null) continue;
          zones.add(AiZone.fromJson({...m, 'lat': lat, 'lon': lon}));
        } catch (_) {}
      }
      return zones;
    } catch (_) {
      return [];
    }
  }

  Future<Map<String, dynamic>> fetchDataStatus() async {
    try {
      final r = await http.get(Uri.parse(kApiDataStatus)).timeout(const Duration(seconds: 10));
      if (r.statusCode == 200) return jsonDecode(r.body) as Map<String, dynamic>;
    } catch (_) {}
    return {};
  }
}
