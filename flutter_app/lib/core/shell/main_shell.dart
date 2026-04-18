import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../l10n/app_localizations.dart';

class MainShell extends ConsumerWidget {
  final Widget child;
  const MainShell({super.key, required this.child});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final location = GoRouterState.of(context).uri.path;

    final navItems = [
      _NavItem('/home', Icons.home_rounded, Icons.home_outlined, l10n.navHome),
      _NavItem('/map', Icons.map_rounded, Icons.map_outlined, l10n.navMap),
      _NavItem('/samudra', Icons.waves_rounded, Icons.waves_outlined, l10n.navSamudra),
      _NavItem('/ai', Icons.assistant_rounded, Icons.assistant_outlined, l10n.navAi),
      _NavItem('/catch', Icons.set_meal_rounded, Icons.set_meal_outlined, l10n.navCatch),
    ];

    int currentIndex = navItems.indexWhere((item) => location.startsWith(item.path));
    if (currentIndex == -1) currentIndex = 0;

    return Scaffold(
      body: child,
      bottomNavigationBar: NavigationBar(
        selectedIndex: currentIndex,
        onDestinationSelected: (index) => context.go(navItems[index].path),
        destinations: navItems.map((item) => NavigationDestination(
          icon: Icon(item.iconOutlined),
          selectedIcon: Icon(item.iconFilled),
          label: item.label,
        )).toList(),
      ),
    );
  }
}

class _NavItem {
  final String path;
  final IconData iconFilled;
  final IconData iconOutlined;
  final String label;
  const _NavItem(this.path, this.iconFilled, this.iconOutlined, this.label);
}
