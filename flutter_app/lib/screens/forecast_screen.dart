import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/theme.dart';
import '../l10n/strings.dart';
import '../providers/app_state.dart';

class ForecastScreen extends StatelessWidget {
  const ForecastScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final state    = context.watch<AppState>();
    final lang     = state.lang;
    final forecast = state.forecast;

    return Scaffold(
      backgroundColor: AppTheme.bg,
      body: Column(children: [
        _TopBar(
          title: S.t('forecast_title', lang),
          onRefresh: () => state.fetchAll(),
          isLoading: state.isLoading,
          onPdf: () => Navigator.pushNamed(context, '/pdf'),
        ),
        Expanded(child: forecast.isEmpty && state.isLoading
          ? const Center(child: CircularProgressIndicator(color: AppTheme.accent))
          : forecast.isEmpty
          ? Center(child: Text(S.t('no_forecast', lang),
              style: const TextStyle(color: AppTheme.textDim)))
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: forecast.length,
              itemBuilder: (ctx, i) =>
                _ForecastDayCard(data: forecast[i] as Map<String, dynamic>, index: i, lang: lang),
            ),
        ),
      ]),
    );
  }
}

class _TopBar extends StatelessWidget {
  final String title;
  final VoidCallback onRefresh;
  final VoidCallback onPdf;
  final bool isLoading;
  const _TopBar({required this.title, required this.onRefresh, required this.onPdf, required this.isLoading});

  @override
  Widget build(BuildContext context) {
    return Container(
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
            Text(title, style: const TextStyle(
              fontSize: 13, fontWeight: FontWeight.bold,
              color: AppTheme.textPrimary, letterSpacing: 2)),
            const Spacer(),
            GestureDetector(
              onTap: onPdf,
              child: const Icon(Icons.picture_as_pdf, color: AppTheme.warn, size: 20),
            ),
            const SizedBox(width: 12),
            GestureDetector(
              onTap: onRefresh,
              child: isLoading
                ? const SizedBox(width: 20, height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2, color: AppTheme.accent))
                : const Icon(Icons.refresh, color: AppTheme.accent, size: 20),
            ),
          ]),
        ),
      ),
    );
  }
}

class _ForecastDayCard extends StatelessWidget {
  final Map<String, dynamic> data;
  final int index;
  final String lang;
  const _ForecastDayCard({required this.data, required this.index, required this.lang});

  @override
  Widget build(BuildContext context) {
    final date   = data['date'] ?? data['day'] ?? 'Day ${index + 1}';
    final sst    = data['sst']?.toString();
    final wind   = (data['wind_speed'] ?? data['wind'])?.toString();
    final wave   = (data['wave_height'] ?? data['wave'])?.toString();
    final score  = (data['fish_score'] ?? data['score'] ?? 0) as num;
    final hotspots = (data['hotspots'] as List?)?.cast<Map<String, dynamic>>() ?? [];
    final uncertainty = (data['uncertainty'] ?? 0) as num;

    final scoreColor = score >= 70
        ? AppTheme.accent2
        : score >= 40
        ? AppTheme.warn
        : AppTheme.danger;

    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      decoration: BoxDecoration(
        color: AppTheme.panel,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppTheme.border),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        // Header row
        Padding(
          padding: const EdgeInsets.fromLTRB(14, 14, 14, 10),
          child: Row(children: [
            // Day circle
            Container(
              width: 40, height: 40,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: scoreColor.withAlpha(30),
                border: Border.all(color: scoreColor.withAlpha(100), width: 2),
              ),
              child: Center(child: Text('D${index + 1}',
                style: TextStyle(fontSize: 11, color: scoreColor, fontWeight: FontWeight.bold))),
            ),
            const SizedBox(width: 12),
            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('$date', style: const TextStyle(fontSize: 13, color: AppTheme.textPrimary, fontWeight: FontWeight.bold)),
              if (uncertainty > 0)
                Text('±${uncertainty.toStringAsFixed(0)}% uncertainty',
                  style: const TextStyle(fontSize: 9, color: AppTheme.textDim)),
            ])),
            // Fish score bar
            Column(crossAxisAlignment: CrossAxisAlignment.end, children: [
              Text('${score.toInt()}%', style: TextStyle(
                fontSize: 18, fontWeight: FontWeight.bold, color: scoreColor)),
              const Text('fish score', style: TextStyle(fontSize: 8, color: AppTheme.textDim, letterSpacing: 1)),
            ]),
          ]),
        ),

        // Score bar
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: score / 100,
              backgroundColor: AppTheme.bg,
              valueColor: AlwaysStoppedAnimation<Color>(scoreColor),
              minHeight: 4,
            ),
          ),
        ),
        const SizedBox(height: 10),

        // Stats row
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14),
          child: Wrap(spacing: 8, runSpacing: 6, children: [
            if (sst  != null) _Tag('SST ${sst}°C', AppTheme.warn),
            if (wind != null) _Tag('WIND $wind kt', Colors.lightBlue),
            if (wave != null) _Tag('WAVE ${wave}m', AppTheme.accent),
          ]),
        ),

        // Hotspots
        if (hotspots.isNotEmpty) ...[
          const Padding(
            padding: EdgeInsets.fromLTRB(14, 12, 14, 6),
            child: Text('HOTSPOTS', style: TextStyle(
              fontSize: 8, color: AppTheme.textDim, letterSpacing: 2)),
          ),
          for (final h in hotspots.take(4))
            Padding(
              padding: const EdgeInsets.fromLTRB(14, 0, 14, 6),
              child: Row(children: [
                Container(width: 6, height: 6,
                  decoration: const BoxDecoration(shape: BoxShape.circle, color: AppTheme.accent2)),
                const SizedBox(width: 8),
                Expanded(child: Text(
                  h['name']?.toString() ?? '${(h['lat'] ?? 0).toStringAsFixed(2)}°N, ${(h['lon'] ?? 0).toStringAsFixed(2)}°E',
                  style: const TextStyle(fontSize: 11, color: AppTheme.textPrimary))),
                if (h['region'] != null)
                  Text(h['region'].toString(),
                    style: const TextStyle(fontSize: 9, color: AppTheme.textDim)),
              ]),
            ),
        ],
        const SizedBox(height: 10),
      ]),
    );
  }
}

class _Tag extends StatelessWidget {
  final String label;
  final Color color;
  const _Tag(this.label, this.color);

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
    decoration: BoxDecoration(color: color.withAlpha(30), borderRadius: BorderRadius.circular(4)),
    child: Text(label, style: TextStyle(fontSize: 10, color: color)),
  );
}
