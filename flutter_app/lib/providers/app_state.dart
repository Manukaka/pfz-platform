import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';
import '../models/ai_zone.dart';
import '../models/incois_zone.dart';
import '../models/pfz_zone.dart';

class AppState extends ChangeNotifier {
  final SharedPreferences _prefs;

  AppState(this._prefs) {
    _lang = _prefs.getString('lang') ?? 'en';
    _showSst = _prefs.getBool('showSst') ?? true;
    _showChl = _prefs.getBool('showChl') ?? false;
    _showWind = _prefs.getBool('showWind') ?? false;
    _showAlgo = _prefs.getBool('showAlgo') ?? true;
    _showAi = _prefs.getBool('showAi') ?? true;
    _showIncois = _prefs.getBool('showIncois') ?? true;
    _showGemini = _prefs.getBool('showGemini') ?? true;
    _showTunaOnly = _prefs.getBool('showTunaOnly') ?? false;
  }

  // ── Language ──────────────────────────────────────────────────────────────
  String _lang = 'en';
  String get lang => _lang;
  void setLang(String l) {
    _lang = l;
    _prefs.setString('lang', l);
    notifyListeners();
  }

  // ── Layer Toggles ─────────────────────────────────────────────────────────
  bool _showSst = true;
  bool _showChl = false;
  bool _showWind = false;
  bool _showAlgo = true;
  bool _showAi = true;
  bool _showIncois = true;
  bool _showGemini = true;
  bool _showTunaOnly = false;

  bool get showSst => _showSst;
  bool get showChl => _showChl;
  bool get showWind => _showWind;
  bool get showAlgo => _showAlgo;
  bool get showAi => _showAi;
  bool get showIncois => _showIncois;
  bool get showGemini => _showGemini;
  bool get showTunaOnly => _showTunaOnly;

  void toggle(String key) {
    switch (key) {
      case 'sst':     _showSst    = !_showSst;    _prefs.setBool('showSst', _showSst); break;
      case 'chl':     _showChl    = !_showChl;    _prefs.setBool('showChl', _showChl); break;
      case 'wind':    _showWind   = !_showWind;   _prefs.setBool('showWind', _showWind); break;
      case 'algo':    _showAlgo   = !_showAlgo;   _prefs.setBool('showAlgo', _showAlgo); break;
      case 'ai':      _showAi     = !_showAi;     _prefs.setBool('showAi', _showAi); break;
      case 'incois':  _showIncois = !_showIncois; _prefs.setBool('showIncois', _showIncois); break;
      case 'gemini':  _showGemini = !_showGemini; _prefs.setBool('showGemini', _showGemini); break;
      case 'tuna':    _showTunaOnly = !_showTunaOnly; _prefs.setBool('showTunaOnly', _showTunaOnly); break;
    }
    notifyListeners();
  }

  // ── Data Status ───────────────────────────────────────────────────────────
  Map<String, dynamic> _dataStatus = {};
  Map<String, dynamic> get dataStatus => _dataStatus;

  // ── Cached Data (shared across screens) ──────────────────────────────────
  List<PfzZone> algoZones = [];
  List<AiZone> aiZones = [];
  List<AiZone> geminiZones = [];
  List<IncoisZone> incoisZones = [];
  List<Map<String, double>> sstGrid = [];
  List<Map<String, double>> chlGrid = [];
  List<Map<String, double>> windGrid = [];
  List<dynamic> forecast = [];
  bool isLoading = false;
  String? error;

  // ── Polling ───────────────────────────────────────────────────────────────
  Timer? _statusTimer;
  Timer? _dataTimer;

  void startPolling() {
    _fetchDataStatus();
    _fetchAllData();
    _statusTimer = Timer.periodic(const Duration(seconds: 60), (_) => _fetchDataStatus());
    _dataTimer   = Timer.periodic(const Duration(minutes: 5), (_) => _fetchAllData());
  }

  Future<void> _fetchDataStatus() async {
    try {
      final s = await ApiService.instance.fetchDataStatus();
      _dataStatus = s;
      notifyListeners();
    } catch (_) {}
  }

  Future<void> fetchAll() => _fetchAllData();

  Future<void> _fetchAllData() async {
    if (isLoading) return;
    isLoading = true;
    error = null;
    notifyListeners();
    try {
      final results = await Future.wait([
        ApiService.instance.fetchPfzZones().onError((_, __) => <PfzZone>[]),
        ApiService.instance.fetchForecast().onError((_, __) => <dynamic>[]),
        ApiService.instance.fetchSstGrid().onError((_, __) => <Map<String,double>>[]),
        ApiService.instance.fetchChlGrid().onError((_, __) => <Map<String,double>>[]),
        ApiService.instance.fetchWindGrid().onError((_, __) => <Map<String,double>>[]),
        ApiService.instance.fetchAiZones().onError((_, __) => <AiZone>[]),
        ApiService.instance.fetchIncoisZones().onError((_, __) => <IncoisZone>[]),
        ApiService.instance.fetchGeminiZones().onError((_, __) => <AiZone>[]),
      ]);
      algoZones    = results[0] as List<PfzZone>;
      forecast     = results[1];
      sstGrid      = results[2] as List<Map<String,double>>;
      chlGrid      = results[3] as List<Map<String,double>>;
      windGrid     = results[4] as List<Map<String,double>>;
      aiZones      = results[5] as List<AiZone>;
      incoisZones  = results[6] as List<IncoisZone>;
      geminiZones  = results[7] as List<AiZone>;
    } catch (e) {
      error = e.toString();
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  @override
  void dispose() {
    _statusTimer?.cancel();
    _dataTimer?.cancel();
    super.dispose();
  }
}
