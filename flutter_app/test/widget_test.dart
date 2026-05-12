import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:darya_sagar/main.dart';

void main() {
  testWidgets('DaryaSagar app builds', (WidgetTester tester) async {
    await tester.pumpWidget(const ProviderScope(child: DaryaSagarApp()));

    expect(find.byType(MaterialApp), findsOneWidget);
  });
}
