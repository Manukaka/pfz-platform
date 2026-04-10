import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../core/theme.dart';
import '../services/api_service.dart';
import 'map_screen.dart';
import 'login_screen.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});
  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  String _status = 'INITIALISING...';
  double _progress = 0.05;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _boot());
  }

  void _set(String msg, double pct) {
    if (!mounted) return;
    setState(() { _status = msg; _progress = pct; });
  }

  Future<void> _boot() async {
    await ApiService.instance.init();
    _set('CONNECTING TO SERVER...', 0.15);

    if (!ApiService.instance.isLoggedIn) {
      await Future.delayed(const Duration(milliseconds: 600));
      _goLogin();
      return;
    }

    // Validate session
    try {
      await ApiService.instance.checkSession();
    } catch (_) {
      await ApiService.instance.logout();
      _goLogin();
      return;
    }

    // Preload all critical data in parallel
    _set('LOADING PFZ ZONES...', 0.35);
    final pfzFuture  = ApiService.instance.fetchPfzZones().catchError((_) => <dynamic>[]);

    _set('LOADING SST DATA...', 0.50);
    final sstFuture  = ApiService.instance.fetchSstGrid().catchError((_) => <dynamic>[]);

    _set('LOADING CHL DATA...', 0.65);
    final chlFuture  = ApiService.instance.fetchChlGrid().catchError((_) => <dynamic>[]);

    _set('LOADING FORECAST...', 0.80);
    final forecastFuture = ApiService.instance.fetchForecast().catchError((_) => <dynamic>[]);

    final results = await Future.wait([pfzFuture, sstFuture, chlFuture, forecastFuture])
        .timeout(const Duration(seconds: 20), onTimeout: () => [[], [], [], []]);

    _set('READY', 1.0);
    await Future.delayed(const Duration(milliseconds: 500));

    if (!mounted) return;
    Navigator.pushReplacement(context, MaterialPageRoute(
      builder: (_) => MapScreen(
        pfzZones: results[0] as dynamic,
        sstGrid:  results[1] as dynamic,
        chlGrid:  results[2] as dynamic,
        forecast: results[3] as dynamic,
      ),
    ));
  }

  void _goLogin() {
    if (!mounted) return;
    Navigator.pushReplacement(context,
        MaterialPageRoute(builder: (_) => const LoginScreen()));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.bg,
      body: Stack(children: [
        // Animated ocean background glow
        Positioned.fill(child: CustomPaint(painter: _OceanGlowPainter())),

        Center(child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Logo
            Container(
              width: 120, height: 120,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(color: AppTheme.accent.withAlpha(76), width: 2),
                boxShadow: [BoxShadow(color: AppTheme.accent.withAlpha(51), blurRadius: 40, spreadRadius: 5)],
              ),
              child: const _FishLogo(),
            )
            .animate().scale(begin: const Offset(0.5, 0.5), duration: 800.ms,
                curve: Curves.elasticOut),

            const SizedBox(height: 28),

            // Title
            Text('दर्यासागर',
              style: const TextStyle(
                fontSize: 30, fontWeight: FontWeight.bold,
                color: AppTheme.accent, letterSpacing: 6,
                shadows: [Shadow(color: AppTheme.accent, blurRadius: 20)],
              ),
            ).animate().fadeIn(delay: 400.ms, duration: 500.ms).slideY(begin: 0.3),

            const SizedBox(height: 6),
            const Text('DARYASAGAR  •  समुद्र',
              style: TextStyle(fontSize: 11, color: Color(0x8000c8ff), letterSpacing: 3),
            ).animate().fadeIn(delay: 600.ms),

            const SizedBox(height: 8),
            const Text('मच्छिमारांसाठी बुद्धिमान मार्गदर्शन',
              style: TextStyle(fontSize: 12, color: Color(0xB3e0f0ff), letterSpacing: 1),
            ).animate().fadeIn(delay: 800.ms),

            const SizedBox(height: 48),

            // Status
            Text(_status,
              style: const TextStyle(
                fontSize: 10, color: Color(0xB300c8ff), letterSpacing: 2,
              ),
            ).animate(key: ValueKey(_status)).fadeIn(duration: 300.ms),

            const SizedBox(height: 12),

            // Progress bar
            Container(
              width: 200, height: 3,
              decoration: BoxDecoration(
                color: AppTheme.accent.withAlpha(30),
                borderRadius: BorderRadius.circular(2),
              ),
              child: FractionallySizedBox(
                alignment: Alignment.centerLeft,
                widthFactor: _progress,
                child: Container(
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [AppTheme.accent, AppTheme.accent2],
                    ),
                    borderRadius: BorderRadius.circular(2),
                    boxShadow: [BoxShadow(color: AppTheme.accent.withAlpha(128), blurRadius: 6)],
                  ),
                ),
              ),
            ).animate(key: ValueKey(_progress))
             .custom(duration: 400.ms, curve: Curves.easeOut, builder: (_, __, child) => child!),

            const SizedBox(height: 50),

            // Bouncing dots
            Row(mainAxisAlignment: MainAxisAlignment.center, children: [
              for (int i = 0; i < 3; i++) ...[
                Container(
                  width: 6, height: 6,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: i == 1 ? AppTheme.accent2 : AppTheme.accent,
                  ),
                ).animate(onPlay: (c) => c.repeat())
                 .scale(begin: const Offset(0.6, 0.6), end: const Offset(1.2, 1.2),
                        delay: Duration(milliseconds: i * 200),
                        duration: 600.ms)
                 .then().scale(begin: const Offset(1.2, 1.2), end: const Offset(0.6, 0.6), duration: 600.ms),
                if (i < 2) const SizedBox(width: 8),
              ]
            ]),
          ],
        )),

        // Version
        Positioned(
          bottom: 24, left: 0, right: 0,
          child: Center(
            child: Text('v1.0  |  Maharashtra Coast',
              style: const TextStyle(fontSize: 9, color: Color(0x807090a0), letterSpacing: 1),
            ).animate().fadeIn(delay: 1200.ms),
          ),
        ),
      ]),
    );
  }
}

