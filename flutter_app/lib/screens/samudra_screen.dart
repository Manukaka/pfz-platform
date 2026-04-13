import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:webview_flutter/webview_flutter.dart';
import '../core/theme.dart';

class SamudraScreen extends StatefulWidget {
  const SamudraScreen({super.key});

  @override
  State<SamudraScreen> createState() => _SamudraScreenState();
}

class _SamudraScreenState extends State<SamudraScreen> {
  late final WebViewController _controller;
  bool _loading = true;
  String? _error;
  bool _autoLoginAttempted = false;

  static const String _url = 'https://samudra.incois.gov.in/index.jsp';
  static const String _email = 'manojdhamdhere@live.com';
  static const String _pass  = 'Ashu@9970';

  static const String _autoLoginJs = r'''
    (function() {
      // Try all common login field selectors
      var emailSelectors = [
        'input[type="email"]',
        'input[name*="email" i]', 'input[name*="user" i]',
        'input[id*="email" i]',  'input[id*="user" i]',
        'input[placeholder*="email" i]', 'input[placeholder*="user" i]',
      ];
      var emailField = null;
      for (var s of emailSelectors) {
        emailField = document.querySelector(s);
        if (emailField) break;
      }
      var passField = document.querySelector('input[type="password"]');
      if (emailField) {
        emailField.focus();
        emailField.value = 'manojdhamdhere@live.com';
        emailField.dispatchEvent(new Event('input',  {bubbles:true}));
        emailField.dispatchEvent(new Event('change', {bubbles:true}));
      }
      if (passField) {
        passField.focus();
        passField.value = 'Ashu@9970';
        passField.dispatchEvent(new Event('input',  {bubbles:true}));
        passField.dispatchEvent(new Event('change', {bubbles:true}));
      }
      // Submit the form
      var submitSelectors = [
        'button[type="submit"]', 'input[type="submit"]',
        'button.login-btn', 'button.btn-login', 'button.signin',
        '#loginBtn', '#submitBtn', '.login-button',
      ];
      for (var s of submitSelectors) {
        var btn = document.querySelector(s);
        if (btn) { btn.click(); break; }
      }
      // Also try submitting the form directly
      if (emailField) {
        var form = emailField.closest('form');
        if (form) form.submit();
      }
    })();
  ''';

  @override
  void initState() {
    super.initState();
    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setNavigationDelegate(NavigationDelegate(
        onPageStarted: (_) => setState(() { _loading = true; _error = null; }),
        onPageFinished: _onPageFinished,
        onWebResourceError: (e) => setState(() { _loading = false; _error = e.description; }),
      ))
      ..loadRequest(Uri.parse(_url));
  }

  Future<void> _launchSamudraApp() async {
    // Try to launch the INCOIS Samudra Android app
    const samudraPackage = 'in.gov.incois.samudra';
    final playStoreUri = Uri.parse('https://play.google.com/store/apps/details?id=$samudraPackage');
    final intentUri = Uri.parse('android-app://$samudraPackage');
    try {
      if (await canLaunchUrl(intentUri)) {
        await launchUrl(intentUri);
        return;
      }
    } catch (_) {}
    // Fallback: open Play Store listing
    try {
      await launchUrl(playStoreUri, mode: LaunchMode.externalApplication);
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Could not open Samudra app. Install from Play Store.')));
      }
    }
  }

  Future<void> _onPageFinished(String url) async {
    if (!mounted) return;
    setState(() => _loading = false);
    // Auto-login only once per session, only on the login/index page
    final isLoginPage = url.contains('index.jsp') || url.contains('login') ||
        url == _url || (!url.contains('/home') && !url.contains('/dashboard') &&
        !url.contains('/pfz') && !url.contains('/map'));
    if (isLoginPage && !_autoLoginAttempted) {
      _autoLoginAttempted = true;
      await Future.delayed(const Duration(milliseconds: 1500));
      try {
        await _controller.runJavaScript(_autoLoginJs);
      } catch (_) {}
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.bg,
      body: Column(children: [
        // Top bar
        Container(
          height: 56,
          decoration: const BoxDecoration(
            color: AppTheme.panel,
            border: Border(bottom: BorderSide(color: AppTheme.border, width: 1.5)),
          ),
          child: SafeArea(
            bottom: false,
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 14),
              child: Row(children: [
                GestureDetector(
                  onTap: () => Navigator.of(context).pop(),
                  child: const Icon(Icons.arrow_back_ios, color: AppTheme.accent, size: 18),
                ),
                const SizedBox(width: 12),
                const Expanded(child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('INCOIS SAMUDRA 2.0', style: TextStyle(
                      fontSize: 13, fontWeight: FontWeight.bold,
                      color: AppTheme.warn, letterSpacing: 1.5)),
                    Text('samudra.incois.gov.in', style: TextStyle(
                      fontSize: 9, color: AppTheme.textDim)),
                  ],
                )),
                GestureDetector(
                  onTap: () async {
                    _autoLoginAttempted = false;
                    await _controller.runJavaScript(_autoLoginJs);
                  },
                  child: const Tooltip(message: 'Auto-fill login',
                    child: Icon(Icons.login, color: AppTheme.accent2, size: 20)),
                ),
                const SizedBox(width: 10),
                GestureDetector(
                  onTap: () => _launchSamudraApp(),
                  child: const Tooltip(message: 'Open Samudra APK',
                    child: Icon(Icons.open_in_new, color: AppTheme.warn, size: 20)),
                ),
                const SizedBox(width: 10),
                GestureDetector(
                  onTap: () => _controller.reload(),
                  child: const Icon(Icons.refresh, color: AppTheme.accent, size: 20),
                ),
                const SizedBox(width: 10),
                GestureDetector(
                  onTap: () {
                    _autoLoginAttempted = false;
                    _controller.loadRequest(Uri.parse(_url));
                  },
                  child: const Icon(Icons.home, color: AppTheme.textDim, size: 20),
                ),
              ]),
            ),
          ),
        ),
        // Loading indicator
        if (_loading) const LinearProgressIndicator(
          color: AppTheme.accent, backgroundColor: AppTheme.panel, minHeight: 2),
        // Error state
        if (_error != null)
          Container(
            padding: const EdgeInsets.all(16),
            color: AppTheme.danger.withAlpha(30),
            child: Row(children: [
              const Icon(Icons.wifi_off, color: AppTheme.danger, size: 16),
              const SizedBox(width: 8),
              Expanded(child: Text('Could not load INCOIS portal. Check internet connection.',
                style: const TextStyle(fontSize: 12, color: AppTheme.textDim))),
              GestureDetector(
                onTap: () => _controller.loadRequest(Uri.parse(_url)),
                child: const Text('Retry', style: TextStyle(color: AppTheme.accent, fontSize: 12)),
              ),
            ]),
          ),
        // WebView
        Expanded(child: WebViewWidget(controller: _controller)),
      ]),
    );
  }
}
