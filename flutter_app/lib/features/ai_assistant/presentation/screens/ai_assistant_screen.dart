import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'package:flutter_tts/flutter_tts.dart';

import '../../../../core/network/api_client.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../l10n/app_localizations.dart';
import '../../../../shared/providers/locale_provider.dart';

class AiAssistantScreen extends ConsumerStatefulWidget {
  const AiAssistantScreen({super.key});

  @override
  ConsumerState<AiAssistantScreen> createState() => _AiAssistantScreenState();
}

class _AiAssistantScreenState extends ConsumerState<AiAssistantScreen> {
  final _controller = TextEditingController();
  final _scrollController = ScrollController();
  final _stt = SpeechToText();
  final _tts = FlutterTts();

  final List<_Message> _messages = [];
  bool _isListening = false;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _tts.setLanguage('mr-IN');
  }

  Future<void> _send(String text) async {
    if (text.trim().isEmpty) return;
    _controller.clear();
    setState(() {
      _messages.add(_Message(text: text, isUser: true));
      _isLoading = true;
    });
    _scrollToBottom();

    try {
      final locale = ref.read(localeProvider);
      final client = ref.read(apiClientProvider);
      final result = await client.queryAI(text, locale.languageCode);
      final answer = result['answer'] as String? ?? 'No response';

      setState(() {
        _messages.add(_Message(text: answer, isUser: false));
        _isLoading = false;
      });
      _scrollToBottom();
      await _tts.speak(answer);
    } catch (e) {
      setState(() {
        _messages.add(_Message(text: 'Error: $e', isUser: false, isError: true));
        _isLoading = false;
      });
    }
  }

  Future<void> _startListening() async {
    final available = await _stt.initialize();
    if (!available) return;
    final locale = ref.read(localeProvider);
    setState(() => _isListening = true);
    await _stt.listen(
      onResult: (r) {
        if (r.finalResult) {
          setState(() => _isListening = false);
          _send(r.recognizedWords);
        }
      },
      localeId: '${locale.languageCode}_IN',
    );
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    _stt.cancel();
    _tts.stop();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.aiTitle),
        backgroundColor: AppTheme.deepBlue,
        foregroundColor: Colors.white,
      ),
      body: Column(
        children: [
          Expanded(
            child: _messages.isEmpty
                ? _EmptyState(l10n: l10n)
                : ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.all(16),
                    itemCount: _messages.length + (_isLoading ? 1 : 0),
                    itemBuilder: (context, index) {
                      if (index == _messages.length) {
                        return const _TypingIndicator();
                      }
                      return _MessageBubble(message: _messages[index]);
                    },
                  ),
          ),
          _InputBar(
            controller: _controller,
            isListening: _isListening,
            onSend: () => _send(_controller.text),
            onVoice: _startListening,
            l10n: l10n,
          ),
        ],
      ),
    );
  }
}

class _Message {
  final String text;
  final bool isUser;
  final bool isError;
  _Message({required this.text, required this.isUser, this.isError = false});
}

class _MessageBubble extends StatelessWidget {
  final _Message message;
  const _MessageBubble({required this.message});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: message.isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.78,
        ),
        decoration: BoxDecoration(
          color: message.isUser
              ? AppTheme.oceanBlue
              : message.isError
                  ? Colors.red[50]
                  : Colors.grey[100],
          borderRadius: BorderRadius.circular(16),
        ),
        child: Text(
          message.text,
          style: TextStyle(
            color: message.isUser ? Colors.white : Colors.black87,
          ),
        ),
      ),
    );
  }
}

class _TypingIndicator extends StatelessWidget {
  const _TypingIndicator();

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.grey[100],
          borderRadius: BorderRadius.circular(16),
        ),
        child: const Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            SizedBox(
              width: 40,
              height: 16,
              child: LinearProgressIndicator(),
            ),
          ],
        ),
      ),
    );
  }
}

class _EmptyState extends StatelessWidget {
  final AppLocalizations l10n;
  const _EmptyState({required this.l10n});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.assistant_rounded, size: 64, color: AppTheme.oceanBlue),
          const SizedBox(height: 16),
          Text(
            l10n.aiTitle,
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 8),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 32),
            child: Text(
              l10n.aiPlaceholder,
              textAlign: TextAlign.center,
              style: const TextStyle(color: Colors.grey),
            ),
          ),
        ],
      ),
    );
  }
}

class _InputBar extends StatelessWidget {
  final TextEditingController controller;
  final bool isListening;
  final VoidCallback onSend;
  final VoidCallback onVoice;
  final AppLocalizations l10n;

  const _InputBar({
    required this.controller,
    required this.isListening,
    required this.onSend,
    required this.onVoice,
    required this.l10n,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.only(
        left: 12,
        right: 12,
        top: 8,
        bottom: MediaQuery.of(context).padding.bottom + 8,
      ),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: controller,
              decoration: InputDecoration(
                hintText: l10n.aiPlaceholder,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(24),
                  borderSide: BorderSide.none,
                ),
                filled: true,
                fillColor: Colors.grey[100],
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 10,
                ),
              ),
              onSubmitted: (_) => onSend(),
            ),
          ),
          const SizedBox(width: 8),
          IconButton(
            onPressed: onVoice,
            icon: Icon(
              isListening ? Icons.mic_rounded : Icons.mic_none_rounded,
              color: isListening ? Colors.red : AppTheme.oceanBlue,
            ),
            tooltip: l10n.aiVoiceHint,
          ),
          IconButton(
            onPressed: onSend,
            icon: const Icon(Icons.send_rounded, color: AppTheme.oceanBlue),
          ),
        ],
      ),
    );
  }
}
