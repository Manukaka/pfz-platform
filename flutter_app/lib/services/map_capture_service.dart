import 'dart:typed_data';
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';

/// Singleton that allows capturing the map as PNG bytes without any external package.
/// MapScreen registers its RepaintBoundary key here; PdfExportScreen calls capture().
class MapCaptureService {
  static final instance = MapCaptureService._();
  MapCaptureService._();

  GlobalKey? _key;

  void register(GlobalKey key) => _key = key;
  void unregister() => _key = null;

  Future<Uint8List?> capture() async {
    final key = _key;
    if (key == null) return null;
    try {
      final boundary = key.currentContext?.findRenderObject() as RenderRepaintBoundary?;
      if (boundary == null) return null;
      final image = await boundary.toImage(pixelRatio: 2.0);
      final byteData = await image.toByteData(format: ui.ImageByteFormat.png);
      return byteData?.buffer.asUint8List();
    } catch (_) {
      return null;
    }
  }
}
