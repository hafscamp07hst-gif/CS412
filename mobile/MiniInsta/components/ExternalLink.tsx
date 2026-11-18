// File: components/ExternalLink.tsx
// Description: Open external links in the browser appropriate for each platform.

import { Link } from 'expo-router';
import * as WebBrowser from 'expo-web-browser';
import type { ComponentProps } from 'react';
import { Platform } from 'react-native';

/** Use a browser tab on web and an in-app browser on native platforms. */
export function ExternalLink(props: Omit<ComponentProps<typeof Link>, 'href'> & { href: string }) {
  // Keep the provided URL compatible with Expo Router's href type.
  return (
    <Link
      target="_blank"
      {...props}
      href={props.href as ComponentProps<typeof Link>['href']}
      onPress={(e) => {
        if (Platform.OS !== 'web') {
          // Prevent the default behavior of linking to the default browser on native.
          e.preventDefault();
          // Open the link in an in-app browser.
          WebBrowser.openBrowserAsync(props.href as string);
        }
      }}
    />
  );
}
