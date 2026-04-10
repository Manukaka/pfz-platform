import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../core/theme.dart';
import '../services/api_service.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _userCtrl = TextEditingController();
  final _passCtrl = TextEditingController();
  bool _loading = false;
  String _error = '';
  bool _obscure = true;

  Future<void> _login() async {
    final u = _userCtrl.text.trim();
    final p = _passCtrl.text.trim();
    if (u.isEmpty || p.isEmpty) {
      setState(() => _error = 'Enter username and password');
      return;
    }
    setState(() { _loading = true; _error = ''; });
    try {
      await ApiService.instance.login(u, p);
      if (!mounted) return;
      // After login, go to splash to preload data
      Navigator.pushReplacementNamed(context, '/splash');
    } catch (e) {
      setState(() { _error = 'Invalid credentials'; _loading = false; });
    }
  }

  @override
  void dispose() {
    _userCtrl.dispose();
    _passCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.bg,
      body: Stack(children: [
        Positioned.fill(child: CustomPaint(painter: _BgPainter())),
        SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 24),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // Logo + title
                  Container(
                    width: 80, height: 80,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(color: AppTheme.accent.withAlpha(76), width: 1.5),
                      boxShadow: [BoxShadow(color: AppTheme.accent.withAlpha(51), blurRadius: 24)],
                    ),
                    child: const Icon(Icons.waves, color: AppTheme.accent, size: 36),
                  ).animate().scale(duration: 600.ms, curve: Curves.elasticOut),

                  const SizedBox(height: 20),
                  const Text('दर्यासागर',
                    style: TextStyle(fontSize: 26, fontWeight: FontWeight.bold,
                      color: AppTheme.accent, letterSpacing: 4,
                      shadows: [Shadow(color: AppTheme.accent, blurRadius: 16)]),
                  ).animate().fadeIn(delay: 200.ms),
                  const SizedBox(height: 4),
                  const Text('FISHERMEN LOGIN',
                    style: TextStyle(fontSize: 10, color: AppTheme.textDim, letterSpacing: 3),
                  ).animate().fadeIn(delay: 300.ms),
                  const SizedBox(height: 8),
                  const Text('Admin: use your password\nFishermen: enter name + access key',
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 11, color: AppTheme.textDim, height: 1.5),
                  ).animate().fadeIn(delay: 400.ms),

                  const SizedBox(height: 32),

                  // Login form card
                  Container(
                    padding: const EdgeInsets.all(24),
                    decoration: BoxDecoration(
                      color: AppTheme.panel,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AppTheme.border),
                      boxShadow: [BoxShadow(color: Colors.black.withAlpha(128), blurRadius: 30)],
                    ),
                    child: Column(children: [
                      TextFormField(
                        controller: _userCtrl,
                        style: const TextStyle(color: AppTheme.textPrimary),
                        decoration: const InputDecoration(
                          labelText: 'USERNAME / YOUR NAME',
                          prefixIcon: Icon(Icons.person_outline, color: AppTheme.textDim, size: 18),
                        ),
                        textInputAction: TextInputAction.next,
                      ),
                      const SizedBox(height: 16),
                      TextFormField(
                        controller: _passCtrl,
                        obscureText: _obscure,
                        style: const TextStyle(color: AppTheme.textPrimary),
                        decoration: InputDecoration(
                          labelText: 'PASSWORD / ACCESS KEY',
                          prefixIcon: const Icon(Icons.lock_outline, color: AppTheme.textDim, size: 18),
                          suffixIcon: IconButton(
                            icon: Icon(_obscure ? Icons.visibility_off : Icons.visibility,
                                color: AppTheme.textDim, size: 18),
                            onPressed: () => setState(() => _obscure = !_obscure),
                          ),
                        ),
                        textInputAction: TextInputAction.done,
                        onFieldSubmitted: (_) => _login(),
                      ),

                      if (_error.isNotEmpty) ...[
                        const SizedBox(height: 12),
                        Text(_error,
                          style: const TextStyle(color: AppTheme.danger, fontSize: 12),
                        ).animate().shake(),
                      ],

                      const SizedBox(height: 24),
                      SizedBox(
                        width: double.infinity,
                        height: 48,
                        child: ElevatedButton(
                          onPressed: _loading ? null : _login,
                          child: _loading
                              ? const SizedBox(width: 20, height: 20,
                                  child: CircularProgressIndicator(strokeWidth: 2, color: Colors.black))
                              : const Text('LOGIN', style: TextStyle(letterSpacing: 2)),
                        ),
                      ),
                    ]),
                  ).animate().fadeIn(delay: 400.ms).slideY(begin: 0.15),
                ],
              ),
            ),
          ),
        ),
      ]),
    );
  }
}

class _BgPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topLeft, end: Alignment.bottomRight,
        colors: [const Color(0xFF050c1a), const Color(0xFF0a1628), const Color(0xFF071220)],
        stops: const [0.0, 0.6, 1.0],
      ).createShader(Rect.fromLTWH(0, 0, size.width, size.height));
    canvas.drawRect(Rect.fromLTWH(0, 0, size.width, size.height), paint);
  }
  @override
  bool shouldRepaint(covariant CustomPainter old) => false;
}
