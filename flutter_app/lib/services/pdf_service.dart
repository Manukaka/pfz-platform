import 'dart:typed_data';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import '../models/pfz_zone.dart';
import '../models/ai_zone.dart';
import '../models/incois_zone.dart';

class PdfService {
  /// Today's PFZ report: map screenshot + algo + AI zones table
  static Future<Uint8List> generatePfzReport({
    required Uint8List? mapImage,
    required List<PfzZone> algoZones,
    required List<AiZone> aiZones,
    required String lang,
  }) async {
    final doc = pw.Document();
    final now = DateTime.now();
    final dateStr = '${now.day.toString().padLeft(2,'0')}/${now.month.toString().padLeft(2,'0')}/${now.year}';

    final title = lang == 'mr' ? 'दर्यासागर - PFZ अहवाल' :
                  lang == 'hi' ? 'दर्यासागर - PFZ रिपोर्ट' :
                                 'Daryasagar - PFZ Report';

    doc.addPage(pw.MultiPage(
      pageFormat: PdfPageFormat.a4,
      margin: const pw.EdgeInsets.all(24),
      build: (ctx) => [
        // Header
        pw.Container(
          padding: const pw.EdgeInsets.all(12),
          decoration: pw.BoxDecoration(
            color: PdfColor.fromHex('#081226'),
            borderRadius: const pw.BorderRadius.all(pw.Radius.circular(8)),
          ),
          child: pw.Row(
            mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
            children: [
              pw.Text(title, style: pw.TextStyle(
                fontSize: 16, fontWeight: pw.FontWeight.bold,
                color: PdfColors.white)),
              pw.Text(dateStr, style: const pw.TextStyle(fontSize: 11, color: PdfColors.grey300)),
            ],
          ),
        ),
        pw.SizedBox(height: 14),

        // Map image
        if (mapImage != null) ...[
          pw.Text('MAP SCREENSHOT', style: const pw.TextStyle(fontSize: 9, color: PdfColors.grey600)),
          pw.SizedBox(height: 6),
          pw.Image(pw.MemoryImage(mapImage), fit: pw.BoxFit.fitWidth, width: double.infinity),
          pw.SizedBox(height: 14),
        ],

        // Algorithmic PFZ zones
        if (algoZones.isNotEmpty) ...[
          pw.Text('ALGORITHMIC PFZ ZONES (${algoZones.length})',
            style: pw.TextStyle(fontSize: 10, fontWeight: pw.FontWeight.bold, color: PdfColor.fromHex('#00c8ff'))),
          pw.SizedBox(height: 6),
          pw.Table(
            border: pw.TableBorder.all(color: PdfColors.grey400, width: 0.5),
            columnWidths: {
              0: const pw.FlexColumnWidth(1.2),
              1: const pw.FlexColumnWidth(1.2),
              2: const pw.FlexColumnWidth(1.5),
              3: const pw.FlexColumnWidth(0.8),
              4: const pw.FlexColumnWidth(0.8),
            },
            children: [
              pw.TableRow(
                decoration: const pw.BoxDecoration(color: PdfColors.grey200),
                children: ['Lat°N', 'Lon°E', 'Species', 'Level', 'Conf%'].map((h) =>
                  pw.Padding(padding: const pw.EdgeInsets.all(6),
                    child: pw.Text(h, style: pw.TextStyle(fontSize: 9, fontWeight: pw.FontWeight.bold)))).toList(),
              ),
              for (final z in algoZones)
                pw.TableRow(children: [
                  z.lat.toStringAsFixed(4),
                  z.lon.toStringAsFixed(4),
                  z.fishEn ?? '--',
                  z.level.toUpperCase(),
                  z.confidenceScore != null ? '${z.confidenceScore}%' : '--',
                ].map((v) =>
                  pw.Padding(padding: const pw.EdgeInsets.all(5),
                    child: pw.Text(v, style: const pw.TextStyle(fontSize: 8)))).toList()),
            ],
          ),
          pw.SizedBox(height: 14),
        ],

        // AI Agent zones
        if (aiZones.isNotEmpty) ...[
          pw.Text('AI AGENT PFZ ZONES (${aiZones.length})',
            style: pw.TextStyle(fontSize: 10, fontWeight: pw.FontWeight.bold, color: PdfColor.fromHex('#00ff88'))),
          pw.SizedBox(height: 6),
          pw.Table(
            border: pw.TableBorder.all(color: PdfColors.grey400, width: 0.5),
            columnWidths: {
              0: const pw.FlexColumnWidth(1.2),
              1: const pw.FlexColumnWidth(1.2),
              2: const pw.FlexColumnWidth(1.5),
              3: const pw.FlexColumnWidth(0.8),
              4: const pw.FlexColumnWidth(1.2),
            },
            children: [
              pw.TableRow(
                decoration: const pw.BoxDecoration(color: PdfColors.grey200),
                children: ['Lat°N', 'Lon°E', 'Species', 'Level', 'Region'].map((h) =>
                  pw.Padding(padding: const pw.EdgeInsets.all(6),
                    child: pw.Text(h, style: pw.TextStyle(fontSize: 9, fontWeight: pw.FontWeight.bold)))).toList(),
              ),
              for (final z in aiZones)
                pw.TableRow(children: [
                  z.lat.toStringAsFixed(4),
                  z.lon.toStringAsFixed(4),
                  z.fishEn ?? '--',
                  z.level.toUpperCase(),
                  z.region ?? '--',
                ].map((v) =>
                  pw.Padding(padding: const pw.EdgeInsets.all(5),
                    child: pw.Text(v, style: const pw.TextStyle(fontSize: 8)))).toList()),
            ],
          ),
          pw.SizedBox(height: 14),
        ],

        // Footer
        pw.Divider(color: PdfColors.grey400),
        pw.SizedBox(height: 6),
        pw.Text('Generated by Daryasagar | samudra-ai.onrender.com | $dateStr',
          style: const pw.TextStyle(fontSize: 8, color: PdfColors.grey500)),
      ],
    ));

    return doc.save();
  }

