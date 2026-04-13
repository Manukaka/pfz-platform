import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:printing/printing.dart';
import '../core/theme.dart';
import '../l10n/strings.dart';
import '../providers/app_state.dart';
import '../services/map_capture_service.dart';
import '../services/pdf_service.dart';

class PdfExportScreen extends StatefulWidget {
  const PdfExportScreen({super.key});

  @override
  State<PdfExportScreen> createState() => _PdfExportScreenState();
}

class _PdfExportScreenState extends State<PdfExportScreen> {
  bool _generating = false;
  String? _status;

  Future<void> _generate(int type) async {
    setState(() { _generating = true; _status = 'Capturing map...'; });
    final state = context.read<AppState>();
    final lang  = state.lang;

    try {
      // Try to capture map screenshot via RepaintBoundary
      final mapImage = await MapCaptureService.instance.capture();

      setState(() => _status = S.t('generating', lang));

      dynamic pdfBytes;
      switch (type) {
        case 0:
          pdfBytes = await PdfService.generatePfzReport(
            mapImage: mapImage, algoZones: state.algoZones,
            aiZones: state.aiZones, lang: lang);
          break;
        case 1:
          pdfBytes = await PdfService.generateIncoisReport(
            zones: state.incoisZones, lang: lang);
          break;
        case 2:
          pdfBytes = await PdfService.generateFullReport(
            mapImage: mapImage, algoZones: state.algoZones,
            aiZones: state.aiZones, incoisZones: state.incoisZones,
            sstGrid: state.sstGrid, forecast: state.forecast, lang: lang);
          break;
      }

      if (!mounted) return;
      setState(() { _generating = false; _status = null; });

      // Open PDF viewer / share dialog
      await Printing.layoutPdf(onLayout: (_) async => pdfBytes);
    } catch (e) {
      if (!mounted) return;
      setState(() { _generating = false; _status = 'Error: $e'; });
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();
    final lang  = state.lang;

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
                Text(S.t('pdf_export', lang), style: const TextStyle(
                  fontSize: 13, fontWeight: FontWeight.bold,
                  color: AppTheme.textPrimary, letterSpacing: 2)),
              ]),
            ),
          ),
        ),

        if (_generating)
          LinearProgressIndicator(
            color: AppTheme.warn, backgroundColor: AppTheme.panel, minHeight: 2),

        Expanded(child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            if (_status != null)
              Container(
                margin: const EdgeInsets.only(bottom: 16),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppTheme.warn.withAlpha(20),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: AppTheme.warn.withAlpha(80)),
                ),
                child: Text(_status!, style: const TextStyle(color: AppTheme.warn, fontSize: 12)),
              ),

            _ExportCard(
              icon: Icons.map,
              color: AppTheme.accent,
              title: S.t('pfz_report', lang),
              description: S.t('pfz_report_desc', lang),
              stats: '${state.algoZones.length} algo + ${state.aiZones.length} AI zones',
              onTap: _generating ? null : () => _generate(0),
            ),
            const SizedBox(height: 12),
            _ExportCard(
              icon: Icons.waves,
              color: AppTheme.warn,
              title: S.t('incois_report', lang),
              description: S.t('incois_report_desc', lang),
              stats: '${state.incoisZones.length} INCOIS zones',
              onTap: _generating ? null : () => _generate(1),
            ),
            const SizedBox(height: 12),
            _ExportCard(
              icon: Icons.article,
              color: AppTheme.accent2,
              title: S.t('full_report', lang),
              description: S.t('full_report_desc', lang),
              stats: 'All data + Day-1 forecast',
              onTap: _generating ? null : () => _generate(2),
            ),
            const SizedBox(height: 24),
            const Center(child: Text(
              'PDF will open for preview and sharing',
              style: TextStyle(fontSize: 11, color: AppTheme.textDim))),
          ],
        )),
      ]),
    );
  }
}

class _ExportCard extends StatelessWidget {
  final IconData icon;
  final Color color;
  final String title;
  final String description;
  final String stats;
  final VoidCallback? onTap;
  const _ExportCard({
    required this.icon, required this.color, required this.title,
    required this.description, required this.stats, this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Opacity(
        opacity: onTap == null ? 0.5 : 1.0,
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppTheme.panel,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: color.withAlpha(80), width: 1.5),
          ),
          child: Row(children: [
            Container(
              width: 48, height: 48,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: color.withAlpha(30),
                border: Border.all(color: color.withAlpha(100)),
              ),
              child: Icon(icon, color: color, size: 22),
            ),
            const SizedBox(width: 14),
            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(title, style: TextStyle(
                fontSize: 13, fontWeight: FontWeight.bold, color: color)),
              const SizedBox(height: 4),
              Text(description, style: const TextStyle(fontSize: 11, color: AppTheme.textDim)),
              const SizedBox(height: 4),
              Text(stats, style: const TextStyle(fontSize: 10, color: AppTheme.textDim)),
            ])),
            Icon(Icons.picture_as_pdf, color: color.withAlpha(150), size: 20),
          ]),
        ),
      ),
    );
  }
}
