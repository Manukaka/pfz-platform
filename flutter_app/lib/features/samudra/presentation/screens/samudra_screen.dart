import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:webview_flutter/webview_flutter.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../l10n/app_localizations.dart';
import '../../../../shared/providers/locale_provider.dart';

class SamudraScreen extends ConsumerStatefulWidget {
  const SamudraScreen({super.key});

  @override
  ConsumerState<SamudraScreen> createState() => _SamudraScreenState();
}

class _SamudraScreenState extends ConsumerState<SamudraScreen> {
  late final WebViewController _webViewController;
  bool _isLoading = true;

  static const _baseUrl = 'https://incois.gov.in/portal/osf/osf.jsp';

  static const Map<String, String> _langUrls = {
    'mr': 'https://incois.gov.in/portal/osf/osf.jsp?lang=mr',
    'gu': 'https://incois.gov.in/portal/osf/osf.jsp?lang=gu',
    'hi': 'https://incois.gov.in/portal/osf/osf.jsp?lang=hi',
    'kn': 'https://incois.gov.in/portal/osf/osf.jsp?lang=kn',
    'ml': 'https://incois.gov.in/portal/osf/osf.jsp?lang=ml',
    'en': 'https://incois.gov.in/portal/osf/osf.jsp',
    'kok': 'https://incois.gov.in/portal/osf/osf.jsp',
  };

  @override
  void initState() {
    super.initState();
    final locale = ref.read(localeProvider);
    final url = _langUrls[locale.languageCode] ?? _baseUrl;

    _webViewController = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setNavigationDelegate(NavigationDelegate(
        onPageStarted: (_) => setState(() => _isLoading = true),
        onPageFinished: (_) => setState(() => _isLoading = false),
        onWebResourceError: (_) => setState(() => _isLoading = false),
      ))
      ..loadRequest(Uri.parse(url));
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.samudraTitle),
        backgroundColor: AppTheme.deepBlue,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: () => _webViewController.reload(),
          ),
          IconButton(
            icon: const Icon(Icons.open_in_browser_rounded),
            onPressed: () async {
              // Open in external browser
              final locale = ref.read(localeProvider);
              final url = _langUrls[locale.languageCode] ?? _baseUrl;
              _webViewController.loadRequest(Uri.parse(url));
            },
          ),
        ],
      ),
      body: Stack(
        children: [
          WebViewWidget(controller: _webViewController),
          if (_isLoading)
            const Center(child: CircularProgressIndicator()),
        ],
      ),
    );
  }
}