class _FishLogo extends StatelessWidget {
  const _FishLogo();
  @override
  Widget build(BuildContext context) => CustomPaint(painter: _FishPainter(), size: const Size(120, 120));
}

class _FishPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final cx = size.width / 2;
    final cy = size.height / 2;

    // Background
    final bgPaint = Paint()..color = const Color(0xFF0a1628);
    canvas.drawCircle(Offset(cx, cy), 54, bgPaint);

    // Ocean glow
    final glowPaint = Paint()
      ..shader = RadialGradient(
        colors: [const Color(0x2E00c8ff), Colors.transparent],
        center: const Alignment(0, 0.6),
      ).createShader(Rect.fromCircle(center: Offset(cx, cy), radius: 54));
    canvas.drawCircle(Offset(cx, cy), 54, glowPaint);

    // Circle border
    final borderPaint = Paint()
      ..color = const Color(0xFF00c8ff)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.5;
    canvas.drawCircle(Offset(cx, cy), 54, borderPaint);

    // Fish body
    final fishPaint = Paint()..color = const Color(0xFF00c8ff);
    canvas.drawOval(Rect.fromCenter(center: Offset(cx - 4, cy - 8), width: 38, height: 20), fishPaint);

    // Tail
    final tailPath = Path()
      ..moveTo(cx + 15, cy - 8)
      ..lineTo(cx + 30, cy - 19)
      ..lineTo(cx + 32, cy - 8)
      ..lineTo(cx + 30, cy + 3)
      ..close();
    canvas.drawPath(tailPath, Paint()..color = const Color(0xFF00ff88));

    // Eye
    canvas.drawCircle(Offset(cx - 17, cy - 11), 3, Paint()..color = const Color(0xFF0a1628));
    canvas.drawCircle(Offset(cx - 17.8, cy - 11.8), 1, Paint()..color = Colors.white54);

    // Signal arcs (AI)
    final arcPaint = Paint()
      ..color = const Color(0xFF00ff88)
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round
      ..strokeWidth = 2.2;
    canvas.drawArc(Rect.fromCenter(center: Offset(cx, cy - 22), width: 32, height: 16),
        3.5, 3.42, false, arcPaint..strokeWidth = 2.2..color = const Color(0xFF00ff88));
    canvas.drawArc(Rect.fromCenter(center: Offset(cx, cy - 22), width: 44, height: 22),
        3.5, 3.42, false, arcPaint..strokeWidth = 1.4..color = const Color(0x8C00ff88));

    // Signal dot
    canvas.drawCircle(Offset(cx, cy - 27), 3, Paint()..color = const Color(0xFF00ff88));
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class _OceanGlowPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..shader = RadialGradient(
        colors: [const Color(0x1400c8ff), Colors.transparent],
        center: const Alignment(0, 0),
      ).createShader(Rect.fromLTWH(0, 0, size.width, size.height));
    canvas.drawRect(Rect.fromLTWH(0, 0, size.width, size.height), paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
