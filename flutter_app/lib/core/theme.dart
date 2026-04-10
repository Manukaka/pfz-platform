import 'package:flutter/material.dart';

class AppTheme {
  static const Color bg        = Color(0xFF0a0f1a);
  static const Color panel     = Color(0xFF081226);
  static const Color accent    = Color(0xFF00c8ff);
  static const Color accent2   = Color(0xFF00ff88);
  static const Color warn      = Color(0xFFffaa00);
  static const Color danger    = Color(0xFFff4444);
  static const Color textPrimary  = Color(0xFFe0f0ff);
  static const Color textDim      = Color(0xFF7090a0);
  static const Color border    = Color(0x4D00c8ff); // 30% opacity

  static ThemeData get darkTheme => ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    scaffoldBackgroundColor: bg,
    colorScheme: const ColorScheme.dark(
      primary: accent,
      secondary: accent2,
      surface: panel,
      error: danger,
    ),
    fontFamily: 'SpaceMono',
    appBarTheme: const AppBarTheme(
      backgroundColor: panel,
      foregroundColor: textPrimary,
      elevation: 0,
      surfaceTintColor: Colors.transparent,
    ),
    cardTheme: CardTheme(
      color: panel,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: const BorderSide(color: border, width: 1),
      ),
      elevation: 0,
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: accent,
        foregroundColor: Colors.black,
        textStyle: const TextStyle(fontWeight: FontWeight.bold, letterSpacing: 1.5),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
        minimumSize: const Size.fromHeight(48),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: Colors.black26,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(6),
        borderSide: const BorderSide(color: border),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(6),
        borderSide: const BorderSide(color: border),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(6),
        borderSide: const BorderSide(color: accent, width: 1.5),
      ),
      hintStyle: const TextStyle(color: textDim, fontSize: 13),
      labelStyle: const TextStyle(color: textDim),
    ),
  );
}