  /// INCOIS advisory zones list
  static Future<Uint8List> generateIncoisReport({
    required List<IncoisZone> zones,
    required String lang,
  }) async {
    final doc = pw.Document();
    final now = DateTime.now();
    final dateStr = '${now.day.toString().padLeft(2,'0')}/${now.month.toString().padLeft(2,'0')}/${now.year}';

    doc.addPage(pw.MultiPage(
      pageFormat: PdfPageFormat.a4,
      margin: const pw.EdgeInsets.all(24),
      build: (ctx) => [
        pw.Container(
          padding: const pw.EdgeInsets.all(12),
          decoration: pw.BoxDecoration(
            color: PdfColor.fromHex('#081226'),
            borderRadius: const pw.BorderRadius.all(pw.Radius.circular(8)),
          ),
          child: pw.Row(
            mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
            children: [
              pw.Text('INCOIS PFZ Advisory', style: pw.TextStyle(
                fontSize: 16, fontWeight: pw.FontWeight.bold, color: PdfColors.white)),
              pw.Text(dateStr, style: const pw.TextStyle(fontSize: 11, color: PdfColors.grey300)),
            ],
          ),
        ),
        pw.SizedBox(height: 14),
        if (zones.isEmpty)
          pw.Text('No INCOIS zones available', style: const pw.TextStyle(color: PdfColors.grey500))
        else ...[
          pw.Text('INCOIS SAMUDRA ZONES (${zones.length})',
            style: pw.TextStyle(fontSize: 10, fontWeight: pw.FontWeight.bold, color: PdfColor.fromHex('#ffaa00'))),
          pw.SizedBox(height: 6),
          pw.Table(
            border: pw.TableBorder.all(color: PdfColors.grey400, width: 0.5),
            children: [
              pw.TableRow(
                decoration: const pw.BoxDecoration(color: PdfColors.grey200),
                children: ['#', 'Lat°N', 'Lon°E', 'Region', 'Date'].map((h) =>
                  pw.Padding(padding: const pw.EdgeInsets.all(6),
                    child: pw.Text(h, style: pw.TextStyle(fontSize: 9, fontWeight: pw.FontWeight.bold)))).toList(),
              ),
              for (int i = 0; i < zones.length; i++)
                pw.TableRow(children: [
                  '${i + 1}',
                  zones[i].lat.toStringAsFixed(4),
                  zones[i].lon.toStringAsFixed(4),
                  zones[i].region ?? '--',
                  zones[i].date ?? '--',
                ].map((v) =>
                  pw.Padding(padding: const pw.EdgeInsets.all(5),
                    child: pw.Text(v, style: const pw.TextStyle(fontSize: 8)))).toList()),
            ],
          ),
        ],
        pw.SizedBox(height: 14),
        pw.Divider(color: PdfColors.grey400),
        pw.SizedBox(height: 6),
        pw.Text('Source: INCOIS Samudra | Generated by Daryasagar | $dateStr',
          style: const pw.TextStyle(fontSize: 8, color: PdfColors.grey500)),
      ],
    ));
    return doc.save();
  }

