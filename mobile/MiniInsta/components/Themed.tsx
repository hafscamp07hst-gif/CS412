// File: components/Themed.tsx
// Description: Provide text and view components that follow the current color theme.

/**
 * Learn more about Light and Dark modes:
 * https://docs.expo.io/guides/color-schemes/
 */
import { Text as DefaultText, View as DefaultView, type TextProps as NativeTextProps, type ViewProps as NativeViewProps } from 'react-native';

import { useColorScheme } from './useColorScheme';

import Colors from '@/constants/Colors';

// Allow callers to override colors separately for light and dark modes.
type ThemeProps = {
  lightColor?: string;
  darkColor?: string;
};

// Combine the theme options with the current React Native component props.
export type TextProps = ThemeProps & NativeTextProps;
export type ViewProps = ThemeProps & NativeViewProps;

/** Return a supplied color override or the default color for the active theme. */
export function useThemeColor(
  props: { light?: string; dark?: string },
  colorName: keyof typeof Colors.light & keyof typeof Colors.dark
) {
  const theme = useColorScheme();
  // Look up the optional override for the selected light or dark theme.
  const colorFromProps = props[theme];

  if (colorFromProps) {
    return colorFromProps;
  } else {
    return Colors[theme][colorName];
  }
}

/** Apply the theme text color while keeping the normal Text props. */
export function Text(props: TextProps) {
  const { style, lightColor, darkColor, ...otherProps } = props;
  const color = useThemeColor({ light: lightColor, dark: darkColor }, 'text');

  return <DefaultText style={[{ color }, style]} {...otherProps} />;
}

/** Apply the theme background color while keeping the normal View props. */
export function View(props: ViewProps) {
  const { style, lightColor, darkColor, ...otherProps } = props;
  const backgroundColor = useThemeColor({ light: lightColor, dark: darkColor }, 'background');

  return <DefaultView style={[{ backgroundColor }, style]} {...otherProps} />;
}
