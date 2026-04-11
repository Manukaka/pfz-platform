import 'package:flutter/material.dart';
import '../core/theme.dart';

class DataSummaryCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final Color color;
  final String subtitle;

  const DataSummaryCard({
    super.key,
    required this.title,
    required this.value,
    required this.icon,
    required this.color,
    required this.subtitle,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.panel,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppTheme.border),
        boxShadow: [BoxShadow(color: color.withAlpha(25), blurRadius: 12)],
      ),
      child: Row(children: [
        Container(
          width: 44, height: 44,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: color.withAlpha(30),
            border: Border.all(color: color.withAlpha(76)),
          ),
          child: Icon(icon, color: color, size: 22),
        ),
        const SizedBox(width: 14),
        Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(title, style: const TextStyle(fontSize: 9, color: AppTheme.textDim, letterSpacing: 2)),
          const SizedBox(height: 3),
          Text(subtitle, style: const TextStyle(fontSize: 12, color: AppTheme.textPrimary)),
        ]),
        const Spacer(),
        Text(value, style: TextStyle(
          fontSize: 18, color: color, fontWeight: FontWeight.bold,
          shadows: [Shadow(color: color.withAlpha(128), blurRadius: 8)],
        )),
      ]),
    );
  }
}