  /// Full ocean report combining everything
  static Future<Uint8List> generateFullReport({
    required Uint8List? mapImage,
    required List<PfzZone> algoZones,
    required List<AiZone> aiZones,
    required List<IncoisZone> incoisZones,
    required List<Map<String, double>> sstGrid,
    required List<dynamic> forecast,
    required String lang,
  }) async {
    final doc = pw.Document();
    final now = DateTime.now();
    final dateStr = '${now.day.toString().padLeft(2,'0')}/${now.month.toString().padLeft(2,'0')}/${now.year}';
    final title = lang == 'mr' ? 'दर्यासागर - संपूर्ण समुद्र अहवाल' :
                  lang == 'hi' ? 'दर्यासागर - पूर्ण समुद्र रिपोर्ट' :
                                 'Daryasagar - Full Ocean Report';

    // SST stats
    double sstSum = 0, sstMin = 99, sstMax = -99;
    for (final p in sstGrid) {
      final v = p['sst'] ?? 0;
      sstSum += v; if (v < sstMin) sstMin = v; if (v > sstMax) sstMax = v;
    }
    final sstAvg = sstGrid.isNotEmpty ? sstSum / sstGrid.length : 0;

    doc.addPage(pw.MultiPage(
      pageFormat: PdfPageFormat.a4,
      margin: const pw.EdgeInsets.all(24),
      build: (ctx) => [
        pw.Container(
          padding: const pw.EdgeInsets.all(12),
          decoration: pw.BoxDecoration(color: PdfColor.fromHex('#081226'),
            borderRadius: const pw.BorderRadius.all(pw.Radius.circular(8))),
          child: pw.Row(mainAxisAlignment: pw.MainAxisAlignment.spaceBetween, children: [
            pw.Text(title, style: pw.TextStyle(fontSize: 14, fontWeight: pw.FontWeight.bold, color: PdfColors.white)),
            pw.Text(dateStr, style: const pw.TextStyle(fontSize: 10, color: PdfColors.grey300)),
          ]),
        ),
        pw.SizedBox(height: 14),
        if (mapImage != null) ...[
          pw.Image(pw.MemoryImage(mapImage), fit: pw.BoxFit.fitWidth),
          pw.SizedBox(height: 14),
        ],
        // Summary stats
        pw.Row(children: [
          _statBox('ALGO PFZ', '${algoZones.length}', PdfColor.fromHex('#00c8ff')),
          pw.SizedBox(width: 8),
          _statBox('AI PFZ', '${aiZones.length}', PdfColor.fromHex('#00ff88')),
          pw.SizedBox(width: 8),
          _statBox('INCOIS', '${incoisZones.length}', PdfColor.fromHex('#ffaa00')),
          pw.SizedBox(width: 8),
          _statBox('SST AVG', '${sstAvg.toStringAsFixed(1)}°C', PdfColors.deepOrange),
        ]),
        pw.SizedBox(height: 14),
        // Day 1 forecast
        if (forecast.isNotEmpty) ...[
          pw.Text('DAY-1 FORECAST', style: pw.TextStyle(fontSize: 10, fontWeight: pw.FontWeight.bold)),
          pw.SizedBox(height: 6),
          _forecastRow(forecast[0] as Map<String, dynamic>),
          pw.SizedBox(height: 14),
        ],
        // All zone coordinates
        pw.Text('ALL PFZ COORDINATES', style: pw.TextStyle(fontSize: 10, fontWeight: pw.FontWeight.bold)),
        pw.SizedBox(height: 6),
        for (final z in algoZones.take(20))
          pw.Text('  Algo  ${z.lat.toStringAsFixed(4)}°N  ${z.lon.toStringAsFixed(4)}°E  ${z.level.toUpperCase()}  ${z.fishEn ?? ""}',
            style: const pw.TextStyle(fontSize: 8, color: PdfColors.grey800)),
        for (final z in aiZones.take(10))
          pw.Text('  AI    ${z.lat.toStringAsFixed(4)}°N  ${z.lon.toStringAsFixed(4)}°E  ${z.level.toUpperCase()}  ${z.fishEn ?? ""}',
            style: const pw.TextStyle(fontSize: 8, color: PdfColors.grey800)),
        for (final z in incoisZones.take(10))
          pw.Text('  INCOIS ${z.lat.toStringAsFixed(4)}°N  ${z.lon.toStringAsFixed(4)}°E  ${z.region ?? ""}',
            style: const pw.TextStyle(fontSize: 8, color: PdfColors.grey800)),
        pw.SizedBox(height: 14),
        pw.Divider(color: PdfColors.grey400),
        pw.Text('Generated by Daryasagar | samudra-ai.onrender.com | $dateStr',
          style: const pw.TextStyle(fontSize: 8, color: PdfColors.grey500)),
      ],
    ));
    return doc.save();
  }

