// File: assets/my_styles.ts
// Description: Share screen, card, input, and image styles across the three tabs.

import { StyleSheet } from 'react-native';

export const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f5f7fb',
  },
  scrollView: {
    flex: 1,
    backgroundColor: '#f5f7fb',
  },
  scrollContent: {
    padding: 20,
    paddingBottom: 32,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f7fb',
  },
  eyebrow: {
    fontSize: 12,
    fontWeight: 'bold',
    letterSpacing: 1.5,
    color: '#295d91',
    marginBottom: 8,
  },
  titleText: {
    fontSize: 28,
    lineHeight: 34,
    fontWeight: 'bold',
    color: '#1e293b',
    marginBottom: 12,
  },
  bodyText: {
    fontSize: 16,
    lineHeight: 24,
    color: '#475569',
    marginBottom: 16,
  },
  card: {
    padding: 18,
    backgroundColor: '#ffffff',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#dce3ed',
  },
  postText: {
    fontSize: 18,
    lineHeight: 26,
    color: '#1e293b',
  },
  authorText: {
    fontSize: 13,
    lineHeight: 20,
    color: '#64748b',
    marginTop: 12,
  },
  profileImage: {
    width: 120,
    height: 120,
    borderRadius: 12,
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1e293b',
    marginTop: 20,
    marginBottom: 12,
  },
  picture: {
    width: '100%',
    height: 220,
    backgroundColor: '#ffffff',
    borderRadius: 12,
    marginTop: 20,
  },
  buttonContainer: {
    marginTop: 16,
    marginBottom: 8,
  },
  caption: {
    fontSize: 13,
    lineHeight: 20,
    color: '#64748b',
    marginTop: 12,
  },
  listHeader: {
    marginBottom: 20,
  },
  separator: {
    height: 16,
  },
  listFooter: {
    fontSize: 13,
    lineHeight: 20,
    color: '#64748b',
    textAlign: 'center',
    padding: 20,
  },
  inputCard: {
    padding: 18,
    backgroundColor: '#ffffff',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#dce3ed',
  },
  labelText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#1e293b',
    marginBottom: 8,
  },
  input: {
    height: 50,
    borderColor: '#94a3b8',
    borderWidth: 1,
    borderRadius: 8,
    padding: 12,
    marginBottom: 20,
    fontSize: 16,
    color: '#1e293b',
    backgroundColor: '#ffffff',
  },
  messageText: {
    fontSize: 16,
    lineHeight: 24,
    color: '#295d91',
    marginTop: 20,
  },
});