  static pw.Widget _statBox(String label, String value, PdfColor color) {
    return pw.Expanded(child: pw.Container(
      padding: const pw.EdgeInsets.all(10),
      decoration: pw.BoxDecoration(
        border: pw.Border.all(color: color, width: 1),
        borderRadius: const pw.BorderRadius.all(pw.Radius.circular(6)),
      ),
      child: pw.Column(crossAxisAlignment: pw.CrossAxisAlignment.start, children: [
        pw.Text(label, style: pw.TextStyle(fontSize: 8, color: PdfColors.grey600)),
        pw.Text(value, style: pw.TextStyle(fontSize: 14, fontWeight: pw.FontWeight.bold, color: color)),
      ]),
    ));
  }

  static pw.Widget _forecastRow(Map<String, dynamic> d) {
    return pw.Container(
      padding: const pw.EdgeInsets.all(10),
      decoration: pw.BoxDecoration(
        border: pw.Border.all(color: PdfColors.grey400, width: 0.5),
        borderRadius: const pw.BorderRadius.all(pw.Radius.circular(6)),
      ),
      child: pw.Row(mainAxisAlignment: pw.MainAxisAlignment.spaceBetween, children: [
        pw.Text('Date: ${d['date'] ?? 'Today'}', style: const pw.TextStyle(fontSize: 9)),
        pw.Text('SST: ${d['sst'] ?? '--'}°C',   style: const pw.TextStyle(fontSize: 9)),
        pw.Text('Wind: ${d['wind_speed'] ?? '--'} kt', style: const pw.TextStyle(fontSize: 9)),
        pw.Text('Score: ${d['fish_score'] ?? '--'}%',  style: const pw.TextStyle(fontSize: 9)),
      ]),
    );
  }
}
